---
title: Ta i bruk bundles
description: Hvordan pakke og deploye jobber til Databricks med bundles.
diataxis: how-to
---

# Ta i bruk bundles

Denne guiden viser hvordan du oppretter, konfigurerer og deployer en bundle til
flere Databricks-workspaces. Se [Declarative Automation Bundles
(konsept)](../../om-plattformen/konsepter/databricks-bundles.md) for bakgrunn om
targets, modes og wheel-strategier.

## Forutsetninger

- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install.html)
  installert og autentisert mot workspacet ditt
- [uv](https://docs.astral.sh/uv/) installert (for wheel-bygging)
- Tilgang til minst ett Databricks-workspace
- Klonet `padda-golden-path`-repoet

## Opprette en ny bundle fra malen

Bruk Padda Asset Bundle Templates til å opprette en ny bundle:

```bash
databricks bundle init /sti/til/padda-golden-path/bundle-templates
```

Du blir spurt om Unity Catalog-navn, workspace-host for stage og prod,
domene-navn, domene-beskrivelse og hvilken `setup_type` du vil bruke (`default`,
`minimal` eller `tailored`). Se
[bundle-templates/README.md](https://github.com/oslokommune/padda-golden-path/blob/main/bundle-templates/README.md)
for hva de ulike valgene betyr.

Med `setup_type: default` genererer malen omtrent denne strukturen:

```
my-domain/
  databricks.yml                       # Hovedkonfigurasjon med targets
  pyproject.toml                       # Python-prosjekt (uv, ruff, mypy)
  resources/
    example_job.yml                    # Jobb på klassisk compute
    example_serverless_job.yml         # Jobb på serverless compute
    example_pipeline_job.yml           # Eksempel-pipeline
  notebooks/
    example_job.py
    pipelines/example-pipeline/...
  src/
    my_domain/
      main.py                          # Python-kode pakket som wheel
```

## Konfigurere targets for stage og prod

### Sette workspace-host per target

Åpne `databricks.yml` og sett `workspace.host` for hvert target til riktig
workspace-URL:

```yaml
targets:
  stage:
    mode: development
    default: true
    workspace:
      host: https://stage-workspace.cloud.databricks.com

  prod:
    mode: production
    workspace:
      host: https://prod-workspace.cloud.databricks.com
      root_path: ~/.bundle/${bundle.name}/${bundle.target}
```

!!! warning "Ikke hardkod workspace-spesifikke stier i jobbdefinisjoner"
    Bruk variabler for alt som endrer seg mellom flere workspaces — kataloger,
    schemaer, filstier. Hardkodede verdier bryter når du deployer til et annet
    miljø.

### Sette variabler per target

Definer variabler i en `variables`-blokk på toppnivå, og sett verdiene
eksplisitt for hvert target:

```yaml
variables:
  catalog:
    description: Unity Catalog-katalog
  schema:
    description: Schema for tabeller

targets:
  stage:
    mode: development
    default: true
    workspace:
      host: https://stage-workspace.cloud.databricks.com
    variables:
      catalog: dev_catalog
      schema: default

  prod:
    mode: production
    workspace:
      host: https://prod-workspace.cloud.databricks.com
      root_path: ~/.bundle/${bundle.name}/${bundle.target}
    variables:
      catalog: prod_catalog
      schema: production
```

Referer til variablene i jobbdefinisjoner med `${var.catalog}` og
`${var.schema}`.

!!! tip "Unngå `default:` for miljøspesifikke variabler"
    Eksplisitt verdi per target gjør at `databricks bundle validate` feiler
    høylytt hvis du glemmer en variabel i et nytt target. Bruk `default:` kun
    for variabler som er miljøuavhengige (for eksempel en timeout).

### Sette `root_path`, permissions og `run_as` for prod

`production`-mode krever et eksplisitt `root_path` (eller at du deployer som
service principal). I tillegg anbefaler vi å definere eierskap med `permissions`
og `run_as`, slik at produksjonsressursene ikke er knyttet til en enkelt
utviklers konto. Begge tar service principalens application ID (en UUID), ikke
visningsnavnet:

```yaml
targets:
  prod:
    mode: production
    workspace:
      host: https://prod-workspace.cloud.databricks.com
      root_path: ~/.bundle/${bundle.name}/${bundle.target}
    run_as:
      service_principal_name: <application-id>
    permissions:
      - service_principal_name: <application-id>
        level: CAN_MANAGE
```

!!! note "Hvorfor dette `root_path`-mønsteret?"
    `~/` peker til service principalens hjemområde, så eierskapet til ressursene blir
    tydelig. Se
    [Root path og eierskap i prod](../../om-plattformen/konsepter/databricks-bundles.md#root-path-og-eierskap-i-prod)
    for detaljer.

## Deklarere volumes som bundle-ressurser

Hvis jobbene dine leser fra og skriver til Unity Catalog Volumes som er tett
koblet til koden (input-opplastinger, mellomliggende output, sluttresultater),
kan du deklarere volumene som bundle-ressurser i samme repo som jobbene. Da
følger volume-definisjonen samme livssyklus som koden, og endringer kan reviewes
i samme pull request.

```yaml
resources:
  volumes:
    uploads:
      catalog_name: ${var.catalog}
      schema_name: bronze_default
      name: uploads
      volume_type: MANAGED
```

Volumes for team-spesifikk data hører hjemme i team-repoet sammen med koden,
mens kataloger og delte schemas administreres i `padda-iac`. Se
[Ansvarsfordeling mellom bundles og
padda-iac](../../referanse/databricks-bundles.md#ansvarsfordeling-mellom-bundles-og-padda-iac)
for full oversikt.

!!! danger "`bundle destroy` sletter underliggende data"
    `databricks bundle destroy` fjerner alle ressurser bundlen eier, inkludert
    volumes. Det samme gjelder hvis du endrer `name`, `catalog_name` eller
    `schema_name` på et eksisterende volume — bundlen sletter det gamle og oppretter
    et nytt. Vær spesielt varsom med volumes som inneholder produksjonsdata, eller
    som refereres fra andre systemer (for eksempel en hardkodet S3-sti i et API).

## Håndtere Python wheels

### Ditt eget prosjekt: artifacts-seksjonen

Hvis prosjektet ditt har en `pyproject.toml`, legg til en `artifacts`-seksjon
som bygger wheelet automatisk ved deploy:

```yaml
artifacts:
  python_artifact:
    type: whl
    build: uv build --wheel

targets:
  stage:
    mode: development
    default: true
    presets:
      artifacts_dynamic_version: true
```

!!! tip "Bruk `artifacts_dynamic_version` i stage"
    Uten dette kan clusteret cache en gammel versjon av
    wheelet. `artifacts_dynamic_version` legger til et unikt tidsstempel slik at
    clusteret alltid henter siste versjon.

Referer til wheelet i jobbdefinisjonen. På serverless compute deklareres
avhengigheter i en `environments`-blokk på jobb-nivå, og tasken peker på
environment via `environment_key`:

```yaml
resources:
  jobs:
    my_job:
      name: my_job
      tasks:
        - task_key: my_task
          timeout_seconds: 600
          python_wheel_task:
            package_name: my_project
            entry_point: main
            parameters:
              - "--input-dir=${var.input_dir}"
              - "--output-dir=${var.output_dir}"
          environment_key: default
      environments:
        - environment_key: default
          spec:
            client: "5"
            dependencies:
              - ../dist/*.whl
```

`spec.client` angir versjonen av
[serverless-environmentet](https://docs.databricks.com/aws/en/release-notes/serverless/environment-version/)
— bruk siste versjon.

Flere tasks i samme jobb kan dele én `environment_key`, eller bruke ulike
`environments` hvis de trenger forskjellige avhengigheter.

!!! info "Klassisk compute"
    Hvis du trenger klassisk compute (for eksempel langtlevende clustere, GPU eller
    init-scripts), definerer du `job_clusters` eller `existing_cluster_id` på
    jobben istedenfor `environments`, og bruker `libraries:` på tasken. Se
    [Klassisk compute (referanse)](../../referanse/databricks-bundles.md#klassisk-compute)
    for et fullt eksempel.

### Tredjepartsbiblioteker

Workspacene har ikke tilgang til internett, så clusteret kan ikke hente
avhengigheter fra PyPI (se [Hvorfor clustere ikke har
internett](../../om-plattformen/konsepter/databricks-bundles.md#hvorfor-clustere-ikke-har-internett)
for bakgrunn). For tredjepartsbiblioteker (for eksempel `openpyxl`) som du ikke
bygger selv, anbefaler vi å _vendore_ wheels inn i bundlen: last dem ned lokalt
før deploy og pakk dem sammen med ditt eget prosjekt.

Last ned avhengighetene til `dist/deps/` før deploy:

```bash
mkdir -p dist/deps
uvx pip download openpyxl==3.1.5 -d dist/deps
```

!!! tip "Pinn versjonen"
    Bruk eksplisitt versjon (`openpyxl==3.1.5`) slik at `vendor`-steget er
    reproduserbart. Lockfilen til prosjektet ditt (`uv.lock`) er sannhetskilden
    for hvilken versjon som faktisk brukes.

!!! warning "Plattform-spesifikke wheels"
    `pip download` på Mac/Windows kan hente et wheel som ikke kjører på
    Databricks (Linux `x86_64`). Pure-Python-pakker som `openpyxl` (klassifisert
    som `py3-none-any`) er trygge. For pakker med native kode må du oppgi
    plattform eksplisitt — se [Laste opp
    Python-biblioteker](laste-opp-python-biblioteker.md#1-hent-wheel-filen-lokalt)
    for kommandoen.

Legg `dist/deps/*.whl` til som ekstra avhengighet på samme `environments`-blokk
som ditt eget prosjekt:

```yaml
environments:
  - environment_key: default
    spec:
      client: "5"
      dependencies:
        - ../dist/*.whl
        - ../dist/deps/*.whl
```

!!! info "Alternativ: Unity Catalog Volume"
    Hvis avhengigheten er stor eller deles på tvers av mange bundles, kan du laste
    den opp én gang til et Unity Catalog Volume og referere til den med en variabel.
    Se [Laste opp Python-biblioteker](laste-opp-python-biblioteker.md). Ulempen er
    at versjonen ikke følger samme livssyklus som koden — du må huske å oppdatere
    volumet manuelt når du oppgraderer avhengigheten.

## Bygge og deploye

### Velge CLI-profil

Databricks CLI bruker profiler i `~/.databrickscfg` for å holde styr på flere
workspace-tilganger. En typisk konfigurasjon for et team med stage og prod ser
slik ut:

```ini
[MY_TEAM_STAGE]
host = https://stage-workspace.cloud.databricks.com
auth_type = databricks-cli

[MY_TEAM_PROD]
host = https://prod-workspace.cloud.databricks.com
auth_type = databricks-cli
```

Logg inn én gang per profil:

```bash
databricks auth login --host https://stage-workspace.cloud.databricks.com --profile MY_TEAM_STAGE
```

I bundle-kommandoer velger du profil med `-p`:

```bash
databricks bundle validate -t stage -p MY_TEAM_STAGE
```

!!! warning "Bruk `-p` eksplisitt"
    Uten `-p` brukes `DEFAULT`-profilen, og en uoppmerksom deploy kan havne i
    feil workspace.

!!! info "CI bruker miljøvariabler"
    I GitHub Actions autentiserer du med OIDC via miljøvariablene
    `DATABRICKS_AUTH_TYPE=github-oidc` og `DATABRICKS_CLIENT_ID`, ikke profiler. Se
    [Deploye til produksjon med GitHub Actions](deploye-til-produksjon.md).

### Validere konfigurasjonen

Kjør validate før du deployer for å fange opp feil i YAML-syntaks, manglende
variabler og ugyldig konfigurasjon:

```bash
databricks bundle validate -t stage -p MY_TEAM_STAGE
```

### Deploye til stage

```bash
databricks bundle deploy -t stage -p MY_TEAM_STAGE
```

Verifiser i Databricks-workspacet at jobben dukker opp under **Workflows**. I
development-mode får jobben et prefiks med brukernavnet ditt, for eksempel
`[dev ola.nordmann] my_job`.

### Kjøre en jobb manuelt

```bash
databricks bundle run -t stage -p MY_TEAM_STAGE my_job
```

### Deploye til prod

```bash
databricks bundle deploy -t prod -p MY_TEAM_PROD
```

!!! info "CI/CD"
    I praksis kjører du `deploy -t prod` fra GitHub Actions med en service
    principal — ikke fra din lokale maskin. CI bruker miljøvariabler for
    autentisering, så `-p`-flagget er ikke aktuelt der.

## Feilsøking

| Symptom                           | Årsak                                                                            | Løsning                                                                                                                            |
|:----------------------------------|:---------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------|
| `permission denied` ved deploy    | Manglende tilgang til workspace eller feil profil                                | Sjekk at `-p`-flagget peker på riktig profil for målet, og at profilen er gyldig (`databricks auth login --profile <navn>`).       |
| Gammel wheel-versjon brukes       | Clusteret cacher wheels basert på versjonsnummer                                 | Legg til `artifacts_dynamic_version: true` i stage-target. I prod: oppgrader versjonen i `pyproject.toml`.                         |
| `ModuleNotFoundError` ved kjøring | Wheelen er ikke tilgjengelig for clusteret                                       | Sjekk at `libraries` refererer til riktig whl-sti. Sjekk `data_security_mode` på clusteret (`SINGLE_USER` eller `USER_ISOLATION`). |
| `validate` feiler for prod        | `production`-mode krever eksplisitt `root_path` eller service principal/`run_as` | Sett `workspace.root_path` i prod-target, for eksempel `~/.bundle/${bundle.name}/${bundle.target}`.                                |

## Trenger du hjelp?

- Spør i [#dig-dataspeilet-support](https://oslokommune.slack.com/archives/C01DE13PLDP) på Slack
- Opprett en issue i [padda-golden-path](https://github.com/oslokommune/padda-golden-path/issues)
- Se [Declarative Automation Bundles (konsept)](../../om-plattformen/konsepter/databricks-bundles.md) for bakgrunn om targets, modes og wheel-strategier
- Se [Declarative Automation Bundles (referanse)](../../referanse/databricks-bundles.md) for konfigurasjonsoversikt og tilgjengelige eksempler
