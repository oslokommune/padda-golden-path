---
title: Kjøre batch-inferens med en registrert modell
description: Hvordan laste en modell fra Unity Catalog via alias, skrive prediksjoner til en Delta-tabell, planlegge jobben og bytte modellversjon uten kodeendring.
diataxis: how-to
---

# Kjøre batch-inferens med en registrert modell

Denne guiden viser hvordan en jobb henter modellen som bærer aliaset
`padda`, skriver prediksjoner til en tabell, og hvordan du bytter versjon
uten å røre koden. Eksempelet fra malen gjør alt dette i tasken `predict`;
guiden viser hva den gjør og hvordan du tilpasser det.

## Før du begynner

Sørg for at du har:

- En registrert modell med aliaset `padda`, for eksempel etter [Trene og
  registrere en modell](trene-og-registrere-modell.md)
- `USE_CATALOG`, `USE_SCHEMA` og `EXECUTE` på modellen, og `SELECT` på
  tabellen du skal skåre
- En feature-tabell med de samme kolonnene som modellen ble trent på

## Trinn 1: Last modellen via alias

Bruk det fulle navnet i Unity Catalog og aliaset, aldri et versjonsnummer.
Slik gjør `predict.py` det i eksempelet:

```python
import mlflow

mlflow.set_registry_uri("databricks-uc")
model_name = f"{catalog}.{schema}.romledighet"
model = mlflow.pyfunc.load_model(f"models:/{model_name}@padda")

client = mlflow.MlflowClient()
version = client.get_model_version_by_alias(model_name, "padda").version
```

`version` brukes bare til å skrive hvilken versjon som laget prediksjonene.
Selve lastingen følger aliaset, så neste kjøring plukker automatisk opp en ny
padda version dersom den er tilgjengelig.

## Trinn 2: Skår radene og skriv prediksjonene

Modellen forventer nøyaktig kolonnene i `FEATURE_COLUMNS`, som `float32`. I
eksempelet er radene som skal skåres de som mangler label:

```python
features = spark.table(f"{catalog}.{schema}.romledighet_features").toPandas()
to_score = features[features["er_booket"].isna()]
probabilities = model.predict(to_score[FEATURE_COLUMNS].astype("float32"))

predictions = to_score[["rom_id", "dato", "time"]].copy()
predictions["sannsynlighet_booket"] = probabilities
predictions["modellversjon"] = int(version)

spark.createDataFrame(predictions).write.mode("overwrite").option(
    "overwriteSchema", "true"
).saveAsTable(f"{catalog}.{schema}.romledighet_prediksjoner")
```

Hvis feature-tabellen er stor, gi poeng med en Spark UDF i stedet for pandas:

```python
predict_udf = mlflow.pyfunc.spark_udf(spark, f"models:/{model_name}@padda", result_type="double")
scored = spark.table(f"{catalog}.{schema}.romledighet_features").withColumn(
    "sannsynlighet_booket", predict_udf(*FEATURE_COLUMNS)
)
```

!!! warning "Overskriv eller legg til?"
    Eksempelet overskriver prediksjonstabellen hver kjøring fordi den bare
    dekker den kommende uken. Skal du beholde historikk, bruk `append` og ta
    med `predikert_tidspunkt` i nøkkelen.

## Trinn 3: Planlegg jobben

Batch-inferens er en vanlig jobb. I malen ligger `predict` i samme jobb som
treningen, med en ukentlig trigger som er satt på pause:

```yaml
trigger:
  pause_status: PAUSED
  periodic:
    interval: 1
    unit: WEEKS
```

Skal prediksjonene oppdateres oftere enn modellen trenes, del jobben i to: én
jobb med `generate_data`, `build_features` og `train`, og én med
`build_features` og `predict`. Begge kan bruke samme `environments`-blokk. I
development-modus er triggere alltid på pause; i prod aktiveres de. Se [Ta i
bruk bundles](../bearbeide-data/ta-i-bruk-bundles.md#sette-root_path-permissions-og-run_as-for-prod) #TODO
for `run_as` i prod.

## Trinn 4: Bytt modellversjon

Du bytter modell ved å flytte aliaset, ikke ved å endre koden. I eksempelet
gjør treningsjobben det selv etter regelen i `registry.py`: en ny versjon blir
`padda` hvis `val_auc` er minst like god som dagens, ellers `utmaner_padda`.

Vil du styre det manuelt, for eksempel etter en gjennomgang av en
`utmaner_padda`:

```bash
databricks model-versions set-alias <katalog>.<skjema>.romledighet padda 2 -p <profil>
```

Neste kjøring av `predict` bruker versjon 2. Ruller du tilbake, peker du
aliaset på den forrige versjonen på samme måte.

## Bekreft resultatet

Kjør en spørring mot prediksjonstabellen, for eksempel i SQL-editoren:

```sql
SELECT COUNT(*) AS rader,
       MIN(tidspunkt) AS fra,
       MAX(tidspunkt) AS til,
       ROUND(AVG(sannsynlighet_booket), 3) AS snitt,
       MAX(modellversjon) AS versjon
FROM <katalog>.<skjema>.romledighet_prediksjoner;
```

Forventet utdata for eksempelet: 1540 rader (20 rom × 7 dager × 11 timer),
et snitt rundt 0,5 og versjonsnummeret aliaset peker på.

## Feilsøking

??? failure "`RESOURCE_DOES_NOT_EXIST` for alias `padda`"
    Ingen versjon bærer aliaset. Treningsjobben har ikke kjørt, eller siste
    versjon ble `utmaner_padda` og en tidligere padda er slettet.

    Løsning:

    - Kjør treningsjobben, eller sett aliaset manuelt med
      `databricks model-versions set-alias`.

??? failure "`MlflowException: Incompatible input types` eller manglende kolonne"
    Feature-tabellen har endret seg siden modellen ble trent. Signaturen
    avviser input som ikke matcher.

    Løsning:

    - Hold `FEATURE_COLUMNS` og SQL-en i `feature_sql` i takt, og tren på nytt
      når kontrakten endres.

??? failure "Jobben feiler på `ModuleNotFoundError: torch`"
    Miljøet mangler PyTorch. `predict` trenger samme miljø som `train`.

    Løsning:

    - Bruk samme `environment_key` som treningstasken, og sjekk at volumet
      har hjulene. Se [Trene og registrere en
      modell](trene-og-registrere-modell.md#trinn-4-last-opp-pytorch-til-volumet).

## Relatert innhold

- [Trene og registrere en modell](trene-og-registrere-modell.md)
- [Publisere en modell som serving-endepunkt](publisere-serving-endepunkt.md)
- [MLflow og modellregister (referanse)](../../referanse/mlflow-og-modellregister.md)
- [Maskinlæring på plattformen](../../om-plattformen/konsepter/maskinlaering.md)
- [Dele data via Unity Catalog](../dele-og-hente-ut/unity-catalog.md)
