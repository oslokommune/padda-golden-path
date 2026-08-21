---
title: Oppdatere Power BI-modeller automatisk
description: Hvordan la en Databricks-jobb oppdatere semantiske modeller i Power BI automatisk etter at datapipelinen har kjørt.
diataxis: how-to
---

# Hvordan oppdatere Power BI-modeller automatisk

Denne guiden viser hvordan du setter opp en Databricks-jobb som automatisk oppdaterer en
semantisk modell i Power BI etter at en datapipeline har kjørt, slik at rapportene alltid
viser ferske tall.

Oppsettet består av tre deler:

1. En Power BI-tilkobling i Unity Catalog (OAuth mot Microsoft Entra ID)
2. Bundle-variabler for Power BI-konfigurasjonen
3. En `power_bi_task` i jobbdefinisjonen

## Før du begynner

Sjekk at:

- Du har en publisert semantisk modell i Power BI Service (se
  [Koble Power BI til Databricks](koble-til-power-bi.md))
- Teamet har en Declarative Automation Bundle med en jobbdefinisjon (se
  [Ta i bruk bundles](../bearbeide-data/ta-i-bruk-bundles.md))
- Bundlen ligger i et GitHub-repo der du har rettigheter til å opprette workflows og
  administrere GitHub Environments
- Du har tilgang til et SQL Warehouse (se [SQL Warehouse](../../referanse/sql-warehouse.md))

## Trinn 1 — Opprett Power BI-tilkobling i Unity Catalog

Tilkoblingen opprettes med Databricks CLI via en GitHub Actions-workflow i samme repo
som bundlen ligger i.

### Sett opp GitHub Environments

Workflowen krever følgende i hvert GitHub Environment (`stage` / `prod`):

**Variabler (vars):**

| Variabel               | Beskrivelse                              | Format                                   |
|------------------------|------------------------------------------|------------------------------------------|
| `DATABRICKS_HOST`      | URL til Databricks-workspacet            | `https://dbc-xxxxx.cloud.databricks.com` |
| `DATABRICKS_CLIENT_ID` | Client ID for OIDC service principal     | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`   |
| `POWERBI_TENANT_ID`    | Microsoft Entra ID tenant ID             | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`   |
| `POWERBI_CLIENT_ID`    | Client ID for Power BI service principal | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`   |

**Secrets:**

| Secret                  | Beskrivelse                                   |
|-------------------------|-----------------------------------------------|
| `POWERBI_CLIENT_SECRET` | Client secret for Power BI service principal |

### Opprett workflowen

Opprett filen `.github/workflows/create-powerbi-connection.yml` i rota av repoet der
bundlen ligger:

```yaml
name: Create Power BI Connection in Unity Catalog

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        type: choice
        options:
          - stage
          - prod

permissions:
  id-token: write
  contents: read

jobs:
  create-powerbi-connection:
    name: Create Power BI Connection
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment }}
    env:
      DATABRICKS_HOST: ${{ vars.DATABRICKS_HOST }}
      DATABRICKS_CLIENT_ID: ${{ vars.DATABRICKS_CLIENT_ID }}
      DATABRICKS_AUTH_TYPE: github-oidc

    steps:
      - uses: actions/checkout@v4

      - name: Install Databricks CLI
        uses: databricks/setup-cli@v0.294.0
        with:
          version: 0.294.0

      - name: Create Power BI Connection
        run: |
          databricks connections create \
            --json '{
                "name": "pbi-databricks-${{ github.event.inputs.environment }}",
                "connection_type": "POWER_BI",
                "options": {
                  "authorization_endpoint": "https://login.microsoftonline.com/${{ vars.POWERBI_TENANT_ID }}/oauth2/v2.0/authorize",
                  "client_id": "${{ vars.POWERBI_CLIENT_ID }}",
                  "client_secret": "${{ secrets.POWERBI_CLIENT_SECRET }}"
                },
                "comment": "Databricks to Power BI connection for ${{ github.event.inputs.environment }}",
                "read_only": true
              }'

      - name: Grant Connection Privileges
        run: |
          databricks grants update connection \
            "pbi-databricks-${{ github.event.inputs.environment }}" \
            --json '{
              "changes": [
                {
                  "principal": "<workspace-admins-group>",
                  "add": ["USE_CONNECTION"]
                }
              ]
            }'

      - name: Verify Connection
        run: |
          databricks connections get \
            "pbi-databricks-${{ github.event.inputs.environment }}"
