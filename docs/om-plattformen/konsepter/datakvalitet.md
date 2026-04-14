---
title: Datakvalitet
description: Hva er datakvalitet.
diataxis: explanation
---

# Datakvalitet

Kvaliteten på data er en måte å snakke om hvor formålstjenlig dataen er. Dette inkluderer ikke bare hvor godt dataen speiler virkeligheten, men også hvor ryddig den er. Bruk av forskjellige synonymer i tekstfelt og dupliserte rader er eksempler på data som ikke strengt tatt er uriktig, men som gjerne resulterer i feil resultat når dataen blir analysert. For at data skal ha høy kvalitet må det altså gi en analytiker et riktig bilde av virkeligheten, og da må dataen ikke bare ikke være uriktig men heller ikke være misvisende. [Det finnes forskjellige definisjoner](https://en.wikipedia.org/wiki/Data_quality#Dimensions_of_data_quality) av hva datakvalitet er, men [Databricks definerer det slik](https://www.databricks.com/blog/what-is-data-quality):

- Dataen skal være konsekvent med andre datasett
- Hver rad skal være nøyaktig og feilfri
- Dataen skal være i riktig og forventet format
- Dataen skal være fullstendig
- Dataen skal være oppdatert
- Det skal ikke forekomme duplikater

## Automatisering

Det finnes ikke noen måte å automatisk sikre datakvalitet. Det er noe som først og fremst krever gode kilder og riktig bruk av disse kildene, men også god kommunikasjon til brukere av dataen gjennom god design og dokumentasjon. Når det er sagt så finnes det måter å flagge dårlig data på, nekte dårlig data å komme inn i systemet, eller flagge endringer i kildeformat. Det er viktig for å kunne vite når menneskelig oppmerksomhet er nødvendig. Databricks selv tilbyr verktøy for dette. I tillegg kan man bruke rammeverk designet for dette. Rammeverkene som er tilgjengelig er gjerne ikke laget for Databricks, men opererer på dataframe-nivå. Unntaket er DQX, som er lagd av Databricks selv. Se linkene under for mer praktisk info vedrørerende verktøy.

## Relatert innhold

- [Verktøy for å sikre datakvalitet i Databricks](../../referanse/datakvalitet.md)
- [Hvordan bruke DQX til å sikre datakvalitet](../../guider/overvaake-og-drifte/bruke-dqx.md)
