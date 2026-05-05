---
title: Backup
description: Hvordan backup fungerer.
diataxis: reference
---

# Hvordan backup fungerer

## Oversikt

Det må være mulig å hente seg inn ved tap av data. For å sikre dette gjør vi følgende:

- Backup av landing zone-bøtte
- Versjonskontroll av kode-artifakter
- Backup av metadata-tabeller i system.information_schema

## Trinnvis forløp av backup

1. For hver workspace dumpes metadataen i system.information_schema til en S3-bøtte
2. Metadata-bøtte og landing zone-bøtte tas backup av med AWS Backup

## Databricks-metadata

Et script som lever inne i hvert workspace tar backup av alt som ligger i system.information_schema gjennom en Databricks-jobb. Det dekker tabeller, views, permissions, etc.

Dette lander i en dedikert S3-bøtte per workspace. Denne bøtten tas så backup av på samme måte som landing zone (se under).

## Landing Zone

Denne S3-bøtten tas backup av ved hjelp av [standard boilerplate for backup](https://github.com/oslokommune/golden-path-boilerplate/tree/main/boilerplate/terraform/backup). Denne bruker AWS Backup.

[Utestet kode](../../../scripts/drafts/backup_tables.py)

## Begrensninger

Det tas ikke backup av ting som notebooks og tabeller. Skulle det være et behov for dette i fremtiden finnes det artikler om [hvordan man gjør eksport](https://docs.databricks.com/aws/en/security/privacy/export-workspace-data).

## Relatert innhold

- [Katastrofe-gjenoppretting](../guider/overvaake-og-drifte/katastrofe-gjenoppretting.md)
