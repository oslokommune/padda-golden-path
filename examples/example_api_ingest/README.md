# API Ingestion Example - Databricks Asset Bundle

Denne bundle'n viser hvordan vi kan hente data fra et eksternt API ved hjelp av DAB (Databricks Asset Bundles).

## Oversikt

Eksemplet dekker:
- hvordan du oppretter et database-skjema for API-data
- hvordan du henter data fra et REST-API med retry-logikk
- hvordan du lagrer rå API-response i en bronse-Delta-tabell
- feilhåndtering og logging

## Bruk

### Bygg wheel

Bundle'n forventer at `dist/` inneholder en fersk wheel før du deployer. Hver gang du endrer kode i `src/`, kjør:

```bash
cd examples/example_api_ingest
uv build
```

### Deploy

```bash
databricks bundle deploy
```

### Kjør jobben

```bash
databricks bundle run api_ingest_job
```

### Kjør ett enkelt notat

```bash
databricks bundle run api_ingest_job -t dev
```

## Konfigurasjon

Bundle'n bruker følgende variabler (definert i `bundle.yml`):

- `catalog`: Navnet på katalogen (standard: `origo_felles`)
- `schema`: Navnet på schema/databasen (standard: `api_ingest`)
- `api_base_url`: Basis-URL for API-et (standard: `https://test.io.web.oslo.kommune.no`)
- `api_endpoint`: Selve endepunktet (standard: `/v3/salaries/current`)
- `alert_notification_id`: ID til en Databricks notification destination som sender varsler (f.eks. til Slack) ved feil (standard: `replace-with-notification-destination-id`)
- `job_cluster_node_type`: Node-typen som brukes for den lille single-node jobbklyngen (standard: `m5.large`)

### Overstyre variabler

Du kan sette verdier ved deploy:

```bash
databricks bundle deploy \
  -v api_base_url=https://api.example.com \
  -v api_endpoint=/v1/data \
  -v alert_notification_id=00000000-0000-0000-0000-000000000000 \
  -v job_cluster_node_type=m5.large
```

## Overvåking og varsling

- Jobben har en global timeout på 10 minutter, og hver oppgave har egne tidsgrenser (`setup`: 10 minutter, `api_ingest`: 30 minutter) med retry-strategi for å fange opp forbigående feil.
- Webhook-varsler går ut når en kjøring feiler. Pek `alert_notification_id` til en Databricks notification destination som poster til kanalen din.
- Hopper eller avbrutte kjøringer utløser også varsler (styrt av `notification_settings` i `bundle.yml`).

### Slack-varsler

1. Lagre Slack-webhooken i en Databricks secret scope (for eksempel `dataspeilet/slack-webhook`).
2. Opprett en notification destination (krever admin) som peker til hemmeligheten:
   ```bash
   databricks notification-destinations create --json '{
     "display_name": "slack-dev-alerts",
     "config": {
       "slack": {
         "url": "{{secrets/dataspeilet/slack-webhook}}"
       }
     }
   }'
   ```
3. Hent ID-en med `databricks notification-destinations list` og sett `alert_notification_id` før du deployer.

## API-klient

`APIClient`-klassen tilbyr:

- **Retry-logikk** med eksponentiell backoff
- **Feilhåndtering** og logging
- **Paginering** rett fra boksen
- **Konfigurerbare headers** for spesialtilpasninger

### Eksempelbruk

```python
from api_ingest.client import APIClient

client = APIClient(
    base_url="https://api.example.com",
    timeout=30,
    max_retries=3,
)

resultat = client.fetch("/endpoint")
```

## Tilpasning

### Bytte API

1. Oppdater `api_base_url` og `api_endpoint` i `bundle.yml`.
2. Endre klienten i `10_api_ingest.py` om du trenger egen autentisering eller tilpassede headers.
3. Juster bronse-tabellen hvis API-responsen ser annerledes ut.

### Legge til autentisering

```python
headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json",
}
api_response = fetch_api_data(
    base_url=api_base_url,
    endpoint=api_endpoint,
    headers=headers,
)
```

### Hemmeligheter

Les hemmeligheter fra Databricks:

```python
api_token = dbutils.secrets.get(scope="api-secrets", key="api_token")
```

## Test
For å kjøre test og få test coverage rapport:

```bash
uv run pytest --cov api-ingest
```

Output
```bash

Name                                                               Stmts   Miss  Cover
--------------------------------------------------------------------------------------
examples/example_api_ingest/src/api_ingest/__init__.py       2      0   100%
examples/example_api_ingest/src/api_ingest/client.py        43      3    93%
examples/example_api_ingest/src/api_ingest/common.py        30      1    97%
examples/example_api_ingest/src/api_ingest/ingest.py        62     16    74%
examples/example_api_ingest/src/api_ingest/setup.py         40     14    65%
--------------------------------------------------------------------------------------
TOTAL                                                                177     34    81%
```
## Eksempel-API

Denne Bundle'n peker mot `https://test.io.web.oslo.kommune.no/v3/salaries/current` som eksempel. Bytt til ditt eget API ved å endre variablene i `bundle.yml`.
