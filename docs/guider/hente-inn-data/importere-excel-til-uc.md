---
title: Importere Excel til Unity Catalog
description: Hvordan laste opp en Excel-fil til en Unity Catalog Volume og skrive den som en Delta-tabell.
diataxis: how-to
---

# Importere Excel til Unity Catalog

Denne guiden viser hvordan du laster opp en Excel-fil til en Unity Catalog Volume og deretter skriver den som en Delta-tabell (som i `examples/excel_ingest`, bundle-navn "Ingest Excel").

## Forutsetninger
- Du har en katalog og et schema du kan skrive til (f.eks. `dig_felles_dev_green.bronze_default`).
- Databricks CLI/bundles er satt opp [start].

## 1) Opprett (eller bruk) en Volume
- I GUI: `Catalog` → velg katalog og schema → `Volumes` → `Create volume` (f.eks. navn `excel_test`).
- Volum-sti blir da `dbfs:/Volumes/<catalog>/<schema>/excel_test/`. (f.eks.: `/Volumes/dig_felles_dev_green/bronze_default/excel_test`)

## 2) Last opp Excel-filen til volumet

### Med CLI
```bash
databricks fs cp \
  --profile <profile> \
  ./min_fil.xlsx \
  dbfs:/Volumes/<catalog>/<schema>/excel_test/min_fil.xlsx
```


## 3) Kjør bundle-eksempelet (Ingest Excel)
I repoet ligger et DAB-eksempel som leser Excel og skriver en Delta-tabell:
```bash
cd examples/excel_ingest
databricks bundle deploy
databricks bundle run ingest_excel_job \
  -v excel_input_path=dbfs:/Volumes/<catalog>/<schema>/excel_test/min_fil.xlsx \
  -v catalog=<catalog> \
  -v schema=<schema> \
  -v table_name=<ønsket_tabellnavn>
```
Jobben leser Excel med pandas/openpyxl, skriver til `${catalog}.${schema}.${table_name}`, og viser resultatet.

## 4) Verifiser data
```sql
SELECT * FROM <catalog>.<schema>.<table_name> LIMIT 10;
```
