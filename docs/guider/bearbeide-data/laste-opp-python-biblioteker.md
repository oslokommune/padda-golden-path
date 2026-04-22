---
title: Laste opp Python-biblioteker
description: Hvordan laste opp Python wheel-filer til en Unity Catalog Volume for bruk uten internett.
diataxis: how-to
---

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

!!! info "ARM vs. x86_64"
    Databricks-klustre forventer vanligvis Linux `x86_64`-wheels, mens mange utviklere jobber på Mac med ARM64. Dette er uproblematisk for universelle wheels som `py3-none-any`, men pakker med "native" kode må matches mot riktig plattform og Python-versjon.

    Hvis du trenger en plattformspesifikk wheel, last den ned eksplisitt for Linux `x86_64` i stedet for a bruke det maskinen din føreslår:

    ```bash
    pip download \
      --only-binary=:all: \
      --platform manylinux2014_x86_64 \
      --implementation cp \
      --python-version 313 \
      <pakke>==<versjon> \
      -d wheels/
    ```

    Bytt ut `313` med Python-versjonen som matcher Databricks-runtimen din. En `macosx_arm64`-wheel vil ikke kunne installeres pa klusteret.

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

## 4) Bruk wheel i notebooks/kode
- I `examples/excel_ingest/notebooks/01_ingest_excel.py` (bundle-navn "Ingest Excel") installeres wheelene lokalt på driveren fra Volume. Sett variablene `openpyxl_whl_path` og `et_xmlfile_whl_path` til Volume-stiene (f.eks. `dbfs:/Volumes/<catalog>/<schema>/wheels/deps/openpyxl-3.1.5-py2.py3-none-any.whl`).
- Notebooken gjør deretter:
  ```python
  local_whls = [
      to_local_volume_path(et_xmlfile_whl_path),
      to_local_volume_path(openpyxl_whl_path),
  ]
  extra_lib_dir = tempfile.mkdtemp(prefix="openpyxl_whl_")
  for whl in local_whls:
      subprocess.check_call(
          [
              sys.executable,
              "-m",
              "pip",
              "install",
              "--no-deps",
              "--target",
              extra_lib_dir,
              whl,
          ],
      )
  if extra_lib_dir not in sys.path:
      sys.path.insert(0, extra_lib_dir)
  importlib.invalidate_caches()
  ```
  Dette gjør wheels tilgjengelige for pandas/openpyxl i samme runtime.

## Tips
- Hold en egen `deps`-mappe per prosjekt/schema for å slippe navnekollisjoner.
- Versjoner filer tydelig (f.eks. `openpyxl-3.1.5-py2.py3-none-any.whl`).
- Kluster som skal installere fra volume må defineres med: `data_security_mode`: `SINGLE_USER` eller `USER_ISOLATION`.
