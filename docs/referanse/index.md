---
title: Referanse
description: Oppslagsverk for plattformens regler, komponenter og konfigurasjon, med navn, felt og verdier slik de faktisk er.
diataxis: reference
---

# Referanse

Referansesidene beskriver plattformen slik den er: hvilke regler som gjelder, hva
Dataspeilet har satt opp for teamet ditt, og hvilke felt og verdier du kan bruke i din
egen konfigurasjon. Sidene er laget for å slå opp i, ikke for å leses fra start til
slutt.

Leter du etter *hvordan* du gjør noe, finner du det i [Guider](../guider/index.md).
Lurer du på *hvorfor* plattformen er som den er, står det i
[Om plattformen](../om-plattformen/index.md).

## Regler og konvensjoner

Det som gjelder uansett hva du bygger.

- **[Brukervilkår og ansvar](brukervilkaar.md)** — hva teamet tar ansvar for når det
  bruker plattformen: dataeierskap, risikovurdering, tilgangsstyring og backup
- **[Roller og rettigheter](roller-og-rettigheter.md)** — gruppene i hvert workspace, hva
  hver rolle kan gjøre, og service principals for GitHub Actions
- **[Navnekonvensjoner](navnekonvensjoner.md)** — navnemønstre for kataloger, skjemaer,
  tabeller, bundles, jobber, sendere og identiteter
- **[Anbefalte språk](anbefalte-spraak.md)** — Python og SQL, og hva som gjelder for
  andre språk
- **[Definisjon av dataprodukt](dataprodukt.md)** — forslag (RFC) til felles definisjon,
  minstekrav og metadatamodell for dataprodukter i Digitaliseringsetaten

## Plattformens komponenter

Det Dataspeilet setter opp og forvalter for hvert workspace.

- **[Landing zone](landing-zone.md)** — bøttestruktur, sendere, autentisering,
  oppbevaring og filformater for innkommende data
- **[SQL Warehouse](sql-warehouse.md)** — de tre warehousene i hvert workspace,
  tilkoblingsdetaljer, tilganger og begrensninger
- **[Backup](backup.md)** — hva som tas backup av, hvordan, og hva som ikke dekkes

## Teamets kode og konfigurasjon

Det teamet selv definerer i egen kode.

- **[Declarative Automation Bundles](databricks-bundles.md)** — mappestruktur, feltene
  i `databricks.yml`, targets og modes, compute og CLI-kommandoer
- **[Varsling og alarmer](varsling-og-alarmer.md)** — varslingskanaler, varsler på
  jobber og pipelines, SQL-alarmer og feltene som styrer dem
- **[Datakvalitet](datakvalitet.md)** — constraints, expectations og sjekkfunksjonene i
  DQX
- **[Lagring og ytelse](lagring-og-ytelse.md)** — Liquid Clustering, partisjonering,
  Z-ordering og vedlikehold av Delta-tabeller
- **[SAM-deploy](sam-deploy.md)** — mappestruktur, navnekrav, permission boundary,
  hemmeligheter og CI/CD for serverless-funksjoner

## Fant du ikke det du leter etter?

Det som er generelt for Databricks, og ikke særegent for plattformen, står i Databricks
sin egen dokumentasjon. Et utvalg er samlet i
[Databricks-opplæring](../hjelp/databricks-opplaering.md#utvalgt-dokumentasjon). Får du
ikke svar der heller, se [Hjelp](../hjelp/index.md).
