---
title: Sette opp Auto Loader
description: Hvordan lese inn filer inkrementelt fra landing zone til Unity Catalog med Auto Loader og Declarative Pipelines.
diataxis: how-to
---

# Sette opp Auto Loader

Denne guiden hjelper deg å sette opp en Declarative Pipeline som leser inn nye filer fra landing zone og lagrer dem i bronze- og silver-tabeller i Unity Catalog. Resultatet er en pipeline som kjører daglig og automatisk plukker opp nye filer uten å lese alt på nytt. Vi bruker en av to eksempler. Guiden bruker disse litt slavisk, men dere må selvsagt tilpasse alt til deres bruksområde.

## Før du begynner

Sørg for at du har:

- En landing zone-sender med en S3-sti du vil lese fra. Se [Laste opp filer til landing zone](./laste-opp-til-landing-zone.md) om du ikke har en.
- Databricks CLI installert og konfigurert mot riktig workspace. Se [Sett opp utviklingsmiljøet](../../kom-i-gang/dev-setup.md).
- Skrivetilgang til en katalog i Unity Catalog der tabellene skal opprettes.

## Trinn 1: Velg tilnærming

To bundle-varianter er tilgjengelige i [`padda-databrikker`-repoet](https://github.com/oslokommune/padda-databrikker/tree/main/bundles). Velg ut fra krav til datakvalitet:

|                           | Permissive                                          | Strict                                          |
| ------------------------- | --------------------------------------------------- | ----------------------------------------------- |
| Ny kolonne i kilden       | Legges automatisk til i bronze                      | Pipeline feiler — krever manuell håndtering     |
| Ugyldig eller korrupt rad | Slipper gjennom til bronze                          | Pipeline feiler                                 |
| Passer for                | Produkter der en feil rad her og der er akseptabelt | Produkter der ingen data er bedre enn feil data |

Dette er ikke egentlig et binært valg. I praksis vil man gjerne mikse og matche litt. Disse eksemplene er ment litt som illustrative ytterpunkter.

## Trinn 2: Kopier bundle-malen

Klon `padda-databrikker` og kopier riktig bundle inn i arbeidsrepoet ditt:

=== "Permissive"

    ```bash
    git clone https://github.com/oslokommune/padda-databrikker.git
    cp -r padda-databrikker/bundles/autoloader_permissive mitt-repo/bundles/min-pipeline
    ```

=== "Strict"

    ```bash
    git clone https://github.com/oslokommune/padda-databrikker.git
    cp -r padda-databrikker/bundles/autoloader_strict mitt-repo/bundles/min-pipeline
    ```

Navngi mappen etter hva pipelinen din gjør, for eksempel `folkeregister-innlasting`.

## Trinn 3: Konfigurer databricks.yml

Åpne `databricks.yml` og oppdater `bundle.name` og `workspace.host`:

```yaml
bundle:
  name: min-pipeline # Bytt til et beskrivende navn

targets:
  prod:
    workspace:
      host: https://<workspace-host>.cloud.databricks.com # Finn i 1Password
    variables:
      catalog: min_katalog # Katalogen der tabellene skal opprettes
      schema: bronze_default
```

Workspace-host og katalogens navn finner du i 1Password. Ta kontakt med [plattformteamet](../../hjelp/index.md#kontakt-plattformteamet) om du ikke har tilgang.

## Trinn 4: Oppdater pipeline-konfigurasjonen

Åpne `resources/*.pipeline.yml` og oppdater `catalog` og `schema` til å samsvare med verdiene fra forrige steg:

```yaml
resources:
  pipelines:
    min-pipeline:
      name: min-pipeline
      catalog: min_katalog # Oppdater
      schema: bronze_default # Oppdater
      serverless: true
      photon: true
      # ...øvrige felter beholdes
```

## Trinn 5: Tilpass pipeline-SQL

Åpne `src/transformations/*.sql`. Her er to steder du må oppdatere:

1. S3-stien i `read_files()` — bytt til din landing zone-sender
2. Alle `katalog.skjema.tabell`-referanser i `CREATE ... TABLE`-setningene

=== "Permissive"

    ```sql
    CREATE OR REFRESH STREAMING TABLE min_katalog.bronze_default.min_tabell AS
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

    Med `inferColumnTypes => false` skrives alle kolonner som `STRING` til bronze. Silver-laget håndterer typekonvertering eksplisitt.

=== "Strict"

    ```sql
    CREATE OR REFRESH STREAMING TABLE min_katalog.bronze_default.min_tabell (
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

## Trinn 6: Deploy

Kjør følgende fra bundle-katalogen din (der `databricks.yml` ligger):

```bash
databricks bundle deploy
```

Første gangs deploy kan ta noe lengre tid fordi Databricks klargjør pipeline-ressursene.

## Bekreft resultatet

1. Gå til **Workflows → Delta Live Tables** i Databricks-arbeidsområdet.
2. Finn pipelinen du nettopp deployet og klikk **Start** for å kjøre den manuelt.
3. Vent til statusen viser **Completed**.
4. Åpne **Catalog Explorer** og kontroller at tabellene er opprettet under din katalog og ditt skjema.

Fremover vil pipelinen kjøre automatisk én gang daglig via den medfølgende jobbkonfigurasjonen.

## Feilsøking

??? failure "`UnknownFieldException`"
Kildedata har fått en ny kolonne som ikke er definert i skjemaet.

=== "Permissive"

    Løsning:

      - Dette løser seg selv. Når denne feilen trigges vil kolonnen legges til bronse-tabellen, og ved neste refresh vil det lese inn på riktig måte.
      - Merk at de videre tabellene ikke blir oppdatert. Pipelinen vil fortsette som før og rett og slett ignorere de nye kolonnene. For å få med disse i etterkant kreves en full refresh.

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

    - Dataen har ikke blitt lest inn i tabellen med expectation. I de forestående tabellene og kildene før den der det feilet, derimot, ligger den problematiske dataen. Dette må korrigeres for hånd.
    - Ved neste refresh leses alt som normalt.

Til slutt: Vurder om enten expectationen må endres, om den inkommende dataen må renses på noe vis, eller om kilden på dataen må kontakteres.

## Ytelsestips

### Regnekraft

Declarative Pipelines kjører på serverless som standard, men det er også mulig å bruke dedikerte beregningsressurser. Hvis du bruker dedikerte beregningsressurser, kan du ofte spare penger ved å bruke et cluster med en mindre driver-instanstype enn worker-instanstype. Dataflyt fra én tabell til en annen er gjerne worker-tung og driver-lett. Når det gjelder valg av instanstype, avhenger det av spørringene dine:

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
