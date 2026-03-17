---
title: [Lag noe konkret med ...]
description: [Norsk beskrivelse for søkemotorer — hva leseren ender opp med.]
diataxis: tutorial
# icon: lucide/construction  # Fjern kommentar for stub-sider
---

<!--
  MAL: TUTORIAL — læringsrettet, guidet opplevelse

  Bruk denne malen for sider under "Kom i gang", eller andre steder
  der leseren lærer noe nytt gjennom en veiledet øvelse.

  Eksempler fra vår dokumentasjon:
    - Din første datapipeline
    - Sett opp utviklingsmiljøet
    - VS Code og Databricks
    - Fra test til produksjon
    - Slik får du tilgang
    - Testdata

  Viktige prinsipper:
    - Læreren (du) bærer ansvaret for leserens suksess
    - Én sti, ingen valg — leseren følger, ikke beslutter
    - Hvert trinn gir et synlig resultat
    - Minimer forklaring — lenk til den i stedet
    - Bruk "vi"-form gjennomgående

  Tips om formatering:
    - IKKE bruk content tabs — tutorials skal ha én sti, ingen valg
    - Bruk admonitions sparsomt; de bryter flyten i en tutorial
    - Kodeannoteringer (# (1)!) kan forklare komplekse kommandoer
      uten å bryte steg-for-steg-flyten
-->


# [Lag noe konkret med ...]

<!-- OBLIGATORISK -->
<!-- Én eller to setninger om hva leseren vil ha bygget eller satt opp
     når de er ferdige. Beskriv sluttresultatet, ikke hva de "vil lære". -->

[I denne opplæringen skal vi sette opp / lage / kjøre ... Beskriv sluttresultatet.]


## Dette skal vi lage

<!-- OBLIGATORISK -->

[Gi nok kontekst til at leseren kan se for seg sluttresultatet.]

Når du er ferdig, har du:

- [konkret resultat 1]
- [konkret resultat 2]
- [konkret resultat 3]


## Før du begynner

<!-- OBLIGATORISK -->

Du trenger:

- [programvare eller verktøy]
- [tilgang eller legitimasjon]
- [eventuelle filer eller verdier]

<!-- VALGFRI: Starttilstand — ta med når leseren trenger et bestemt
     miljø før start (f.eks. et klonet repo, en kjørende klynge). -->

Starttilstand:

- [hvordan miljøet bør se ut før start]


## Trinn 1: [Første konkrete handling]

<!-- OBLIGATORISK: Minst to trinn. Hvert trinn må gi et synlig resultat. -->

[Beskriv nøyaktig hva leseren skal gjøre.]

<!-- Kodeannoteringer er nyttige i tutorials for å forklare hva delene
     av en kommando gjør, uten å avbryte flyten med et avsnitt. -->

```bash
databricks bundle init --template default-python \  # (1)!
  --project-dir mitt-prosjekt  # (2)!
```

1. Bruker den innebygde Python-malen.
2. Oppretter prosjektet i mappen `mitt-prosjekt`.

Forventet resultat:

- [hva som skal skje]
- [hva leseren skal se]

<!-- VALGFRI: "Legg merke til" — ta med når det er noe leseren bør
     observere, men kanskje ikke ser av seg selv. Refleksjon styrker
     læring. Bruk en tip-admonition for å skille observasjonen visuelt
     fra handlingstrinnene. -->

!!! tip "Legg merke til"
    [Ting leseren bør observere — tegn på at alt er riktig.]


## Trinn 2: [Neste handling]

[Beskriv neste handling kort og konkret.]

```bash
[kommando]
```

Forventet resultat:

```text
[eksempel på utdata]
```

<!-- VALGFRI: Repetisjon — om leseren kan gjenta dette trinnet med
     andre verdier for å forsterke mønsteret, si det eksplisitt.
     Repetisjon bygger trygghet og dypere forståelse. -->


## Trinn 3: [Bygg videre]

<!-- Legg til så mange trinn som trengs. Hold fast ved
     én-sti-prinsippet: ingen alternativer, ingen "du kan også"-avsporing. -->

[Fortsett langs én tydelig sti uten alternativer.]

```yaml
[eksempel på konfigurasjon]
```

Forventet resultat:

- [hva som skal være på plass nå]


## Kontroller resultatet

<!-- OBLIGATORISK -->

Sjekk at alt virker:

```bash
[kontrollkommando]
```

Du skal se:

- [kontrollpunkt 1]
- [kontrollpunkt 2]


## Hvis noe ikke stemmer

<!-- VALGFRI: Ta med når det finnes kjente fallgruver. Læreren bærer
     ansvaret — om vanlige feil finnes, bør du adressere dem her.

     Bruk sammenleggbare admonitions for feilsøking. Da holder du
     den glade stien ren, men tilbyr hjelp for de som trenger det. -->

??? failure "Feilmelding: `[feilmelding]`"
    [Den mest sannsynlige årsaken.]

    Prøv dette:

    - [en enkel retting]
    - [en enkel kontroll]

??? failure "[En annen vanlig feil]"
    [Kort forklaring.]

    Prøv dette:

    - [retting]


## Du har nå

<!-- OBLIGATORISK: Oppsummer hva leseren faktisk har oppnådd. -->

[Beskriv kort hva leseren faktisk har oppnådd.]

Du har nå:

- [resultat 1]
- [resultat 2]


## Neste steg

<!-- VALGFRI: Ta med når det finnes naturlige neste sider i dokumentasjonen.
     Bruk interne lenker, ikke generiske råd. -->

- [Lenke til relevant how-to guide]
- [Lenke til relevant referanseside]
- [Lenke til relevant forklaring under "Om plattformen"]
