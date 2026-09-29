---
title: Deploye til produksjon med GitHub Actions
description: La GitHub Actions validere og planlegge en bundle med jobber og pipelines på pull requests, og deploye den til prod når endringen merges inn i main.
diataxis: how-to
---

# Deploye til produksjon med GitHub Actions

Denne guiden viser hvordan GitHub Actions kan ta over deployen av en
[bundle](../../om-plattformen/konsepter/databricks-bundles.md). På hver pull request
validerer og planlegger workflowen bundlen mot både stage og prod, så du ser hva endringen
vil gjøre i prod før du merger den inn. Når endringen merges inn i `main`, deployes
bundlen til prod. Autentiseringen bruker OpenID Connect (OIDC) mellom GitHub og
Databricks, mot service principals som Dataspeilet setter opp, så ingen hemmeligheter
lagres i GitHub.

## Før du begynner

Sørg for at du har:

- En bundle med targetene `stage` og `prod`, se [Ta i bruk bundles](ta-i-bruk-bundles.md).
- Bundlen i et repo under `oslokommune` på GitHub, der du kan opprette workflows og
  administrere miljøer (**Settings → Environments**).
- Godtatt brukervilkårene og gjennomført personvern- og risikovurdering for teamets bruk
  av data, se [Brukervilkår og ansvar](../../referanse/brukervilkaar.md). Dette må være på
  plass før noe kjører i prod.

## Trinn 1: Be Dataspeilet om OIDC-oppsett

