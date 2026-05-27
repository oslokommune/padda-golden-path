---
title: Koble Power BI til Databricks
description: Hvordan koble Power BI Desktop til SQL Warehouse og sette opp automatisk refresh av semantiske modeller.
diataxis: how-to
---

# Hvordan koble Power BI til Databricks

Denne guiden dekker to bruksscenarier:

- **[Power BI Desktop](#koble-til-fra-power-bi-desktop)** — ad hoc-rapportering mot SQL Warehouse
- **[Automatisk refresh](#automatisk-refresh-av-semantiske-modeller)** — oppdatere Power BI-modeller automatisk fra en Databricks-jobb

## Før du begynner

Sjekk at:
- Du har tilgang til et Databricks-workspace med et SQL Warehouse (se [SQL Warehouse](../../referanse/sql-warehouse.md))
- Du har Power BI Desktop installert

For automatisk refresh trenger du i tillegg:

- En Power BI-tilkobling i Unity Catalog (se [Opprette Power BI-tilkobling](#trinn-1-opprett-power-bi-tilkobling-i-unity-catalog))
- En Declarative Automation Bundle med en jobb-definisjon (se [Ta i bruk bundles](../../guider/bearbeide-data/ta-i-bruk-bundles.md))

---

## Koble til fra Power BI Desktop

Bruk dette når du vil utforske data interaktivt eller bygge rapporter i Power BI Desktop mot Databricks-tabeller.

### Trinn 1 — Finn tilkoblingsdetaljer

Du trenger **Server Hostname** og **HTTP Path** fra SQL Warehouse:

1. Åpne Databricks-workspacet
2. Gå til **SQL Warehouses** i venstremenyen
3. Klikk på warehouset du vil bruke
4. Gå til fanen **Connection details**
5. Kopier **Server Hostname** og **HTTP Path**

### Trinn 2 — Koble til fra Power BI Desktop

1. Åpne Power BI Desktop
2. Klikk **Get Data** → **More...**
3. Søk etter **Databricks** og velg **Azure Databricks**
4. Fyll inn:
    - **Server Hostname**: verdien fra Trinn 1
    - **HTTP Path**: verdien fra Trinn 1
5. Velg datakonnektivitetsmodus (se [DirectQuery vs. Import](#directquery-vs-import) under)
6. Klikk **OK**

### Trinn 3 — Autentiser

Ved første tilkobling blir du bedt om å autentisere:

1. Velg **Azure Active Directory** (Microsoft Entra ID) i venstre panel
2. Klikk **Sign in**
3. Logg inn med din organisasjonskonto
4. Klikk **Connect**

### Trinn 4 — Velg tabeller

1. Navigasjonsvinduet viser tilgjengelige kataloger og skjemaer i Unity Catalog
2. Utvid katalogen (f.eks. `<workspace-name>_green`) → skjemaet → velg tabellene du trenger
3. Klikk **Load** (Import) eller **Transform Data** (for å redigere før lasting)

### DirectQuery vs. Import

| Modus | Når bruke | Fordeler | Ulemper |
|-------|-----------|----------|---------|
| **DirectQuery** | Dataene endres ofte, alltid ferske data trengs | Alltid oppdatert, ingen lokal kopi | Tregere spørringer, krever at warehouse kjører |
| **Import** | Rapporter skal være raske, data oppdateres sjeldnere | Rask interaksjon, fungerer offline | Data er et øyeblikksbilde, må refreshes manuelt eller på schedule |

!!! tip "Anbefaling"
    Start med **Import** for de fleste rapporter. Bruk **DirectQuery** bare når du trenger sanntidsdata eller datasettet er for stort til å importere.

### Trinn 5 — Publiser til Power BI Service (valgfritt)

1. Klikk **Publish** i Power BI Desktop
2. Velg workspace i Power BI Service (f.eks. "Teamet mitt - Prod")
3. Rapporten og datasettet blir lastet opp

For automatisk oppdatering av publiserte rapporter, se neste seksjon.

---

## Automatisk refresh av semantiske modeller

Bruk dette når du vil at en Databricks-jobb automatisk oppdaterer en Power BI semantisk modell etter at en datapipeline har kjørt. Dette krever tre ting:

1. En Power BI-tilkobling i Unity Catalog (OAuth mot Microsoft Entra ID)
2. Bundle-variabler for Power BI-konfigurasjon
3. En `power_bi_task` i jobb-definisjonen

### Trinn 1 — Opprett Power BI-tilkobling i Unity Catalog

Tilkoblingen opprettes med Databricks CLI via en GitHub Actions workflow. Opprett filen `.github/workflows/create-powerbi-connection.yml`:

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

#### GitHub Environment-oppsett

Workflowen krever følgende i hvert GitHub Environment (`stage` / `prod`):

**Variabler (vars):**

| Variabel | Beskrivelse | Eksempel |
|----------|-------------|---------|
| `DATABRICKS_HOST` | URL til Databricks-workspacet | `https://dbc-xxxxx.cloud.databricks.com` |
| `DATABRICKS_CLIENT_ID` | Client ID for OIDC service principal | UUID |
| `POWERBI_TENANT_ID` | Microsoft Entra ID tenant ID | UUID |
| `POWERBI_CLIENT_ID` | Client ID for Power BI service principal | UUID |

**Secrets:**

| Secret | Beskrivelse |
|--------|-------------|
| `POWERBI_CLIENT_SECRET` | Client secret for Power BI service principal |

#### Kjøre workflowen

1. Gå til **Actions** i GitHub-repoet
2. Velg **Create Power BI Connection in Unity Catalog**
3. Klikk **Run workflow**
4. Velg miljø (`stage` eller `prod`)
5. Start kjøring

Etter vellykket kjøring finnes tilkoblingen `pbi-databricks-<environment>` i Unity Catalog med `USE_CONNECTION`-rettighet for `<workspace-admins-group>`.

### Trinn 2 — Legg til Power BI-variabler i bundle

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

1. Finn warehouse ID-en under **SQL Warehouses** → ditt warehouse → **Connection details** i Databricks-workspacet.

### Trinn 3 — Legg til `power_bi_task` i jobb-definisjonen

I jobb-ressursfilen (f.eks. `resources/my_job.yml`), legg til en `power_bi_task` som kjører etter datapipelinen:

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
2. `refresh_after_update: true` trigger en refresh av modellen etter oppdatering
3. Navnet på den semantiske modellen i Power BI (må matche nøyaktig)
4. `overwrite_existing: false` betyr at eksisterende tabeller i modellen beholdes — nye legges til

### Trinn 4 — Deploy og verifiser

```bash
databricks bundle validate --target stage
databricks bundle deploy --target stage
```

Etter deploy kjører jobben daglig og oppdaterer Power BI-modellen automatisk etter at pipelinen har hentet ferske data.

!!! warning "SQL Warehouse må kjøre"
    `power_bi_task` krever at SQL Warehouse er tilgjengelig. Hvis warehouset er stoppet vil tasken starte det automatisk, men dette kan legge til oppstartstid.

---

## Feilsøking

| Problem | Løsning |
|---------|---------|
| "Connection not found" i `power_bi_task` | Sjekk at `pbi_connection`-variabelen matcher tilkoblingsnavnet i Unity Catalog |
| OAuth-feil ved tilkoblingsopprettelse | Verifiser at `POWERBI_TENANT_ID`, `POWERBI_CLIENT_ID` og `POWERBI_CLIENT_SECRET` er riktige |
| "Permission denied" på tilkoblingen | Sjekk at `<workspace-admins-group>` har `USE_CONNECTION` (`databricks grants get connection <name>`) |
| Power BI Desktop kan ikke koble til | Sjekk at SQL Warehouse kjører og at du bruker riktig Server Hostname / HTTP Path |
| Modellnavn matcher ikke | `model_name` i `power_bi_task` må matche det eksakte navnet på den semantiske modellen i Power BI |
