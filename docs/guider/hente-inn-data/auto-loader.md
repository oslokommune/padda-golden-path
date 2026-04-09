---
title: Sette opp Auto Loader
description: Hvordan konfigurere Auto Loader for inkrementell filinnlasting fra landing zone.
diataxis: how-to
---

# Sette opp Auto Loader

For hvordan man kan sette opp autoloader, se [autoloader-eksemplene her](https://github.com/oslokommune/padda-databrikker/tree/main/bundles). Disse tar for seg litt forskjellige måter å inkrementelt lese inn rader fra linjeskift-separerte JSON-filer på S3.

Dette er et stort tema, og eksemplene dekker bare en liten del av funksjonaliteten som er tilgjengelig. Se [Databricks sin dokumentasjon](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/) for mer informasjon.

## Ytelse

### Regnekraft

Declarative Pipelines kjører på serverless som standard, men det er også mulig å bruke dedikerte beregningsressurser. Hvis du bruker dedikerte beregningsressurser, kan du ofte spare penger ved å bruke et cluster med en mindre driver-instanstype enn worker-instanstype. Dataflyt fra én tabell til en annen er gjerne worker-tung og driver-lett. Når det gjelder valg av instanstype, avhenger det av spørringene dine:

- Enkle (ingen aggregeringer eller joins, eller joins der kun én tabell er stor): Bruk compute-optimaliserte instanser
- Komplekse: Bruk få (ideelt sett én) stor worker-instans med mye minne og lagring

Du vil som regel befinne deg nærmere den enkle enden av dette spekteret.

### Lesing av data

Hvis antallet inndatafiler blir tilstrekkelig stort, kan det være verdt å vurdere å bruke [filvarslinger](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/file-notification-mode). I skrivende stund tillater dessverre ikke infrastrukturkonfigurasjonen vår dette, men det kan endres ved behov.

### Lagring

Se [Lagring og ytelse](../../referanse/lagring-og-ytelse.md)
