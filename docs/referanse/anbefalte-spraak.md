---
title: Anbefalte språk
description: Hvilke programmeringsspråk plattformen støtter og anbefaler.
diataxis: reference
---

# Anbefalte språk

**Python** og **SQL** er de anbefalte språkene på plattformen. Dette følger [Databricks'
anbefaling](https://docs.databricks.com/aws/en/languages/overview#recommendations) for nye
dataprosjekter. Guidene og eksemplene på plattformen bruker disse to språkene.

| Språk      | Egner seg for                                                                                                                |
|------------|------------------------------------------------------------------------------------------------------------------------------|
| **Python** | Datapipelines og transformasjoner med PySpark, testbar og modulær kode, avansert databehandling med økosystemets biblioteker |
| **SQL**    | Spørringer og manipulering av relasjonelle datasett, transformasjoner, analyse via SQL Warehouse                             |

Språkene kan kombineres: SQL kan kjøres fra Python med `spark.sql`, og begge kan brukes om hverandre
i notebooks og pipelines.

## Andre språk

Databricks støtter også Scala og R, men med begrensninger, og [anbefaler dem ikke for nye
prosjekter](https://docs.databricks.com/aws/en/languages/overview#recommendations). Plattformen har
ikke støtte eller eksempler for andre språk enn Python og SQL.
