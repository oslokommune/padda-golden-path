---
title: Silver til gold
description: Hvordan aggregere og legge på forretningslogikk fra silver- til gold-laget.
diataxis: how-to
---

# Silver til gold

Denne guiden viser hvordan du transformerer silver-data til gold — det vil si
hvordan du kobler sammen kilder, aggregerer og legger på forretningslogikk for å
lage datasett som er klare for analyse og rapportering. Vi bruker
`to_gold`-funksjonen fra referanseeksempelet
[`examples/csv_pipeline`](https://github.com/oslokommune/padda-golden-path/tree/main/examples/csv_pipeline).

Gold-tabeller og silver-tabeller er det som utgjør [dataprodukter](../../om-plattformen/konsepter/dataprodukter.md).
De skal være dokumenterte, pålitelige og forståelige for sluttbrukere — uten at
de trenger å kjenne transformasjonene bak. For bakgrunn, se [Klassifisering av
datakvalitet
(konsept)](../../om-plattformen/konsepter/klassifisering-datakvalitet.md#gold-forretningsklare-data).

## Forutsetninger

- En silver-tabell å lese fra (se [Bronze til silver](bronze-til-silver.md))
- Du har lest [Skrive transformasjoner](skrive-transformasjoner.md) — denne
  guiden bygger på mønsteret derifra (rene transformasjonsfunksjoner kalt fra
  `main.py`)

## Hva gold-laget skal gjøre

Mens silver gjør dataene konsistente uavhengig av bruk, er gold tilpasset
konkrete bruksområder. Typiske transformasjoner, fra
[konseptsiden](../../om-plattformen/konsepter/klassifisering-datakvalitet.md#gold-forretningsklare-data):

- Tabeller fra flere silver-kilder kobles sammen
- Aggregeringer beregnes (summer, gjennomsnitt, antall)
- Forretningslogikk anvendes (klassifiseringer, utledede kolonner)
- Data struktureres for rapportering og BI-verktøy

## Lese silver-tabellen

```python
silver_df = spark.read.table(f"{catalog}.{schema}.csv_silver")
```

## Velge forretningskolonner og fjerne metadata

Det enkleste gold-steget velger ut kolonnene konsumentene faktisk trenger, og
fjerner interne sporingskolonner. `to_gold` gjør nettopp dette:

```python title="src/csv_pipeline/transform.py"
def to_gold(df: DataFrame, *, select_columns: list[str] | None = None) -> DataFrame:
    """Transform a silver DataFrame into the gold layer."""
    if select_columns:  # (1)!
        missing = [c for c in select_columns if c not in df.columns]
        if missing:
            raise ValueError(
                f"Columns not found in DataFrame: {missing}. "
                f"Available: {df.columns}"
            )
        df = df.select(*select_columns)
    else:  # (2)!
        non_meta = [c for c in df.columns if not c.startswith("_ingest_")]
        df = df.select(*non_meta)

    return df
```

1. Hvis du oppgir `select_columns`, velges kun disse — og funksjonen feiler
   høylytt hvis en av dem ikke finnes, i stedet for å produsere en tabell med
   manglende kolonner.
2. Hvis du ikke oppgir noe, droppes alle interne `_ingest_*`-metadatakolonner, og
   resten beholdes.

```python
gold_df = to_gold(silver_df, select_columns=["id", "name", "amount"])
```

!!! tip "Skjul interne kolonner fra konsumentene"
    Metadata som `_ingest_run_id` er nyttig for sporing i bronze og silver, men
    forvirrer sluttbrukere i gold. Å fjerne dem her holder dataproduktet rent.

## Aggregere

De fleste gold-tabeller aggregerer silver-data ned til det nivået rapporten
trenger:

```python
from pyspark.sql import functions as F

gold_df = (
    silver_df
    .groupBy("category")
    .agg(
        F.sum("amount").alias("total_amount"),
        F.countDistinct("id").alias("num_items"),
    )
)
```

!!! tip "La aggregeringsnivået følge spørsmålet"
    Gold skal svare på et konkret forretningsspørsmål. Aggreger til den
    granulariteten rapporten faktisk bruker — ikke finere «for sikkerhets
    skyld», for det gjør tabellen tyngre og mindre tydelig.

## Koble sammen flere silver-kilder

Forretningslogikk krever ofte data fra flere tabeller. Berik silver-data med en
join før aggregering:

```python
orders = spark.read.table(f"{catalog}.{schema}.orders_silver")
customers = spark.read.table(f"{catalog}.{schema}.customers_silver")

gold_df = orders.join(customers, on="customer_id", how="left")
```

!!! warning "Joins kan multiplisere rader"
    Hvis nøkkelen ikke er unik på begge sider, gir en join flere rader enn du
    forventer, og aggregeringer blir feil. Bekreft at join-nøkkelen er unik i
    den siden den skal være det (for eksempel én rad per `customer_id` i
    `customers_silver`).

## Skrive gold-tabellen

```python
gold_df.write.format("delta").mode("overwrite").saveAsTable(
    f"{catalog}.{schema}.csv_gold"
)
```

## Dokumentere datasettet

Et gold-datasett er et dataprodukt, og konsumentene trenger å vite hva det
inneholder. Legg på en tabellkommentar og kolonnekommentarer:

```sql
COMMENT ON TABLE padda_catalog.csv_example.csv_gold IS
  'Aggregated order totals per category. Updated daily.';

ALTER TABLE padda_catalog.csv_example.csv_gold
  ALTER COLUMN total_amount COMMENT 'Sum of order amounts in NOK';
```

Tenk gjennom hva konsumentene må vite: hva representerer hver rad, hvor ofte
oppdateres tabellen, og hvilke kolonner er nøkler. Se [Dataprodukter
(konsept)](../../om-plattformen/konsepter/dataprodukter.md) for hvilke krav som
stilles til et dataprodukt.

## Bekreft resultatet

Sjekk at gold-tabellen ser ut som forventet:

```sql
SELECT * FROM padda_catalog.csv_example.csv_gold LIMIT 20;
DESCRIBE EXTENDED padda_catalog.csv_example.csv_gold;
```

Du skal se:

- Ingen interne `_ingest_*`-kolonner
- Aggregerte verdier på riktig granularitet
- Tabell- og kolonnekommentarer (`DESCRIBE EXTENDED`)

## Feilsøking

??? failure "Aggregerte summer er for høye etter en join"
    Join-nøkkelen er ikke unik på den ene siden, så rader ble multiplisert før
    aggregeringen.

    Prøv dette:

    - Sjekk unikhet: `customers.groupBy("customer_id").count().where("count > 1")`
    - Dedupliser eller aggreger den siden før join

??? failure "`to_gold` feiler med `Columns not found in DataFrame`"
    En kolonne i `select_columns` finnes ikke i silver-tabellen — ofte fordi den
    heter noe annet etter standardisering i silver.

    Prøv dette:

    - Inspiser tilgjengelige navn med `silver_df.columns`
    - Bruk de standardiserte navnene fra silver, ikke de opprinnelige kildenavnene

## Relatert innhold

- [Bronze til silver](bronze-til-silver.md) — forrige steg: rensing og standardisering
- [Skrive transformasjoner](skrive-transformasjoner.md) — mønsteret for å skrive og teste transformasjoner
- [Dataprodukter (konsept)](../../om-plattformen/konsepter/dataprodukter.md) — hva et dataprodukt er og hvilke krav som stilles
- [Ta i bruk bundles](ta-i-bruk-bundles.md) — pakke og deploye pipelinen
- [Klassifisering av datakvalitet
  (konsept)](../../om-plattformen/konsepter/klassifisering-datakvalitet.md) — hvorfor bronze, silver og gold
