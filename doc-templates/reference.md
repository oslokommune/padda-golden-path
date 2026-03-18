---
title: [Navn på det som dokumenteres]
description: [Beskrivelse for søkemotorer — hva dette er.]
diataxis: reference
# icon: lucide/construction  # Fjern kommentar for stub-sider
---

!!! info "Mal: Referanse — informasjonsrettet, nøytral beskrivelse"
    Bruk denne malen for sider der leseren skal slå opp fakta, regler
    eller spesifikasjoner mens de jobber (f.eks. sider under "Referanse").

    Referansesidene i dette prosjektet dekker et bredt spekter — fra
    tekniske spesifikasjoner til policy og styring til navnestandarder
    og systembeskrivelser.

    **Prinsipper:**

    - Nøytralt, saklig, objektivt — beskriv hva noe ER, ikke hva man skal GJØRE
    - Strukturen speiler det som dokumenteres, ikke brukeroppgaver
    - Konsistent formatering innenfor og på tvers av sider
    - Komplett: dokumenter alt, ikke bare vanlige tilfeller
    - Ingen instruksjoner (det er how-to), ingen "hvorfor" (det er forklaring)
    - Korte eksempler for å illustrere, ikke for å lære bort

    **Formatering:**

    - Bruk tabeller til alt som har faste kolonner (roller, parametere,
      innstillinger, feilkoder)
    - Content tabs fungerer godt for eksempler i flere formater
      (Python vs. SQL, JSON vs. YAML)
    - Bruk `!!! warning "Utgått"` for utgåtte funksjoner

    **Seksjonene under er en meny** — velg de som passer det du
    dokumenterer, gi dem gjerne nye navn, og hopp over resten.

    Slett denne boksen når du begynner å skrive.


# [Navn på det som dokumenteres]

[Kort, nøytral beskrivelse av hva dette er.] [OBLIGATORISK]


## Oversikt [OBLIGATORISK]

Gir leseren nøkkelfakta med én gang. Velg feltene som passer og fjern resten.

- **Type:** [kommando | endepunkt | ressurs | konfigurasjon | regelverk | ...]
- **Gjelder for:** [produkt, modul eller komponent]
- **Tilgjengelig fra:** [versjon, dato eller miljø]
- **Standardoppførsel:** [kort]
- **Avhengigheter:** [kort]


## Syntaks / signatur / format [FRIVILLIG]

Bruk for kommandoer, API-er, konfigurasjonsfiler eller annet med en formell struktur.

```text
[generell syntaks, signatur eller struktur]
```


## Parametere / felt / alternativer [FRIVILLIG]

Bruk for kommandoer, API-er eller konfigurasjonsobjekter med navngitte parametere.

### `[navn]`

- **Type:** [string | integer | boolean | object | ...]
- **Påkrevd:** [ja | nei]
- **Standardverdi:** [verdi]
- **Gyldige verdier:** [liste eller mønster]
- **Beskrivelse:** [nøytral forklaring]


## Roller / tilganger / ansvar [FRIVILLIG]

Bruk for styrings- og tilgangssider. Tabeller fungerer godt her.

| Rolle | Rettigheter | Ansvar |
|-------|-------------|--------|
| [rolle] | [rettigheter] | [ansvar] |


## Regler og oppførsel [FRIVILLIG]

Bruk for navnekonvensjoner, policyer eller annet med eksplisitte regler.

- [regel 1]
- [regel 2]
- [begrensning]
- [særtilfelle]


## Konfigurasjon [FRIVILLIG]

Bruk for infrastruktur- eller tjenestesider der det finnes innstillinger som kan endres.

| Innstilling | Verdi | Beskrivelse |
|-------------|-------|-------------|
| [innstilling] | [verdi] | [beskrivelse] |


## Feil og advarsler [FRIVILLIG]

Bruk når det som dokumenteres kan gi bestemte feilkoder eller advarsler.

### `[feilkode eller feilmelding]`

- **Betydning:** [hva den betyr]
- **Når den oppstår:** [situasjon]
- **Merknad:** [viktig presisering]

!!! warning "Utgått"
    [Bruk for funksjoner som er på vei ut. Angi versjon og alternativ.]


## Eksempler [FRIVILLIG]

Korte, illustrerende eksempler — vis syntaks og forventet resultat, ikke en læringsreise. Content tabs er nyttige for eksempler i flere formater:

=== "Python"

    ```python
    [eksempel]
    ```

=== "SQL"

    ```sql
    [eksempel]
    ```


## Begrensninger [FRIVILLIG]

Bruk når det finnes kjente begrensninger, versjonsavhengigheter eller plattformkrav.

- [kjent begrensning]
- [versjonsavhengighet]
- [plattformbegrensning]


## Relaterte elementer [FRIVILLIG]

Lenker til søster-referansesider — andre kommandoer, relaterte konfigurasjonsobjekter osv.

- [beslektet referanseside]
- [overordnet eller underordnet element]


## Relatert innhold [OBLIGATORISK]

- [Lenke til relevant tutorial]
- [Lenke til relevant guide]
- [Lenke til relevant forklaring]