Skriv i [#dig-dataspeilet-support](https://oslokommune.slack.com/archives/C01DE13PLDP)
hvilket repo bundlen ligger i og hvilke workspaces den skal deployes til. Er repoet
opprettet etter 15. juli 2026, si fra om det, da trenger OIDC-oppsettet et annet format.
Dataspeilet setter opp to service principals per workspace:

- `<workspace>-gha-prs`, som validerer og planlegger fra pull requests
- `<workspace>-gha-deploy`, som deployer fra et GitHub-miljø og kjører jobbene

Denne guiden bruker `gha-prs` i både stage- og prod-workspacet, og `gha-deploy` i
prod-workspacet. Be samtidig om at `gha-deploy` får rettigheter i katalogen og skjemaene
jobbene skal lese og skrive i. Det følger ikke med oppsettet av service principalen.

Du får tilbake application ID for hver service principal, og navnet på GitHub-miljøet for
prod-workspacet, normalt `prod`. Navnet er en del av OIDC-oppsettet, så det må brukes
nøyaktig slik i neste trinn. Se [Roller og
rettigheter](../../referanse/roller-og-rettigheter.md#github-actions-service-principals) for
hva de to service principalene kan gjøre.

## Trinn 2: Opprett GitHub-miljøet og variablene

1. Gå til **Settings → Environments** i repoet og opprett miljøet `prod`.
2. Legg til variabelen `DATABRICKS_CLIENT_ID` i miljøet, med application ID for
   `gha-deploy` i prod-workspacet.
3. Gå til **Settings → Secrets and variables → Actions → Variables** og legg til
   repovariablene `DATABRICKS_PR_CLIENT_ID_STAGE` og `DATABRICKS_PR_CLIENT_ID_PROD`, med
   application ID for `gha-prs` i henholdsvis stage- og prod-workspacet.

Application ID er ikke en hemmelighet, så variabler er riktig sted. Workspace-adressen
trenger du ikke oppgi, den står allerede i `workspace.host` per target i `databricks.yml`.

## Trinn 3: Sett identitet og rettigheter i prod-targetet

Åpne `databricks.yml` og sett hvem som kjører jobbene i prod, og hvem som kan se og styre
dem. Bytt ut plassholderne med verdiene fra trinn 1 og teamets admin-gruppe:

```yaml
targets:
  prod:
    mode: production
    workspace:
      host: https://prod-workspace.cloud.databricks.com
      root_path: ~/.bundle/${bundle.name}/${bundle.target}
    run_as:
      service_principal_name: <application-id for gha-deploy>
    permissions:
      - group_name: <teamets admin-gruppe>
        level: CAN_MANAGE
      - service_principal_name: <application-id for gha-prs>
        level: CAN_VIEW
```

- `run_as` tar application ID, ikke visningsnavnet.
- `~/` i `root_path` er hjemområdet til identiteten som deployer, altså deploy-service
  principalen.
- `permissions` gjelder både jobbene, pipelinene og deploy-mappa. `CAN_VIEW` til
  PR-service principalen er det som lar pull request-workflowen lese deploy-tilstanden og
  vise en plan mot prod.
- Stage-targetet lar du stå i `development`-mode uten `run_as`, ellers må alle som
  deployer fra egen maskin ha `CAN_USE` på service principalen.

## Trinn 4: Skriv workflowene

Opprett `.github/workflows/pr.yml`, som validerer og planlegger mot begge targetene på hver
pull request mot `main`:

```yaml
name: PR

on:
  pull_request:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  plan:
    name: plan (${{ matrix.target }})
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        include:
          - target: stage
            client_id: ${{ vars.DATABRICKS_PR_CLIENT_ID_STAGE }}
          - target: prod
            client_id: ${{ vars.DATABRICKS_PR_CLIENT_ID_PROD }}
    env:
      DATABRICKS_AUTH_TYPE: github-oidc
      DATABRICKS_CLIENT_ID: ${{ matrix.client_id }}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: astral-sh/setup-uv@c18668ad3cf93ea998bef934396af7bb5c839dc7 # v10.2.0
      - uses: databricks/setup-cli@fd1d91d9d3b5f1191a2aae9206f7c68a997dc52d # v1.16.0
      - name: Validate
        run: databricks bundle validate -t ${{ matrix.target }}
      - name: Plan
        run: databricks bundle plan -t ${{ matrix.target }}
```

Opprett så `.github/workflows/deploy.yml`, som deployer til prod når noe pushes til `main`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

concurrency: deploy

jobs:
  prod:
    runs-on: ubuntu-latest
    environment: prod
    env:
      DATABRICKS_AUTH_TYPE: github-oidc
      DATABRICKS_CLIENT_ID: ${{ vars.DATABRICKS_CLIENT_ID }}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: astral-sh/setup-uv@c18668ad3cf93ea998bef934396af7bb5c839dc7 # v10.2.0
      - uses: databricks/setup-cli@fd1d91d9d3b5f1191a2aae9206f7c68a997dc52d # v1.16.0
      - name: Deploy
        run: databricks bundle deploy -t prod
```

- `id-token: write` lar jobben hente et OIDC-token fra GitHub. `environment` avgjør hvilket
  miljø tokenet utstedes for, og dermed hvilken service principal jobben kan logge inn som.
- `concurrency` hindrer at to kjøringer deployer om hverandre.
- Actions er pinnet til commit-hash, ikke til tag. En tag kan flyttes av den som eier
  actionen, en hash kan ikke. Kommentaren bak sier hvilken versjon hashen tilsvarer.
- `uv` trengs fordi `plan` og `deploy` bygger wheelet før de sammenligner med det som er
  deployet.
- Deployen har ikke `--auto-approve`. En endring som vil slette og gjenskape en pipeline
  med tabellene dens stopper derfor jobben i stedet for å gjøre det uten å spørre, se
  [Feilsøking](#feilsking).

## Bekreft resultatet

Lag en liten endring på en branch og åpne en pull request. Under **Checks** skal `plan`
kjøre for begge targetene. Planen for prod viser hva som endres når du merger inn, for
eksempel:

```
update jobs.paddeobservasjoner_job

Plan: 0 to add, 1 to change, 0 to delete, 2 unchanged
```

Planen for stage viser at konfigurasjonen er gyldig for stage-workspacet, men sier «to add»
for alle ressursene, siden `development`-mode gir hver identitet sin egen kopi.

Merge inn, og følg workflowen **Deploy** under **Actions**. I prod-workspacet finner du
jobbene og pipelinene under **Jobs & Pipelines** uten `[dev ...]`-prefiks, med
deploy-service principalen som **Run as**. Filene ligger under
`/Workspace/Users/<application-id>/.bundle/`.

## Feilsøking

??? failure "Autentiseringen feiler i workflowen"

    OIDC-tokenet inneholder reponavnet og miljønavnet, og begge må stemme med det
    Dataspeilet registrerte. Sjekk at `environment` i jobben er skrevet nøyaktig som
    miljønavnet du fikk i trinn 1, og at repoet ikke er gitt nytt navn eller flyttet. Er
    repoet opprettet etter 15. juli 2026, trenger OIDC-oppsettet et annet format, se
    trinn 1. Stemmer alt, si fra til Dataspeilet.

??? failure "Plan mot prod feiler på den første pull requesten"

    PR-service principalen får lesetilgang til deploy-mappa først når bundlen er deployet
    med `permissions` fra trinn 3. Merge inn endringen én gang. Fra neste pull request får
    du plan mot prod.

??? failure "Deploy feiler fordi en pipeline må slettes og gjenskapes"

    Noen endringer kan ikke gjøres på en eksisterende pipeline. Da sletter bundlen
    pipelinen og tabellene dens, og lager dem på nytt. Planen på pull requesten viser
    dette som `recreate`. Er det meningen, legg til `--auto-approve` på `bundle deploy` i
    workflowen for denne ene deployen, og fjern flagget etterpå. Er det ikke meningen, ta
    endringen tilbake.

??? failure "Jobben kjører, men feiler med manglende rettigheter i katalogen"

    Deploy-service principalen kjører jobbene og trenger rettigheter i katalogen og
    skjemaene den skriver til. Be Dataspeilet om å gi den det.

??? failure "Deploy feiler med at service principalen ikke finnes"

    `run_as.service_principal_name` skal være application ID, en UUID, ikke visningsnavnet
    `<workspace>-gha-deploy`. `validate` fanger ikke dette, feilen kommer først i deploy.

## Relatert innhold

**Guider:**

- [Ta i bruk bundles](ta-i-bruk-bundles.md)

**Forklaringer og referanser:**

- [Declarative Automation Bundles](../../om-plattformen/konsepter/databricks-bundles.md#deployflyt)
- [Roller og rettigheter](../../referanse/roller-og-rettigheter.md#github-actions-service-principals)
- [Brukervilkår og ansvar](../../referanse/brukervilkaar.md)

**Ekstern dokumentasjon:**

- [Enable workload identity federation for GitHub Actions](https://docs.databricks.com/aws/en/dev-tools/auth/provider-github)
- [Specify a run identity for a Declarative Automation Bundles workflow](https://docs.databricks.com/aws/en/dev-tools/bundles/run-as)
- [Managing environments for deployment](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)
