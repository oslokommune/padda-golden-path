# SAT — Databricks Asset Bundle (isolated VPC, serverless)

Single-workspace serverless deployment of the Databricks Security Analysis Tool.
No internet access needed in the workspace — wheels, TruffleHog binary, and
workspace configs are all bundled and deployed together.

## Architecture

```
Your machine (has internet + account API access)
  ├── setup_workspaces.py   → calls Accounts API, generates workspace_configs.csv
  ├── download_wheels.sh    → downloads Python wheels for the SAT SDK
  ├── download_trufflehog.sh→ downloads TruffleHog binary (Linux x86_64)
  └── databricks bundle deploy → pushes everything to the workspace

Workspace (SRA isolated, no internet)
  ├── sat_initializer job   → one-time: loads config into tables, imports dashboard
  ├── sat_driver job        → scheduled: runs security analysis
  └── sat_secrets_scanner   → scheduled: scans notebooks/clusters for secrets
```

- **padda-iac** `tf/modules/sat/`: Secrets, SQL warehouse, Service Principal
- **This DAB**: Notebooks, wheels, TruffleHog binary, serverless job definitions

## Setup

### 1. Prerequisites

```bash
pip install databricks-sdk
databricks auth login --account-id <ACCOUNT_ID>
```

### 2. Configure workspaces (runs locally, calls Accounts API)

```bash
# All running workspaces in the account:
python setup_workspaces.py --account-id <ACCOUNT_ID>

# Specific workspaces only:
python setup_workspaces.py --account-id <ACCOUNT_ID> \
    --workspace-ids 2727440053493594 1234567890123456

# Skip connection tests:
python setup_workspaces.py --account-id <ACCOUNT_ID> --skip-connection-test
```

This generates `configs/workspace_configs.csv`.

### 3. Download dependencies (runs locally, needs internet)

```bash
./download_wheels.sh
./download_trufflehog.sh
```

### 4. Deploy + initialize

```bash
databricks bundle deploy --target dev
databricks bundle run sat_initializer --target dev
```

### 5. Done

The driver (Mon/Wed/Fri 07:00 Oslo) and secrets scanner (daily 08:00 Oslo)
run on schedule. No further internet or account API access needed.

## Adding a new workspace

Re-run `setup_workspaces.py` and redeploy:

```bash
python setup_workspaces.py --account-id <ACCOUNT_ID>
databricks bundle deploy --target dev
databricks bundle run sat_initializer --target dev
```
