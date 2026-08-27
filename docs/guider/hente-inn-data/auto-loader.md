---
title: Sette opp Auto Loader
description: Hvordan lese inn filer inkrementelt fra landing zone til Unity Catalog med Auto Loader og Declarative Pipelines.
diataxis: how-to
---

# Sette opp Auto Loader

Denne guiden hjelper deg å sette opp en Declarative Pipeline som leser inn nye filer fra
landing zone og lagrer dem i bronze- og silver-tabeller i Unity Catalog. Resultatet er en
pipeline som kjører daglig og automatisk plukker opp nye filer uten å lese alt på
nytt. Guiden tar utgangspunkt i to eksempelbundler og følger dem tett — tilpass navn,
tabeller og transformasjoner til ditt eget bruksområde.

## Før du begynner

Sørg for at du har:

- En landing zone-sender med en S3-sti du vil lese fra. Se [Laste opp filer til landing zone](./laste-opp-til-landing-zone.md) om du ikke har en.
- Databricks CLI installert og konfigurert mot riktig workspace. Se [Sett opp utviklingsmiljøet](../../kom-i-gang/dev-setup.md).
- Skrivetilgang til en katalog i Unity Catalog der tabellene skal opprettes.

## Trinn 1: Velg tilnærming

To bundle-varianter er tilgjengelige i
[`padda-databrikker`-repoet](https://github.com/oslokommune/padda-databrikker/tree/main/bundles). Velg
ut fra krav til datakvalitet:

|                           | Permissive                                 | Strict                                          |
|---------------------------|--------------------------------------------|-------------------------------------------------|
| Ny kolonne i kilden       | Legges automatisk til i bronze             | Pipeline feiler — krever manuell håndtering     |
| Ugyldig eller korrupt rad | Slipper gjennom til bronze                 | Pipeline feiler                                 |
| Passer for                | Produkter som tåler en feil rad her og der | Produkter der ingen data er bedre enn feil data |

Dette er egentlig ikke et binært valg — i praksis vil man gjerne kombinere elementer fra
begge. Eksemplene er ment som illustrative ytterpunkter.

Eksemplene legger dessuten bronze- og silver-tabellene i samme pipeline og gir pipelinen
en egen planlagt jobb — snarveier som passer eksempelformatet, men ikke nødvendigvis
produktet ditt.

## Trinn 2: Kopier bundle-malen

Klon `padda-databrikker` og kopier riktig bundle inn i arbeidsrepoet ditt:

=== "Permissive"

    ```bash
    git clone git@github.com:oslokommune/padda-databrikker.git
    cp -r padda-databrikker/bundles/autoloader_permissive mitt-repo/bundles/min-pipeline
    ```

=== "Strict"

    ```bash
    git clone git@github.com:oslokommune/padda-databrikker.git
    cp -r padda-databrikker/bundles/autoloader_strict mitt-repo/bundles/min-pipeline
    ```

Navngi mappa etter hva pipelinen din gjør — for eksempel `folkeregister-innlasting` i
stedet for `min-pipeline`, som guiden bruker videre.

## Trinn 3: Konfigurer databricks.yml

Åpne `databricks.yml` og oppdater `bundle.name`, `workspace.host` og variabelverdiene under
`targets.prod`. De øvrige feltene skal beholdes som de er:

```yaml
bundle:
  name: min-pipeline # Bytt til et beskrivende navn

# ...

targets:
  prod:
    # ...
    workspace:
      host: https://<workspace-host>.cloud.databricks.com # Finn i 1Password
      # ...
    variables:
      catalog: min_katalog # Katalogen der tabellene skal opprettes
      schema: bronze_default # Skjemaet der tabellene skal opprettes
```

Workspace-host og katalogens navn finner du i 1Password. Ta kontakt med [plattformteamet](../../hjelp/index.md#kontakt-plattformteamet) om du ikke har tilgang.

La `workspace.root_path` stå — production-modus krever en eksplisitt root path. Se
[Mode-referansen](../../referanse/databricks-bundles.md#mode-referanse) for bakgrunnen.

## Trinn 4: Oppdater pipeline-konfigurasjonen

Åpne `resources/*.pipeline.yml` og gi pipelinen et beskrivende navn. `catalog` og `schema` hentes
fra variablene du satte i forrige trinn og skal ikke endres her:

```yaml
resources:
  pipelines:
    min_pipeline: # Oppdater
      name: min_pipeline # Oppdater
      catalog: ${var.catalog} # Hentes fra databricks.yml
      schema: ${var.schema} # Hentes fra databricks.yml
      # ...øvrige felter beholdes
```

Oppdaterer du ressursnøkkelen (`min_pipeline` rett under `pipelines`), må du også oppdatere
referansen `${resources.pipelines.<nøkkel>.id}` i `resources/*.job.yml`.

Gjør tilsvarende i `resources/*.job.yml`: gi jobben et beskrivende navn, og bytt ut adressa
under `email_notifications.on_failure` med den teamet ditt bruker for feilvarsler. Det er denne
jobben som starter pipelinen daglig.

## Trinn 5: Tilpass pipeline-SQL

Åpne `src/transformations/*.sql`. Malen definerer en bronze-tabell som leser fra landing
zone med Auto Loader, og silver-tabeller som viser typekonvertering og datakvalitetsregler
(expectations). Her er tre steder du må oppdatere:

1. S3-stien i `read_files()` — bytt til din landing zone-sender
2. Tabellnavnene i `CREATE ... TABLE`-setningene — de er på formen `skjema.tabell`, og katalogen
   hentes automatisk fra `catalog`-variabelen du satte i trinn 3
3. Silver-tabellene — tilpass kolonnenavn, typekonverteringer og expectations til dine
   data

=== "Permissive"

    ```sql
    CREATE OR REFRESH STREAMING TABLE bronze_default.min_tabell AS
    SELECT
      *,
      _metadata.file_path AS source_file_path,
      _metadata.file_modification_time AS source_file_modified_at,
      current_timestamp() AS ingested_at
    FROM
      STREAM read_files(
        's3://<landing-zone-bucket>/<sender-navn>/green/*.json',  -- Oppdater
        format => "json",
        schemaEvolutionMode => 'addNewColumns',
        inferColumnTypes => false
      );
    ```

    Med `inferColumnTypes => false` skrives alle kolonner som `STRING` til bronze. Silver-laget håndterer typekonvertering eksplisitt:

    ```sql
    CREATE OR REFRESH STREAMING TABLE silver_default.min_tabell (
        felt_1 STRING PRIMARY KEY NOT NULL COMMENT 'Beskriv kolonnen her',
        felt_2 INT NOT NULL COMMENT 'Beskriv kolonnen her',
        -- Gir bare en advarsel i loggene når regelen brytes
        CONSTRAINT gyldig_felt_2 EXPECT (felt_2 >= 0)
      ) AS
    SELECT
      felt_1,
      CAST(felt_2 AS INT) AS felt_2
    FROM
      STREAM bronze_default.min_tabell;
    ```

    Expectations uten `ON VIOLATION`-klausul gir bare en advarsel i loggene — radene som bryter regelen slipper gjennom.

=== "Strict"

    ```sql
    CREATE OR REFRESH STREAMING TABLE bronze_default.min_tabell (
        felt_1 STRING NOT NULL,
        felt_2 INT NOT NULL,
        -- Legg til alle forventede kolonner her
        source_file_path STRING NOT NULL,
        source_file_modified_at TIMESTAMP NOT NULL,
        ingested_at TIMESTAMP NOT NULL
      ) AS
    SELECT
      *,
      _metadata.file_path AS source_file_path,
      _metadata.file_modification_time AS source_file_modified_at,
      current_timestamp() AS ingested_at
    FROM
      STREAM read_files(
        's3://<landing-zone-bucket>/<sender-navn>/green/*.json',  -- Oppdater
        format => "json",
        schemaEvolutionMode => 'failOnNewColumns',
        mode => 'FAILFAST',
        schema => 'felt_1 string, felt_2 int, ...'  -- Angi forventet skjema
      );
    ```

    Med `FAILFAST` og `failOnNewColumns` vil pipelinen stoppe ved første uventede rad eller kolonne. Dette krever manuell oppdatering av skjemaet og en full refresh ved skjemaendringer i kilden.

    Silver-laget bruker expectations med `ON VIOLATION FAIL UPDATE`, som stopper oppdateringa når en rad bryter regelen:

    ```sql
    CREATE OR REFRESH STREAMING TABLE silver_default.min_tabell (
        felt_1 STRING PRIMARY KEY NOT NULL COMMENT 'Beskriv kolonnen her',
        felt_2 INT NOT NULL COMMENT 'Beskriv kolonnen her',
        -- Stopper oppdateringa når regelen brytes
        CONSTRAINT gyldig_felt_2 EXPECT (felt_2 >= 0) ON VIOLATION FAIL UPDATE
      ) AS
    SELECT
      felt_1,
      felt_2
    FROM
      STREAM bronze_default.min_tabell;
    ```

    Malen viser i tillegg hvordan silver-laget kan normaliseres med en `MATERIALIZED VIEW` og en fremmednøkkel — se `bundles/autoloader_strict/src/transformations/strict.sql` i malrepoet.

## Trinn 6: Deploy

Kjør følgende fra bundle-katalogen din (der `databricks.yml` ligger):

```bash
databricks bundle validate
databricks bundle deploy
```

`validate` fanger opp feil i konfigurasjonen — som skrivefeil i YAML eller manglende
variabelverdier — før noe når workspacet.

Den første deployen kan ta noe lengre tid fordi Databricks klargjør pipeline-ressursene.

## Bekreft resultatet

1. Gå til **Jobs & Pipelines** i sidemenyen i workspacet.
2. Finn pipelinen du nettopp deployet og start den manuelt med kjøreknappen. Du kan også
   starte den fra terminalen med `databricks bundle run <ressursnøkkel>`.
3. Vent til statusen viser **Completed**.
4. Åpne **Catalog Explorer** og kontroller at tabellene er opprettet under din katalog og ditt skjema.

Fremover vil pipelinen kjøre automatisk én gang daglig via den medfølgende jobbkonfigurasjonen.

## Feilsøking

??? failure "`UnknownFieldException`"

    Kildedata har fått en ny kolonne som ikke er definert i skjemaet.

    === "Permissive"

        Løsning:

        - Dette løser seg selv. Når feilen trigges, legges kolonnen til bronze-tabellen, og ved neste refresh leses dataene inn på riktig måte.
        - Merk at de videre tabellene ikke blir oppdatert. Pipelinen vil fortsette som før og rett og slett ignorere de nye kolonnene. For å få med disse i etterkant må du oppdatere silver-definisjonene og kjøre en full refresh.

    === "Strict"

        Løsning:

        - Legg til den nye kolonnen i `schema`-parameteren i `read_files()` og i de relevante `CREATE TABLE`-kommandoene.
        - Start en refresh. Full refresh er ikke nødvendig, siden radene aldri ble lest inn og det derfor ikke er noe å korrigere.

??? failure "Expectations feiler eller du får advarsler i loggene"

    Data samsvarer ikke med kvaliteten den skal ha.

    === "Permissive"

        Løsning:

        - Dataen har gått gjennom hele pipelinen. Alle relevante tabeller må korrigeres for hånd.

    === "Strict"

        Løsning:

        - Dataen har ikke blitt lest inn i tabellen der expectationen feilet, men den ligger i tabellene og kildene tidligere i pipelinen. Disse må korrigeres for hånd.
        - Når dataen er korrigert, leses alt som normalt ved neste refresh.

    Til slutt: Vurder om expectationen må endres, om den innkommende dataen må renses på noe vis, eller om kilden til dataen må kontaktes.

## Ytelsestips

Auto Loader lønner seg først og fremst for tabeller der det blir for dyrt å lese inn alt
på nytt hver gang. Det innebærer et visst datavolum, med utfordringene som følger med det.

### Regnekraft

Declarative Pipelines kjører på serverless som standard, men det er også mulig å bruke
dedikerte beregningsressurser. Gjør du det, kan du ofte spare penger ved å bruke et
cluster med en mindre driver-instanstype enn worker-instanstype. Dataflyt fra én tabell
til en annen er gjerne worker-tung og driver-lett. Når det gjelder valg av instanstype,
avhenger det av spørringene dine:

- **Enkle** (ingen aggregeringer eller joins, eller joins der kun én tabell er stor): Bruk compute-optimaliserte instanser.
- **Komplekse**: Bruk få (ideelt sett én) stor worker-instans med mye minne og lagring.

Du vil som regel befinne deg nærmere den enkle enden av dette spekteret.

### Lesing av data

Hvis antallet inndatafiler blir tilstrekkelig stort, kan det være verdt å vurdere [filvarslinger](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/file-notification-mode). I skrivende stund tillater ikke infrastrukturkonfigurasjonen vår dette, men det kan endres ved behov.

### Lagring

Se [Lagring og ytelse](../../referanse/lagring-og-ytelse.md).

## Relatert innhold

- [Laste opp filer til landing zone](./laste-opp-til-landing-zone.md)
- [Databricks-dokumentasjon om Auto Loader](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/)
- [Databricks-dokumentasjon om Declarative Pipelines (SQL)](https://docs.databricks.com/aws/en/ldp/dbsql/streaming)
