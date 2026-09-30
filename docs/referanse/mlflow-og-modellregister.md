---
title: MLflow og modellregister
description: Referanse for ML-delen av bundle-malen, bundle-ressursene for eksperimenter, registrerte modeller og serving-endepunkter, privilegier og kjente feil.
diataxis: reference
---

# MLflow og modellregister

Denne siden dokumenterer det bundle-malen setter opp når du svarer `yes` på
`include_ml_workflow`: ressurser, variabler, jobben, privilegier og
begrensninger. For bakgrunn, se [Maskinlæring på
plattformen](../om-plattformen/konsepter/maskinlaering.md).

## Oversikt

- **Type:** malvalg i Padda Asset Bundle Templates og bundle-ressurser
- **Gjelder for:** bundles generert med `include_ml_workflow: yes`
- **Compute:** serverless, miljøversjon 6
- **Modellregister:** Unity Catalog (`databricks-uc`)
- **Rammeverk i eksempelet:** PyTorch, logget med `mlflow.pytorch`

## Malvalget `include_ml_workflow`

| Egenskap | Verdi |
|----------|-------|
| Verdier | `no` (standard), `yes` |
| Spørres når | `setup_type` er `default` eller `tailored`; aldri for `minimal` |
| Legger til | Ressursfilene, `scripts/upload_ml_wheels.sh`, pakken `src/<pakke>/ml/`, testene `tests/test_ml_*.py`, avhengighetene `mlflow-skinny`, `numpy`, `pandas`, `scikit-learn`, `torch`, entry points `ml_generate_data`, `ml_build_features`, `ml_train`, `ml_predict`, variablene under, og `pandas-stubs` som dev-avhengighet |

Filer som genereres:

| Fil | Innhold |
|-----|---------|
| `resources/example_ml.schema.yml` | Skjemaet bundlen eier, med grants til konsumentgruppen |
| `resources/example_ml.volume.yml` | Volumet `wheels` for tredjepartsbiblioteker |
| `resources/example_ml.experiment.yml` | MLflow-eksperimentet |
| `resources/example_ml.registered_model.yml` | Den registrerte modellen `romledighet`, med `EXECUTE` til konsumentgruppen |
| `resources/example_ml.job.yml` | Serverless-jobben `example_ml_job` |
| `resources/optional/example_ml.serving.yml` | Serving-endepunktet. Ikke med i `include` |
| `scripts/upload_ml_wheels.sh` | Laster ned og opp hjul til volumet |
| `src/<pakke>/ml/data.py` | Syntetiske bookinger (ren pandas) |
| `src/<pakke>/ml/features.py` | Feature-kontrakten `FEATURE_COLUMNS` og SQL-en som bygger feature-tabellen |
| `src/<pakke>/ml/model.py` | Nettverket, treningsløkke og evaluering (ren torch) |
| `src/<pakke>/ml/registry.py` | Alias-regelen `choose_alias` og MLflow-hjelpere |
| `src/<pakke>/ml/train.py` | Treningsflyten: MLflow-kjøring, logging, registrering, alias |
| `src/<pakke>/ml/predict.py` | Batch-inferens med `@padda` |
| `src/<pakke>/ml/tasks.py` | Entry points for jobben |

## Variabler

| Variabel | Standardverdi | Beskrivelse |
|----------|---------------|-------------|
| `ml_schema` | `ml_example` | Skjemaet bundlen oppretter og eier. Tabeller, volum, modell og prediksjoner havner her |
| `ml_consumer_group` | `account users` | Principal som får `USE_SCHEMA` og `SELECT` på skjemaet og `EXECUTE` på modellen |
| `ml_model_version` | `"1"` | Versjonen serving-endepunktet serverer. Leses bare når `resources/optional/*.yml` er inkludert |

`catalog` fra hovedmalen brukes som katalog for alt.

## Bundle-ressurser

Jobben refererer til skjema og modell via ressursnavn, ikke via variabler,
slik at prefiksene i development-modus følger med:

```yaml
schema: ${resources.schemas.example_ml_schema.name}
model-name: ${var.catalog}.${resources.schemas.example_ml_schema.name}.${resources.registered_models.example_ml_model.name}
experiment-id: ${resources.experiments.example_ml_experiment.id}
```

### `schemas`

| Felt | Type | Beskrivelse |
|------|------|-------------|
| `name` | string | Skjemanavn |
| `catalog_name` | string | Katalog |
| `comment` | string | Beskrivelse |
| `grants` | list | `principal` og `privileges` per mottaker |

```yaml
resources:
  schemas:
    example_ml_schema:
      name: ${var.ml_schema}
      catalog_name: ${var.catalog}
      grants:
        - principal: ${var.ml_consumer_group}
          privileges: [USE_SCHEMA, SELECT]
```

### `experiments`

| Felt | Type | Beskrivelse |
|------|------|-------------|
| `name` | string | Full workspace-sti. Foreldremappen må finnes |
| `permissions` | list | Tilgang per bruker, gruppe eller service principal |
| `artifact_location` | string | Valgfri lagringssti for artefakter |

```yaml
resources:
  experiments:
    example_ml_experiment:
      name: /Users/${workspace.current_user.userName}/${bundle.name}-ml-example
```

### `registered_models`

| Felt | Type | Beskrivelse |
|------|------|-------------|
| `name` | string | Modellnavn (siste ledd) |
| `catalog_name` | string | Katalog |
| `schema_name` | string | Skjema |
| `comment` | string | Beskrivelse |
| `grants` | list | `principal` og `privileges`, typisk `EXECUTE` |

```yaml
resources:
  registered_models:
    example_ml_model:
      name: romledighet
      catalog_name: ${var.catalog}
      schema_name: ${resources.schemas.example_ml_schema.name}
      grants:
        - principal: ${var.ml_consumer_group}
          privileges: [EXECUTE]
```

Ressursen oppretter selve modellobjektet. Versjoner opprettes av
treningsjobben via `registered_model_name` i `mlflow.pytorch.log_model`.

### `model_serving_endpoints`

| Felt | Type | Beskrivelse |
|------|------|-------------|
| `name` | string | Endepunktnavn. Brukes i URL-en |
| `config.served_entities[].entity_name` | string | Full modellnavn `<katalog>.<skjema>.<modell>` |
| `config.served_entities[].entity_version` | string | Versjonsnummer. Alias støttes ikke |
| `config.served_entities[].workload_size` | string | `Small`, `Medium` eller `Large` |
| `config.served_entities[].scale_to_zero_enabled` | bool | Skalerer til null ved inaktivitet |
| `tags` | list | `key`/`value`-par. Kosttagger settes her |
| `permissions` | list | Hvem som kan spørre (`CAN_QUERY`) eller administrere (`CAN_MANAGE`) endepunktet |

```yaml
resources:
  model_serving_endpoints:
    example_ml_endpoint:
      name: romledighet
      config:
        served_entities:
          - entity_name: ${var.catalog}.${resources.schemas.example_ml_schema.name}.${resources.registered_models.example_ml_model.name}
            entity_version: ${var.ml_model_version}
            workload_size: Small
            scale_to_zero_enabled: true
      tags:
        - key: CostTeam
          value: padda
        - key: CostProcess
          value: Serve
```

