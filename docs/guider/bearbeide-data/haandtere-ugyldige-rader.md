---
title: Håndtere rader som ikke lar seg konvertere
description: Hvordan konvertere typer med try_cast og samle rader som bryter reglene i en karantenetabell, i stedet for å la én ugyldig verdi stoppe pipelinen.
diataxis: how-to
---

# Håndtere rader som ikke lar seg konvertere

Bronze-tabeller har gjerne alle kolonner som `STRING`, og får riktige datatyper først i
silver. En verdi som ikke lar seg konvertere blir `NULL`. Har kolonnen `NOT NULL`, så
stopper hele oppdateringen opp, mens hvis den ikke har `NOT NULL` så forsvinner verdien i
det stille. Denne guiden viser hvordan du konverterer med `try_cast`, lar expectations
forkaste radene som ikke ble konverterte, og samler dem i en karantenetabell.

## Før du begynner

Sørg for at du har:

- En bronze-tabell i Unity Catalog der kolonnene er `STRING`. I guiden brukes en
  eksempeltabell som heter `bronze_default.paddeobservasjoner`, men bare bytt ut dette med
  din egen.
- En Declarative Pipeline i bundlen din med egen kildemappe, se trinn 1 i [Skrive
  transformasjoner](skrive-transformasjoner.md). Guiden bruker mappa
  `src/paddeobservasjoner/transformations/`, ressursnøkkelen `paddeobservasjoner_pipeline`
  og target `stage`. Har bundlen din bare `prod`, slik Auto Loader-malen har, bytter du ut
  `stage` i kommandoene nedenfor.
- Databricks CLI innlogget mot stage-workspacet, se [Sett opp
  utviklingsmiljøet](../../kom-i-gang/dev-setup.md).
- Skrivetilgang til skjemaet `silver_default` i katalogen.

??? tip "Har du ikke en bronze-tabell å bruke?"

    Kjør dette i SQL-editoren eller en notebook. Bytt ut `min_katalog` med katalogen din.
    `obs-004` har negativt antall, `obs-006` har tekst i tallkolonnen, og `obs-007` har
    tidspunktet på et annet format.

    ```sql
    CREATE OR REPLACE TABLE min_katalog.bronze_default.paddeobservasjoner AS
    SELECT * FROM VALUES
      ('obs-001', 'Østensjøvannet', '12',     '2026-04-14T21:30:00'),
      ('obs-002', 'Sognsvann',      '3',      '2026-04-14T22:05:00'),
      ('obs-003', 'Østensjøvannet', '27',     '2026-04-15T21:45:00'),
      ('obs-004', 'Bogstadvannet',  '-1',     '2026-04-15T22:10:00'),
      ('obs-005', 'Sognsvann',      '8',      '2026-04-16T21:20:00'),
      ('obs-006', 'Bogstadvannet',  'ukjent', '2026-04-16T21:50:00'),
      ('obs-007', 'Østensjøvannet', '5',      '17.04.2026 21:40')
    AS t(observasjon_id, lokalitet, antall, observert);
    ```

## Trinn 1: Konverter med `try_cast` og forkast radene som feiler

`try_cast` gir `NULL` når verdien ikke kan konverteres, og `try_to_timestamp` gjør det
samme for tidspunkter, med et eksplisitt format, så du styrer hva som godtas.

`NULL`-verdiene fanges av expectations med `ON VIOLATION DROP ROW`, som forkaster raden
før den skrives. Har du fulgt [Skrive transformasjoner](skrive-transformasjoner.md),
erstatter du silver-tabellen derfra med denne:

=== "SQL"

    I filen `src/paddeobservasjoner/transformations/silver_paddeobservasjoner.sql`:

    ```sql
    CREATE OR REFRESH STREAMING TABLE silver_default.paddeobservasjoner (
        observasjon_id STRING PRIMARY KEY NOT NULL COMMENT 'Unik ID for observasjonen',
        lokalitet STRING NOT NULL COMMENT 'Dammen eller vannet der paddene ble observert',
        antall INT NOT NULL COMMENT 'Antall padder observert',
        observert TIMESTAMP NOT NULL COMMENT 'Tidspunkt for observasjonen',
        CONSTRAINT gyldig_antall EXPECT (antall IS NOT NULL AND antall >= 0) ON VIOLATION DROP ROW,
        CONSTRAINT gyldig_observert EXPECT (observert IS NOT NULL) ON VIOLATION DROP ROW
      )
      COMMENT 'Paddeobservasjoner med riktige typer'
      AS
    SELECT
      observasjon_id,
      lokalitet,
      try_cast(antall AS INT) AS antall,
      try_to_timestamp(observert, "yyyy-MM-dd'T'HH:mm:ss") AS observert
    FROM
      STREAM bronze_default.paddeobservasjoner;
    ```

