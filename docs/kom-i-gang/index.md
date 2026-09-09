---
title: Kom i gang
description: Læringsløp for å komme i gang med dataplattformen, fra tilgang til en kjørende datapipeline i teamets workspace.
diataxis: tutorial
---

# Kom i gang

Dette læringsløpet tar deg fra null til en kjørende datapipeline i ditt teams
Databricks-workspace. Når du er gjennom, har du:

- tilgang til plattformen med kommunebrukeren din
- verktøyene installert og Databricks CLI innlogget i workspacet
- en pipeline som leser filer fra et volum og bygger bronze- og silver-tabeller i Unity
  Catalog

## Hvem løpet er for

Løpet er skrevet for utviklere og data engineers som skal bygge dataprodukter på
plattformen, og som er vant til kommandolinja, Git og SQL. Du trenger ikke kjenne
Databricks fra før. Lurer du på om plattformen passer for teamet ditt, se [Målgrupper og
forutsetninger](../om-plattformen/overordnet/maalgrupper.md) og [Velg riktig
dataplattform](../om-plattformen/overordnet/velg-riktig-plattform.md).

## Stegene

Ta stegene i rekkefølge. Hvert steg bygger på det forrige:

1. [Slik får du tilgang](slik-faar-du-tilgang.md): meld inn teamet via Slack og logg inn.
2. [Sett opp utviklingsmiljøet](dev-setup.md): installer uv og Databricks CLI, og logg inn
   fra kommandolinja.
3. [Last opp ditt første datasett](last-opp-ditt-forste-datasett.md): lag en testdatafil
   og last den opp til et volum i Unity Catalog.
4. [Bygg din første datapipeline](din-forste-datapipeline.md): skriv en bundle med en
   pipeline som leser fila inn i bronze- og silver-tabeller.

## Hvem gjør hva

Dataspeilet setter opp det teamet trenger for å komme i gang. Resten bygger teamet selv:

| Dataspeilet                                | Teamet                                       |
|--------------------------------------------|----------------------------------------------|
| Workspace, kataloger og skjemaer           | Pipelines, tabeller og dataprodukter         |
| Landing zone og sendere for kildesystemene | Koden som laster inn og bearbeider data      |
| Tilgang for teamets medlemmer              | Klassifisering av dataene og tilgang til dem |

Hvordan delene henger sammen, står i [Arkitektur](../om-plattformen/konsepter/arkitektur.md).

## Neste steg

Start med [Slik får du tilgang](slik-faar-du-tilgang.md).
