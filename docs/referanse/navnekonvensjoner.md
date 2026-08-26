---
title: Navnekonvensjoner
description: Navnemønstre for kataloger, skjemaer, tabeller, kolonner, bundles, jobber, pipelines og plattformressurser.
diataxis: reference
---

# Navnekonvensjoner

Denne siden samler navnemønstrene på plattformen: de som Dataspeilet bruker når
workspaces, kataloger og landing zones settes opp, og de som gjelder for det teamene selv
navngir.

## Generelle regler

Databricks setter noen [tekniske
grenser](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-names) for navn i
Unity Catalog:

- Navn på kataloger, skjemaer, tabeller, views og volumer kan ikke inneholde punktum,
  mellomrom eller skråstrek, og kan være opptil 255 tegn.
- Navnene lagres med små bokstaver. `MinTabell` og `mintabell` er samme tabell.
- Navn med andre tegn enn ASCII-bokstaver, tall og understrek må omsluttes av `` ` `` i
  SQL. Det gjelder for eksempel bindestrek (`` `min-tabell` ``) og norske bokstaver (``
  `målinger` ``).

Av den grunn bruker Dataspeilet én stil for alt som navngis i Unity Catalog: små bokstaver
og understrek (`snake_case`).

Workspaces, bøtter, IAM-roller og service principals bruker bindestrek i stedet for
understrek.

## Workspaces og miljøer

Et workspace har et kort navn med små bokstaver og bindestrek, ofte `<org>-<miljø>`, for
eksempel `sye-stage`. Workspace-navnet inngår i navnet på mange andre ressurser: landing
zone-bøtta, sendere, service principals og serverless-funksjoner.

Miljøene heter **sandbox**, **stage** og **prod** — se
[Arkitektur](../om-plattformen/konsepter/arkitektur.md#bearbeiding-ett-workspace-per-team-og-milj).
I katalognavn brukes likevel `dev`, `stage` og `prod`: Kataloger i et sandbox-workspace
får `dev` som miljøledd.

## Unity Catalog

### Kataloger

| Mønster                 | Eksempel                  | Innhold                                                                                                                      |
|-------------------------|---------------------------|------------------------------------------------------------------------------------------------------------------------------|
| `<org>_<miljø>_<farge>` | `dig_booking_stage_green` | Data. Én katalog per farge — se [Klassifisering av sensitivitet](../om-plattformen/konsepter/klassifisering-sensitivitet.md) |
| `<org>_<miljø>_utils`   | `dig_booking_stage_utils` | Delte hjelperessurser uten sensitivitetsfarge                                                                                |

- `<org>` er teamets eller virksomhetens korte navn, eventuelt med etatsprefiks: for
  eksempel `sye` eller `dig_booking`.
- `<miljø>` er `dev`, `stage` eller `prod`.
- `<farge>` er `green`, `yellow` eller `red`.

Kataloger opprettes av Dataspeilet. Katalognavnet, sammen med workspace-adressen, legges i
teamets 1Password-hvelv.

### Skjemaer

Hver katalog kommer med fem standardskjemaer:

| Skjema            | Formål                                                   |
|-------------------|----------------------------------------------------------|
| `landing_default` | Volumer for innkommende filer                            |
| `bronze_default`  | Rådata som Delta-tabeller                                |
| `silver_default`  | Vaskede og standardiserte data                           |
| `gold_default`    | Forretningsklare data og dataprodukter                   |
| `analyst_default` | Dataanalytikernes område for egne tabeller og prototyper |

Hva bronze, silver og gold betyr, er forklart i [Klassifisering av
datakvalitet](../om-plattformen/konsepter/klassifisering-datakvalitet.md). En
`utils`-katalog har ett skjema, `utils`.

Team kan opprette egne skjemaer. To mønstre er i bruk på plattformen, og innenfor ett
workspace velges én av dem:

| Mønster                | Skjema          | Tabell                  | Eksempel                         |
|------------------------|-----------------|-------------------------|----------------------------------|
| Lag som skjema         | `<lag>_default` | Uten lagprefiks         | `bronze_default.alarmer`         |
| Skjema per dataprodukt | `<dataprodukt>` | Med lagprefiks `<lag>_` | `pasientvarsling.bronze_alarmer` |

### Tabeller og views

Tabellnavn er `snake_case` og beskriver innholdet, med laget uttrykt enten i skjemaet
eller som prefiks etter modellen teamet har valgt. Utover det gjelder bare de tekniske
grensene over.

### Kolonner

Kolonnenavn er teamets sak, men mellomrom bør unngås. Unity Catalog tillater mellomrom i
kolonnenavn, men Delta-tabeller krever da [column
mapping](https://docs.databricks.com/aws/en/delta/column-mapping), og navnet må omsluttes
av `` ` `` i alle spørringer.

### Volumer

