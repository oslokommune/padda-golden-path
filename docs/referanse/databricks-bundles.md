---
title: Declarative Automation Bundles
description: Oversikt over tilgjengelige Declarative Automation Bundles, mappestruktur, konfigurasjon og navnekonvensjoner.
diataxis: reference
---

# Declarative Automation Bundles

Denne referansen dokumenterer bundle-konfigurasjonen, tilgjengelige eksempler og navnekonvensjoner brukt på plattformen.

## Mappestruktur

Kanonisk layout for en bundle:

```
my-bundle/
  databricks.yml          # Hovedkonfigurasjon
  resources/
    my_job.yml            # Jobbdefinisjoner (en eller flere)
  src/
    my_package/
      __init__.py
      task.py             # Python-kode
  pyproject.toml          # Wheel-konfigurasjon (valgfri)
  notebooks/
    01_notebook.py        # Databricks-notebooks (valgfri)
```

| Fil | Formaal |
|-----|:--------|
| `databricks.yml` | Hovedkonfigurasjon: bundle-navn, targets, artifacts, variabler, sync |
| `resources/*.yml` | Jobbdefinisjoner med tasks, clusters og schedules |
| `pyproject.toml` | Python-pakkekonfigurasjon for wheel-bygging via `artifacts` |
| `src/` | Python-kildekode som pakkes til wheel eller refereres som `spark_python_task` |
| `notebooks/` | Databricks-notebooks brukt i `notebook_task` |

## Konfigurasjon: databricks.yml

### bundle

| Felt | Type | Beskrivelse |
|------|:-----|:------------|
| `name` | string | Unikt navn på bundlen. Brukes i root path og som prefix. |
| `uuid` | string | Valgfri unik identifikator. Genereres ved `bundle init`. |

```yaml
bundle:
  name: my-project
```

### include

Glob-mønstre for filer som skal inkluderes i bundle-konfigurasjonen:

```yaml
include:
  - resources/*.yml
  - resources/*/*.yml
```

### targets

