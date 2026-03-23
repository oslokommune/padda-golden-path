---
title: Brukervilkår og ansvar
description: Brukervilkår, dataeierskap, risikovurdering og ansvar ved bruk av plattformen.
diataxis: reference
icon: lucide/split
---

# Brukervilkår og ansvar

!!! info "Opprinnelse"
    Denne siden inneholder referansedelen fra `docs/ONBOARDING.md`. Onboarding-prosedyren (slik du bekrefter via PR) ligger nå under [Slik får du tilgang](../kom-i-gang/slik-faar-du-tilgang.md).

## Formål

Padda er Oslo kommunes dataplattform for datainnsamling, prosessering og analyse. Plattformen gjør det mulig for dataproduktteam å jobbe effektivt med data på en sikker og strukturert måte.

## Sjekkliste før bruk av Dataplattformen (Databricks)

**Dataeierskap og samtykke**
Du har ansvar for at dataeier har samtykket til opplasting og er kjent med risikoen ved bruk av plattformen.

**Risikovurdering (ROS)**
Det må gjennomføres en egen risikovurdering for bruk av dine data samt en personvernvurdering dersom det behandles personopplysninger. Risikovurdering av Databricks er beskrevet i [gjeldende ROS](https://oslokommune.sharepoint.com/:b:/r/sites/21b20/Felles-dokumenter/Dataspeilet/ROS%20Data%20engineering%20plattform/ROS-rapport%20Dataengineeringplattform%20med%20Databricks.pdf?csf=1&web=1&e=VxwG4d). Du må ha satt deg inn i dette før plattformen tas i bruk. Vi har utarbeidet mal for gjennomføring av en ROS-prosess som kan benyttes om ønskelig, som ligger [her](https://miro.com/app/board/uXjVGQbi2BY=/). Vi har også utarbeidet en mal for en ROS-rapport som kan benyttes, som ligger [her](https://oslokommune.sharepoint.com/:w:/r/sites/TEAM-DIG-JIPI/Delte%20dokumenter/General/ROS%20Metoder/ROS-NextGen/MAL%20Rosrapport%20Databricks%20dataproduktteam.docx?d=w3ceef0c9ba314bc595e458967e19342d&csf=1&web=1&e=lCahPa).

**Tilgangsstyring**
Du er ansvarlig for å forstå og velge riktig tilgangsnivå for datasettene dine.

**Ingen SLA**
Plattformen er under utvikling, og det foreligger per i dag ingen SLA knyttet til oppetid eller tilgjengelighet.

**Backup og redundans**
Du er selv ansvarlig for å sørge for redundant lagring av dataene.
Dataplattformen tar ikke backup av datasettene i løsningen.

## Kontakt

Har du spørsmål eller trenger hjelp? Ta kontakt via:

- **Slack**: [#dig-dataspeilet](https://oslokommune.slack.com/archives/C01SFNFEXK7)
- **GitHub**: [oslokommune/padda-golden-path](https://github.com/oslokommune/padda-golden-path) — opprett et issue eller ta kontakt via PR
