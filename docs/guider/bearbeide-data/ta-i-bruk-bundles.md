---
title: Ta i bruk Bundles
description: Hvordan pakke og deploye jobber til Databricks med Bundles.
diataxis: how-to
---

# Ta i bruk Bundles

Denne guiden viser hvordan du oppretter, konfigurerer og deployer en Databricks Bundle til flere workspaces.

## Forutsetninger

- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install.html) installert og autentisert mot workspacen din
- [uv](https://docs.astral.sh/uv/) installert (for wheel-bygging)
- Tilgang til minst en Databricks-workspace
- Klonet `padda-golden-path`-repoet

## Opprette en ny bundle fra malen

Bruk den innebygde malen `dab-simple` til a opprette en ny bundle:

```bash
databricks bundle init /sti/til/padda-golden-path/src/golden_path/dab-simple
```

Oppgi prosjektnavn nar du blir spurt. Malen genererer denne mappestrukturen:

```
my-project/
  databricks.yml          # Hovedkonfigurasjon med targets
  resources/
    my_project_job.yml    # Jobbdefinisjon
  src/
    my_project/
      task.py             # Python-kode som kjøres av jobben
```

## Konfigurere targets for stage og prod

### Sette workspace-host per target

Apne `databricks.yml` og sett `workspace.host` for hvert target til riktig workspace-URL:

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
      root_path: /Shared/.bundle/prod/${bundle.name}
```

!!! warning "Ikke hardkod workspace-spesifikke stier i jobbdefinisjoner"
    Bruk variabler for alt som endrer seg mellom workspaces — kataloger, schemaer, filstier. Hardkodede verdier bryter nar du deployer til et annet miljo.

### Overstyre variabler per target

Definer variabler med standardverdier og overstyr dem per target:

```yaml
variables:
  catalog:
    description: Unity Catalog-katalog
    default: dev_catalog
  schema:
    description: Schema for tabeller
    default: default

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
      root_path: /Shared/.bundle/prod/${bundle.name}
    variables:
      catalog: prod_catalog
      schema: production
```

Referer til variablene i jobbdefinisjoner med `${var.catalog}` og `${var.schema}`.

### Sette permissions og run_as for prod

`production`-mode krever at du definerer eierskap. Legg til `permissions` og eventuelt `run_as`:

```yaml
targets:
  prod:
    mode: production
    workspace:
      host: https://prod-workspace.cloud.databricks.com
      root_path: /Shared/.bundle/prod/${bundle.name}
    run_as:
      service_principal_name: my-deploy-sp
    permissions:
      - service_principal_name: my-deploy-sp
        level: CAN_MANAGE
```

## Bygge og deploye

### Validere konfigurasjonen

Kjør validate før du deployer for a fange opp feil i YAML-syntaks, manglende variabler og ugyldig konfigurasjon:

```bash
databricks bundle validate
```

For a validere mot et spesifikt target:

```bash
databricks bundle validate -t prod
```

### Deploye til stage

Deploy til default-target (stage):

```bash
databricks bundle deploy
```

Verifiser i Databricks-workspacen at jobben dukker opp under **Workflows**. I development-mode får jobben et prefix med brukernavnet ditt, f.eks. `[dev ola.nordmann] my_project_job`.

### Kjøre en jobb manuelt

```bash
databricks bundle run my_project_job
```

### Deploye til prod

```bash
databricks bundle deploy -t prod
```

!!! info "CI/CD"
    I praksis kjører du `deploy -t prod` fra GitHub Actions med en service principal — ikke fra din lokale maskin.

## Håndtere Python wheels

### Ditt eget prosjekt: artifacts-seksjonen

Hvis prosjektet ditt har en `pyproject.toml`, legg til en `artifacts`-seksjon som bygger wheelen automatisk ved deploy:

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
    Uten dette kan klusteret cache en gammel versjon av wheelen. `artifacts_dynamic_version` legger til et unikt tidsstempel slik at klusteret alltid henter siste versjon.

Referer til wheelen i jobbdefinisjonen:

```yaml
resources:
  jobs:
    my_job:
      tasks:
        - task_key: main_task
          python_wheel_task:
            package_name: my_project
            entry_point: main
          libraries:
            - whl: ../dist/*.whl
```

### Tredjepartsbiblioteker uten kildekode

For tredjepartsbiblioteker (f.eks. `openpyxl`) som du ikke bygger selv, last dem opp til en UC Volume og referer til dem med variabler. Se [Laste opp Python-biblioteker](laste-opp-python-biblioteker.md) for en steg-for-steg-guide.

## Feilsøking

| Symptom | Arsak | Løsning |
|---------|:------|:---------|
| `permission denied` ved deploy | Manglende tilgang til workspace eller feil autentisering | Kjør `databricks auth login` på nytt. Sjekk at `workspace.host` er riktig for target. |
| Gammel wheel-versjon brukes | Clusteret cacher wheels basert på versjonsnummer | Legg til `artifacts_dynamic_version: true` i stage-target. I prod: bump versjonen i `pyproject.toml`. |
| `ModuleNotFoundError` ved kjøring | Wheelen er ikke tilgjengelig for clusteret | Sjekk at `libraries` refererer til riktig whl-sti. Sjekk `data_security_mode` på klusteret (`SINGLE_USER` eller `USER_ISOLATION`). |
| `validate` feiler for prod | `production`-mode krever `permissions` eller `run_as` | Legg til en `permissions`-blokk eller `run_as` i prod-target. |

## Trenger du hjelp?

- Spør i [#dig-dataspeilet](https://oslokommune.slack.com/archives/C01SFNFEXK7) på Slack
- Opprett en issue i [padda-golden-path](https://github.com/oslokommune/padda-golden-path/issues)
- Se [Declarative Automation Bundles (konsept)](../../om-plattformen/konsepter/databricks-bundles.md) for bakgrunn om targets, modes og wheel-strategier
- Se [Declarative Automation Bundles (referanse)](../../referanse/databricks-bundles.md) for konfigurasjonsoversikt og tilgjengelige eksempler

