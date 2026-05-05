---
title: Backup
description: Hvordan backup fungerer.
diataxis: explanation
---

# Backup

Backup gjøres slik:

- Backup av landing zone-bøtte
- Versjonskontroll av kode-artifakter
- Backup av tabeller i system.information_schema for å få med seg permissions etc. (dumpes til ny S3-bøtte som i sin tur tas backup av)

Backup følger default KM-oppførsel. Avvikende behov tas når den tid kommer. GDPR er ikke relevant for backup.

## Databricks-metadata

Denne tar backup av alt som ligger i system.information_schema. Det dekker tabeller, views, permissions, etc.

```python
import sys
spark.catalog.setCurrentCatalog("system")
spark.catalog.setCurrentDatabase("information_schema")
bucket = sys.argv[1]
for table in spark.catalog.listTables():
    file_name = table.name.replace(".", "_") + ".json"
    df = spark.read.table(table.name)
    rdd = df.toJSON().collect()
    jsonlist = [row.value for row in rdd]
    json_string = "\n".join(jsonlist)
    dbutils.fs.put(f"s3://{bucket}/{file_name}", json_string, True)
```

Dette lander i en dedikert S3-bøtte per workspace. Denne bøtten tas så backup av. Backupen speiler slik clickops-config, og kan brukes til å gjenopprette f.eks. tillatelser. Se [eksempel-script](../../../scripts/restore/generate_privilege_sql.py).

## Landing Zone

Golden Path har [boilerplate for backup](https://github.com/oslokommune/golden-path-boilerplate/tree/main/boilerplate/terraform/backup).

## Restore

Det er viktig å merke seg at default rolle for restore ikke har rettigheter til å jobbe med S3. Til det trenger man policien `AWSBackupServiceRolePolicyForS3Restore`. I forbindelse med at backup tas opprettes det en rolle som har denne. Navn skal være på formen `aws-backup-[dato][masse tall]`. Bruk denne i stedet.

## Databricks-tabeller (ikke i drift)

Ettersom all data per nå kommer gjennom landing zone så er det redundant å ta backup av tabeller. Skulle dette være et behov som kommer så ser jeg for meg noe sånt som dette:

- Vi har en tabell med liste over alle tabeller, hvor ofte de skal backes opp, og når de sist ble backet opp
- Vi leser ut alle brukerstyrte tabeller og oppdaterer tabellen over om nødvendig
- Vi gjør backup i henhold til tabell

[Utestet kode](../../../scripts/drafts/backup_tables.py)
