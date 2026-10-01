---
title: Importere Excel til Unity Catalog
description: Hvordan laste opp en Excel-fil til et Unity Catalog Volume og skrive den som en Delta-tabell.
diataxis: how-to
---

# Importere Excel til Unity Catalog

Denne guiden viser hvordan du laster opp en Excel-fil til et Unity Catalog Volume og
deretter skriver den som en Delta-tabell. Bundlen
[`bundles/excel_ingest`](https://github.com/oslokommune/padda-databrikker/tree/main/bundles/excel_ingest)
i `padda-databrikker` gjør det samme og brukes som eksempel i trinn 3.

## Forutsetninger
- Du har en katalog og et schema du kan skrive til (f.eks. `eksempelteam_dev_green.bronze_default`).
- Databricks CLI er satt opp (se [Sett opp utviklingsmiljøet](../../kom-i-gang/dev-setup.md)).
- Du vet hvordan du deployer en bundle (se [Ta i bruk bundles](../utvikle-og-deploye/ta-i-bruk-bundles.md)).

## 1) Opprett (eller bruk) et Volume
- I GUI: `Catalog` → velg katalog og schema → `Volumes` → `Create volume` (f.eks. navn `excel_test`).
- Volum-sti blir da `dbfs:/Volumes/<catalog>/<schema>/excel_test/`. (f.eks.: `/Volumes/eksempelteam_dev_green/bronze_default/excel_test`)

## 2) Last opp Excel-filen til volumet

### Med CLI
```bash
databricks fs cp \
  --profile <profile> \
  ./min_fil.xlsx \
  dbfs:/Volumes/<catalog>/<schema>/excel_test/min_fil.xlsx
```


## 3) Kjør bundle-eksempelet

Klon [`padda-databrikker`](https://github.com/oslokommune/padda-databrikker) og kjør bundlen
som leser Excel og skriver en Delta-tabell:

```bash
git clone git@github.com:oslokommune/padda-databrikker.git
cd padda-databrikker/bundles/excel_ingest
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
