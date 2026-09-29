---
title: Skrive transformasjoner
description: Hvordan skrive, kjøre og verifisere en transformasjon fra bronze til silver og gold som en Declarative Pipeline i bundlen din.
diataxis: how-to
---

# Skrive transformasjoner

Denne guiden viser hvordan du legger en transformasjon i bundlen din som en egen
[Declarative Pipeline](https://docs.databricks.com/aws/en/ldp/): den leser fra en
bronze-tabell, skriver en silver-tabell med riktige typer og kvalitetsregler, og en
gold-tabell med aggregerte tall. Du kan skrive transformasjonen i SQL eller Python, se
[Anbefalte språk](../../referanse/anbefalte-spraak.md). Hva silver og gold skal inneholde,
står i [Klassifisering av
datakvalitet](../../om-plattformen/konsepter/klassifisering-datakvalitet.md). Eksemplet
bruker et lite, fiktivt datasett med paddeobservasjoner fra dammer i Oslo. Bytt ut tabell-
og kolonnenavn med dine egne, eller bruk testtabellen som den er.

## Før du begynner

Sørg for at du har:

- En bronze-tabell i Unity Catalog, for eksempel fra [Sette opp Auto
  Loader](../hente-inn-data/auto-loader.md). Guiden antar at den heter
  `bronze_default.paddeobservasjoner`, og at alle kolonner er `STRING`. Har du ingen,
  lager du en testtabell nedenfor.
- En bundle å legge transformasjonen i, med variabelen `catalog` satt per target. Se [Ta i
  bruk bundles](../utvikle-og-deploye/ta-i-bruk-bundles.md). Guiden deployer til targetet `stage`. Har bundlen
  din bare `prod`, slik Auto Loader-malen har, bytter du ut `stage` i kommandoene
  nedenfor.
- Databricks CLI innlogget mot stage-workspacet, se [Sett opp
  utviklingsmiljøet](../../kom-i-gang/dev-setup.md).
- Skrivetilgang til skjemaene `silver_default` og `gold_default` i katalogen.

### Lag en testtabell

Kjør dette i SQL-editoren eller en notebook for å få en bronze-tabell å øve på. Bytt ut
`min_katalog` med katalogen din. Alle kolonner er `STRING`, slik Auto Loader leverer dem,
og én rad har negativt antall og skal forkastes i transformasjonssteget før den når
silver-tabellen.

```sql
CREATE TABLE min_katalog.bronze_default.paddeobservasjoner AS
SELECT * FROM VALUES
  ('obs-001', 'Østensjøvannet', '12', '2026-04-14T21:30:00'),
  ('obs-002', 'Sognsvann',      '3',  '2026-04-14T22:05:00'),
  ('obs-003', 'Østensjøvannet', '27', '2026-04-15T21:45:00'),
  ('obs-004', 'Bogstadvannet',  '-1', '2026-04-15T22:10:00'),
  ('obs-005', 'Sognsvann',      '8',  '2026-04-16T21:20:00')
AS t(observasjon_id, lokalitet, antall, observert);
```

## Trinn 1: Legg til en pipeline i bundlen

Transformasjonen får sin egen pipeline, adskilt fra innlastinga. Hvorfor, og hva
alternativet er, står i
[Datainnlasting](../../om-plattformen/konsepter/datainnlasting.md#en-pipeline-eller-flere).

Hver pipeline trenger sin egen kildemappe, siden en fil, og dermed tabellene den
definerer, bare kan tilhøre én pipeline. Innlastingspipelinen fra Auto Loader-malen eier
alt under `src/transformations/`, så transformasjonene får mappa
`src/paddeobservasjoner/transformations/`.

Opprett `resources/paddeobservasjoner.pipeline.yml`:

```yaml
resources:
  pipelines:
    paddeobservasjoner_pipeline:
      name: paddeobservasjoner_pipeline
      catalog: ${var.catalog}
      # Standardskjema. Koden under oppgir skjema eksplisitt på hver tabell.
      schema: silver_default
      serverless: true
      root_path: ../src/paddeobservasjoner
      libraries:
        - glob:
            include: ../src/paddeobservasjoner/transformations/**
```

Alle filer under `src/paddeobservasjoner/transformations/` blir en del av pipelinen.
Definerer innlastingspipelinen allerede silver-tabeller, som Auto Loader-malen gjør,
fjerner du dem derfra og skriver dem her i stedet.

## Trinn 2: Skriv silver-tabellen

Silver-tabellen er en
[streaming-tabell](https://docs.databricks.com/aws/en/ldp/concepts/streaming-tables): den
leser bronze-tabellen radvis, gir kolonnene riktige typer og legger på kvalitetsregler.
Opprett én fil per tabell i `src/paddeobservasjoner/transformations/`:

=== "SQL"

    I filen `src/paddeobservasjoner/transformations/silver_paddeobservasjoner.sql`:

    ```sql
    CREATE OR REFRESH STREAMING TABLE silver_default.paddeobservasjoner (
        observasjon_id STRING PRIMARY KEY NOT NULL COMMENT 'Unik ID for observasjonen',
        lokalitet STRING NOT NULL COMMENT 'Dammen eller vannet der paddene ble observert',
        antall INT NOT NULL COMMENT 'Antall padder observert',
        observert TIMESTAMP NOT NULL COMMENT 'Tidspunkt for observasjonen',
        -- Rader med negativt antall forkastes, og antallet telles i pipelinen
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

=== "Python"

    I filen `src/paddeobservasjoner/transformations/silver_paddeobservasjoner.py`:

    ```python
    from pyspark import pipelines as dp
    from pyspark.sql import functions as F


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
    # Rader med negativt antall forkastes, og antallet telles i pipelinen
    @dp.expect_or_drop("gyldig_antall", "antall >= 0")
    def paddeobservasjoner():
        return spark.readStream.table("bronze_default.paddeobservasjoner").select(
            F.col("observasjon_id"),
            F.col("lokalitet"),
            F.col("antall").cast("int").alias("antall"),
            F.col("observert").cast("timestamp").alias("observert"),
        )
    ```

    `spark` er tilgjengelig i pipeline-filer uten import.

`STREAM` i SQL og `readStream` i Python gjør at hver kjøring bare tar med rader som er nye
siden sist. `NOT NULL` stopper hele oppdateringa ved brudd, mens en expectation kan
advare, forkaste raden eller stoppe, se
[Datakvalitet](../../referanse/datakvalitet.md#constraints-og-expectations).

## Trinn 3: Skriv gold-tabellen

Gold-tabellen teller observasjoner og padder per dag. Aggregeringer og joins skrives som
[materialisert view](https://docs.databricks.com/aws/en/ldp/concepts/materialized-views),
som pipelinen oppdaterer ved hver kjøring fra gjeldende silver-data.

=== "SQL"

    I filen `src/paddeobservasjoner/transformations/gold_padder_per_dag.sql`:

    ```sql
    CREATE OR REFRESH MATERIALIZED VIEW gold_default.padder_per_dag
      COMMENT 'Antall observasjoner og antall padder per dag'
      AS
    SELECT
      DATE(observert) AS dato,
      COUNT(*) AS antall_observasjoner,
      SUM(antall) AS antall_padder
    FROM
      silver_default.paddeobservasjoner
    GROUP BY
      DATE(observert);
    ```

=== "Python"

    I filen `src/paddeobservasjoner/transformations/gold_padder_per_dag.py`:

    ```python
    from pyspark import pipelines as dp
    from pyspark.sql import functions as F


    @dp.materialized_view(
        name="gold_default.padder_per_dag",
        comment="Antall observasjoner og antall padder per dag",
    )
    def padder_per_dag():
        return (
            spark.read
            .table("silver_default.paddeobservasjoner")
            .groupBy(F.to_date("observert").alias("dato"))
            .agg(
                F.count("*").alias("antall_observasjoner"),
                F.sum("antall").alias("antall_padder"),
            )
        )
    ```

## Trinn 4: Legg transformasjonen inn i innlastingsjobben

Legg pipelinen til som en task i jobben som starter innlastinga, med avhengighet til
innlastingstasken. Alternativet, en egen jobb med egen tidsplan, er beskrevet i
[Datainnlasting](../../om-plattformen/konsepter/datainnlasting.md#egen-jobb-eller-task-i-en-strre-jobb).

Utvid `resources/*.job.yml`:

```yaml
resources:
  jobs:
    paddeobservasjoner_job:
      name: paddeobservasjoner_job
      # ...
      tasks:
        - task_key: innlasting_task
          pipeline_task:
            pipeline_id: ${resources.pipelines.innlasting_pipeline.id}
        - task_key: transformasjon_task
          depends_on:
            - task_key: innlasting_task
          pipeline_task:
            pipeline_id: ${resources.pipelines.paddeobservasjoner_pipeline.id}
```

Den første tasken er den som allerede finnes i jobben. Bytt ut `innlasting_pipeline` med
ressursnøkkelen til innlastingspipelinen din, og gi tasken nøkkelen `innlasting_task`,
eller behold nøkkelen den har og bruk den i `depends_on`. Kjør jobben når du vil teste
innlasting og transformasjon sammen. Øver du med testtabellen, hopper du over dette
trinnet og kjører pipelinen direkte i neste trinn.

## Trinn 5: Deploy og kjør

Valider og deploy bundlen til stage, og kjør transformasjonen:

```bash
databricks bundle validate -t stage -p MY_TEAM_STAGE
databricks bundle deploy -t stage -p MY_TEAM_STAGE
databricks bundle run -t stage -p MY_TEAM_STAGE paddeobservasjoner_pipeline
```

Legg til `--validate-only` på `run`-kommandoen for å sjekke syntaks og avhengigheter uten
å oppdatere data.

## Bekreft resultatet

1. Gå til **Jobs & Pipelines** i sidemenyen, åpne pipelinen og vent til statusen viser
   **Completed**. Grafen skal vise silver-tabellen med gold-tabellen etter seg.
2. Klikk på silver-tabellen i grafen og åpne fanen **Data quality**. Der står hvor mange
   rader som passerte og hvor mange som ble forkastet av `gyldig_antall`. Med testtabellen
   skal fire rader ha passert og én være forkastet.
3. Åpne **Catalog Explorer** og kontroller at tabellene ligger i `silver_default` og
   `gold_default` i katalogen din, med kolonnekommentarene du skrev. Med testtabellen skal
   `padder_per_dag` ha tre rader:

    | dato       | antall_observasjoner | antall_padder |
    |------------|----------------------|---------------|
    | 2026-04-14 | 2                    | 15            |
    | 2026-04-15 | 1                    | 27            |
    | 2026-04-16 | 1                    | 8             |

## Endre transformasjonen senere

For et materialisert view er det nok å deploye og kjøre på nytt. En streaming-tabell
trenger en full refresh for at endringa skal gjelde rader som allerede er lest inn, se
[Gjenopprette etter feil i
pipelines](../overvaake-og-drifte/gjenopprette-etter-feil.md#trinn-4-handter-en-schema-endring-som-bryter-pipelinen).

## Feilsøking

??? failure "Pipelinen finner ikke bronze-tabellen"

    Sannsynlige årsaker:

    - `catalog` i pipelinen peker på en annen katalog enn den bronze-tabellen ligger i.
      Sjekk variabelverdien for targetet du deployet til.
    - Tabellnavnet i koden mangler skjema. Oppgi `bronze_default.<tabell>`, ikke bare
      `<tabell>`, siden pipelinens standardskjema er et annet.
    - Innlastingspipelinen har ikke kjørt ennå i dette workspacet, så tabellen finnes
      ikke.

??? failure "Pipelinen feiler fordi en tabell allerede tilhører en annen pipeline"

    Sannsynlige årsaker:

    - Innlastingspipelinen definerer fortsatt en silver-tabell med samme navn. Fjern den
      derfra.
    - `libraries`-globen i de to pipelinene overlapper, så samme fil leses av begge.
      Gi hver pipeline sin egen mappe under `src/`, som i trinn 1.

Feiler kjøringa av andre grunner, se [Feilsøke med
logger](../overvaake-og-drifte/logging.md) og [Gjenopprette etter feil i
pipelines](../overvaake-og-drifte/gjenopprette-etter-feil.md).

## Relatert innhold

**Guider:**

- [Deduplisere data i silver](deduplisere-data.md)
- [Håndtere rader som ikke lar seg konvertere](haandtere-ugyldige-rader.md)
- [Dokumentere et dataprodukt](../dele-og-hente-ut/dokumentere-dataprodukt.md)
- [Sette opp Auto Loader](../hente-inn-data/auto-loader.md)
- [Ta i bruk bundles](../utvikle-og-deploye/ta-i-bruk-bundles.md)

**Forklaringer:**

- [Datainnlasting](../../om-plattformen/konsepter/datainnlasting.md)
- [Klassifisering av datakvalitet](../../om-plattformen/konsepter/klassifisering-datakvalitet.md)

**Referanser:**

- [Datakvalitet](../../referanse/datakvalitet.md)
- [Navnekonvensjoner](../../referanse/navnekonvensjoner.md#bundles-jobber-og-pipelines)

**Ekstern dokumentasjon:**

- [Develop pipeline code with SQL](https://docs.databricks.com/aws/en/ldp/developer/sql-dev)
- [Develop pipeline code with Python](https://docs.databricks.com/aws/en/ldp/developer/python-dev)