| Felt | Type | Beskrivelse |
|------|:-----|:------------|
| `mode` | `development` \| `production` | Styrer prefix, schedules, validering. Se [Mode-referanse](#mode-referanse). |
| `default` | bool | Om dette er standard-target når ingen `-t` er spesifisert. |
| `workspace.host` | string | URL til Databricks-workspacen. |
| `workspace.root_path` | string | Rotmappe i workspacen for deployen. Standard: `/Workspace/Users/<bruker>/.bundle/<target>/<bundle>`. |
| `permissions` | list | Liste med brukere/grupper og deres rettighetsniva. |
| `run_as` | object | Bruker eller service principal som kjører jobbene. |
| `presets` | object | Forhaaandsinnstillinger. Se [Presets](#presets). |
| `variables` | object | Overstyrte variabelverdier for dette target. |

```yaml
targets:
  stage:
    mode: development
    default: true
    workspace:
      host: https://stage-workspace.cloud.databricks.com
    presets:
      artifacts_dynamic_version: true

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
    variables:
      catalog: prod_catalog
```

### artifacts

| Felt | Type | Beskrivelse |
|------|:-----|:------------|
| `type` | `whl` | Artifact-type. Kun `whl` (Python wheel) støttes. |
| `build` | string | Kommando som kjøres for a bygge wheelen. |

```yaml
artifacts:
  python_artifact:
    type: whl
    build: uv build --wheel
```

### variables

| Felt | Type | Beskrivelse |
|------|:-----|:------------|
| `default` | string | Standardverdi brukt når target ikke overstyrer. |
| `description` | string | Valgfri beskrivelse av variabelen. |

Referansesyntaks i jobbdefinisjoner: `${var.<variabelnavn>}`.

```yaml
variables:
  catalog:
    description: Unity Catalog-katalog
    default: stage_catalog
  schema:
    description: Schema for tabeller
    default: default
```

### sync

Kontrollerer hvilke filer som synkroniseres til workspacen utover kode og notebooks.

| Felt | Type | Beskrivelse |
|------|:-----|:------------|
| `include` | list | Glob-mønstre for filer som skal inkluderes i sync. |
| `exclude` | list | Glob-mønstre for filer som skal ekskluderes fra sync. |

```yaml
sync:
  include:
    - wheels/*.whl
    - configs/**
```

## Target-konfigurasjon

### Mode-referanse

| Egenskap | `development` | `production` |
|----------|:-------------|:-------------|
| Navneprefix | `[dev <brukernavn>]` | Ingen |
| Schedules | Deaktiveres automatisk | Aktive |
| Root path | Brukerens personlige mappe | Må settes eksplisitt (anbefalt: `/Shared/.bundle/prod/`) |
| Validering | Minimal | Streng — krever `permissions` eller `run_as` |
| Delta Live Tables | Development-modus | Production-modus |

!!! warning "`production`-mode krever `permissions` eller `run_as`"
    Deploy feiler hvis ingen av disse er definert i prod-target.

### Presets

| Preset | Effekt |
|--------|:-------|
| `artifacts_dynamic_version` | Legger til tidsstempel i wheel-versjon for a unnga cluster-caching. Anbefalt for dev. |
| `name_prefix` | Overstyrer standard navneprefix. |
| `pipelines_development` | Overstyrer DLT-mode uavhengig av target-mode. |
| `trigger_pause_status` | Overstyrer pausing av triggers (`PAUSED` / `UNPAUSED`). |
| `jobs_max_concurrent_runs` | Setter maks samtidige kjøeringer for alle jobber. |

### Innebygde workspace-variabler

Disse variablene er tilgjengelige i alle konfigurasjonsfiler uten at du definerer dem:

| Variabel | Beskrivelse | Eksempel |
|----------|:------------|:--------|
| `${workspace.current_user.userName}` | Fullstendig brukernavn (e-post) | `ola.nordmann@oslo.kommune.no` |
| `${workspace.current_user.short_name}` | Kort brukernavn | `ola.nordmann` |
| `${bundle.name}` | Bundle-navnet fra `bundle.name` | `my-project` |
| `${bundle.target}` | Aktivt target-navn | `stage`, `prod` |

## Jobbdefinisjoner (resources)

Jobbdefinisjoner ligger i `resources/*.yml` og refereres via `include` i `databricks.yml`.

### Task-typer

| Task-type | Bruk | Eksempel |
|-----------|:-----|:--------|
| `notebook_task` | Kjører en Databricks-notebook | `excel_ingest` |
| `spark_python_task` | Kjører et Python-script direkte | `dab-simple` |
| `python_wheel_task` | Kjører en entry point fra en installert wheel | `vscode-demo` |

### Cluster-konfigurasjon

Jobber kan bruke enten eksisterende clustre eller jobbspesifikke:

```yaml
# Eksisterende cluster
tasks:
  - task_key: my_task
    existing_cluster_id: ${var.existing_cluster_id}

# Jobbspesifikt cluster
tasks:
  - task_key: my_task
    job_cluster_key: job_cluster
job_clusters:
  - job_cluster_key: job_cluster
    new_cluster:
      node_type_id: m5.large
      spark_version: 14.3.x-scala2.12
```

## Navnekonvensjoner

| Ressurs | Konvensjon | Eksempel |
|---------|:-----------|:--------|
| Bundle-navn | kebab-case | `my-project`, `excel-ingest` |
| Jobb-navn (YAML-nokkel) | snake_case med `_job`-suffix | `my_project_job`, `ingest_excel_job` |
| Task-nøkkel | snake_case med `_task`-suffix | `ingest_excel_task`, `python_task` |
| Cluster-nokkel | snake_case | `job_cluster` |
| Variabler | snake_case | `catalog`, `excel_input_path` |

## CLI-kommandoer

| Kommando | Beskrivelse |
|----------|:------------|
| `databricks bundle init <mal>` | Opprett ny bundle fra en mal |
| `databricks bundle validate` | Valider konfigurasjon uten a deploye |
| `databricks bundle validate -t <target>` | Valider mot et spesifikt target |
| `databricks bundle deploy` | Deploy til default-target |
| `databricks bundle deploy -t <target>` | Deploy til et spesifikt target |
| `databricks bundle run <jobb>` | Kjør en jobb manuelt |
| `databricks bundle destroy` | Fjern alle ressurser fra workspacen |

## Trenger du hjelp?

- Se [Ta i bruk Bundles](../guider/bearbeide-data/ta-i-bruk-bundles.md) for steg-for-steg-instruksjoner
- Se [Declarative Automation Bundles (konsept)](../om-plattformen/konsepter/databricks-bundles.md) for bakgrunn om targets, modes og wheel-strategier
- Se [Databricks-opplaering](../hjelp/databricks-opplaering.md#utvalgt-dokumentasjon) for offisiell Databricks-dokumentasjon
- Spør i [#dig-dataspeilet](https://oslokommune.slack.com/archives/C01SFNFEXK7) på Slack
