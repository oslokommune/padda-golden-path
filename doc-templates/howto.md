---
title: Hvordan [oppnå et bestemt resultat]
description: [Norsk beskrivelse for søkemotorer — hva leseren får til.]
diataxis: how-to
# icon: lucide/construction  # Fjern kommentar for stub-sider
---

<!--
  MAL: HOW-TO — oppgaverettet, målfokusert

  Bruk denne malen for sider under "Guider", eller andre steder
  der leseren allerede vet hva de vil oppnå og trenger praktiske
  anvisninger.

  Eksempler fra vår dokumentasjon:
    - Laste opp til landing zone
    - Sette opp Auto Loader
    - Excel til Unity Catalog
    - Deploy med Databricks Asset Bundles
    - Koble til Power BI
    - Slack-alarmer
    - Secrets
    - Feilsøke med logger
    - Dele data via Unity Catalog

  Viktige prinsipper:
    - Leseren vet allerede hva de vil — hjelp dem raskt i mål
    - Anta kompetanse; ikke lær bort grunnleggende
    - Bare handling — ingen bakgrunn, ingen teori
    - Tillat variasjon: bruk "hvis/når" for forgreninger
    - Lenk videre til tutorials, referanse og forklaring

  Tips om formatering:
    - Content tabs er perfekt for varianter (CLI vs. UI, Python vs. SQL,
      ulike filformater) — bruk dem i stedet for egne underseksjoner
    - Bruk warning-admonition for destruktive eller irreversible steg
    - Kodeannoteringer (# (1)!) kan erstatte lange forklaringer
-->


# Hvordan [oppnå et bestemt resultat]

<!-- OBLIGATORISK -->
<!-- Én eller to setninger: hva denne veiledningen hjelper leseren med,
     og hvordan et vellykket resultat ser ut. -->

[Kort innledning: si hva denne veiledningen hjelper leseren med, og hvordan et vellykket resultat ser ut.]


## Før du begynner

<!-- OBLIGATORISK når det finnes reelle forutsetninger. Kan droppes
     helt om leseren kan starte uten forberedelser. -->

Sørg for at du har:

- [nødvendig tilgang, rettigheter eller legitimasjon]
- [nødvendig programvare, miljø eller versjon]
- [nødvendige inndatafiler, verdier eller avhengigheter]

<!-- VALGFRI: Lenk til forutsetnings-tutorial i stedet for å forklare
     oppsett her. -->

Denne veiledningen forutsetter at du har gjennomført [Sett opp utviklingsmiljøet](../kom-i-gang/dev-setup.md) eller tilsvarende.


## Trinn 1: [Første handling]

<!-- OBLIGATORISK: Minst ett trinn. Trinnene skal være korte og
     handlingsrettede. Ingen "Forventet resultat" etter hvert
     trinn — spar det til verifikasjonen på slutten. -->

[Beskriv handlingen tydelig og direkte.]

```bash
[eksempelkommando]
```

<!-- VALGFRI: Betinget veiledning — ta med når det finnes legitime
     variasjoner. Dette er det som skiller en how-to fra en tutorial.

     Content tabs er ideelle for parallelle fremgangsmåter som oppnår
     samme mål. Bruk dem når leseren velger mellom likeverdige
     alternativer. -->

=== "CLI"

    ```bash
    databricks bundle deploy --target dev
    ```

=== "UI"

    1. Gå til **Workflows** i Databricks-arbeidsområdet.
    2. Klikk **Create Job**.


## Trinn 2: [Neste handling]

[Beskriv neste handling.]

```yaml
[eksempel på konfigurasjon]
```

<!-- VALGFRI: Korte merknader — bare når de direkte hjelper leseren
     å fullføre oppgaven. Lenk ut for dypere forklaringer. -->

!!! note
    [Viktig merknad som hjelper leseren fullføre oppgaven.]
    Se [Arkitektur](../om-plattformen/konsepter/arkitektur.md) for bakgrunn.

<!-- VALGFRI: Bruk warning for steg som er destruktive eller
     irreversible. -->

!!! warning
    [Denne operasjonen kan ikke angres. Sørg for at du har ...]


## Trinn 3: [Fullfør fremgangsmåten]

<!-- Legg til så mange trinn som trengs. -->

[Beskriv den siste handlingen.]

```bash
[kommando for siste steg]
```


## Bekreft resultatet

<!-- OBLIGATORISK -->

Kontroller at oppgaven ble fullført:

```bash
[kontrollkommando]
```

Forventet utdata:

```text
[eksempel på utdata]
```


## Feilsøking

<!-- VALGFRI: Ta med når det finnes kjente fallgruver for denne
     spesifikke oppgaven. For generell plattformfeilsøking, lenk
     heller til relevant side under "Hjelp".

     Sammenleggbare admonitions holder siden ryddig for de som
     ikke trenger feilsøking. -->

??? failure "Feilmelding: `[feilmelding]`"
    [Sannsynlig årsak.]

    Løsning:

    - [retting]
    - [alternativ retting]

??? failure "[Et annet problem]"
    [Sannsynlig årsak.]

    Løsning:

    - [retting]


## Rydd opp

<!-- VALGFRI: Ta med når oppgaven oppretter ressurser, testdata eller
     konfigurasjon som leseren kan ønske å fjerne etterpå. -->

[Beskriv hvordan du fjerner testdata, angrer endringen, eller gjenoppretter forrige tilstand.]

```bash
[kommando for opprydding]
```


## Relatert innhold

<!-- VALGFRI: Ta med når det finnes naturlige koblinger til andre sider.
     Bruk interne lenker. -->

- [Lenke til relevant tutorial under "Kom i gang"]
- [Lenke til relevant referanseside]
- [Lenke til relevant forklaring under "Om plattformen"]
