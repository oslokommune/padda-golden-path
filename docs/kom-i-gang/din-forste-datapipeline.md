---
title: Bygg din første datapipeline
description: Tutorial som dekker hele dataflyten fra applikasjon til Power BI.
diataxis: tutorial
---

# Bygg din første datapipeline

Denne guiden gir deg en oversikt over alle stegene som trengs for å sette opp en fungerende datapipeline fra din applikasjon til Power BI via Padda-plattformen.

## Oversikt over dataflyten

```mermaid
flowchart LR
    A[Din applikasjon] -->|AWS S3 API| B[Landing zone<br/>S3-bøtte]
    B -->|External Location| C[Databricks<br/>Bronze-lag]
    C -->|Notebook/pipeline| D[Silver/Gold-lag]
    D -->|SQL Warehouse| E[Power BI]
```

| Steg                  | Hva                                            | Hvem            |
|-----------------------|------------------------------------------------|-----------------|
| 1. Onboarding         | Lese retningslinjer og bekrefte                | Ditt team       |
| 2. Landing zone       | Opprette sender i landing zone                 | Plattformteamet |
| 3. Last opp data      | Sende data fra app til S3                      | Ditt team       |
| 4. Les inn data       | Lese data fra landing zone inn i Databricks    | Ditt team       |
| 5. Transformer data   | Prosessere data gjennom bronze → silver → gold | Ditt team       |
| 6. Koble til Power BI | Koble Power BI til Databricks SQL Warehouse    | Ditt team       |

## Steg 1 — Onboarding

Før du kan bruke plattformen må du gjennomføre onboarding. Dette innebærer å lese retningslinjene og bekrefte at du forstår dem via en pull request.

Se [Brukervilkår og ansvar](../referanse/brukervilkaar.md) for detaljer.

## Steg 2 — Få en landing zone-sender

!!! info "Dette gjør plattformteamet for deg"
    Landing zone-bøtta opprettes og administreres av plattformteamet via Terraform (padda-iac). Du trenger **ikke** opprette S3-bøtta selv.

Hvert Databricks-workspace har **en** landing zone S3-bøtte. Dataen din kommer inn via en **sender** — en logisk identitet som representerer kilden din (for eksempel din applikasjon).

**Slik får du en sender:**

