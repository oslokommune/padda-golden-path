---
title: Last opp ditt første datasett
description: Lag et lite testdatasett, last det opp til et volum i Unity Catalog og les fila direkte med SQL.
diataxis: tutorial
---

# Last opp ditt første datasett

I dette steget får vi data inn i teamets workspace. Vi lager en fil med fiktive
paddeobservasjoner fra dammer i Oslo, laster den opp til et volum i Unity Catalog med
Databricks CLI, og kjører en SQL-spørring mot fila. Datasettet bruker vi videre i [Bygg
din første datapipeline](din-forste-datapipeline.md).

## Dette skal vi lage

Når du er ferdig, har du:

- en prosjektmappe på maskinen din med en testdatafil
- et volum i skjemaet `landing_default` i teamets katalog, med fila i
- en SQL-spørring som leser fila rett fra volumet

## Før du begynner

Du trenger:

- [Sett opp utviklingsmiljøet](dev-setup.md) gjennomført, med Databricks CLI innlogget i
  workspacet ditt. Kommandoene nedenfor bruker `<profilnavn>` om profilen du valgte der.
- Navnet på teamets katalog. Det ligger i teamets 1Password-hvelv sammen med
  workspace-adressen. Vi bruker `min_katalog` som eksempel, bytt ut med navnet på din.
- Rett til å opprette volumer i katalogen. Er du usikker, prøv deg fram: mangler
  rettigheten, får du `PERMISSION_DENIED` i trinn 2, se [Hvis noe ikke
  stemmer](#hvis-noe-ikke-stemmer).

## Trinn 1: Lag en fil med testdata

Opprett en mappe for prosjektet, med en undermappe for testdataene:

```bash
mkdir -p paddeobservasjoner/testdata
cd paddeobservasjoner
```

Lag fila `testdata/paddeobservasjoner-2026-04-15.json` med dette innholdet:

```json
{"observasjon_id": "obs-001", "lokalitet": "Østensjøvannet", "antall": 12, "observert": "2026-04-14T21:30:00"}
{"observasjon_id": "obs-002", "lokalitet": "Sognsvann", "antall": 3, "observert": "2026-04-14T22:05:00"}
{"observasjon_id": "obs-003", "lokalitet": "Østensjøvannet", "antall": 27, "observert": "2026-04-15T21:45:00"}
```

Hver linje er én observasjon som et JSON-objekt.

## Trinn 2: Opprett et volum

Et volum er et område for filer i Unity Catalog. Skjemaet `landing_default` finnes
allerede i katalogen din og er ment for innkommende filer. Opprett et volum der:

```bash
databricks volumes create min_katalog landing_default paddeobservasjoner MANAGED -p <profilnavn>
```

Forventet resultat: CLI-en skriver ut volumet den opprettet, med blant annet `"full_name":
"min_katalog.landing_default.paddeobservasjoner"`.

## Trinn 3: Last opp fila

CLI-en krever `dbfs:/` foran volumstien:

```bash
databricks fs cp testdata/paddeobservasjoner-2026-04-15.json \
  dbfs:/Volumes/min_katalog/landing_default/paddeobservasjoner/ -p <profilnavn>
```

Sjekk at fila ligger der:

```bash
databricks fs ls dbfs:/Volumes/min_katalog/landing_default/paddeobservasjoner/ -p <profilnavn>
```

Forventet resultat:

```text
paddeobservasjoner-2026-04-15.json
```

## Kontroller resultatet

Åpne **SQL Editor** i sidemenyen i workspacet, og les fila rett fra volumet:

```sql
SELECT observasjon_id, lokalitet, antall, observert
FROM read_files('/Volumes/min_katalog/landing_default/paddeobservasjoner/', format => 'json')
ORDER BY observert;
```

Du skal se de tre observasjonene fra fila:

| observasjon_id | lokalitet      | antall | observert           |
|----------------|----------------|--------|---------------------|
| obs-001        | Østensjøvannet | 12     | 2026-04-14T21:30:00 |
| obs-002        | Sognsvann      | 3      | 2026-04-14T22:05:00 |
| obs-003        | Østensjøvannet | 27     | 2026-04-15T21:45:00 |

Inne i Databricks heter stien bare `/Volumes/...`, uten `dbfs:/`. Du finner volumet og
fila under **Catalog** i sidemenyen også.

## Hvis noe ikke stemmer

??? failure "`PERMISSION_DENIED` når du oppretter volumet eller laster opp"

    Du mangler rettigheter i katalogen. Kontakt workspace-admin i teamet ditt, eller
    Dataspeilet i [#dig-dataspeilet-support](https://oslokommune.slack.com/archives/C01DE13PLDP).

??? failure "Volumet finnes allerede"

    Volumet deles med resten av teamet, så en kollega har antakelig tatt løpet før deg.
    Ta stegene én om gangen på teamet, eller vent til kollegaen har ryddet opp etter
    [Bygg din første datapipeline](din-forste-datapipeline.md).

??? failure "`read_files` finner ingen filer"

    Sjekk at `min_katalog` er byttet ut med katalogen din i stien, og at `databricks fs
    ls` viser fila.

## Du har nå

- Et volum i `landing_default` som tar imot filer, og en fil i det
- En SQL-spørring som leser fila rett fra volumet, uten at den er lastet inn i en tabell

## Neste steg

Gå videre til [Bygg din første datapipeline](din-forste-datapipeline.md), der en pipeline
leser fila inn i bronze- og silver-tabeller.
