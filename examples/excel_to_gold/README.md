# Excel to Gold - Databricks Asset Bundle

En enkel DAB som leser en Excel-fil og lagrer den som en Delta-tabell i gull-laget.

## Forutsetninger
- Excel-fil tilgjengelig i et lesbart sted for Databricks (f.eks. `dbfs:/FileStore/...` eller en Volume/ABFSS-sti).
- Databricks CLI/bundles er satt opp.

## Variabler (bundle.yml)
- `catalog` (default: `padda_catalog_2727440053493594`)
- `schema` (default: `wheels`)
- `table_name` (default: `excel_gold`)
- `excel_input_path` (default: `dbfs:/Volumes/dig_felles_dev_green/bronze_default/excel_test/exceltest-fil.xlsx`)
- `job_cluster_node_type` (default: `m5.large`)

> Bruk en **Unity Catalog Volume**-sti (`dbfs:/Volumes/<catalog>/<schema>/<volume>/...` eller `/Volumes/...`). Unngå DBFS root/monteringer i UC-workspaces.

## Hvordan laste opp en Excel-fil til Unity Catalog (Volume) og bruke den her
1. Opprett (eller gjenbruk) et volume i UC:
   - I Databricks UI: Catalog → Velg katalog/schema → Volumes → Create volume (f.eks. `excel`).
2. Last opp Excel-filen til volumet. Eksempel med CLI:
   ```bash
   databricks fs cp \
     --profile <profile> \
     ./min_fil.xlsx \
     dbfs:/Volumes/<catalog>/<schema>/excel/min_fil.xlsx
   ```
3. Sett `excel_input_path` til filstien du lastet opp:
   ```bash
   databricks bundle run excel_to_gold_job \
     -v excel_input_path=dbfs:/Volumes/<catalog>/<schema>/excel/min_fil.xlsx \
     -v catalog=<catalog> \
     -v schema=<schema> \
     -v table_name=<ønsket_tabellnavn>
   ```
4. Jobben leser Excel, skriver Delta-tabellen `${catalog}.${schema}.${table_name}`, og viser resultatet.

## Kjøring
```bash
cd examples/excel_to_gold
databricks bundle deploy
databricks bundle run excel_to_gold_job \
  -v excel_input_path=dbfs:/Volumes/padda_catalog_2727440053493594/wheels/deps/myfile.xlsx \
  -v catalog=padda_catalog_2727440053493594 \
  -v schema=wheels \
  -v table_name=excel_gold
```

Jobben kjører notebooken `notebooks/01_excel_to_gold.py`, leser Excel-filen med `pandas`/`openpyxl`, skriver en Delta-tabell til `${catalog}.${schema}.${table_name}`, og viser resultatet.

## Tilpasning
- Overstyr variablene via `-v` når du kjører.
- Legg på egen skjema-validering eller datavask i notebooken om nødvendig.