Volumet er dokumentert under [Unity Catalog
Volumes](databricks-bundles.md#unity-catalog-volumes).

## Jobben `example_ml_job`

| Task | Entry point | Parametere | Gjør |
|------|-------------|------------|------|
| `generate_data` | `ml_generate_data` | `catalog`, `schema`, valgfritt `weeks`, `rooms`, `seed` | Skriver `rom` og `bookinger` |
| `build_features` | `ml_build_features` | `catalog`, `schema`, valgfritt `horizon-days` (1–7) | Skriver `romledighet_features`; rader etter siste bookingdag får `er_booket = NULL` |
| `train` | `ml_train` | `catalog`, `schema`, `model-name`, `experiment-id`, valgfritt `epochs` | Trener, logger, registrerer ny versjon, setter alias |
| `predict` | `ml_predict` | `catalog`, `schema`, `model-name` | Skriver `romledighet_prediksjoner` for radene uten label |

Miljøet:

```yaml
environments:
  - environment_key: ml
    spec:
      environment_version: "6"
      dependencies:
        - "--no-index"
        - "--find-links /Volumes/${var.catalog}/${resources.schemas.example_ml_schema.name}/${resources.volumes.example_ml_wheels.name}"
        - ../dist/*.whl
```

Triggeren er en ukentlig `periodic` med `pause_status: PAUSED`. Tagger:
`CostTeam` fra teamet og `CostProcess: ML`.

## Tabeller

| Tabell | Nøkkel | Innhold |
|--------|--------|---------|
| `rom` | `rom_id` | `bygg`, `etasje`, `kapasitet`, `har_video` |
| `bookinger` | `booking_id` | `rom_id`, `start`, `slutt`, `enhet`, `opprettet` (lokal tid uten tidssone) |
| `romledighet_features` | `rom_id`, `dato`, `time` | Kolonnene i `FEATURE_COLUMNS` som `DOUBLE`, og `er_booket` (`1.0`, `0.0` eller `NULL`) |
| `romledighet_prediksjoner` | `rom_id`, `dato`, `time` | `tidspunkt`, `sannsynlighet_booket`, `modellversjon`, `predikert_tidspunkt` |

`FEATURE_COLUMNS` er, i rekkefølge: `ukedag`, `time_num`, `etasje`,
`kapasitet`, `har_video`, `booket_forrige_uke`, `andel_booket_siste_4_uker`,
og én kolonne `bygg_<navn>` per bygg.

## Privilegier

| Rolle | Trenger | Får det fra |
|-------|---------|-------------|
| Den som deployer bundlen | `USE_CATALOG` og `CREATE_SCHEMA` på katalogen | katalogeier |
| Jobbens `run_as` | Eierskap til skjema, volum, modell og tabeller | Blir eier ved deploy |
| Konsument av prediksjoner | `USE_CATALOG`, `USE_SCHEMA`, `SELECT` | `ml_consumer_group` via bundlen (`USE_CATALOG` fra katalogeier) |
| Konsument av modellen (batch fra egen jobb) | `USE_CATALOG`, `USE_SCHEMA`, `EXECUTE` på modellen | `ml_consumer_group` via bundlen |
| Den som oppretter endepunktet | `EXECUTE` på modellversjonen | Eier eller `ml_consumer_group` |
| Den som kaller endepunktet | `CAN_QUERY` på endepunktet | `permissions` på endepunktet |

## Navn i development-modus

| Ressurs | Navn i `development` | Navn i `production` |
|---------|----------------------|---------------------|
| Skjema | `dev_<bruker>_<ml_schema>` | `<ml_schema>` |
| Registrert modell | `dev_<bruker>_romledighet` | `romledighet` |
| Eksperiment | `/Users/<bruker>/[dev <bruker>] <bundle>-ml-example` | `/Users/<deployer>/<bundle>-ml-example` |
| Jobb | `[dev <bruker>] example_ml_job` | `example_ml_job` |

`databricks bundle summary -t <target>` viser de faktiske navnene.

## Serverless-miljø

| Pakke | I miljøversjon 6 | Kilde i jobben |
|-------|------------------|----------------|
| `mlflow-skinny` 3.12 | Ja | Forhåndsinstallert |
| `pandas`, `numpy`, `scikit-learn`, `pyarrow` | Ja | Forhåndsinstallert |
| `torch` | Nei | Volumet `wheels` (`torch==2.12.0+cpu`, Linux x86_64, Python 3.12) |
| `sympy`, `networkx`, `mpmath` | Nei | Volumet `wheels` (avhengigheter av torch) |

`scripts/upload_ml_wheels.sh <target> <profil>` laster ned hjulene med
`pip download` for `manylinux_2_28_x86_64` og `cp312`, og laster dem opp med
`databricks fs cp` til `/Volumes/<katalog>/<skjema>/wheels/`.

## Feil og advarsler

### `Library installation failed: ... Unable to find or download the required package`

- **Betydning:** pip fikk ikke tak i en pakke.
- **Når den oppstår:** volumet er tomt eller mangler et hjul, eller
  jobbmiljøet peker på en pakkeindeks på internett.
- **Merknad:** kjør `scripts/upload_ml_wheels.sh` og sjekk at `dependencies`
  starter med `--no-index`. Feiler bare det første forsøket på den første
  tasken rett etter en deploy, mens Databricks' automatiske nye forsøk
  lykkes, er det ikke noe galt med oppsettet; mønsteret er observert flere
  ganger på plattformen.

### `Parent directory does not exist: /Users/<bruker>/<mappe>`

- **Betydning:** eksperimentets foreldremappe finnes ikke.
- **Når den oppstår:** `experiments.<navn>.name` peker på en undermappe.
- **Merknad:** legg eksperimentet rett under brukermappen.

### `Invalid base environment ... Only custom base environments ... are currently supported`

- **Betydning:** Jobs API-et godtar ikke Databricks-leverte basemiljøer.
- **Når den oppstår:** `base_environment: workspace-base-environments/...` i
  jobbmiljøet.
- **Merknad:** bruk `environment_version` og hjul fra volumet.

### `Function '<modell>' is not empty. The function has N model versions(s)`

- **Betydning:** en registrert modell med versjoner kan ikke slettes.
- **Når den oppstår:** `databricks bundle destroy`, eller en deploy som må
  gjenskape modellen fordi ressursnøkkelen eller navnet er endret.
- **Merknad:** slett versjonene først med `databricks model-versions delete
  <modell> <versjon>`, og kjør kommandoen på nytt. Bundlen sletter aldri
  modellversjoner selv.

## CLI-kommandoer

| Kommando | Beskrivelse |
|----------|-------------|
| `databricks model-versions get-by-alias <modell> padda` | Hvilken versjon aliaset peker på |
| `databricks model-versions set-alias <modell> <alias> <versjon>` | Flytt et alias manuelt |
| `databricks model-versions list <modell>` | Alle versjoner |
| `databricks model-versions delete <modell> <versjon>` | Slett en versjon; nødvendig før modellen eller skjemaet kan slettes |
| `databricks experiments search-runs --experiment-ids <id>` | Kjøringer med metrikker |
| `databricks serving-endpoints get <navn>` | Status for et endepunkt |
| `databricks environments list-workspace-base-environments` | Basemiljøer i workspacet |

## Begrensninger

- Stien dekker CPU på serverless. GPU og klassisk ML-runtime settes ikke opp
  av malen.
- Databricks-leverte basemiljøer kan ikke velges via `base_environment` i
  jobber ennå.
- Serving-endepunkter serverer et versjonsnummer, ikke et alias.
- Serverless-miljøet er Python 3.12 selv om prosjektet lokalt bruker en nyere
  versjon; hjul til volumet må lastes ned for 3.12.

## Relatert innhold

- [Maskinlæring på plattformen](../om-plattformen/konsepter/maskinlaering.md)
- [Trene og registrere en modell](../guider/maskinlaering/trene-og-registrere-modell.md)
- [Kjøre batch-inferens med en registrert modell](../guider/maskinlaering/batch-inferens.md)
- [Publisere en modell som serving-endepunkt](../guider/maskinlaering/publisere-serving-endepunkt.md)
- [Declarative Automation Bundles (referanse)](databricks-bundles.md)
- [Navnekonvensjoner](navnekonvensjoner.md#bundles-jobber-og-pipelines)