```

### Kjør workflowen

1. Gå til **Actions** i repoet der bundlen ligger
2. Velg **Create Power BI Connection in Unity Catalog**
3. Klikk **Run workflow**
4. Velg miljø (`stage` eller `prod`)
5. Start kjøringen

Etter vellykket kjøring finnes tilkoblingen `pbi-databricks-<environment>` i Unity Catalog
med `USE_CONNECTION`-rettighet for `<workspace-admins-group>`.

## Trinn 2 — Legg til Power BI-variabler i bundlen

Legg til variabler for Power BI-tilkoblingen og SQL Warehouse i `databricks.yml`:

```yaml
variables:
  pbi_connection:
    description: Power BI connection name in Unity Catalog
  pbi_workspace_name:
    description: Power BI workspace name
  warehouse_id:
    description: Databricks SQL Warehouse ID for Power BI semantic model refreshes

targets:
  stage:
    variables:
      pbi_connection: pbi-databricks-stage
      pbi_workspace_name: "Mitt team - Stage"
      warehouse_id: <warehouse-id> # (1)!

  prod:
    variables:
      pbi_connection: pbi-databricks-prod
      pbi_workspace_name: "Mitt team - Prod"
      warehouse_id: <warehouse-id>
```

1. Finn warehouse-ID-en under **SQL Warehouses** → warehouset ditt → **Connection
   details** i Databricks-workspacet — ID-en er siste ledd i **HTTP path**.

## Trinn 3 — Legg til `power_bi_task` i jobbdefinisjonen

I jobb-ressursfilen (for eksempel `resources/my_job.yml`) legger du til en `power_bi_task`
som kjører etter datapipelinen. Merk at `power_bi_task` foreløpig er i forhåndsvisning
(Public Preview) hos Databricks:

```yaml
resources:
  jobs:
    my_etl_job:
      name: my_etl_job

      schedule:
        quartz_cron_expression: "0 0 3 * * ?"  # Kl. 03:00 daglig
        timezone_id: Europe/Oslo

      parameters:
        - name: pbi_connection
          default: ${var.pbi_connection}
        - name: pbi_workspace_name
          default: ${var.pbi_workspace_name}

      tasks:
        - task_key: run_pipeline
          pipeline_task:
            pipeline_id: ${resources.pipelines.my_pipeline.id}

        - task_key: refresh_powerbi_model # (1)!
          depends_on:
            - task_key: run_pipeline
          power_bi_task:
            warehouse_id: ${var.warehouse_id}
            connection_resource_name: ${var.pbi_connection}
            refresh_after_update: true  # (2)!
            power_bi_model:
              workspace_name: ${var.pbi_workspace_name}
              model_name: "Min rapport"  # (3)!
              storage_mode: IMPORT
              authentication_method: OAUTH
              overwrite_existing: false  # (4)!
```

1. Tasken kjører etter at `run_pipeline` har fullført
2. `refresh_after_update: true` utløser en refresh av modellen etter at den er oppdatert
3. Navnet på den semantiske modellen i Power BI (må matche nøyaktig)
4. `overwrite_existing: false` betyr at eksisterende tabeller i modellen beholdes — nye
   legges til

## Trinn 4 — Deploy og verifiser

```bash
databricks bundle validate --target stage
databricks bundle deploy --target stage
```

Etter deploy kjører jobben etter tidsplanen — i eksempelet over daglig klokka 03:00 — og
oppdaterer Power BI-modellen automatisk etter at pipelinen har hentet ferske data.

!!! warning "SQL Warehouse må kjøre"
    `power_bi_task` krever at SQL Warehouse er tilgjengelig. Er warehouset stoppet,
    starter tasken det automatisk, men da må du regne med ekstra oppstartstid.

## Feilsøking

| Problem                                  | Løsning                                                                                                         |
|------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| "Connection not found" i `power_bi_task` | Sjekk at `pbi_connection`-variabelen matcher tilkoblingsnavnet i Unity Catalog                                  |
| OAuth-feil ved tilkoblingsopprettelse    | Verifiser at `POWERBI_TENANT_ID`, `POWERBI_CLIENT_ID` og `POWERBI_CLIENT_SECRET` er riktige                     |
| "Permission denied" på tilkoblingen      | Sjekk at `<workspace-admins-group>` har `USE_CONNECTION` (`databricks grants get connection <name>`)            |
| Modellnavnet matcher ikke                | `model_name` i `power_bi_task` må matche navnet på den semantiske modellen i Power BI nøyaktig                  |
| Modellen henger i «Pending changes»      | Ikke rediger modellen i Power BI Service mens `power_bi_task` oppdaterer den — vent til jobbkjøringen er ferdig |

## Se også

- [Koble Power BI til Databricks](koble-til-power-bi.md) — koble Power BI Desktop til SQL
  Warehouse og publiser rapporten
- [Versjonskontrollere Power BI-rapporter](versjonskontrollere-power-bi-rapporter.md) —
  lagre rapporten som prosjektfil i git og synkroniser arbeidsområdet med GitHub
- [Ta i bruk bundles](../bearbeide-data/ta-i-bruk-bundles.md) — sett opp en Declarative
  Automation Bundle med jobber og pipelines
