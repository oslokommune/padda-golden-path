---
title: Bygg din første datapipeline
description: Skriv en bundle med en pipeline som leser filene i volumet inn i bronze- og silver-tabeller, og se at bare nye filer leses ved neste kjøring.
diataxis: tutorial
---

# Bygg din første datapipeline

I dette steget bygger vi en datapipeline på datasettet fra [Last opp ditt første
datasett](last-opp-ditt-forste-datasett.md). Vi skriver en bundle med en pipeline som
leser filene i volumet inn i en bronze-tabell og videre til en silver-tabell med riktige
typer. Til slutt laster vi opp en ny fil og ser at pipelinen bare plukker opp det som er
nytt.

## Dette skal vi lage

Når du er ferdig, har du:

- en bundle på maskinen din, deployet til workspacet som en pipeline
- tabellene `bronze_default.paddeobservasjoner` og `silver_default.paddeobservasjoner`,
  som du kan slå opp i med SQL

## Før du begynner

Du trenger:

- [Last opp ditt første datasett](last-opp-ditt-forste-datasett.md) gjennomført, så mappa
  `paddeobservasjoner` finnes på maskinen din og fila ligger i volumet.
- Rett til å opprette tabeller i skjemaene `bronze_default` og `silver_default` i
  katalogen.

Som før står `<profilnavn>` for CLI-profilen din og `min_katalog` for teamets katalog.

## Trinn 1: Skriv bundlen

En [bundle](../om-plattformen/konsepter/databricks-bundles.md) er en mappe med
konfigurasjon og kode som Databricks CLI deployer til workspacet. Stå i mappa
`paddeobservasjoner` og lag tre filer.

Først `databricks.yml`, som gir bundlen et navn og sier hvilket workspace den skal til.
Bytt ut `<workspace-url>` med adressen til workspacet ditt:

```yaml
bundle:
  name: paddeobservasjoner

include:
  - resources/*.yml

targets:
  stage:
    default: true
    mode: development
    workspace:
      host: https://<workspace-url>
```

!!! warning "Én om gangen på teamet"
    Pipelinen får navnet ditt som prefiks, men tabellene den lager deles i katalogen. Ta
    derfor dette steget én om gangen på teamet, og rydd opp til slutt.

Så `resources/paddeobservasjoner.pipeline.yml`, som definerer pipelinen:

```yaml
resources:
  pipelines:
    paddeobservasjoner_pipeline:
      name: paddeobservasjoner_pipeline
      catalog: min_katalog
      schema: bronze_default
      serverless: true
      root_path: ../src
      libraries:
        - glob:
            include: ../src/transformations/**
```

Til slutt tabellene, i `src/transformations/paddeobservasjoner.sql`:

```sql
CREATE OR REFRESH STREAMING TABLE bronze_default.paddeobservasjoner AS
SELECT
  *,
  _metadata.file_path AS source_file_path,
  _metadata.file_modification_time AS source_file_modified_at,
  current_timestamp() AS ingested_at
FROM
  STREAM read_files(
    '/Volumes/min_katalog/landing_default/paddeobservasjoner/',
    format => 'json',
    inferColumnTypes => false
  );

CREATE OR REFRESH STREAMING TABLE silver_default.paddeobservasjoner (
    observasjon_id STRING PRIMARY KEY NOT NULL COMMENT 'Unik ID for observasjonen',
    lokalitet STRING NOT NULL COMMENT 'Dammen eller vannet der paddene ble observert',
    antall INT NOT NULL COMMENT 'Antall padder observert',
    observert TIMESTAMP NOT NULL COMMENT 'Tidspunkt for observasjonen',
    CONSTRAINT gyldig_antall EXPECT (antall >= 0) ON VIOLATION DROP ROW
  )
  COMMENT 'Paddeobservasjoner med riktige typer'
  AS
SELECT
  observasjon_id,
  lokalitet,
  CAST(antall AS INT) AS antall,
  CAST(observert AS TIMESTAMP) AS observert
FROM
  STREAM bronze_default.paddeobservasjoner;
```

