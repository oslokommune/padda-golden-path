---
title: Declarative Automation Bundles
description: Oversikt over tilgjengelige Declarative Automation Bundles, mappestruktur, konfigurasjon og navnekonvensjoner.
diataxis: reference
---

# Declarative Automation Bundles

Denne referansen dokumenterer bundle-konfigurasjonen, eksempler og
navnekonvensjoner brukt på plattformen.

## Mappestruktur

Standard struktur for en bundle:

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

| Fil               | Formål                                                                        |
|-------------------|:------------------------------------------------------------------------------|
| `databricks.yml`  | Hovedkonfigurasjon: bundle-navn, targets, artifacts, variabler, sync          |
| `resources/*.yml` | Jobbdefinisjoner med tasks, clustere og schedules                             |
| `pyproject.toml`  | Python-pakkekonfigurasjon for wheel-bygging via `artifacts`                   |
| `src/`            | Python-kildekode som pakkes til wheel eller refereres som `spark_python_task` |
| `notebooks/`      | Databricks-notebooks brukt i `notebook_task`                                  |

## Konfigurasjon: databricks.yml

### bundle

| Felt   | Type   | Beskrivelse                                               |
|--------|:-------|:----------------------------------------------------------|
| `name` | string | Unikt navn på bundlen. Brukes i root path og som prefiks. |
| `uuid` | string | Valgfri unik identifikator. Genereres ved `bundle init`.  |

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

