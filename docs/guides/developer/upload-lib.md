# Laste opp Python-pakker (wheel) til en Unity Catalog Volume

Denne guiden viser hvordan du legger en wheel-fil (f.eks. `openpyxl`) på en UC Volume slik at scripts/notebooks kan installere den uten internett.

## Forutsetninger
- Du har tilgang til en Volume under et katalog/schema (f.eks. `dbfs:/Volumes/dig_felles_dev_green/analyst_default/wheels`).
- Databricks CLI

## 1) Hent wheel-filen lokalt
- Last ned ønsket wheel på din maskin (f.eks. `openpyxl-3.1.5-py2.py3-none-any.whl`).
- Med `pip`:
  ```bash
  pip download openpyxl==3.1.5 -d wheels/
  ```

## 2) Opprett en mappe for dependencies i Volume
- I UI: Catalog → velg katalog/schema → Volumes → lag Volume `wheels`.
- Resultatsti: `dbfs:/Volumes/<catalog>/<schema>/wheels`.

## 3) Last opp wheel til Volume

### Med Databricks CLI
```bash
cd wheels
databricks fs cp -r \
  --profile DEFAULT \
  ./ \     
  dbfs:/Volumes/padda_catalog_2727440053493594/wheels/deps/
```

## 4) Bruk wheel i scripts/notebooks
- Referer til wheel-stien i `libraries` eller i kode:
  - Legg til variabel `openpyxl_whl_path` = `dbfs:/Volumes/dig_felles_dev_green/analyst_default/wheels/openpyxl-3.1.5-py2.py3-none-any.whl`
  - Libraries i bundle:
    ```yaml
    libraries:
      - whl: ${var.openpyxl_whl_path}
    ```
- I notebook kan du installere midlertidig:
  ```python
  whl = "dbfs:/Volumes/<catalog>/<schema>/<volume>/openpyxl-3.1.5-py2.py3-none-any.whl"
  spark.sparkcontext.addPyFile(whl)
  ```

## Tips
- Hold en egen `deps`-mappe per prosjekt/schema for å slippe navnekollisjoner.
- Versjoner filer tydelig (f.eks. `openpyxl-3.1.5-py2.py3-none-any.whl`).
- Kluster som skal installere fra volume må defineres med: data_security_mode: SINGLE_USER eller USER_ISOLATION
