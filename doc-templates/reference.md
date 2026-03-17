---
title: [Navn på det som dokumenteres]
description: [Norsk beskrivelse for søkemotorer — hva dette er.]
diataxis: reference
# icon: lucide/construction  # Fjern kommentar for stub-sider
---

<!--
  MAL: REFERANSE — informasjonsrettet, nøytral beskrivelse

  Bruk denne malen for sider under "Referanse", eller andre steder
  der leseren skal slå opp fakta, regler eller spesifikasjoner
  mens de jobber.

  Eksempler fra vår dokumentasjon:
    - Roller og rettigheter
    - Navnekonvensjoner
    - Landing zone
    - SQL Warehouse
    - Databricks Asset Bundles
    - Brukervilkår og ditt ansvar
    - Varsling

  Merk: referansesidene i dette prosjektet dekker et bredt spekter —
  fra tekniske spesifikasjoner (SQL Warehouse, Databricks Asset Bundles)
  til policy og styring (brukervilkår, roller og rettigheter) til
  navnestandarder (navnekonvensjoner) til systembeskrivelser (landing
  zone, varsling). Seksjonene under er en meny; velg det som passer.

  Viktige prinsipper:
    - Nøytralt, saklig, objektivt — beskriv hva noe ER, ikke hva man skal GJØRE
    - Strukturen speiler det som dokumenteres, ikke brukeroppgaver
    - Konsistent formatering innenfor og på tvers av sider
    - Komplett: dokumenter alt, ikke bare vanlige tilfeller
    - Ingen instruksjoner (det er how-to), ingen "hvorfor" (det er forklaring)
    - Korte eksempler for å illustrere, ikke for å lære bort

  Tips om formatering:
    - Bruk tabeller til alt som har faste kolonner (roller, parametere,
      innstillinger, feilkoder)
    - Content tabs fungerer godt for eksempler i flere formater
      (Python vs. SQL, JSON vs. YAML)
    - Bruk warning/deprecated-admonitions for utgåtte funksjoner
      eller destruktiv oppførsel
-->


# [Navn på det som dokumenteres]

<!-- OBLIGATORISK -->
<!-- Én eller to setninger: en nøytral beskrivelse av hva dette er. -->

[Kort, nøytral beskrivelse av hva dette er.]


## Oversikt

<!-- OBLIGATORISK: Gir leseren nøkkelfakta med én gang. Velg feltene
     som passer og fjern resten. -->

- **Type:** [kommando | endepunkt | ressurs | konfigurasjon | regelverk | ...]
- **Gjelder for:** [produkt, modul eller komponent]
- **Tilgjengelig fra:** [versjon, dato eller miljø]
- **Standardoppførsel:** [kort]
- **Avhengigheter:** [kort]


<!--
  == VELG SEKSJONENE SOM PASSER ==

  En side om "Navnekonvensjoner" ville brukt "Regler" og "Eksempler".
  En side om "SQL Warehouse" ville brukt "Konfigurasjon", "Begrensninger"
  og kanskje "Feil og advarsler".
  En side om "Brukervilkår" ville brukt "Regler" og kanskje en tabell.
  En side om "Roller og rettigheter" ville brukt tabeller og "Regler".

  Seksjonene under dekker de vanligste formene for referanseinnhold
  i dette prosjektet. Bruk det du trenger, gi gjerne nye navn,
  og hopp over resten.
-->


## Syntaks / signatur / format

<!-- VALGFRI: Bruk for kommandoer, API-er, konfigurasjonsfiler eller
     annet med en formell struktur. -->

```text
[generell syntaks, signatur eller struktur]
```


## Parametere / felt / alternativer

<!-- VALGFRI: Bruk for kommandoer, API-er eller konfigurasjonsobjekter
     med navngitte parametere. -->

### `[navn]`

- **Type:** [string | integer | boolean | object | ...]
- **Påkrevd:** [ja | nei]
- **Standardverdi:** [verdi]
- **Gyldige verdier:** [liste eller mønster]
- **Beskrivelse:** [nøytral forklaring]


## Roller / tilganger / ansvar

<!-- VALGFRI: Bruk for styrings- og tilgangssider som
     "Roller og rettigheter". Tabeller fungerer godt her. -->

| Rolle | Rettigheter | Ansvar |
|-------|-------------|--------|
| [rolle] | [rettigheter] | [ansvar] |


## Regler og oppførsel

<!-- VALGFRI: Bruk for navnekonvensjoner, policyer eller annet med
     eksplisitte regler. -->

- [regel 1]
- [regel 2]
- [begrensning]
- [særtilfelle]


## Konfigurasjon

<!-- VALGFRI: Bruk for infrastruktur- eller tjenestesider som
     "SQL Warehouse" eller "Landing zone" der det finnes innstillinger
     som kan endres. -->

| Innstilling | Verdi | Beskrivelse |
|-------------|-------|-------------|
| [innstilling] | [verdi] | [beskrivelse] |


## Feil og advarsler

<!-- VALGFRI: Bruk når det som dokumenteres kan gi bestemte
     feilkoder eller advarsler. -->

### `[feilkode eller feilmelding]`

- **Betydning:** [hva den betyr]
- **Når den oppstår:** [situasjon]
- **Merknad:** [viktig presisering]

<!-- Bruk deprecated-admonition for funksjoner som er på vei ut. -->

!!! warning "Utgått"
    [Denne funksjonen er utgått fra versjon X. Bruk Y i stedet.]


## Eksempler

<!-- VALGFRI: Korte, illustrerende eksempler. Ikke en tutorial —
     vis syntaks og forventet resultat, ikke en læringsreise.

     Content tabs er nyttige når du viser samme operasjon i flere
     formater eller språk. -->

=== "Python"

    ```python
    [eksempel]
    ```

=== "SQL"

    ```sql
    [eksempel]
    ```


## Begrensninger

<!-- VALGFRI: Bruk når det finnes kjente begrensninger,
     versjonsavhengigheter eller plattformkrav. -->

- [kjent begrensning]
- [versjonsavhengighet]
- [plattformbegrensning]


## Relaterte elementer

<!-- VALGFRI: Lenker til søster-referansesider — andre kommandoer,
     relaterte konfigurasjonsobjekter osv. -->

- [beslektet referanseside]
- [overordnet eller underordnet element]


## Relatert innhold

<!-- OBLIGATORISK: Lenk alltid til konkrete sider i dokumentasjonen. -->

- [Lenke til relevant tutorial under "Kom i gang"]
- [Lenke til relevant guide under "Guider"]
- [Lenke til relevant forklaring under "Om plattformen"]
