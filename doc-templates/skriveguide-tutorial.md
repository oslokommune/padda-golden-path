# Mal: Tutorial

En tutorial er en **læringsopplevelse**. Leseren følger med steg for steg og
ender opp med å ha bygget eller oppnådd noe konkret. Målet er ikke å forklare
— det er å la leseren *gjøre* og *se resultater*.

## Prinsipper

- **Vis destinasjonen.** Leseren skal vite hva de vil ha bygget før de
  begynner.
- **Bruk «vi» gjennomgående.** «I denne opplæringen skal vi ...» — du guider
  noen, du gir ikke ordrer.
- **Hvert trinn gir et synlig resultat.** Hvis leseren ikke kan bekrefte at
  et trinn fungerte, mister de tilliten.
- **Ikke forklar.** En tutorial er ikke stedet for dype forklaringer. Lenk til
  forklaringssider i stedet.
- **Ikke tilby valg.** Følg én sti. Alternativer hører hjemme i how-to-guider.
- **Gi et konkret utgangspunkt.** For en dataplattform betyr dette ofte
  testdata. Uten det stopper leseren på trinn én.

## Faste elementer

Disse skal alltid med, uavhengig av tema:

### Frontmatter

```yaml
---
title: Bygg en datapipeline fra landing zone til Power BI
description: >-
  Steg-for-steg-tutorial som tar deg fra opplasting av en fil til
  landing zone til visning i en Power BI-rapport.
diataxis: tutorial
tags:
  - kom-i-gang
---
```

### Åpning

Et kort avsnitt: hva vi skal bygge, og hva leseren har når de er ferdige.
Beskriv **resultatet**, ikke hva de vil «lære».

### «Før du begynner»-seksjon

Hva leseren trenger før de starter. Vær konkret — nøyaktige verktøy,
versjoner, tilgang. For Padda-tutorials er dette typisk:

- Tilgang til Databricks workspace
- Utviklingsmiljø satt opp (lenk til how-to)
- Testdata eller instruksjoner for å generere dem

### «Kontroller resultatet»-seksjon

En konkret måte å verifisere at tutorialen fungerte fra ende til ende.

### «Neste steg»-seksjon

Lenker til relevante guider, referansesider eller forklaringer — med
beskrivende norsk lenketekst, ikke Diataxis-etiketter.

## Eksempelstrukturer

### A: Lineær pipeline-tutorial (f.eks. «Din første datapipeline»)

```markdown
# Vi bygger en datapipeline fra landing zone til Power BI

I denne opplæringen bygger vi en komplett datapipeline. Vi starter med å
laste opp en CSV-fil, transformerer den gjennom medallion-arkitekturen,
og kobler til Power BI.

## Dette skal vi bygge

Når vi er ferdige, har vi:

- En CSV-fil i landing zone
- En bronze-tabell med rådata
- En gold-tabell klar for rapportering
- En Power BI-rapport som viser dataene

## Før du begynner

Du trenger:

- Tilgang til Databricks-workspace ([slik får du tilgang](../...))
- Utviklingsmiljø satt opp ([sett opp miljøet](../...))
- Testfilen `salgsdata.csv` ([last ned her](../...))

## Trinn 1: Vi laster opp en fil til landing zone

Vi starter med å laste opp testfilen ...

    [konkret instruksjon med kodeeksempel]

Vi skal nå se at filen ligger i bøtta:

    [verifikasjonskommando og forventet resultat]

Legg merke til at filen havnet under `green/` — det er fordi ...

## Trinn 2: Vi leser filen inn i en bronze-tabell

Nå skal vi lese filen ...

    [kode]

Vi kan sjekke at tabellen ble opprettet:

    [verifikasjon]

## Trinn 3: Vi transformerer til gold

    ...

## Kontroller resultatet

Sjekk at hele kjeden fungerer:

    [ende-til-ende-verifikasjon]

## Neste steg

- [Sette opp Auto Loader](../...) for å automatisere innlastingen
- [Om medallion-arkitekturen](../...) for å forstå bronze/silver/gold
```

### B: Verktøy-tutorial (f.eks. «VS Code og Databricks»)

```markdown
# Vi kobler VS Code til Databricks

I denne opplæringen setter vi opp VS Code for lokal utvikling mot
Databricks. Vi installerer utvidelsen, kobler til et workspace, og
kjører en notebook lokalt.

## Dette skal vi sette opp

Når vi er ferdige, kan du:

- Redigere notebooks lokalt i VS Code
- Kjøre kode mot Databricks fra editoren
- Synkronisere endringer tilbake

## Før du begynner

    ...

## Trinn 1: Vi installerer Databricks-utvidelsen

    ...

## Trinn 2: Vi kobler til workspace

    ...

## Trinn 3: Vi kjører en notebook

    ...

## Kontroller resultatet

    ...

## Neste steg

    ...
```

Hovedforskjellen fra struktur A: færre trinn, fokusert på å *sette opp et
verktøy* i stedet for å *bygge et dataprodukt*. Verifikasjonen er «det
fungerer», ikke «data fløt gjennom».
