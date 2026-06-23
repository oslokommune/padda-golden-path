---
title: Skrive transformasjoner
description: Hvordan skrive, teste og kjøre en datatransformasjon i en notebook eller pipeline.
diataxis: how-to
---

# Skrive transformasjoner

Denne guiden viser hvordan du skriver en transformasjon som leser fra én tabell,
gjør om dataene, og skriver resultatet til en ny tabell — og hvordan du tester
og pakker den som en jobb. Vi bruker referanseeksempelet
[`examples/csv_pipeline`](https://github.com/oslokommune/padda-golden-path/tree/main/examples/csv_pipeline)
gjennom hele guiden.

For bakgrunn om hvorfor data beveger seg gjennom bronze, silver og gold, se
[Klassifisering av datakvalitet
(konsept)](../../om-plattformen/konsepter/klassifisering-datakvalitet.md). For de
lagspesifikke transformasjonene, se [Bronze til silver](bronze-til-silver.md) og
[Silver til gold](silver-til-gold.md).

## Forutsetninger

- [uv](https://docs.astral.sh/uv/) installert
- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install.html)
  installert og autentisert mot workspacet ditt
- Klonet `padda-golden-path`-repoet
- En kildetabell å lese fra (for eksempel en bronze-tabell fra [Auto
  Loader](../hente-inn-data/auto-loader.md))

## Skill transformasjonslogikk fra orkestrering

Den viktigste vanen når du skriver transformasjoner: legg selve logikken i rene
funksjoner som tar en `DataFrame` inn og returnerer en `DataFrame` ut. Disse
funksjonene kjenner ikke til Spark-sesjonen, kataloger eller tabellnavn — de gjør
bare én transformasjon. Det er det som gjør dem enkle å teste.

I `csv_pipeline` ligger logikken i `src/csv_pipeline/transform.py`:

```python title="src/csv_pipeline/transform.py"
from __future__ import annotations

from typing import TYPE_CHECKING

from common.logging import get_logger

if TYPE_CHECKING:
    from pyspark.sql import DataFrame

logger = get_logger(__name__)


def to_silver(df: DataFrame, *, drop_nulls_in: list[str] | None = None) -> DataFrame:
    """Transform a bronze DataFrame into the silver layer."""
    df = df.dropDuplicates()

    if drop_nulls_in:
        for col_name in drop_nulls_in:
            if col_name in df.columns:
                df = df.where(df[col_name].isNotNull())

    from pyspark.sql import functions as F
    from pyspark.sql.types import StringType

    for col_field in df.schema.fields:
        if isinstance(col_field.dataType, StringType):
            df = df.withColumn(col_field.name, F.trim(F.col(col_field.name)))

    return df
```

Funksjonen tar imot en `DataFrame` og returnerer en ny — den leser ikke fra og
skriver ikke til noen tabell selv. Lesing og skriving håndteres av
orkestreringen (`main.py`), ikke av transformasjonen.

!!! tip "Hold transformasjoner rene og uten sideeffekter"
    En funksjon som både leser, transformerer og skriver er vanskelig å teste,
    fordi den krever en levende Spark-sesjon med ekte tabeller. En funksjon som
    kun tar en `DataFrame` inn og gir en `DataFrame` ut kan testes med
    syntetiske data på sekunder.

## Lese kilde og skrive resultat i orkestreringen

`main.py` er limet: den henter Spark-sesjonen, leser kildetabellen, kaller
transformasjonsfunksjonene, og skriver resultatet. Her bestemmes katalog, schema
og tabellnavn — du bør bruke miljøvariabler slik at samme kode kan kjøre mot ulike
miljøer.

```python title="src/csv_pipeline/main.py"
from __future__ import annotations

import os

from common.logging import get_logger
from csv_pipeline.ingest import ingest_csv, write_bronze
from csv_pipeline.transform import to_gold, to_silver

logger = get_logger(__name__)


def main() -> None:
    """Run the full CSV medallion pipeline."""
    from databricks.sdk.runtime import spark  # (1)!

    catalog = os.environ.get("CSV_PIPELINE_CATALOG", "padda_catalog")
    schema = os.environ.get("CSV_PIPELINE_SCHEMA", "csv_example")
    source_path = os.environ.get(
        "CSV_PIPELINE_SOURCE_PATH",
        "/Volumes/padda_catalog/csv_example/landing/sample.csv",
    )

    # Bronze: raw ingest
    bronze_df = ingest_csv(spark, source_path)
    write_bronze(bronze_df, spark, catalog, schema, "csv_bronze")

    # Silver: clean
    silver_df = to_silver(bronze_df)
    silver_df.write.format("delta").mode("overwrite").saveAsTable(
        f"{catalog}.{schema}.csv_silver"
    )

    # Gold: business-ready
    gold_df = to_gold(silver_df)
    gold_df.write.format("delta").mode("overwrite").saveAsTable(
        f"{catalog}.{schema}.csv_gold"
    )
```

1. `from databricks.sdk.runtime import spark` gir deg den aktive Spark-sesjonen
   både i en jobb og i en notebook. Importér den inne i funksjonen, ikke på
   toppnivå, så koden kan importeres i tester uten en levende sesjon.

Hvis kilden din allerede er en tabell (ikke en fil), bytt ut `ingest_csv` med en
vanlig tabell-lesing:

```python
source_df = spark.read.table(f"{catalog}.{schema}.csv_bronze")
silver_df = to_silver(source_df)
```

!!! note "Tabellnavn er tredelte"
    Unity Catalog-tabeller refereres alltid som
    `{catalog}.{schema}.{table}`. I `csv_pipeline` ligger alle tre lagene i
    samme schema med tabellnavn `csv_bronze`, `csv_silver` og `csv_gold`. Et
    vanlig alternativ er ett schema per lag (`bronze_default`, `silver_default`,
    `gold_default`) — se [Din første
    datapipeline](../../kom-i-gang/din-forste-datapipeline.md) for det mønsteret.

## Gjenbruke felles transformasjoner

Transformasjoner som flere pipelines trenger — for eksempel å gjøre kolonnenavn
Delta-kompatible eller å legge på sporingsmetadata — bor i det delte biblioteket
`padda_pipelines`, ikke kopiert inn i hver pipeline. `ingest_csv` bruker dem:

```python title="src/csv_pipeline/ingest.py (utdrag)"
from pipelines.transforms import add_ingest_metadata, sanitize_column_names

df = sanitize_column_names(df)  # (1)!
df = add_ingest_metadata(df, source_path=source_path)  # (2)!
```

1. Bytter ut tegn som ikke er gyldige i Delta-kolonnenavn (mellomrom, komma,
   parenteser ...) med understrek, og løser duplikate navn.
2. Legger på `_ingest_timestamp`, `_ingest_source_path` og `_ingest_run_id` for
   sporbarhet.

!!! tip "Sjekk biblioteket før du skriver noe nytt"
    Hvis en transformasjon er generell nok til at andre team kan trenge den,
    hører den hjemme i `libs/padda_pipelines`. Da slipper alle å vedlikeholde
    hver sin kopi.

## Teste transformasjonen

Fordi transformasjonene er rene funksjoner, kan du teste dem med små,
håndskrevne `DataFrame`-er. `csv_pipeline` har testene i
`tests/test_transform.py`:

```python title="tests/test_transform.py (utdrag)"
from csv_pipeline.transform import to_silver


class TestToSilver:
    def test_drops_duplicates(self, spark):
        df = spark.createDataFrame([(1, "a"), (1, "a"), (2, "b")], ["id", "name"])
        result = to_silver(df)
        assert result.count() == 2

    def test_trims_string_whitespace(self, spark):
        df = spark.createDataFrame([("  hello  ",)], ["name"])
        result = to_silver(df)
        assert result.collect()[0]["name"] == "hello"
```

`spark`-fiksturen kommer fra `conftest.py` og kobler seg til en Spark-sesjon via
[Databricks Connect](https://docs.databricks.com/dev-tools/databricks-connect/index.html).
Kjør testene med:

```bash
uv run pytest examples/csv_pipeline
```

!!! info "PySpark 4 krever Databricks Connect lokalt"
    PySpark 4 oppretter ikke en lokal sesjon på egen hånd — testene bruker
    Databricks Connect mot et workspace. Hvis Connect ikke er konfigurert,
    hopper fiksturen over Spark-testene i stedet for å feile.

## Pakke transformasjonen som en jobb

For å kjøre transformasjonen på en tidsplan eller fra CI, pakker du den som en
Databricks-jobb med en bundle. `csv_pipeline` kjører `main` som en
`python_wheel_task`:

```yaml title="resources/csv_pipeline_job.yml (utdrag)"
resources:
  jobs:
    csv_pipeline_job:
      name: "CSV Pipeline - Golden Path Example"
      tasks:
        - task_key: run_csv_pipeline
          job_cluster_key: pipeline_cluster
          python_wheel_task:
            package_name: csv_pipeline
            entry_point: main
          libraries:
            - whl: ../dist/*.whl
```

Deploy og kjør den med:

```bash
databricks bundle deploy --target dev
databricks bundle run csv_pipeline_job --target dev
```

Se [Ta i bruk bundles](ta-i-bruk-bundles.md) for full gjennomgang av targets,
variabler, wheels og deploy.

!!! info "Når bør transformasjonen være en DLT-pipeline i stedet?"
    For strømmende innlasting med innebygde kvalitetssjekker passer ofte en
    [Lakeflow Declarative Pipeline](bronze-til-silver.md#alternativ-deklarative-expectations-med-dlt)
    bedre enn en wheel-jobb. Begge deler deployes som bundle-ressurser.

## Bekreft resultatet

Sjekk at jobben kjørte og at tabellen ble skrevet:

```bash
databricks bundle run csv_pipeline_job --target dev
```

Inspiser så resultatet i en notebook eller med SQL i workspacet:

```sql
SELECT * FROM padda_catalog.csv_example.csv_silver LIMIT 20;
SELECT count(*) FROM padda_catalog.csv_example.csv_silver;
```

Du skal se:

- En `csv_silver`-tabell med rensede rader
- Færre rader enn i `csv_bronze` hvis kilden hadde duplikater eller `NULL`-er

## Feilsøking

??? failure "`ModuleNotFoundError: No module named 'common'` ved kjøring"
    Wheelet med de delte bibliotekene er ikke tilgjengelig for clusteret, eller
    `dependencies`/`libraries` peker på feil sti.

    Prøv dette:

    - Bygg på nytt med `uv build --wheel` og sjekk at `dist/*.whl` finnes
    - Bekreft at `libraries` (eller `environments`) i jobben peker på riktig
      whl-sti

??? failure "Testen feiler med at Spark-sesjon ikke kan opprettes"
    PySpark 4 trenger Databricks Connect for å lage en sesjon lokalt.

    Prøv dette:

    - Konfigurer Databricks Connect mot et workspace, eller
    - Kjør testene i CI der Connect er satt opp

## Relatert innhold

- [Bronze til silver](bronze-til-silver.md) — rensing, deduplisering og standardisering
- [Silver til gold](silver-til-gold.md) — aggregering og forretningslogikk
- [Ta i bruk bundles](ta-i-bruk-bundles.md) — pakke og deploye jobben
- [Klassifisering av datakvalitet
  (konsept)](../../om-plattformen/konsepter/klassifisering-datakvalitet.md) —
  hvorfor bronze, silver og gold
- [Verktøy for datakvalitet](../../referanse/datakvalitet.md) — Constraints,
  Expectations og DQX
