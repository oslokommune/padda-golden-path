---
title: Sette opp Auto Loader
description: Hvordan konfigurere Auto Loader for inkrementell filinnlasting fra landing zone.
diataxis: how-to
icon: lucide/construction
---

# Sette opp Auto Loader

Denne guiden er ikke skrevet ennå.

Claude foreslår at denne siden bør dekke:

- Konfigurere Auto Loader for inkrementell innlasting fra landing zone
- Schema-lokasjon og checkpoint
- Streaming vs. trigger-once
- Vanlige filformater og opsjoner

## Ytelse

### Regnekraft

Declarative Pipelines runs on serverless by default, but does allow you to use dedicated compute instead. If you were to use dedicated compute, You can often save some money by using a cluster with a smaller driver instance type than worker instance type. Piping data from one table to another tends to be worker-heavy and driver-light. When it comes to instance type selection, it depends on your queries:

- Simple (No aggregates or joins, or joins where only one table is big): Use compute-optimized instances
- Complex: Use few (ideally 1) big worker instance with lots of memory and storage

You will generally find yourself on the simple end of this spectrum.

### Lesing av data

Hvis antallet inndatafiler blir tilstrekkelig stort, kan det være verdt å vurdere å bruke [filvarslinger](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/file-notification-mode). I skrivende stund tillater dessverre ikke infrastrukturkonfigurasjonen vår dette, men det kan endres ved behov.
