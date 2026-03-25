---
title: Landing zone-struktur
description: Landing zone S3-bøttestruktur, IAM-roller, tilgangsmodell og anbefalte filformater.
diataxis: reference
icon: lucide/split
---

# Landing zone

Landing zone er en S3-bucket som opprettes for hvert Databricks-workspace for innkommende data. Hver landing zone har en liste med "sendere" som skal laste opp data til bucketen. For hver sender blir det opprettet tre prefikser (green, yellow, red) med tilhørende brukere som kan laste opp til disse, etter skjemaet:

`s3://bucket_name/sender_name/confidentiality_color/`

## Struktur og tilgang

- 1:1 — Et workspace har en og bare en landing zone-bucket
- Hver sender representerer en ekstern aktør (f.eks. en applikasjon) som skal kunne laste opp filer
- For hver sender opprettes tre sub-prefikser basert på konfidensialitetsnivå:
    - **green** — offentlige/åpne data
    - **yellow** — interne data
    - **red** — konfidensielle data
- For hvert prefiks lages en IAM-bruker slik at en bruker kun kan laste opp til sitt eget område

```
s3://69d82-workspace-landing-zone/
├── sender-a/
│   ├── green/
│   ├── yellow/
│   └── red/
└── sender-b/
    ├── green/
    ├── yellow/
    └── red/
```

## Tilgang til IAM-brukere

For hver sender opprettes IAM-brukere med nøkler (access key + secret key). Nøklene gir kun tilgang til senderens egne prefikser og må formidles over sikker kanal.

Hver IAM-bruker kan:

- `s3:ListBucket` — liste filer i sitt prefiks
- `s3:PutObject` — laste opp filer
- `s3:GetObject` — lese filer
- `s3:DeleteObject` — slette filer

## Anbefalt filformat og struktur

Databricks støtter mange filformater. Vi anbefaler:

| Format            | Når                                   | Merknad                  |
|-------------------|---------------------------------------|--------------------------|
| **Parquet**       | Store datasett, kolonnebasert analyse | Best ytelse              |
| **JSON** (ndjson) | API-responser, nestede strukturer     | En JSON-rad per linje    |
| **CSV**           | Enkle tabulære data                   | Husk UTF-8 og header-rad |

### Organisering for inkrementell innlasting

Organiser filene i mapper etter dato eller batch slik at Databricks Auto Loader enkelt kan plukke opp nye filer:

```
s3://bucket/min-app/green/2026/02/17/data-001.parquet
s3://bucket/min-app/green/2026/02/17/data-002.parquet
s3://bucket/min-app/green/2026/02/18/data-001.parquet
```

Auto Loader holder styr på hvilke filer som allerede er prosessert, slik at kun nye filer leses inn ved neste kjøring.
