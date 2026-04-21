---
title: Backup
description: Hvordan backup fungerer.
diataxis: explanation
---

# Backup

## Databricks-tabeller

## Databricks-metadata

```python
from datetime import datetime
spark.catalog.setCurrentCatalog("system")
spark.catalog.setCurrentDatabase("information_schema")
for table in spark.catalog.listTables():
    file_name = table.name.replace(".", "_")
    dir_path = "s3://backup_place/my_workspace/" + datetime.now().strftime("%Y-%m-%d")
    file_path = dir_path + "/" + file_name
    spark.read.table(table.name).write.json(dir_path, mode="overwrite")
```

## Landing Zone