1. Kontakt plattformteamet via [#dig-dataspeilet-support](https://oslokommune.slack.com/archives/C01DE13PLDP) og oppgi:
    - Hvilket workspace du tilhører
    - Navnet du ønsker på senderen (for eksempel `min-app`)
    - AWS-kontonummeret deres, hvis dere har egen AWS-konto
    - Eventuell IP-begrensning for opplasting

2. Plattformteamet oppretter senderen med tre prefikser basert på konfidensialitetsnivå:

    | S3-prefiks                    | Bruksområde         |
    |-------------------------------|---------------------|
    | `s3://bucket/min-app/green/`  | Offentlige data     |
    | `s3://bucket/min-app/yellow/` | Interne data        |
    | `s3://bucket/min-app/red/`    | Konfidensielle data |

3. Du mottar tilgang: en IAM-rolle dere inntar fra egen AWS-konto (anbefalt), eller AWS-nøkler gjennom 1Password. Se [Laste opp filer til landing zone](../guider/hente-inn-data/laste-opp-til-landing-zone.md) for oppsett.

Se [Referanse: Landing zone](../referanse/landing-zone.md) for mer detaljer om struktur og tilgang.

## Steg 3 — Last opp data til landing zone

Når du har fått tilgang kan du laste opp data til landing zone fra din applikasjon.

### Filformat

Databricks håndterer mange formater, men vi anbefaler:

| Format            | Anbefalt for                          | Merknad                   |
|-------------------|---------------------------------------|---------------------------|
| **Parquet**       | Store datasett, kolonnebasert analyse | Best ytelse, sterk typing |
| **JSON** (ndjson) | API-responser, nestede strukturer     | En JSON-rad per linje     |
| **CSV**           | Enkle tabulære data                   | Husk header-rad og UTF-8  |

!!! tip "Inkrementell opplasting"
    Organiser filer i mapper etter dato eller batch, for eksempel:

    ```
    s3://bucket/min-app/green/2026/02/17/data-001.parquet
    s3://bucket/min-app/green/2026/02/17/data-002.parquet
    ```

    Dette gjør det enkelt for Databricks Auto Loader å bare plukke opp nye filer.

### Eksempel: Last opp med Python (boto3)

```python
import boto3

session = boto3.Session(profile_name="min-sender")
s3 = session.client("s3")

s3.upload_file(
    Filename="data.parquet",
    Bucket="12345-workspace-landing-zone",
    Key="min-app/green/2026/02/17/data.parquet",
)
```

Profilen `min-sender` settes opp som beskrevet i [Laste opp filer til landing zone](../guider/hente-inn-data/laste-opp-til-landing-zone.md).

!!! warning "Ikke hardkod hemmeligheter"
    I produksjon bør du bruke Secrets Manager eller Parameter Store i stedet for å hardkode nøkler eller external ID. Se [boto3-dokumentasjonen om påloggingsinformasjon](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html) for alternativer.

### Eksempel: Last opp med AWS CLI

```bash
AWS_PROFILE=min-sender aws s3 cp data.parquet \
  s3://12345-workspace-landing-zone/min-app/green/2026/02/17/data.parquet
```

Se [Laste opp filer til landing zone](../guider/hente-inn-data/laste-opp-til-landing-zone.md) for hvordan du setter opp autentiseringen (IAM-rolle eller nøkler).

## Steg 4 — Les data inn i Databricks

Når data ligger i landing zone kan du lese den inn i Databricks via en **External Location** som plattformteamet allerede har satt opp.

### Med Auto Loader (anbefalt)

Auto Loader overvåker landing zone og plukker automatisk opp nye filer. Bruk dette for inkrementell innlasting:

```python
df = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "parquet")
    .option("cloudFiles.schemaLocation", "/tmp/schema/min-app")
    .load("s3://12345-workspace-landing-zone/min-app/green/")
)

df.writeStream.option("checkpointLocation", "/tmp/checkpoint/min-app").toTable(
    "min_katalog.bronze_default.min_tabell"
)
```

Auto Loader holder styr på hvilke filer som allerede er prosessert, slik at kun nye filer leses inn ved neste kjøring. Se [Sette opp Auto Loader](../guider/hente-inn-data/auto-loader.md) for komplett oppsett med Declarative Pipelines.

### Med batch-lesning

For enklere tilfeller kan du lese filer direkte:

```python
df = spark.read.format("parquet").load(
    "s3://12345-workspace-landing-zone/min-app/green/2026/02/17/"
)

df.write.mode("append").saveAsTable("min_katalog.bronze_default.min_tabell")
```

### Med Databricks Bundle (golden path)

Vi har ferdiglagde eksempler du kan kopiere og tilpasse:

- [Importere Excel til Unity Catalog](../guider/hente-inn-data/importere-excel-til-uc.md) — leser Excel-filer fra Unity Catalog Volume til Delta-tabell

Se [Ta i bruk bundles](../guider/bearbeide-data/ta-i-bruk-bundles.md) for hvordan du setter opp en bundle fra malene, og [Declarative Automation Bundles](../referanse/databricks-bundles.md) for konfigurasjonsdetaljene.

## Steg 5 — Transformer data (bronze → silver → gold)

Databricks-workspace er organisert etter **medallion-arkitekturen**:

```mermaid
flowchart LR
    L[Landing zone<br/>Rådata i S3] --> B[Bronze<br/>Rådata i Delta]
    B --> S[Silver<br/>Vasket og standardisert]
    S --> G[Gold<br/>Forretningsklare data]
```

| Lag | Schema | Formål |
|-----|--------|--------|
| **Bronze** | `bronze_default` | Rå kopi av data fra landing zone, minimalt prosessert |
| **Silver** | `silver_default` | Vasket, deduplisert, standardiserte kolonnenavn og typer |
| **Gold** | `gold_default` | Aggregert, forretningsklart, klart for analyse og BI |

Du bygger pipelines som notebooks eller Databricks-jobber, og deployer dem med [Declarative Automation Bundles](../referanse/databricks-bundles.md). Skriv transformasjonene i Python eller SQL — se [Anbefalte språk](../referanse/anbefalte-spraak.md). Se [Skrive transformasjoner](../guider/bearbeide-data/skrive-transformasjoner.md) for hvordan du skriver transformasjonene.

## Steg 6 — Koble til Power BI

Når data ligger i gold-laget (eller silver, avhengig av behov) kan du koble til Power BI via Databricks SQL Warehouse.

**Slik kobler du til:**

1. **Finn tilkoblingsdetaljer** i Databricks:
    - Gå til **SQL Warehouses** i Databricks-workspacet
    - Velg ditt warehouse og klikk **Connection details**
    - Noter **Server hostname** og **HTTP path**

2. **Koble til fra Power BI Desktop:**
    - Åpne Power BI Desktop → **Get Data** → **Databricks**
    - Skriv inn **Server hostname** og **HTTP path**
    - Autentiser med din Databricks-konto
    - Velg katalog, schema og tabeller du vil bruke

3. **Publiser til Power BI Service** for å dele rapporter med andre.

!!! info "Tilgang"
    Du må ha tilgang til SQL Warehouse og de relevante katalogene/schemaene i Unity Catalog. Kontakt workspace admin om du mangler tilgang.

## Oppsummering

| Steg | Handling                       | Ressurs                                                                                    |
|------|--------------------------------|--------------------------------------------------------------------------------------------|
| 1    | Onboarding                     | [Brukervilkår og ansvar](../referanse/brukervilkaar.md)                                    |
| 2    | Få landing zone-sender         | Kontakt [#dig-dataspeilet-support](https://oslokommune.slack.com/archives/C01DE13PLDP)     |
| 3    | Last opp data til S3           | [Laste opp filer til landing zone](../guider/hente-inn-data/laste-opp-til-landing-zone.md) |
| 4    | Les inn i Databricks           | [Sette opp Auto Loader](../guider/hente-inn-data/auto-loader.md)                           |
| 5    | Bygg pipelines (bronze → gold) | [Skrive transformasjoner](../guider/bearbeide-data/skrive-transformasjoner.md)             |
| 6    | Koble til Power BI             | [Koble Power BI til Databricks](../guider/dele-og-hente-ut/koble-til-power-bi.md)          |

## Trenger du hjelp?

- **Slack**: [#dig-dataspeilet-support](https://oslokommune.slack.com/archives/C01DE13PLDP)
- **GitHub**: [oslokommune/padda-golden-path](https://github.com/oslokommune/padda-golden-path) — opprett et issue

Se [Hjelp](../hjelp/index.md) for flere kontaktkanaler og fellesskap.