| Felt                  | Type                          | Beskrivelse                                                                                          |
|-----------------------|:------------------------------|:-----------------------------------------------------------------------------------------------------|
| `mode`                | `development` \| `production` | Styrer prefiks, schedules, validering. Se [Mode-referanse](#mode-referanse).                         |
| `default`             | bool                          | Om dette er standard-target når ingen `-t` er spesifisert.                                           |
| `workspace.host`      | string                        | URL til Databricks-workspacet.                                                                       |
| `workspace.root_path` | string                        | Rotmappe i workspacet for deployen. Standard: `/Workspace/Users/<bruker>/.bundle/<target>/<bundle>`. |
| `permissions`         | list                          | Liste med brukere/grupper og deres rettighetsnivå.                                                   |
| `run_as`              | object                        | Bruker eller service principal som kjører jobbene.                                                   |
| `presets`             | object                        | Forhåndsinnstillinger. Se [Presets](#presets).                                                       |
| `variables`           | object                        | Overstyrte variabelverdier for dette targetet.                                                       |

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
      root_path: ~/.bundle/${bundle.name}/${bundle.target}
    run_as:
      service_principal_name: my-deploy-sp
    permissions:
      - service_principal_name: my-deploy-sp
        level: CAN_MANAGE
    variables:
      catalog: prod_catalog
```

### artifacts

| Felt    | Type   | Beskrivelse                                      |
|---------|:-------|:-------------------------------------------------|
| `type`  | `whl`  | Artifact-type. Kun `whl` (Python wheel) støttes. |
| `build` | string | Kommando som kjøres for å bygge wheelet.         |

```yaml
artifacts:
  python_artifact:
    type: whl
    build: uv build --wheel
```

### variables

| Felt          | Type   | Beskrivelse                                     |
|---------------|:-------|:------------------------------------------------|
| `default`     | string | Standardverdi brukt når target ikke overstyrer. |
| `description` | string | Valgfri beskrivelse av variabelen.              |

Referansesyntaks i jobbdefinisjoner: `${var.<variabelnavn>}`.

```yaml
variables:
  catalog:
    description: Unity Catalog-katalog
  schema:
    description: Schema for tabeller
```

Variabelverdiene settes per target under `targets.<target>.variables`. Se [Ta i
bruk bundles — Sette variabler per
target](../guider/bearbeide-data/ta-i-bruk-bundles.md#sette-variabler-per-target)
for hvorfor `default:` typisk unngås for miljøspesifikke variabler.

### sync

Kontrollerer hvilke filer som synkroniseres til workspacet utover kode og notebooks.

| Felt      | Type | Beskrivelse                                           |
|-----------|:-----|:------------------------------------------------------|
| `include` | list | Glob-mønstre for filer som skal inkluderes i sync.    |
| `exclude` | list | Glob-mønstre for filer som skal ekskluderes fra sync. |

```yaml
sync:
  include:
    - wheels/*.whl
    - configs/**
```

## Target-konfigurasjon

### Mode-referanse

| Egenskap                | `development`              | `production`                                                                 |
|-------------------------|:---------------------------|:-----------------------------------------------------------------------------|
| Navneprefiks            | `[dev <brukernavn>]`       | Ingen                                                                        |
| Schedules               | Deaktiveres automatisk     | Aktive                                                                       |
| Root path               | Brukerens personlige mappe | Må settes eksplisitt (anbefalt: `~/.bundle/${bundle.name}/${bundle.target}`) |
| Validering              | Minimal                    | Streng — krever `permissions` eller `run_as`                                 |
| Delta Live Tables (DLT) | Development-modus          | Production-modus                                                             |

!!! warning "`production`-mode krever `permissions` eller `run_as`"
    Deploy feiler hvis ingen av disse er definert i prod-target.

### Presets

| Preset                      | Effekt                                                                                                |
|-----------------------------|:------------------------------------------------------------------------------------------------------|
| `artifacts_dynamic_version` | Legger til tidsstempel i wheel-versjon for å unngå cluster-caching. Brukes typisk i development-mode. |
| `name_prefix`               | Overstyrer standard navneprefiks.                                                                     |
| `pipelines_development`     | Overstyrer DLT-mode uavhengig av target-mode.                                                         |
| `trigger_pause_status`      | Overstyrer pausing av triggers (`PAUSED` / `UNPAUSED`).                                               |
| `jobs_max_concurrent_runs`  | Setter maks samtidige kjøringer for alle jobber.                                                      |

### Innebygde workspace-variabler

Disse variablene er tilgjengelige i alle konfigurasjonsfiler uten at du
definerer dem:

| Variabel                               | Beskrivelse                     | Eksempel                       |
|----------------------------------------|:--------------------------------|:-------------------------------|
| `${workspace.current_user.userName}`   | Fullstendig brukernavn (e-post) | `ola.nordmann@oslo.kommune.no` |
| `${workspace.current_user.short_name}` | Kort brukernavn                 | `ola.nordmann`                 |
| `${bundle.name}`                       | Bundle-navnet fra `bundle.name` | `my-project`                   |
| `${bundle.target}`                     | Aktivt target-navn              | `stage`, `prod`                |

## Jobbdefinisjoner (resources)

Jobbdefinisjoner ligger i `resources/*.yml` og refereres via `include` i
`databricks.yml`.

### Task-typer

| Task-type           | Bruk                                          | Eksempel       |
|---------------------|:----------------------------------------------|:---------------|
| `notebook_task`     | Kjører en Databricks-notebook                 | `excel_ingest` |
| `python_wheel_task` | Kjører en entry point fra en installert wheel | `vscode-demo`  |
| `spark_python_task` | Kjører et Python-script direkte               | —              |

### Compute-konfigurasjon

Jobber kan kjøre på serverless eller klassisk compute.

#### Serverless compute

Avhengigheter deklareres i en `environments`-blokk på jobbnivå, og hver task
peker på et environment via `environment_key`:

```yaml
tasks:
  - task_key: my_task
    python_wheel_task:
      package_name: my_package
      entry_point: main
    environment_key: default

environments:
  - environment_key: default
    spec:
      client: "5"
      dependencies:
        - ../dist/*.whl
```

`spec.client` angir serverless-miljøets versjon. Se [Databricks' release notes
for serverless
environments](https://docs.databricks.com/aws/en/release-notes/serverless/environment-version/)
for tilgjengelige versjoner.

#### Klassisk compute

Bruker enten eksisterende cluster eller jobbspesifikt cluster:

```yaml
# Eksisterende cluster
tasks:
  - task_key: my_task
    existing_cluster_id: ${var.existing_cluster_id}

# Jobbspesifikt cluster
tasks:
  - task_key: my_task
    job_cluster_key: job_cluster
    libraries:
      - whl: ../dist/*.whl

job_clusters:
  - job_cluster_key: job_cluster
    new_cluster:
      node_type_id: i3.xlarge
      spark_version: 17.3.x-scala2.13
```

## Unity Catalog Volumes

Volumes kan deklareres som bundle-ressurser under `resources.volumes`. Da følger
volume-definisjonen samme livssyklus som koden.

| Felt               | Type   | Beskrivelse                                 |
|--------------------|:-------|:--------------------------------------------|
| `catalog_name`     | string | Unity Catalog-katalog volumet ligger under. |
| `schema_name`      | string | Schema volumet ligger under.                |
| `name`             | string | Volumets navn.                              |
| `volume_type`      | string | `MANAGED` eller `EXTERNAL`.                 |
| `storage_location` | string | Ekstern lagringssti. Kun for `EXTERNAL`.    |

```yaml
resources:
  volumes:
    uploads:
      catalog_name: ${var.catalog}
      schema_name: bronze_default
      name: uploads
      volume_type: MANAGED
```

Se [Deklarere volumes som
bundle-ressurser](../guider/bearbeide-data/ta-i-bruk-bundles.md#deklarere-volumes-som-bundle-ressurser)
i guiden for praktisk bruk og advarsler rundt `bundle destroy`.

## Ansvarsfordeling mellom bundles og padda-iac

Hvilke ressurser som hører hjemme i team-repoet (bundlen) versus plattform-repoet
(`padda-iac`):

| Hører hjemme i `padda-iac`         | Hører hjemme i team-repoet (bundlen) |
|:-----------------------------------|:-------------------------------------|
| Databricks-workspace               | Jobber og triggere                   |
| Unity Catalog-katalog              | Volumes for team-spesifikk data      |
| Schemas som deles på tvers av team | Andre team-spesifikke ressurser      |
| Nettverks- og VPC-konfigurasjon    |                                      |

Tommelfingerregel: ressurser som deles på tvers av team eller eies av
plattformteamet, lever i `padda-iac`. Ressurser som er tett koblet til ett team
sin kode, lever i team-repoet.

## Navnekonvensjoner

| Ressurs                 | Konvensjon                     | Eksempel                      |
|-------------------------|:-------------------------------|:------------------------------|
| Bundle-navn             | kebab-case                     | `my-project`, `excel-ingest`  |
| Jobb-navn (YAML-nøkkel) | snake_case med `_job`-suffiks  | `my_job`, `ingest_excel_job`  |
| Task-nøkkel             | snake_case med `_task`-suffiks | `my_task`, `python_task`      |
| Cluster-nøkkel          | snake_case                     | `job_cluster`                 |
| Variabler               | snake_case                     | `catalog`, `excel_input_path` |

## CLI-kommandoer

| Kommando                                 | Beskrivelse                          |
|------------------------------------------|:-------------------------------------|
| `databricks bundle init <mal>`           | Opprett ny bundle fra en mal         |
| `databricks bundle validate`             | Valider konfigurasjon uten å deploye |
| `databricks bundle validate -t <target>` | Valider mot et spesifikt target      |
| `databricks bundle deploy`               | Deploy til default-target            |
| `databricks bundle deploy -t <target>`   | Deploy til et spesifikt target       |
| `databricks bundle run <jobb>`           | Kjør en jobb manuelt                 |
| `databricks bundle destroy`              | Fjern alle ressurser fra workspacet  |

!!! note "Profilvalg med `-p <profil>`"
    Kommandoene over treffer workspacet definert av aktiv CLI-profil (eller
    `DEFAULT` om ingen er valgt). `-p <profil>` velger hvilken profil — og dermed
    hvilket workspace — kommandoen treffer. Se [Ta i bruk bundles — Velge
    CLI-profil](../guider/bearbeide-data/ta-i-bruk-bundles.md#velge-cli-profil) for
    praktisk oppsett.

## Trenger du hjelp?

- Se [Ta i bruk bundles](../guider/bearbeide-data/ta-i-bruk-bundles.md) for
  steg-for-steg-instruksjoner
- Se [Declarative Automation Bundles
  (konsept)](../om-plattformen/konsepter/databricks-bundles.md) for bakgrunn om
  targets, modes og wheel-strategier
- Se [Databricks-opplæring](../hjelp/databricks-opplaering.md#utvalgt-dokumentasjon)
  for offisiell Databricks-dokumentasjon
- Spør i [#dig-dataspeilet](https://oslokommune.slack.com/archives/C01SFNFEXK7)
  på Slack
