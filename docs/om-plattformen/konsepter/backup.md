---
title: Backup
description: Hvordan backup fungerer.
diataxis: explanation
---

# Backup

Backup is done to S3 in a separate AWS account to guard against account deletion.

## Databricks-tabeller

## Databricks-metadata

```python
from datetime import datetime
spark.catalog.setCurrentCatalog("system")
spark.catalog.setCurrentDatabase("information_schema")
workspace = spark.conf.get("spark.databricks.workspaceUrl").split(".")[0]
dir_path = "s3://backup_place/" + workspace + "/" + datetime.now().strftime("%Y-%m-%d")
for table in spark.catalog.listTables():
    file_name = table.name.replace(".", "_")
    file_path = dir_path + "/" + file_name
    spark.read.table(table.name).write.json(dir_path, mode="overwrite")
```

## Landing Zone
