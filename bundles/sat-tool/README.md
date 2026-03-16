# SAT — Databricks Asset Bundle (isolated VPC, serverless)

Single-workspace serverless deployment of the Databricks Security Analysis Tool.
No internet access needed in the workspace — wheels, TruffleHog binary, and
workspace configs are all bundled and deployed together.

## Architecture

```
Your machine
  ├── download_wheels.sh    → downloads Python wheels for the SAT SDK
  ├── download_trufflehog.sh→ downloads TruffleHog binary (Linux x86_64)
  └── databricks bundle deploy → pushes everything to the workspace

Workspace (SRA isolated, no internet)
  ├── sat_initializer job   → one-time: detects workspace from runtime, loads config
  ├── sat_driver job        → scheduled: runs security analysis
  └── sat_secrets_scanner   → scheduled: scans notebooks/clusters for secrets
```

- **padda-iac** `tf/modules/sat/`: Secrets, SQL warehouse, Service Principal
- **This DAB**: Notebooks, wheels, TruffleHog binary, serverless job definitions

## Setup

### 1. Prerequisites

```bash
databricks auth login --host <WORKSPACE_URL>
```

### 2. Download dependencies (runs locally, needs internet)

```bash
./download_wheels.sh
./download_trufflehog.sh
```

### 3. Deploy + initialize

```bash
databricks bundle deploy --target dev
databricks bundle run sat_initializer --target dev
```

### 4. Done

The driver (Mon/Wed/Fri 07:00 Oslo) and secrets scanner (daily 08:00 Oslo)
run on schedule. No further internet or account API access needed.

Workspace ID and deployment URL are detected automatically from the runtime
context at initializer time. Boolean config flags (sso_enabled, scim_enabled,
etc.) default to safe values and can be updated via notebook 8
(update_workspace_configuration) after initialization.

## Deploying to a different workspace

Update the target host in `databricks.yml` and redeploy:

```bash
databricks bundle deploy --target dev
databricks bundle run sat_initializer --target dev
```
