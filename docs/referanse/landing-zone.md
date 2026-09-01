---
title: Landing zone-struktur
description: Landing zone S3-bøttestruktur, autentiseringsmekanismer, tilgangsmodell, oppbevaring og anbefalte filformater.
diataxis: reference
---

# Landing zone

Landing zone er en S3-bøtte som opprettes for hvert Databricks-workspace for innkommende data. Hver landing zone har en liste med "sendere" som skal laste opp data til bøtta. For hver sender blir det opprettet tre prefikser (green, yellow, red) som senderen kan laste opp til, etter mønsteret:

`s3://bucket_name/sender_name/confidentiality_color/`

## Struktur

- En-til-en — Et workspace har en og bare en landing zone-bøtte
- Bøttenavnet følger mønsteret `<fem første tegn av Databricks-konto-ID>-<workspace-navn>-landing-zone`
- Hver sender representerer en ekstern aktør (for eksempel en applikasjon) som skal kunne laste opp filer
- Bøtta er tilgjengelig i Databricks via en External Location som plattformteamet setter opp
- For hver sender opprettes tre underprefikser i S3 basert på konfidensialitetsnivå:
    - **green** — offentlige/åpne data
    - **yellow** — interne data
    - **red** — konfidensielle data

```
s3://12345-workspace-landing-zone/
├── sender-a/
│   ├── green/
│   ├── yellow/
│   └── red/
└── sender-b/
    ├── green/
    ├── yellow/
    └── red/
```

## Autentisering

En sender autentiseres på én av to måter. Se [Laste opp filer til landing zone](../guider/hente-inn-data/laste-opp-til-landing-zone.md) for hvordan du ber om en sender og setter opp opplasting.

### IAM-rolle

For sendere med egen AWS-konto opprettes en IAM-rolle i plattformkontoen, med ARN etter mønsteret:

`arn:aws:iam::<plattformkonto>:role/landing-zone/senders/<workspace>-<sendernavn>-ingest`

Bare senderens registrerte AWS-konto (eventuelt en spesifikk rolle i den) kan innta rollen med `sts:AssumeRole`, og bare med riktig **external ID** — en tilfeldig generert verdi som formidles til senderen gjennom 1Password. Én rolle dekker alle tre konfidensialitetsprefiksene til senderen.

### IAM-bruker med nøkler

For sendere uten egen AWS-konto opprettes i stedet én IAM-bruker per konfidensialitetsnivå, med navn etter mønsteret `<workspace>-<sendernavn>-<color>`. Brukerne har langlivede tilgangsnøkler (access key + secret key) som formidles gjennom 1Password.

### Rettigheter

Begge mekanismene gir de samme rettighetene, avgrenset til senderens egne prefikser:

- `s3:ListBucket` — liste filer (betinget på senderens prefikser)
- `s3:PutObject` — laste opp filer
- `s3:GetObject` — lese filer
- `s3:DeleteObject` — slette filer

Opplasting kan i tillegg begrenses til gitte IP-adresser (`aws:SourceIp`-betingelse).

## Sletting og oppbevaring

Filer i landing zone slettes ikke automatisk: plattformen rydder aldri i bøtta og setter
ingen frist for hvor lenge filer kan bli liggende. Hvor lenge filene skal beholdes, er
teamets vurdering. Filene er grunnlaget bronze-tabeller gjenskapes fra ved en full
refresh, se
[Datainnlasting](../om-plattformen/konsepter/datainnlasting.md#kan-vi-slette-filene-i-landing-zone-etter-innlasting).

## Anbefalt filformat og struktur

Databricks støtter mange filformater. Vi anbefaler:

| Format            | Når                                   | Merknad                  |
|-------------------|---------------------------------------|--------------------------|
| **Parquet**       | Store datasett, kolonnebasert analyse | Best ytelse              |
| **JSON** (ndjson) | API-responser, nestede strukturer     | En JSON-rad per linje    |
| **CSV**           | Enkle tabulære data                   | Husk UTF-8 og header-rad |

### Organisering for inkrementell innlasting

Organiser filene i mapper etter dato eller batch slik at [Databricks Auto Loader](../guider/hente-inn-data/auto-loader.md) enkelt kan plukke opp nye filer:

```
s3://bucket/min-app/green/2026/02/17/data-001.parquet
s3://bucket/min-app/green/2026/02/17/data-002.parquet
s3://bucket/min-app/green/2026/02/18/data-001.parquet
```

Auto Loader holder styr på hvilke filer som allerede er prosessert, slik at kun nye filer leses inn ved neste kjøring.
