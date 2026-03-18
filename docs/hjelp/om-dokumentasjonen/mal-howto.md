---
title: Hvordan [oppnå et bestemt resultat]
description: [Beskrivelse for søkemotorer — hva leseren får til.]
diataxis: how-to
# icon: lucide/construction  # Fjern kommentar for stub-sider
---

!!! info "Mal: How-to — oppgaverettet, målfokusert"
    Bruk denne malen for sider der leseren allerede vet hva de vil
    oppnå og trenger praktiske anvisninger (f.eks. sider under "Guider").

    **Prinsipper:**

    - Leseren vet allerede hva de vil — hjelp dem raskt i mål
    - Anta kompetanse; ikke lær bort grunnleggende
    - Bare handling — ingen bakgrunn, ingen teori
    - Tillat variasjon: bruk "hvis/når" for forgreninger
    - Lenk videre til tutorials, referanse og forklaring

    **Formatering:**

    - Content tabs er perfekt for varianter (CLI vs. UI, Python vs. SQL)
    - Bruk `!!! warning` for destruktive eller irreversible steg
    - Kodeannoteringer (`# (1)!`) kan erstatte lange forklaringer

    Slett denne boksen når du begynner å skrive.


# Hvordan [oppnå et bestemt resultat]

[Kort innledning: si hva denne veiledningen hjelper leseren med, og hvordan et vellykket resultat ser ut.]


## Før du begynner [OBLIGATORISK]

Kan droppes helt om leseren kan starte uten forberedelser.

Sørg for at du har:

- [nødvendig tilgang, rettigheter eller legitimasjon]
- [nødvendig programvare, miljø eller versjon]
- [nødvendige inndatafiler, verdier eller avhengigheter]

Denne veiledningen forutsetter at du har gjennomført [Sett opp utviklingsmiljøet](../kom-i-gang/dev-setup.md) eller tilsvarende.


## Trinn 1: [Første handling] [OBLIGATORISK]

Minst ett trinn. Trinnene skal være korte og handlingsrettede. Ingen "Forventet resultat" etter hvert trinn — spar det til verifikasjonen på slutten.

[Beskriv handlingen tydelig og direkte.]

```bash
[eksempelkommando]
```

Betinget veiledning skiller en how-to fra en tutorial — ta med når det finnes legitime variasjoner:

Hvis du bruker [alternativ A] i stedet for [alternativ B]:

```bash
[alternativ kommando]
```

Content tabs er ideelle for parallelle fremgangsmåter som oppnår samme mål:

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

!!! note
    [Viktig merknad som hjelper leseren fullføre oppgaven.
    Lenk ut for dypere forklaringer.]

!!! warning
    [Bruk for steg som er destruktive eller irreversible.]


## Trinn 3: [Fullfør fremgangsmåten]

[Beskriv den siste handlingen. Legg til så mange trinn som trengs.]

```bash
[kommando for siste steg]
```


## Bekreft resultatet [OBLIGATORISK]

Kontroller at oppgaven ble fullført:

```bash
[kontrollkommando]
```

Forventet utdata:

```text
[eksempel på utdata]
```


## Feilsøking [FRIVILLIG]

Ta med når det finnes kjente fallgruver for denne spesifikke oppgaven. For generell plattformfeilsøking, lenk heller til relevant side under "Hjelp".

??? failure "Feilmelding: `[feilmelding]`"
    [Sannsynlig årsak.]

    Løsning:

    - [retting]
    - [alternativ retting]

??? failure "[Et annet problem]"
    [Sannsynlig årsak.]

    Løsning:

    - [retting]


## Rydd opp [FRIVILLIG]

Ta med når oppgaven oppretter ressurser, testdata eller konfigurasjon som leseren kan ønske å fjerne etterpå.

```bash
[kommando for opprydding]
```


## Relatert innhold [FRIVILLIG]

- [Lenke til relevant tutorial]
- [Lenke til relevant referanseside]
- [Lenke til relevant forklaring]
