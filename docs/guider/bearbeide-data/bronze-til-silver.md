---
title: Bronze til silver
description: Hvordan rense, deduplisere og standardisere data fra bronze- til silver-laget.
diataxis: how-to
---

# Bronze til silver

Denne guiden viser hvordan du transformerer en bronze-tabell til silver — det vil
si hvordan du renser, dedupliserer og standardiserer rådata til en konsistent og
pålitelig versjon. Vi bruker `to_silver`-funksjonen fra referanseeksempelet
[`examples/csv_pipeline`](https://github.com/oslokommune/padda-golden-path/tree/main/examples/csv_pipeline).

Silver-laget skal være en sannferdig, ryddig versjon av dataen — uavhengig av hva
den senere skal brukes til. For bakgrunn om hva hvert lag representerer, se
[Klassifisering av datakvalitet
(konsept)](../../om-plattformen/konsepter/klassifisering-datakvalitet.md#silver-vasket-og-standardisert).

## Forutsetninger

- En bronze-tabell å lese fra (se [Sette opp Auto
  Loader](../hente-inn-data/auto-loader.md) for innlasting til bronze)
- Du har lest [Skrive transformasjoner](skrive-transformasjoner.md) — denne
  guiden bygger på mønsteret derfra (rene transformasjonsfunksjoner kalt fra
  `main.py`)

## Hva silver-laget skal gjøre

Silver er der du gjør dataene konsistente. Typiske transformasjoner, fra
[konseptsiden](../../om-plattformen/konsepter/klassifisering-datakvalitet.md#silver-vasket-og-standardisert):

- Kolonnenavn standardiseres (`snake_case`)
- Datatyper settes riktig (strenger blir datoer, heltall osv.)
- Duplikater fjernes
- Ugyldige rader filtreres bort eller flagges
- Expectations sjekker at verdier er innenfor forventede rammer

Du trenger ikke alle på én gang. Start med det dataene faktisk krever.

## Lese bronze-tabellen

Les kilden inn som en `DataFrame` i `main.py`:

```python
source_df = spark.read.table(f"{catalog}.{schema}.csv_bronze")
```

## Deduplisere, fjerne nuller og trimme

`to_silver` gjør tre standardiserende grep: fjerner duplikate rader, fjerner
eventuelt rader med `NULL` i utvalgte kolonner, og trimmer mellomrom fra alle
strengkolonner.

```python title="src/csv_pipeline/transform.py"
def to_silver(df: DataFrame, *, drop_nulls_in: list[str] | None = None) -> DataFrame:
    """Transform a bronze DataFrame into the silver layer."""
    df = df.dropDuplicates()  # (1)!

    if drop_nulls_in:  # (2)!
        for col_name in drop_nulls_in:
            if col_name in df.columns:
                df = df.where(df[col_name].isNotNull())

    from pyspark.sql import functions as F
    from pyspark.sql.types import StringType

    for col_field in df.schema.fields:  # (3)!
        if isinstance(col_field.dataType, StringType):
            df = df.withColumn(col_field.name, F.trim(F.col(col_field.name)))

    return df
```

1. Fjerner rader som er fullstendig like. Bronze beholder duplikater bevisst;
   silver fjerner dem.
2. Valgfritt: dropp rader der en nøkkelkolonne mangler verdi. Kolonner som ikke
   finnes ignoreres, så funksjonen er trygg å kalle med en fast liste.
3. Trimmer ledende/etterfølgende mellomrom fra hver strengkolonne — en svært
   vanlig kilde til «usynlige» duplikater og mislykkede joins senere.

Kall den fra orkestreringen og skriv resultatet:

```python
silver_df = to_silver(source_df, drop_nulls_in=["id"])
silver_df.write.format("delta").mode("overwrite").saveAsTable(
    f"{catalog}.{schema}.csv_silver"
)
```

## Standardisere kolonnenavn

Kolonnenavn fra kilden er ofte ikke gyldige som Delta-kolonner (mellomrom,
parenteser, komma). I `csv_pipeline` gjøres dette allerede ved innlasting med
`sanitize_column_names` fra `padda_pipelines`, slik at bronze-tabellen har rene
navn:

```python
from pipelines.transforms import sanitize_column_names

df = sanitize_column_names(df)
```

Funksjonen erstatter ugyldige tegn med understrek, kollapser gjentatte understrek
og løser duplikate navn med numerisk suffiks. Hvis bronze-tabellen din ennå har
rå kildenavn, kjør den som første steg i `to_silver`.

!!! tip "Standardiser til `snake_case`"
    Konsekvente, små kolonnenavn gjør silver forutsigbar for alle som bygger gold
    oppå. `sanitize_column_names` gjør navnene gyldige; å gjøre dem til
    `snake_case` er et lite ekstra steg du kan legge til der team-konvensjonen
    krever det.

## Sette riktige datatyper

Bronze lagrer ofte alt som `STRING` for at typefeil ikke skal stoppe
innlastingen. I silver caster du til riktige typer:

```python
from pyspark.sql import functions as F

silver_df = (
    silver_df
    .withColumn("amount", F.col("amount").cast("decimal(10,2)"))
    .withColumn("event_date", F.to_date("event_date", "yyyy-MM-dd"))
)
```

!!! warning "Cast som feiler gir `NULL`, ikke en feilmelding"
    Spark setter verdien til `NULL` når en cast ikke går opp (for eksempel en
    dato i feil format). Sjekk antallet `NULL`-er etter casting, eller bruk en
    expectation (under) for å fange det.

## Legge på datakvalitetssjekker

Silver er det riktige stedet å håndheve at verdier er innenfor forventede rammer.
Det finnes to hovedtilnærminger på plattformen.

=== "DQX"

    For gjenbrukbare, deklarative regler med innebygd karantene-håndtering
    bruker plattformen
    [DQX](../overvaake-og-drifte/bruke-dqx.md). `apply_checks_and_split` deler
    inn-dataene i gyldige og ugyldige rader:

    ```python
    valid_df, invalid_df, _ = dq_engine.apply_checks_and_split(silver_df, checks)
    ```

    Se [Bruke DQX](../overvaake-og-drifte/bruke-dqx.md) for oppsett av regler.

=== "Imperativt (PySpark/SQL)"

    Filtrer eller flagg rader direkte i transformasjonen. Enkelt og fullt
    testbart:

    ```python
    valid = silver_df.where(F.col("amount") > 0)
    ```

    Du kan også beholde de ugyldige radene i en egen tabell for sporbarhet i
    stedet for å slette dem.


### Alternativ: deklarative expectations med DLT

Hvis innlastingen din er en strøm, kan du la en [Lakeflow Declarative
Pipeline](../../om-plattformen/konsepter/databricks-bundles.md) håndtere både
ingest og kvalitet. Bundle-malen viser mønsteret med `@dp.expect_all_or_drop`:

```python
from pyspark import pipelines as dp

expectations: dict[str, str] = {
    "valid_trip_distance": "trip_distance > 0",
    "valid_fare_amount": "fare_amount > 0",
}


@dp.table(name=f"bronze_{table}", table_properties={"quality": "bronze"})
@dp.expect_all_or_drop(expectations)
def set_expectations() -> DataFrame:
    return spark.readStream.table(f"raw_{table}")
```

Rader som bryter en expectation droppes (`_or_drop`). Andre håndhevingsmodus
(`WARN`, `FAIL UPDATE`) er beskrevet i [Verktøy for
datakvalitet](../../referanse/datakvalitet.md).

## Håndtere schema-evolusjon

Når kilden får nye kolonner, vil du som regel at de skal følge med inn i bronze
uten å bryte pipelinen. Dette håndteres ved innlasting med Auto Loader
(`schemaEvolutionMode`) — se [Sette opp Auto
Loader](../hente-inn-data/auto-loader.md) for `addNewColumns` (tillat) versus
`failOnNewColumns` (streng). Velg "streng" modus når en uventet kolonne skal stoppe
pipelinen i stedet for å gå ubemerket gjennom til silver.

## Skrive silver-tabellen

```python
silver_df.write.format("delta").mode("overwrite").saveAsTable(
    f"{catalog}.{schema}.csv_silver"
)
```

## Bekreft resultatet

Sjekk at silver-tabellen er renere enn bronze:

```sql
SELECT count(*) AS bronze_rows FROM padda_catalog.csv_example.csv_bronze;
SELECT count(*) AS silver_rows FROM padda_catalog.csv_example.csv_silver;
```

Du skal se:

- Færre eller like mange rader i silver enn i bronze (duplikater/nuller fjernet)
- Riktige datatyper på kolonnene (`DESCRIBE padda_catalog.csv_example.csv_silver`)
- Ingen ledende/etterfølgende mellomrom i strengkolonner

## Feilsøking

??? failure "Silver har like mange rader som bronze, men du forventet færre"
    `dropDuplicates()` fjerner kun rader som er helt like. Hvis radene skiller
    seg på en metadatakolonne (for eksempel `_ingest_timestamp`), regnes de ikke
    som duplikater.

    Prøv dette:

    - Dedupliser på forretningsnøklene:
      `df.dropDuplicates(["id", "event_date"])`

??? failure "En kolonne ble plutselig full av `NULL` etter casting"
    Casting til feil type gir `NULL` uten feilmelding (for eksempel feil
    datoformat).

    Prøv dette:

    - Sjekk kildeformatet og bruk riktig mønster i `to_date`/`to_timestamp`
    - Tell `NULL`-er før og etter castingen for å se hvor mange rader som feilet

## Relatert innhold

- [Silver til gold](silver-til-gold.md) — neste steg: aggregering og forretningslogikk
- [Skrive transformasjoner](skrive-transformasjoner.md) — mønsteret for å skrive og teste transformasjoner
- [Sette opp Auto Loader](../hente-inn-data/auto-loader.md) — innlasting og schema-evolusjon til bronze
- [Bruke DQX](../overvaake-og-drifte/bruke-dqx.md) — deklarative datakvalitetsregler
- [Verktøy for datakvalitet](../../referanse/datakvalitet.md) — Constraints, Expectations og DQX
- [Klassifisering av datakvalitet
  (konsept)](../../om-plattformen/konsepter/klassifisering-datakvalitet.md) — hvorfor bronze, silver og gold
