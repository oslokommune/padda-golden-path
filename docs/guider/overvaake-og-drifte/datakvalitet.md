---
title: Datakvalitet
description: Hvordan automatisere deler av arbeidet med å sikre datakvalitet.
diataxis: how-to
---

# Datakvalitet

## Innebygde mekanismer i Databricks

Databricks har selv en oversikt [her](https://www.databricks.com/discover/pages/data-quality-management)

### Expectations og Constraints

Databricks har

## DQX

### Installering

Først må du lokalt kjøre noe slikt som `pip download --python-version=3.12 --only-binary=:all: databricks-labs-dqx`. Dette laster ned all avhengigheter lokalt. Deretter kan du finne et passende volum å last disse opp til. Når det er gjort, kan du lage en notebook med dette som første celle:

```sh
%sh
pip install --no-index --find-links /Volumes/padda_catalog_2727440053493594/tormod_test/tormod_test databricks_labs_dqx
```
