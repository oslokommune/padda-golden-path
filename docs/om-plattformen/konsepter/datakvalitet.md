---
title: Datakvalitet
description: Hva datakvalitet betyr, hvorfor det er vanskelig å oppnå, og hvilke avveininger som gjelder når man forsøker å håndtere det automatisk.
diataxis: explanation
---

# Datakvalitet

Kvaliteten på data handler om hvor formålstjenlig dataen er — ikke bare om den er teknisk korrekt, men om den gir et riktig bilde av virkeligheten. En analyse er bare så god som dataen den bygger på, og feil i dataen forplanter seg ofte stille gjennom hele kjeden frem til et dashboard eller en rapport. Denne siden forklarer hva datakvalitet innebærer, hvorfor det er et vedvarende problem, og hvilke avveininger som finnes når man forsøker å håndtere det.

## Hva utgjør god datakvalitet

Det finnes [flere definisjoner av datakvalitet](https://en.wikipedia.org/wiki/Data_quality#Dimensions_of_data_quality), men de peker gjerne mot de samme grunnleggende egenskapene. [Databricks' definisjon](https://www.databricks.com/blog/what-is-data-quality) er et godt utgangspunkt: data har høy kvalitet når den er nøyaktig, fullstendig, oppdatert, konsekvent, i riktig format og fri for duplikater.

Det er altså ikke nok at data ikke er uriktig, den må heller ikke være misvisende. Data kan være nøyaktig men ufullstendig, eller fullstendig men inkonsekvent på tvers av datasett. Bruk av synonymer i tekstfelt er et eksempel: Ingen enkeltrad er teknisk feil, men samlet sett gir dataen et misvisende bilde, for eksempel når man grupperer basert på tekstfeltet. Dupliserte rader er et annet — ingen rad er teknisk feil, men duplikater vil nesten uunngåelig føre til feil i analyser i det en analytiker bruker `COUNT` eller lignende.

## Hvorfor datakvalitet er vanskelig

Datakvalitet kan ikke sikres med teknologi alene. God datakvalitet starter med gode kilder og riktig bruk av dem — noe som krever menneskelig innsikt, god kommunikasjon mellom dataeiere og databrukere, og dokumentasjon som er god nok til at folk forstår hva de jobber med.

Det er også et bevegelig mål. Kildeformater endres, forretningsregler oppdateres, og nye integrasjoner introduserer uforutsette problemer. En datapipeline som produserte riktig data i går, gjør ikke nødvendigvis det i dag — uten at noe teknisk har endret seg i selve pipelinen. Datakvalitet krever derfor løpende oppmerksomhet, ikke bare et engangstiltak.

## Automatisering — muligheter og avveininger

Selv om automatisering ikke kan _sikre_ datakvalitet, kan den flagge avvik tidlig, nekte ugyldig data å komme inn i systemet, og varsle om endringer i kildeformat — noe som er avgjørende for å vite når menneskelig oppmerksomhet er nødvendig.

Databricks selv tilbyr forskjellige verktøy for å hjelpe med datakvalitet. I tillegg finnes det forskjellige rammeverk som kan brukes. På Databricks er DQX et naturlig valg fordi det er laget spesifikt for Databricks-miljøet. Andre rammeverk opererer gjerne på dataframes i stedet for på tabeller, og krever derfor litt mer boilerplate. Se lenkene under for mer praktisk informasjon om tilgjengelige verktøy.

## Relatert innhold

- [Verktøy for å sikre datakvalitet i Databricks](../../referanse/datakvalitet.md)
- [Hvordan installere og bruke DQX](../../guider/overvaake-og-drifte/bruke-dqx.md)
- [Klassifisering av datakvalitet](./klassifisering-datakvalitet.md)
