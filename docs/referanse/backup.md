---
title: Backup
description: Beskrivelse av backup-løsningen for landing zone og Databricks-metadata.
diataxis: reference
---

# Backup

Backup-løsningen dekker landing zone-bøtta og Databricks-metadata for hvert workspace, med
AWS Backup som mekanisme. Notebooks og tabellene i Unity Catalog, altså selve
Delta-dataene, inngår ikke. Ansvaret for redundant lagring av dem ligger hos teamet, se
[Brukervilkår og ansvar](brukervilkaar.md#backup-og-redundans). Løsningen bygger på
[standard boilerplate for
backup](https://github.com/oslokommune/golden-path-boilerplate/tree/main/boilerplate/terraform/backup).

## Backup-komponenter

| Komponent           | Hva som backes opp                                                           | Mekanisme                    | Destinasjon                                                |
| ------------------- | ---------------------------------------------------------------------------- | ---------------------------- | ---------------------------------------------------------- |
| Landing zone        | S3-bøtte med rådata                                                          | AWS Backup                   | AWS Backup vault                                           |
| Databricks-metadata | Innhold fra `system.information_schema` (tabeller, views, permissions, m.m.) | Databricks-jobb + AWS Backup | Dedikert S3-bøtte per workspace, deretter AWS Backup vault |

## Databricks-metadata

Et script som kjører som en Databricks-jobb inne i hvert workspace eksporterer alt innhold fra `system.information_schema`. Eksporten lagres i en dedikert S3-bøtte per workspace. Denne bøtta tas deretter backup av med AWS Backup på samme måte som landing zone.

## Landing zone

Landing zone-bøtta tas backup av med AWS Backup via [standard boilerplate for backup](https://github.com/oslokommune/golden-path-boilerplate/tree/main/boilerplate/terraform/backup).

## Begrensninger

- Notebooks og Delta-tabeller (selve datainnholdet) inngår ikke i backup-løsningen.
- Backup dekker kun det som er eksplisitt listet i [Backup-komponenter](#backup-komponenter).

## Relatert innhold

**Referanser:**

- [Brukervilkår og ansvar](brukervilkaar.md#backup-og-redundans) — teamets ansvar for
  redundant lagring av tabellene
- [Landing zone](landing-zone.md) — bøtta som tas backup av

**Guider:**

- [Gjenopprette etter feil i
  pipelines](../guider/overvaake-og-drifte/gjenopprette-etter-feil.md) — gjenskape
  tabeller fra filene i landing zone

**Ekstern dokumentasjon:**

- [Databricks: Disaster Recovery](https://docs.databricks.com/aws/en/admin/disaster-recovery)
