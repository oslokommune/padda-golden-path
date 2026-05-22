---
title: Velg riktig dataplattform
description: Oversikt over dataplattformene i Oslo kommune og hvilken som passer ditt behov.
diataxis: explanation
---

# Velg riktig dataplattform

Digitaliseringsetaten tilbyr flere dataplattformer som er tilgjengelige på tvers. Hvilken du bør bruke avhenger av hva du skal gjøre og hvordan du jobber.

## To plattformer — ulike formål

### [Fabric-plattformen](https://oslokommune.sharepoint.com/sites/KOM-6aace/SitePages/Data-Oslo.aspx)

Her finner du mange felles datakilder i kommunen, samlet på Microsoft Fabric. Godt egnet for deg som vil bygge integrasjoner med 365-plattformen, gjøre lavkode eller no code-behandlinger, og bruke Power BI på eksisterende datakilder. Har også kodemuligheter, men er mer sentrert rundt et grafisk grensesnitt for transformasjoner.

Fabric er kommunens motorvei for datadeling og vil løse de fleste utfordringene.

### Databricks-plattformen *Padda*

For deg som skriver kode (SQL, Python) for å hente inn, transformere og tilgjengeliggjøre data. Bygget for utviklere og kodende analytikere. Data kan utveksles med Fabric-plattformen.

Padda er bygget for en kode-først-arbeidsflyt — der alt fra pipelines til deploy styres gjennom Git.

## Padda passer for deg hvis du:

- Bygger datapipelines med SQL og/eller Python
- Trenger versjonering, testing og automatisert deploy av dataflyter
- Foretrekker å styre alt av transformasjoner og kvalitetssikring gjennom kode

## Du trenger sannsynligvis ikke Padda hvis du:

- Primært jobber i Power BI eller Excel
- Har nok med datakildene som allerede er tilgjengelige i Fabric
- Ikke har utviklere eller kodende analytikere i teamet

<!-- Bilde/diagram: enkel visuell som viser de to plattformene og hvordan data flyter mellom dem -->

## Plattformene utfyller hverandre

Plattformene er ikke konkurrenter, selv om de har delvis overlappende funksjonalitet. Dataprodukter som bygges på Padda kan konsumeres fra Fabric og Power BI — plattformene er designet for å fungere sammen.
