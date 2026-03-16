# Mal: How-to-guide

En how-to-guide hjelper leseren med å **utføre en konkret oppgave**. Leseren
vet allerede hva de vil gjøre — de trenger praktiske, handlingsrettede steg
for å komme i mål.

## Prinsipper

- **Anta kompetanse.** Leseren kan domenet sitt. Ikke lær bort grunnleggende
  ting.
- **Vær målorientert.** Hver setning skal hjelpe leseren med å fullføre
  oppgaven.
- **Bruk betinget språk.** «Hvis du trenger X, gjør Y.» Oppgaver i den
  virkelige verden har ofte forgreninger — ikke lat som det alltid finnes
  én sti.
- **Ikke forklar i dybden.** Lenk til forklaringssider for «hvorfor». En
  how-to handler om «hvordan».
- **Navngi resultatet i tittelen.** Bra: «Sette opp Slack-alarmer for en
  pipeline». Dårlig: «Slack-alarmer». Leseren skal vite fra tittelen om
  denne siden løser problemet deres.

## Faste elementer

### Frontmatter

```yaml
---
title: Laste opp filer til landing zone
description: >-
  Hvordan laste opp datafiler til S3 landing zone med AWS CLI
  eller SDK, inkludert IAM-konfigurasjon og filformatanbefalinger.
diataxis: how-to
tags:
  - hente-inn-data
---
```

### Åpning

Én til to setninger: hva denne guiden hjelper deg med, og hva et vellykket
resultat ser ut som.

### «Før du begynner»-seksjon

Forutsetninger — men bare ting leseren faktisk trenger *for denne oppgaven*.
Ikke list opp generelle plattformforutsetninger.

### «Bekreft resultatet»-seksjon

Hvordan bekrefte at oppgaven ble fullført.

### «Relatert innhold»-seksjon

Lenker til relevante tutorials, referansesider eller forklaringer — med
beskrivende norsk lenketekst.

## Eksempelstrukturer

### A: Sekvensielle trinn (f.eks. «Laste opp filer til landing zone»)

Det vanligste mønsteret. Bruk når det er en tydelig rekkefølge av handlinger.

```markdown
# Laste opp filer til landing zone

Denne guiden viser hvordan du laster opp datafiler til S3 landing zone
slik at de kan leses inn i Databricks.

## Før du begynner

- AWS CLI installert og konfigurert
- IAM-bruker med skrivetilgang til din domene-bøtte

## Last opp filen

    [kommando og forklaring]

## Kontroller at filen er tilgjengelig

    [verifikasjonskommando]

## Feilsøking

### Tilgang nektet (403 Forbidden)

IAM-brukeren mangler trolig skrivetilgang. Sjekk at ...

## Rydd opp

Hvis du lastet opp testdata du ikke lenger trenger:

    [oppryddingskommando]

## Relatert innhold

- [Referanse: Landing zone-struktur](../...) for detaljer om stier og tilgangsnivåer
- [Om dataklassifisering](../...) for å forstå grønn/gul/rød
```

### B: Forgreninger (f.eks. «Hente data fra en ekstern kilde»)

Bruk når oppgaven har meningsfulle varianter. Zensical content tabs (`===`)
fungerer godt her.

```markdown
# Hente data fra en ekstern kilde

Denne guiden viser hvordan du setter opp innlasting fra en ekstern
datakilde til Databricks.

## Før du begynner

    ...

## Velg innlastingsmetode

=== "Filer via landing zone"

    Bruk dette når datakilden kan levere filer (CSV, Parquet, JSON).

        [steg for filopplasting]

=== "API via Lambda"

    Bruk dette når datakilden har et REST API.

        [steg for Lambda-oppsett]

## Kontroller at data er tilgjengelig i Databricks

    [felles verifikasjon uavhengig av metode]
```

### C: Enkeltstående handling med viktig kontekst (f.eks. «Håndtere secrets»)

Noen how-to-guider er korte — én handling med viktige forbehold. Ikke tving
frem en flerstegsstruktur når det ikke trengs.

```markdown
# Håndtere secrets i Databricks

Denne guiden viser hvordan du lagrer og bruker hemmeligheter
(API-nøkler, passord) i Databricks.

!!! warning "Påvirkning"
    Secrets er synlige for alle brukere med tilgang til ditt workspace.
    Bruk aldri secrets for data som krever individuell tilgangskontroll.

## Opprett et secret scope

    [kommando]

## Lagre en secret

    [kommando]

## Bruk en secret i en notebook

    [kodeeksempel]

## Bekreft at secret er tilgjengelig

    [verifikasjon]

## Relatert innhold

    ...
```
