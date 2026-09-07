---
title: Deduplisere data i silver
description: Hvordan beholde siste versjon av hver rad i silver med AUTO CDC når bronze inneholder flere leveranser av samme data.
diataxis: how-to
---

# Deduplisere data i silver

Leverer kilden hele datasettet på nytt hver gang, eller sender samme rad flere ganger, får
bronze flere rader per nøkkel. Denne guiden viser hvordan du bygger en silver-tabell som
alltid inneholder siste versjon av hver rad, med [AUTO
CDC](https://docs.databricks.com/aws/en/ldp/cdc) i en Declarative Pipeline. Det er
mekanismen Databricks anbefaler for kildedata som endrer seg over tid. Du kan skrive
transformasjonen i SQL eller Python. Eksemplene bruker et fiktivt datasett med
paddeobservasjoner fra dammer i Oslo, men framgangsmåten er den samme for dine egne data.

## Før du begynner

Sørg for at du har:

- En bronze-tabell i Unity Catalog med en nøkkelkolonne og en kolonne som sier hvilken
  leveranse raden kom med. Tabeller fra [Sette opp Auto
  Loader](../hente-inn-data/auto-loader.md) har `source_file_modified_at`. Guiden antar at
  tabellen heter `bronze_default.paddeobservasjoner`.
- En Declarative Pipeline i bundlen din med egen kildemappe, se trinn 1 i [Skrive
  transformasjoner](skrive-transformasjoner.md). Guiden bruker mappa
  `src/paddeobservasjoner/transformations/`, ressursnøkkelen `paddeobservasjoner_pipeline`
  og targetet `stage`. Har bundlen din bare `prod`, slik Auto Loader-malen har, bytter du
  ut `stage` i kommandoene nedenfor.
- Databricks CLI innlogget mot stage-workspacet, se [Sett opp
  utviklingsmiljøet](../../kom-i-gang/dev-setup.md).
- Skrivetilgang til skjemaet `silver_default` i katalogen.

Eksemplene bruker kolonnene i `bronze_default.paddeobservasjoner`. Med egne data bytter du
ut tre ting: nøkkelkolonnen `observasjon_id` i `KEYS`, leveransekolonnen
`source_file_modified_at` i `SEQUENCE BY`, og kolonnelista med typekonverteringer i
staging-viewet i trinn 1.

??? tip "Har du ikke en bronze-tabell å teste med?"

    Kjør dette i SQL-editoren eller en notebook. Bytt ut `min_katalog` med katalogen din.
    Tabellen har to leveranser: den andre leverer alt på nytt, retter antallet i `obs-003`
    fra 27 til 25 og legger til `obs-004`.

    ```sql
    CREATE OR REPLACE TABLE min_katalog.bronze_default.paddeobservasjoner AS
    SELECT * FROM VALUES
      ('obs-001', 'Østensjøvannet', '12', '2026-04-14T21:30:00', TIMESTAMP '2026-04-16 06:00:00'),
      ('obs-002', 'Sognsvann',      '3',  '2026-04-14T22:05:00', TIMESTAMP '2026-04-16 06:00:00'),
      ('obs-003', 'Østensjøvannet', '27', '2026-04-15T21:45:00', TIMESTAMP '2026-04-16 06:00:00'),
      ('obs-001', 'Østensjøvannet', '12', '2026-04-14T21:30:00', TIMESTAMP '2026-04-17 06:00:00'),
      ('obs-002', 'Sognsvann',      '3',  '2026-04-14T22:05:00', TIMESTAMP '2026-04-17 06:00:00'),
      ('obs-003', 'Østensjøvannet', '25', '2026-04-15T21:45:00', TIMESTAMP '2026-04-17 06:00:00'),
      ('obs-004', 'Bogstadvannet',  '8',  '2026-04-16T22:10:00', TIMESTAMP '2026-04-17 06:00:00')
    AS t(observasjon_id, lokalitet, antall, observert, source_file_modified_at);
    ```

## Trinn 1: Skriv staging-viewet

Flowen som skal fylle silver-tabellen, leser fra en tabell eller et view, ikke fra en
`SELECT`. Typekonverteringen legger du derfor i et midlertidig view som leser
bronze-tabellen som strøm. Viewet finnes bare inne i pipelinen og lagres ikke i
katalogen. Opprett en fil i `src/paddeobservasjoner/transformations/`. Har du fulgt
[Skrive transformasjoner](skrive-transformasjoner.md), erstatter du silver-tabellen derfra
med viewet her og flowen i trinn 2, siden en tabell bare kan defineres én gang i
pipelinen:

=== "SQL"

    I filen `src/paddeobservasjoner/transformations/silver_paddeobservasjoner.sql`:

    ```sql
    CREATE TEMPORARY VIEW paddeobservasjoner_staged AS
    SELECT
      observasjon_id,
      lokalitet,
      CAST(antall AS INT) AS antall,
      CAST(observert AS TIMESTAMP) AS observert,
      source_file_modified_at
    FROM
      STREAM bronze_default.paddeobservasjoner;
    ```

=== "Python"

    I filen `src/paddeobservasjoner/transformations/silver_paddeobservasjoner.py`:

    ```python
    from pyspark import pipelines as dp
    from pyspark.sql import functions as F


    @dp.temporary_view
    def paddeobservasjoner_staged():
        return spark.readStream.table("bronze_default.paddeobservasjoner").select(
            F.col("observasjon_id"),
            F.col("lokalitet"),
            F.col("antall").cast("int").alias("antall"),
            F.col("observert").cast("timestamp").alias("observert"),
            F.col("source_file_modified_at"),
        )
    ```

## Trinn 2: Opprett silver-tabellen og flowen

Silver-tabellen opprettes uten spørring. Radene kommer fra en *flow* som leser viewet og
oppdaterer tabellen per nøkkel. Legg dette til i samme fil:

=== "SQL"

    ```sql
    CREATE OR REFRESH STREAMING TABLE silver_default.paddeobservasjoner (
        observasjon_id STRING PRIMARY KEY NOT NULL COMMENT 'Unik ID for observasjonen',
        lokalitet STRING NOT NULL COMMENT 'Dammen eller vannet der paddene ble observert',
        antall INT NOT NULL COMMENT 'Antall padder observert',
        observert TIMESTAMP NOT NULL COMMENT 'Tidspunkt for observasjonen',
        source_file_modified_at TIMESTAMP NOT NULL COMMENT 'Leveransen raden sist ble oppdatert fra'
      )
      COMMENT 'Paddeobservasjoner, siste versjon av hver observasjon';

    CREATE FLOW paddeobservasjoner_siste_versjon AS
    AUTO CDC INTO silver_default.paddeobservasjoner
    FROM stream(paddeobservasjoner_staged)
    KEYS (observasjon_id)
    SEQUENCE BY source_file_modified_at
    STORED AS SCD TYPE 1;
    ```

=== "Python"

    ```python
    dp.create_streaming_table(
        name="silver_default.paddeobservasjoner",
        comment="Paddeobservasjoner, siste versjon av hver observasjon",
        schema="""
            observasjon_id STRING PRIMARY KEY NOT NULL COMMENT 'Unik ID for observasjonen',
            lokalitet STRING NOT NULL COMMENT 'Dammen eller vannet der paddene ble observert',
            antall INT NOT NULL COMMENT 'Antall padder observert',
            observert TIMESTAMP NOT NULL COMMENT 'Tidspunkt for observasjonen',
            source_file_modified_at TIMESTAMP NOT NULL COMMENT 'Leveransen raden sist ble oppdatert fra'
        """,
    )

    dp.create_auto_cdc_flow(
        target="silver_default.paddeobservasjoner",
        source="paddeobservasjoner_staged",
        keys=["observasjon_id"],
        sequence_by=F.col("source_file_modified_at"),
        stored_as_scd_type=1,
    )
    ```

`KEYS` er kolonnene som peker ut én rad i kilden, og `SEQUENCE BY` er kolonnen som sier
hvilken versjon som er nyest. Har kilden et eget tidspunkt for siste endring, bruk det
heller enn `source_file_modified_at`. `SCD TYPE 1` betyr at bare siste versjon lagres, se
[Beholde historikk](#beholde-historikk) for alternativet. En rad med lavere sekvensverdi
enn den som står i tabellen forkastes, så rekkefølgen radene leses inn i spiller ingen
rolle.

## Trinn 3: Deploy og kjør

Valider og deploy bundlen til stage, og kjør pipelinen:

```bash
databricks bundle validate -t stage -p MY_TEAM_STAGE
databricks bundle deploy -t stage -p MY_TEAM_STAGE
databricks bundle run -t stage -p MY_TEAM_STAGE paddeobservasjoner_pipeline
```

## Bekreft resultatet

Når pipelinen viser **Completed** under **Jobs & Pipelines**, skal denne spørringen ikke
returnere noen rader:

```sql
SELECT observasjon_id, COUNT(*) AS antall_rader
FROM min_katalog.silver_default.paddeobservasjoner
GROUP BY observasjon_id
HAVING COUNT(*) > 1;
```

Med testtabellen skal silver-tabellen ha fire rader, og `obs-003` skal ha `antall` 25.

## Beholde historikk

Skal tidligere versjoner også være tilgjengelige, bytter du ut `SCD TYPE 1` med `SCD TYPE
2`, eller `stored_as_scd_type=1` med `stored_as_scd_type=2`. Tabellen får da én rad per
versjon, med kolonnene `__START_AT` og `__END_AT`. Gjeldende versjon har `__END_AT` lik
`NULL`. Oppgir du skjema for tabellen, må de to kolonnene stå i skjemaet med samme type
som sekvenskolonnen. Leverer kilden alt på nytt hver gang, får også uendrede rader ny
versjon, fordi `source_file_modified_at` endrer seg. Unnta kolonnen med `TRACK HISTORY
ON * EXCEPT (source_file_modified_at)` i SQL eller
`track_history_except_column_list=["source_file_modified_at"]` i Python.

## Endre transformasjonen senere

Endringer i viewet eller flowen gjelder bare rader som leses inn etterpå. Skal de gjelde
rader som allerede ligger i silver-tabellen, trenger tabellen en full refresh, se
[Gjenopprette etter feil i
pipelines](../overvaake-og-drifte/gjenopprette-etter-feil.md#trinn-4-handter-en-schema-endring-som-bryter-pipelinen).

## Feilsøking

??? failure "Pipelinen feiler fordi sekvenskolonnen er `NULL`"

    `SEQUENCE BY` godtar ikke `NULL`. Filtrer bort radene uten verdi i staging-viewet,
    eller bruk en annen kolonne.

??? failure "Silver-tabellen har feil versjon av en rad"

    `source_file_modified_at` er tidspunktet fila ble lagt i landing zone, ikke når raden
    ble endret i kilden. Leverer kilden gamle filer på nytt, bruk et tidspunkt fra kilden
    som sekvenskolonne.

Feiler kjøringa av andre grunner, se [Feilsøke med
logger](../overvaake-og-drifte/logging.md) og [Gjenopprette etter feil i
pipelines](../overvaake-og-drifte/gjenopprette-etter-feil.md).

## Relatert innhold

**Guider:**

- [Skrive transformasjoner](skrive-transformasjoner.md)
- [Håndtere rader som ikke lar seg konvertere](haandtere-ugyldige-rader.md)
- [Sette opp Auto Loader](../hente-inn-data/auto-loader.md)

**Forklaringer:**

- [Klassifisering av datakvalitet](../../om-plattformen/konsepter/klassifisering-datakvalitet.md)

**Ekstern dokumentasjon:**

- [The AUTO CDC APIs](https://docs.databricks.com/aws/en/ldp/cdc)
- [AUTO CDC INTO (SQL)](https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-apply-changes-into)
- [create_auto_cdc_flow (Python)](https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-apply-changes)