Legg merke til at bronze-tabellen beholder alle kolonner som tekst, mens silver-tabellen
gir dem riktige typer og forkaster rader med negativt antall. Hvorfor lagene deles slik,
står i [Klassifisering av
datakvalitet](../om-plattformen/konsepter/klassifisering-datakvalitet.md), og hvordan Auto
Loader holder styr på hvilke filer som er lest, står i
[Datainnlasting](../om-plattformen/konsepter/datainnlasting.md#fra-landing-zone-til-bronze).

## Trinn 2: Deploy og kjør pipelinen

Valider konfigurasjonen, deploy bundlen og kjør pipelinen:

```bash
databricks bundle validate -p <profilnavn>
databricks bundle deploy -p <profilnavn>
databricks bundle run paddeobservasjoner_pipeline -p <profilnavn>
```

Forventet resultat: valideringa ender med `Validation OK!`, deployen skriver `Created
pipelines.paddeobservasjoner_pipeline`, og kjøringa skriver framdriften til den ender med
`Update ... is COMPLETED`. Første kjøring tar gjerne rundt et minutt, senere kjøringer går
raskere.

Åpne **SQL Editor** i sidemenyen og kjør:

```sql
SELECT observasjon_id, lokalitet, antall, observert
FROM min_katalog.silver_default.paddeobservasjoner
ORDER BY observert;
```

Du skal se de tre observasjonene fra fila, nå med `antall` som tall og `observert` som
tidspunkt. Under **Jobs & Pipelines** finner du pipelinen som `[dev <brukernavn>]
paddeobservasjoner_pipeline`, med grafen over bronze- og silver-tabellen.

## Trinn 3: Last opp en ny fil og kjør igjen

Kilder leverer nye filer over tid, og pipelinen skal bare lese det som er nytt. Lag fila
`testdata/paddeobservasjoner-2026-04-16.json`, der den første raden har negativt antall
med hensikt:

```json
{"observasjon_id": "obs-004", "lokalitet": "Bogstadvannet", "antall": -1, "observert": "2026-04-15T22:10:00"}
{"observasjon_id": "obs-005", "lokalitet": "Sognsvann", "antall": 8, "observert": "2026-04-16T21:20:00"}
```

Last opp fila og kjør pipelinen på nytt:

```bash
databricks fs cp testdata/paddeobservasjoner-2026-04-16.json \
  dbfs:/Volumes/min_katalog/landing_default/paddeobservasjoner/ -p <profilnavn>
databricks bundle run paddeobservasjoner_pipeline -p <profilnavn>
```

Forventet resultat: kjøringa ender med `COMPLETED` som sist.

## Kontroller resultatet

Kjør spørringen fra trinn 2 på nytt. Silver-tabellen skal nå ha fire rader:

| observasjon_id | lokalitet      | antall | observert           |
|----------------|----------------|--------|---------------------|
| obs-001        | Østensjøvannet | 12     | 2026-04-14 21:30:00 |
| obs-002        | Sognsvann      | 3      | 2026-04-14 22:05:00 |
| obs-003        | Østensjøvannet | 27     | 2026-04-15 21:45:00 |
| obs-005        | Sognsvann      | 8      | 2026-04-16 21:20:00 |

`obs-004` mangler fordi `gyldig_antall` forkastet den. Bronze-tabellen har alle fem
radene, og viser at hver fil bare er lest én gang:

```sql
SELECT substring_index(source_file_path, '/', -1) AS fil, count(*) AS rader
FROM min_katalog.bronze_default.paddeobservasjoner
GROUP BY fil
ORDER BY fil;
```

| fil                                | rader |
|------------------------------------|-------|
| paddeobservasjoner-2026-04-15.json | 3     |
| paddeobservasjoner-2026-04-16.json | 2     |

## Hvis noe ikke stemmer

??? failure "`Resources: 0 created` etter deploy"

    Bundlen fant ikke pipeline-definisjonen. Sjekk at `databricks.yml` har
    `include: - resources/*.yml`, og at fila ligger i mappa `resources`.

??? failure "Pipelinen feiler med at stien eller katalogen ikke finnes"

    Sjekk at `min_katalog` er byttet ut med katalogen din på begge stedene: `catalog` i
    `resources/paddeobservasjoner.pipeline.yml` og volumstien i
    `src/transformations/paddeobservasjoner.sql`.

Feiler kjøringa av andre grunner, se [Feilsøke med
logger](../guider/overvaake-og-drifte/logging.md).

## Du har nå

- En pipeline som leser filer inkrementelt fra volumet inn i en bronze-tabell, og
  videre til en silver-tabell med riktige typer og en kvalitetsregel
- En bundle du kan endre, deploye og kjøre på nytt så ofte du vil

Produksjonspipelines på plattformen er bygd av de samme delene. To ting er gjerne
annerledes: ekte kilder leverer filene til [landing zone](../referanse/landing-zone.md) i
stedet for at du laster dem opp selv, og innlasting og transformasjon ligger ofte i hver
sin pipeline, se [Én pipeline eller
flere](../om-plattformen/konsepter/datainnlasting.md#en-pipeline-eller-flere).

## Rydd opp

Når du er ferdig med å utforske, fjerner du pipelinen og volumet. Tabellene slettes sammen
med pipelinen:

```bash
databricks bundle destroy -p <profilnavn>
databricks volumes delete min_katalog.landing_default.paddeobservasjoner -p <profilnavn>
```

Da er katalogen klar for neste på teamet, og for guidene, som lager sine egne
testtabeller.

## Neste steg

- [Ta i bruk bundles](../guider/utvikle-og-deploye/ta-i-bruk-bundles.md) viser hvordan du
  setter opp en bundle fra malene, med targets og variabler for stage og prod
- [Skrive transformasjoner](../guider/bearbeide-data/skrive-transformasjoner.md) viser
  hvordan du legger silver og gold i en egen pipeline i en slik bundle
- [Sette opp Auto Loader](../guider/hente-inn-data/auto-loader.md) viser samme mønster mot
  ekte filer i landing zone