Et volum adresseres som `/Volumes/<katalog>/<skjema>/<volume>/`, for eksempel
`/Volumes/dig_booking_stage_green/landing_default/opplastinger/`. Volumnavn følger samme
stil som skjemaer og tabeller. Volum for innkommende filer hører hjemme i
`landing_default`. Volumer med Python-pakker er beskrevet i [Laste opp Python-pakker
(wheel) til en Unity Catalog
Volume](../guider/bearbeide-data/laste-opp-python-biblioteker.md).

## Bundles, jobber og pipelines

| Ressurs                     | Konvensjon                                                  | Eksempel                               |
|-----------------------------|-------------------------------------------------------------|----------------------------------------|
| Bundle-navn (`bundle.name`) | `kebab-case`                                                | `folkeregister-innlasting`             |
| Python-pakke i bundelen     | Bundle-navnet med understrek i stedet for bindestrek        | `folkeregister_innlasting`             |
| Jobb (ressursnøkkel)        | `snake_case` med `_job`-suffiks                             | `folkeregister_job`                    |
| Pipeline (ressursnøkkel)    | `snake_case` med `_pipeline`-suffiks                        | `folkeregister_pipeline`               |
| Task-nøkkel                 | `snake_case` med `_task`-suffiks                            | `bronze_task`                          |
| Cluster-nøkkel              | `snake_case`                                                | `job_cluster`                          |
| Variabler                   | `snake_case`                                                | `catalog`, `landing_path`              |
| Ressursfiler                | `resources/<navn>.job.yml`, `resources/<navn>.pipeline.yml` | `resources/folkeregister.pipeline.yml` |
| Targets                     | Miljønavnet                                                 | `stage`, `prod`                        |

Ressursnøkkelen og `name`-feltet på jobber og pipelines holdes like, slik at navnet i
Databricks-grensesnittet er det samme som i koden. I `development`-mode legger Databricks
selv til prefikset `[dev <brukernavn>]` på alle ressurser.

Jobber og clustere tagges med `CostTeam` og `CostProcess` — se [Tagging av
kostnader](../guider/overvaake-og-drifte/kostnadstagging.md). Øvrig konfigurasjon er
beskrevet i [Declarative Automation Bundles](databricks-bundles.md).

## Landing zone og sendere

| Ressurs               | Mønster                                                             | Eksempel                             |
|-----------------------|---------------------------------------------------------------------|--------------------------------------|
| Bøtte                 | `<fem første tegn av Databricks-konto-ID>-<workspace>-landing-zone` | `12345-booking-stage-landing-zone`   |
| Prefiks per sender    | `<sender>/<farge>/`                                                 | `folkeregister/red/`                 |
| IAM-rolle for sender  | `<workspace>-<sender>-ingest`                                       | `booking-stage-folkeregister-ingest` |
| IAM-bruker for sender | `<workspace>-<sender>-<farge>`                                      | `booking-stage-folkeregister-red`    |

Sendernavnet velges av teamet når senderen bestilles: små bokstaver og bindestrek, ofte
navnet på kildesystemet. Se [Landing zone](landing-zone.md) for struktur og autentisering.

## Identiteter

Grupper følger mønsteret `DS-<ORG>_<ROLLE>` i Entra ID, og hvert workspace har to service
principals for GitHub Actions, `<workspace>-gha-prs` og `<workspace>-gha-deploy`. Begge er
dokumentert i [Roller og rettigheter](roller-og-rettigheter.md).

## Compute

Clustere og SQL Warehouses i et workspace heter `Small`, `Medium` og `Large` (clustere
også `Many Small`). Navnene har ingen team- eller miljøledd. Se [SQL
Warehouse](sql-warehouse.md).

## Serverless-funksjoner

Lambda-funksjoner, IAM-roller, CloudFormation-stacker og andre ressurser som deployes med
SAM, må ha workspace-navnet som prefiks. Prefiksene håndheves av en permission boundary,
og deploy feiler uten dem. Mønstrene, og navnereglene for hemmeligheter i SSM Parameter
Store, er dokumentert i [SAM-deploy](sam-deploy.md#navnekonvensjoner).

## Relatert innhold

**Referanser:**

- [Landing zone](landing-zone.md) — bøttestruktur, sendere og autentisering
- [Roller og rettigheter](roller-og-rettigheter.md) — grupper og service principals
- [Declarative Automation Bundles](databricks-bundles.md) — bundle-konfigurasjon
- [SAM-deploy](sam-deploy.md) — prefikskrav for serverless-funksjoner
- [Definisjon av dataprodukt](dataprodukt.md) — metadatafeltene `name` og `title`

**Forklaringer:**

- [Klassifisering av sensitivitet](../om-plattformen/konsepter/klassifisering-sensitivitet.md)
  — fargene i katalognavnet
- [Klassifisering av datakvalitet](../om-plattformen/konsepter/klassifisering-datakvalitet.md)
  — lagene i skjemanavnene