=== "Python"

    I filen `src/paddeobservasjoner/transformations/silver_paddeobservasjoner.py`:

    ```python
    from pyspark import pipelines as dp
    from pyspark.sql import functions as F

    # Konverteringene defineres én gang og brukes av begge tabellene
    ANTALL = F.col("antall").try_cast("int")
    OBSERVERT = F.try_to_timestamp(F.col("observert"), F.lit("yyyy-MM-dd'T'HH:mm:ss"))


    @dp.table(
        name="silver_default.paddeobservasjoner",
        comment="Paddeobservasjoner med riktige typer",
        schema="""
            observasjon_id STRING PRIMARY KEY NOT NULL COMMENT 'Unik ID for observasjonen',
            lokalitet STRING NOT NULL COMMENT 'Dammen eller vannet der paddene ble observert',
            antall INT NOT NULL COMMENT 'Antall padder observert',
            observert TIMESTAMP NOT NULL COMMENT 'Tidspunkt for observasjonen'
        """,
    )
    @dp.expect_or_drop("gyldig_antall", "antall IS NOT NULL AND antall >= 0")
    @dp.expect_or_drop("gyldig_observert", "observert IS NOT NULL")
    def paddeobservasjoner():
        return spark.readStream.table("bronze_default.paddeobservasjoner").select(
            F.col("observasjon_id"),
            F.col("lokalitet"),
            ANTALL.alias("antall"),
            OBSERVERT.alias("observert"),
        )
    ```

