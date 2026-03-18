---
title: [Lag noe konkret med ...]
description: [Beskrivelse for søkemotorer — hva leseren ender opp med.]
diataxis: tutorial
# icon: lucide/construction  # Fjern kommentar for stub-sider
---

!!! info "Mal: Tutorial — læringsrettet, guidet opplevelse"
    Bruk denne malen for sider der leseren lærer noe nytt gjennom en
    veiledet øvelse (f.eks. sider under "Kom i gang").

    **Prinsipper:**

    - Læreren (du) bærer ansvaret for leserens suksess
    - Én sti, ingen valg — leseren følger, ikke beslutter
    - Hvert trinn gir et synlig resultat
    - Minimer forklaring — lenk til den i stedet
    - Bruk "vi"-form gjennomgående

    **Formatering:**

    - IKKE bruk content tabs — tutorials skal ha én sti, ingen valg
    - Bruk admonitions sparsomt; de bryter flyten i en tutorial
    - Kodeannoteringer (`# (1)!`) kan forklare komplekse kommandoer
      uten å bryte steg-for-steg-flyten

    **Admonition-typer i Zensical:**
    `note` · `abstract` · `info` · `tip` · `success` ·
    `question` · `warning` · `failure` · `danger` · `bug` ·
    `example` · `quote` —
    alle støtter `!!!` (fast), `???` (sammenleggbar) og `???+` (åpen).

    Slett denne boksen når du begynner å skrive.


# [Lag noe konkret med ...]

[I denne opplæringen skal vi sette opp / lage / kjøre ... Beskriv sluttresultatet, ikke hva leseren "vil lære".]


## Dette skal vi lage [OBLIGATORISK]

[Gi nok kontekst til at leseren kan se for seg sluttresultatet.]

Når du er ferdig, har du:

- [konkret resultat 1]
- [konkret resultat 2]
- [konkret resultat 3]


## Før du begynner [OBLIGATORISK]

Du trenger:

- [programvare eller verktøy]
- [tilgang eller legitimasjon]
- [eventuelle filer eller verdier]

Starttilstand (ta med om leseren trenger et bestemt miljø før start):

- [hvordan miljøet bør se ut før start]


## Trinn 1: [Første konkrete handling] [OBLIGATORISK]

Minst to trinn. Hvert trinn må gi et synlig resultat.

[Beskriv nøyaktig hva leseren skal gjøre.]

```bash
databricks bundle init --template default-python \  # (1)!
  --project-dir mitt-prosjekt  # (2)!
```

1. Bruker den innebygde Python-malen.
2. Oppretter prosjektet i mappen `mitt-prosjekt`.

Forventet resultat:

- [hva som skal skje]
- [hva leseren skal se]

!!! tip "Legg merke til"
    [Ting leseren bør observere — tegn på at alt er riktig. Bruk denne
    admonition-typen for å skille observasjoner visuelt fra handlingstrinn.
    Ta med når det er noe leseren bør se, men kanskje ikke legger merke
    til selv.]


## Trinn 2: [Neste handling]

[Beskriv neste handling kort og konkret.]

```bash
[kommando]
```

Forventet resultat:

```text
[eksempel på utdata]
```

Om leseren kan gjenta dette trinnet med andre verdier for å forsterke mønsteret, si det eksplisitt. Repetisjon bygger trygghet.


## Trinn 3: [Bygg videre]

[Legg til så mange trinn som trengs. Fortsett langs én tydelig sti uten alternativer.]

```yaml
[eksempel på konfigurasjon]
```

Forventet resultat:

- [hva som skal være på plass nå]


## Kontroller resultatet [OBLIGATORISK]

Sjekk at alt virker:

```bash
[kontrollkommando]
```

Du skal se:

- [kontrollpunkt 1]
- [kontrollpunkt 2]


## Hvis noe ikke stemmer [FRIVILLIG]

Ta med når det finnes kjente fallgruver. Læreren bærer ansvaret — om vanlige feil finnes, bør du adressere dem her. Sammenleggbare admonitions holder den glade stien ren.

??? failure "Feilmelding: `[feilmelding]`"
    [Den mest sannsynlige årsaken.]

    Prøv dette:

    - [en enkel retting]
    - [en enkel kontroll]

??? failure "[En annen vanlig feil]"
    [Kort forklaring.]

    Prøv dette:

    - [retting]


## Du har nå [OBLIGATORISK]

[Beskriv kort hva leseren faktisk har oppnådd.]

Du har nå:

- [resultat 1]
- [resultat 2]


## Neste steg [FRIVILLIG]

Ta med når det finnes naturlige neste sider i dokumentasjonen. Bruk interne lenker.

- [Lenke til relevant how-to guide]
- [Lenke til relevant referanseside]
- [Lenke til relevant forklaring]
