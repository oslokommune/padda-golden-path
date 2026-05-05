---
title: Backup
description: Beskrivelse av backup-løsningen for landing zone og Databricks-metadata.
diataxis: reference
---

# Backup

Backup-løsningen sikrer at data og metadata kan gjenopprettes ved tap. Den dekker landing zone-bøtten og Databricks-metadata per workspace.

## Oversikt

- **Gjelder for:** Alle Databricks-workspaces og tilhørende S3-bøtter
- **Mekanisme:** AWS Backup
- **Komponenter som backes opp:** Landing zone-bøtte, Databricks-metadata-bøtte per workspace
- **Komponenter som ikke backes opp:** Notebooks, tabeller (Delta-data)
- **Avhengigheter:** [Standard boilerplate for backup](https://github.com/oslokommune/golden-path-boilerplate/tree/main/boilerplate/terraform/backup)

## Backup-komponenter

| Komponent           | Hva som backes opp                                                           | Mekanisme                    | Destinasjon                                                |
| ------------------- | ---------------------------------------------------------------------------- | ---------------------------- | ---------------------------------------------------------- |
| Landing zone        | S3-bøtte med rådata                                                          | AWS Backup                   | AWS Backup vault                                           |
| Databricks-metadata | Innhold fra `system.information_schema` (tabeller, views, permissions, m.m.) | Databricks-jobb + AWS Backup | Dedikert S3-bøtte per workspace, deretter AWS Backup vault |

## Databricks-metadata

Et script som kjører som en Databricks-jobb inne i hvert workspace eksporterer alt innhold fra `system.information_schema`. Eksporten lagres i en dedikert S3-bøtte per workspace. Denne bøtten tas deretter backup av med AWS Backup på samme måte som landing zone.

## Landing zone

Landing zone-bøtten tas backup av med AWS Backup via [standard boilerplate for backup](https://github.com/oslokommune/golden-path-boilerplate/tree/main/boilerplate/terraform/backup).

## Begrensninger

- Notebooks og Delta-tabeller (selve datainnholdet) inngår ikke i backup-løsningen.
- Backup dekker kun det som er eksplisitt listet i [Backup-komponenter](#backup-komponenter).

## Relatert innhold

- [Katastrofe-gjenoppretting](../guider/overvaake-og-drifte/katastrofe-gjenoppretting.md)