Expectations evalueres på raden slik den ser ut etter `SELECT`, så `antall IS NOT NULL`
gjelder den konverterte verdien, og raden forkastes før `NOT NULL` på kolonnen sjekkes.
Skal en manglende verdi heller stoppe pipelinen, for eksempel i nøkkelkolonnen
`observasjon_id`, bruker du `ON VIOLATION FAIL UPDATE` eller `@dp.expect_or_fail`. Se
[Datakvalitet](../../referanse/datakvalitet.md#constraints-og-expectations) for detaljer.

Tall med desimalkomma eller tusenskille konverterer du med
[`try_to_number`](https://docs.databricks.com/aws/en/sql/language-manual/functions/try_to_number),
og formatbokstavene for tidspunkter står i [Datetime
patterns](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-datetime-pattern).
Bruker du AUTO CDC slik [Deduplisere data i silver](deduplisere-data.md) viser, legger du
konverteringene og expectations i staging-viewet i stedet, som tar `CONSTRAINT`-klausuler
og `@dp.expect_or_drop` på samme måte.

## Trinn 2: Skriv karantenetabellen

Karantenetabellen leser samme bronze-tabell og beholder radene som silver forkastet, med
verdiene slik de var i bronze og navnet på regelen de brøt. Reglene er de samme som i
silver, men anvendt på de ukonverterte verdiene, så de to må endres i takt. Legg dette til
i samme fil:

=== "SQL"

    ```sql
    CREATE OR REFRESH STREAMING TABLE silver_default.paddeobservasjoner_karantene
      COMMENT 'Rader fra bronze som brøt reglene for silver_default.paddeobservasjoner'
      AS
    WITH sjekket AS (
      SELECT
        *,
        concat_ws(', ',
          CASE WHEN try_cast(antall AS INT) IS NULL OR try_cast(antall AS INT) < 0
            THEN 'gyldig_antall' END,
          CASE WHEN try_to_timestamp(observert, "yyyy-MM-dd'T'HH:mm:ss") IS NULL
            THEN 'gyldig_observert' END
        ) AS brutte_regler,
        current_timestamp() AS lagt_i_karantene
      FROM
        STREAM bronze_default.paddeobservasjoner
    )
    SELECT * FROM sjekket WHERE brutte_regler <> '';
    ```

=== "Python"

    ```python
    @dp.table(
        name="silver_default.paddeobservasjoner_karantene",
        comment="Rader fra bronze som brøt reglene for silver_default.paddeobservasjoner",
    )
    def paddeobservasjoner_karantene():
        brutte_regler = F.concat_ws(
            ", ",
            F.when(ANTALL.isNull() | (ANTALL < 0), "gyldig_antall"),
            F.when(OBSERVERT.isNull(), "gyldig_observert"),
        )
        return (
            spark.readStream
            .table("bronze_default.paddeobservasjoner")
            .withColumn("brutte_regler", brutte_regler)
            .withColumn("lagt_i_karantene", F.current_timestamp())
            .where("brutte_regler <> ''")
        )
    ```

Kolonnen `lagt_i_karantene` sier når raden ble skrevet til karantenetabellen. Kommer
bronze-tabellen fra Auto Loader, følger `source_file_path` og `source_file_modified_at`
med, så du ser hvilken fil hver rad kom fra.

## Trinn 3: Deploy og kjør

Valider og deploy bundlen til stage, og kjør pipelinen:

```bash
databricks bundle validate -t stage -p MY_TEAM_STAGE
databricks bundle deploy -t stage -p MY_TEAM_STAGE
databricks bundle run -t stage -p MY_TEAM_STAGE paddeobservasjoner_pipeline
```

## Bekreft resultatet

Når pipelinen viser **Completed** under **Jobs & Pipelines**, klikk på silver-tabellen i
grafen og åpne fanen **Data quality**. Med testtabellen skal `gyldig_antall` ha forkastet
to rader og `gyldig_observert` én, og silver-tabellen skal ha fire rader.
Karantenetabellen skal ha de tre som ble forkastet:

| observasjon_id | lokalitet      | antall | observert           | brutte_regler    |
|----------------|----------------|--------|---------------------|------------------|
| obs-004        | Bogstadvannet  | -1     | 2026-04-15T22:10:00 | gyldig_antall    |
| obs-006        | Bogstadvannet  | ukjent | 2026-04-16T21:50:00 | gyldig_antall    |
| obs-007        | Østensjøvannet | 5      | 17.04.2026 21:40    | gyldig_observert |

## Følge opp karantenetabellen

Rettes en rad i kilden, kommer rettelsen som en ny rad i bronze og går til silver som
vanlig, mens karanteneraden står igjen som historikk. Sjekk tabellen jevnlig, eller sett
opp et varsel som utløses når den får nye rader, se [Varsling og
alarmer](../../referanse/varsling-og-alarmer.md). Er det regelen eller formatet som er
feil, endrer du transformasjonen og gir begge tabellene en full refresh, se [Gjenopprette
etter feil i
pipelines](../overvaake-og-drifte/gjenopprette-etter-feil.md#trinn-4-handter-en-schema-endring-som-bryter-pipelinen).

## Feilsøking

??? failure "`DELTA_NOT_NULL_CONSTRAINT_VIOLATED`"

    En verdi ble `NULL` uten at noen expectation forkastet raden. Finn raden i bronze ved å
    kjøre konverteringen som spørring:

    ```sql
    SELECT * FROM min_katalog.bronze_default.paddeobservasjoner
    WHERE try_cast(antall AS INT) IS NULL;
    ```

    Legg så til en expectation for kolonnen, eller rett verdien i kilden.

??? failure "`EXPECTATION_VIOLATION`"

    En expectation med `FAIL UPDATE` slo til, og feilmeldinga viser regelen og raden. Rett
    dataene i kilden, eller endre regelen, før du kjører på nytt.

Feiler kjøringa av andre grunner, se [Feilsøke med
logger](../overvaake-og-drifte/logging.md) og [Gjenopprette etter feil i
pipelines](../overvaake-og-drifte/gjenopprette-etter-feil.md).

## Relatert innhold

**Guider:**

- [Skrive transformasjoner](skrive-transformasjoner.md)
- [Deduplisere data i silver](deduplisere-data.md)
- [Sette opp Auto Loader](../hente-inn-data/auto-loader.md)

**Forklaringer:**

- [Klassifisering av datakvalitet](../../om-plattformen/konsepter/klassifisering-datakvalitet.md)

**Referanser:**

- [Datakvalitet](../../referanse/datakvalitet.md)

**Ekstern dokumentasjon:**

- [Manage data quality with pipeline expectations](https://docs.databricks.com/aws/en/ldp/expectations)
- [Expectation recommendations and advanced patterns](https://docs.databricks.com/aws/en/ldp/expectation-patterns)
- [try_cast function](https://docs.databricks.com/aws/en/sql/language-manual/functions/try_cast)
