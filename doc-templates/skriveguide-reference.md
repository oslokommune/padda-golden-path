# Mal: Referanse

Referansedokumentasjon **beskriver maskineriet**. Den er nøytral, nøyaktig
og strukturert for raskt oppslag — ikke for å leses fra start til slutt.

## Prinsipper

- **Vær nøytral.** Beskriv hva noe *er* og *gjør*, ikke hva leseren bør gjøre
  med det. Det hører hjemme i en how-to.
- **Speil strukturen til det du beskriver.** En referanse for et tabellskjema
  bør se ut som en tabell. En referanse for en mappestruktur bør se ut som
  et tre. Ikke press alt inn i samme format.
- **Vær konsistent innenfor en type.** Hvis du har tre referansesider om
  forskjellige IAM-roller, bør de alle følge samme struktur. Leseren skal
  vite hvor informasjonen finnes basert på posisjon.
- **Inkluder eksempler, men ikke instruksjoner.** Vis hvordan gyldige verdier
  ser ut. Ikke fortell leseren hva de skal taste inn.
- **Vær autoritativ.** Ingen nøling, ingen «du vil kanskje». Slå fast fakta.

## Faste elementer

### Frontmatter

```yaml
---
title: "Landing zone-struktur"
description: >-
  S3-bøttestruktur, IAM-tilgangsmodell og støttede filformater
  for Padda landing zone.
diataxis: reference
tags:
  - hente-inn-data
---
```

### Åpning

Én nøytral setning som beskriver hva denne referansen dekker.

### «Relatert innhold»-seksjon

Lenker til relevante guider og forklaringer.

## Eksempelstrukturer

### A: Konfigurasjon / parametere (f.eks. Auto Loader-innstillinger)

Bruk når du dokumenterer noe med navngitte parametere, felt eller alternativer.

```markdown
# Referanse: Auto Loader-konfigurasjon

Auto Loader leser nye filer inkrementelt fra landing zone inn i
Delta-tabeller.

## Påkrevde innstillinger

### `cloudFiles.format`

- **Type:** string
- **Gyldige verdier:** `csv`, `json`, `parquet`, `avro`
- **Beskrivelse:** Filformatet som skal leses.

### `cloudFiles.schemaLocation`

- **Type:** string
- **Beskrivelse:** Sti til katalog der Auto Loader lagrer og
  utvikler skjemaet. Må være en unik sti per innlastingsjobb.

## Valgfrie innstillinger

### `cloudFiles.maxFilesPerTrigger`

- **Type:** integer
- **Standardverdi:** 1000
- **Beskrivelse:** Maks antall filer per mikrobatch.

## Eksempel

    [minimalt, komplett konfigurasjonseksempel]

## Begrensninger

- [kjent begrensning]
- [versjonskrav]

## Relatert innhold

- [Sette opp Auto Loader](../...) for steg-for-steg-instruksjoner
- [Om datainnlasting](../...) for strategier og formatvalg
```

### B: Struktur / modell (f.eks. landing zone, navnekonvensjoner)

Bruk når du dokumenterer hvordan noe er organisert — mapper, skjemaer,
navnemønstre, tilgangsnivåer. Tabeller og trær fungerer bedre enn
parameterlister.

```markdown
# Referanse: Landing zone-struktur

Landing zone er S3-bøttestrukturen der virksomheter laster opp
filer for innlasting til Databricks.

## Mappestruktur

    s3://{miljø}-landing-{domene}/
    ├── green/          # offentlige data
    ├── yellow/         # interne data
    └── red/            # konfidensielle data

## Tilgangsnivåer

| Nivå   | Fargekode | Tilgang                          | Eksempel               |
| ------ | --------- | -------------------------------- | ---------------------- |
| Åpen   | green     | Alle med plattformtilgang        | Publiserte datasett    |
| Intern | yellow    | Rollebasert, innenfor virksomhet | Saksbehandlingsdata    |
| Strengt| red       | Navngitte brukere                | Personopplysninger     |

## Støttede filformater

| Format  | Anbefalt | Merknad                               |
| ------- | -------- | ------------------------------------- |
| Parquet | Ja       | Beste ytelse, skjemastøtte            |
| CSV     | Ja       | Krever skjemadefinisjon ved innlesing  |
| JSON    | Delvis   | Støttes, men dårligere ytelse         |
| Excel   | Nei      | Konverter til CSV eller bruk DAB      |

## Navnekonvensjoner

- Domene: lowercase, bindestreker (`helse-og-omsorg`)
- Filnavn: lowercase, understreker, dato-suffiks (`saksdata_2026-01-15.parquet`)

## Relatert innhold

- [Laste opp filer til landing zone](../...) for instruksjoner
- [Om dataklassifisering](../...) for bakgrunn om grønn/gul/rød
```

### C: Roller / rettigheter (f.eks. plattformroller)

Bruk når du dokumenterer hvem som kan gjøre hva.

```markdown
# Referanse: Roller og rettigheter

Oversikt over roller i Databricks-plattformen og hva de gir
tilgang til.

## Roller

| Rolle                | Beskrivelse                          | Typisk bruker         |
| -------------------- | ------------------------------------ | --------------------- |
| Ansatt/datautforsker | Lesetilgang til delte datasett       | Analytiker            |
| Dataanalytiker       | Lese + opprette tabeller i eget skjema | Data engineer       |
| Dataansvarlig        | Full tilgang til eget domene         | Fagleder / dataeier   |
| Workspace-admin      | Administrasjon av workspace          | Teknisk leder         |

## Rettigheter per rolle

| Handling                  | Datautforsker | Dataanalytiker | Dataansvarlig | Workspace-admin |
| ------------------------- | :-----------: | :------------: | :-----------: | :-------------: |
| USE CATALOG               | x             | x              | x             | x               |
| USE SCHEMA                |               | x              | x             | x               |
| CREATE TABLE              |               | x              | x             | x               |
| Administrere tilgang      |               |                | x             | x               |
| Konfigurere workspace     |               |                |               | x               |

## Relatert innhold

- [Konto og tilgang](../...) for hvordan du får riktig rolle
- [Om tilgangsstyring](../...) for bakgrunn om tilgangsmodellen
```
