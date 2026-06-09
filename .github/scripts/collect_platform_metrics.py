"""Collect platform metrics from all Databricks workspaces.

Connects to both the dev and prod Databricks accounts via GitHub OIDC
federation, enumerates workspaces, and for each workspace counts jobs,
pipelines, and tables by medallion layer (bronze / silver / gold).
Results are uploaded as JSONL to a Unity Catalog volume so the Databricks
Auto Loader in the platform_metrics bundle can ingest them.

No AWS hop — auth to storage is the federated Databricks token.

Auth: GitHub OIDC federation (RFC 8693 token-exchange). The workflow mints an
OIDC token with the Databricks account as audience and passes it in; client_id
selects the collector SP, whose federation policy in padda-iac authorizes the
exchange. No stored secret.

Single environment per run. The workflow runs this once per GitHub environment
(dev, prod); each run inventories that environment's own Databricks account and
uploads to that environment's landing volume. Only the catalog varies the path
— schema, volume, and collection subdir follow the LANDING_SCHEMA /
LANDING_VOLUME / COLLECTION convention below.

Required environment variables:
  DATABRICKS_ACCOUNT_ID       Databricks account ID for this environment
  DATABRICKS_CLIENT_ID        Collector SP application id (selects the SP; not secret)
  DATABRICKS_OIDC_TOKEN       GitHub OIDC JWT (audience = the account ID)
  DATABRICKS_HOST             Workspace host hosting this environment's volume
  DATABRICKS_METRICS_CATALOG  Catalog (padda_dev_green / dig_eksempelteam_stage_green)
  ACCOUNT_LABEL               Label stored in the records, e.g. dev / prod
"""

import json
import os
import sys
import urllib.parse
from datetime import UTC, datetime

import urllib3

http = urllib3.PoolManager(retries=urllib3.Retry(total=3, backoff_factor=0.5))

ACCOUNTS_HOST = "https://accounts.cloud.databricks.com"
MEDALLION_KEYWORDS = ("bronze", "silver", "gold")

# Landing-zone layout. One volume per environment holds all collector output,
# with one subdirectory per collection. The only part that varies per
# environment is the catalog; schema, volume, and collection are fixed.
#   /Volumes/<catalog>/<LANDING_SCHEMA>/<LANDING_VOLUME>/<COLLECTION>/
# The platform_metrics DLT pipeline (padda-databrikker) reads the same path.
LANDING_SCHEMA = "landing_default"
LANDING_VOLUME = "platform_events"
COLLECTION = "workspace_inventory"  # this collector's subdirectory


def collection_path(catalog: str) -> str:
    """Landing-volume path for this collection in the given catalog."""
    return f"/Volumes/{catalog}/{LANDING_SCHEMA}/{LANDING_VOLUME}/{COLLECTION}"


# ---------------------------------------------------------------------------
# GitHub OIDC -> Databricks token federation (RFC 8693 token-exchange)
# ---------------------------------------------------------------------------


def get_account_token(account_id: str, client_id: str, oidc_token: str) -> str:
    """Federate a GitHub OIDC token into a Databricks account-level token.

    RFC 8693 token exchange against the account OIDC endpoint. The GitHub
    Actions OIDC JWT is the subject_token; client_id selects the collector SP,
    whose service-principal federation policy (in padda-iac) authorizes the
    exchange. No stored client secret.
    """
    url = f"{ACCOUNTS_HOST}/oidc/accounts/{account_id}/v1/token"
    body = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": oidc_token,
        "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
        "client_id": client_id,
        "scope": "all-apis",
    })
    resp = http.request(
        "POST",
        url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body=body,
        timeout=30,
    )
    if resp.status != 200:
        raise RuntimeError(
            f"OIDC token exchange failed ({resp.status}): {resp.data.decode()}"
        )
    return json.loads(resp.data.decode())["access_token"]


# ---------------------------------------------------------------------------
# Databricks REST API helpers
# ---------------------------------------------------------------------------


def _get(url: str, token: str, params: dict | None = None) -> dict:
    """Authenticated GET against a Databricks REST endpoint."""
    headers = {"Authorization": f"Bearer {token}"}
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    resp = http.request("GET", url, headers=headers, timeout=60)
    if resp.status != 200:
        raise RuntimeError(f"GET {url} failed ({resp.status}): {resp.data.decode()}")
    return json.loads(resp.data.decode())


def _get_paginated(url: str, token: str, items_key: str) -> list:
    """Paginate through a Databricks list endpoint and return all items."""
    all_items: list = []
    params: dict = {"page_size": "100"}
    while True:
        data = _get(url, token, params)
        all_items.extend(data.get(items_key, []))
        next_token = data.get("next_page_token")
        if not next_token:
            break
        params["page_token"] = next_token
    return all_items


def list_workspaces(account_id: str, token: str) -> list[dict]:
    """List all workspaces in a Databricks account."""
    url = f"{ACCOUNTS_HOST}/api/2.0/accounts/{account_id}/workspaces"
    raw = _get(url, token)
    return raw if isinstance(raw, list) else raw.get("workspaces", [])


def count_jobs(workspace_url: str, token: str, errors: list[str]) -> int | None:
    """Count all jobs in a workspace.

    Returns None (not -1) when the API call fails, so an unreachable workspace
    is recorded as "unknown" rather than a value that looks like real data.
    The failure is appended to ``errors`` for observability.
    """
    try:
        jobs = _get_paginated(f"{workspace_url}/api/2.1/jobs/list", token, "jobs")
        return len(jobs)
    except RuntimeError as exc:
        print(f"  Warning: could not list jobs for {workspace_url}: {exc}")
        errors.append(f"jobs: {exc}")
        return None


def count_pipelines(workspace_url: str, token: str, errors: list[str]) -> int | None:
    """Count all DLT pipelines in a workspace.

    Returns None on failure (see :func:`count_jobs`).
    """
    try:
        pipelines = _get_paginated(
            f"{workspace_url}/api/2.0/pipelines", token, "statuses"
        )
        return len(pipelines)
    except RuntimeError as exc:
        print(f"  Warning: could not list pipelines for {workspace_url}: {exc}")
        errors.append(f"pipelines: {exc}")
        return None


def count_tables_by_medallion(
    workspace_url: str, token: str, errors: list[str]
) -> dict[str, int | None]:
    """Count tables grouped by medallion layer (bronze/silver/gold).

    A layer count is None when it could not be collected, so a transient
    failure is not silently reported as zero tables:
    - catalog listing fails  -> all three layers are unknown (None)
    - schema listing fails    -> all layers for that catalog are unknown
    - table listing fails     -> only that schema's layer is unknown
    Failures are appended to ``errors``.
    """
    counts: dict[str, int] = {layer: 0 for layer in MEDALLION_KEYWORDS}
    unknown: set[str] = set()
    try:
        catalogs = _get(f"{workspace_url}/api/2.1/unity-catalog/catalogs", token).get(
            "catalogs", []
        )
    except RuntimeError as exc:
        print(f"  Warning: could not list catalogs for {workspace_url}: {exc}")
        errors.append(f"catalogs: {exc}")
        return {layer: None for layer in MEDALLION_KEYWORDS}

    for catalog in catalogs:
        catalog_name = catalog["name"]
        if catalog_name in ("system", "__databricks_internal", "hive_metastore"):
            continue
        try:
            schemas = _get(
                f"{workspace_url}/api/2.1/unity-catalog/schemas",
                token,
                {"catalog_name": catalog_name},
            ).get("schemas", [])
        except RuntimeError as exc:
            # We can't tell which medallion layers this catalog held, so every
            # layer count is now incomplete — mark them all unknown.
            errors.append(f"schemas[{catalog_name}]: {exc}")
            unknown.update(MEDALLION_KEYWORDS)
            continue

        for schema in schemas:
            schema_name = schema["name"].lower()
            layer = next((kw for kw in MEDALLION_KEYWORDS if kw in schema_name), None)
            if layer is None:
                continue
            try:
                tables = _get(
                    f"{workspace_url}/api/2.1/unity-catalog/tables",
                    token,
                    {"catalog_name": catalog_name, "schema_name": schema["name"]},
                ).get("tables", [])
                counts[layer] += len(tables)
            except RuntimeError as exc:
                errors.append(f"tables[{catalog_name}.{schema['name']}]: {exc}")
                unknown.add(layer)
                continue

    return {
        layer: (None if layer in unknown else counts[layer])
        for layer in MEDALLION_KEYWORDS
    }


# ---------------------------------------------------------------------------
# Main collection logic
# ---------------------------------------------------------------------------


def collect_account_metrics(
    account_id: str,
    account_label: str,
    account_token: str,
    timestamp: str,
) -> list[dict]:
    """Collect metrics for all workspaces in one Databricks account."""
    print(f"Listing workspaces for {account_label} ({account_id})")
    workspaces = list_workspaces(account_id, account_token)
    print(f"  Found {len(workspaces)} workspaces")

    records = []
    for ws in workspaces:
        ws_name = ws.get("workspace_name", ws.get("deployment_name", "unknown"))
        ws_id = ws.get("workspace_id", "")
        deployment = ws.get("deployment_name", "")
        workspace_url = f"https://{deployment}.cloud.databricks.com"

        print(f"  Collecting metrics for {ws_name} ({workspace_url})")
        errors: list[str] = []
        num_jobs = count_jobs(workspace_url, account_token, errors)
        num_pipelines = count_pipelines(workspace_url, account_token, errors)
        table_counts = count_tables_by_medallion(workspace_url, account_token, errors)

        records.append({
            "collection_timestamp": timestamp,
            "account": account_label,
            "account_id": account_id,
            "workspace_id": str(ws_id),
            "workspace_name": ws_name,
            "num_jobs": num_jobs,
            "num_pipelines": num_pipelines,
            "num_bronze_tables": table_counts["bronze"],
            "num_silver_tables": table_counts["silver"],
            "num_gold_tables": table_counts["gold"],
            # Failure metadata: distinguishes "could not collect" (NULL counts)
            # from a genuine zero, so partial failures stay visible downstream
            # instead of dropping the workspace or faking a count.
            "partial_failure": bool(errors),
            "collection_errors": "; ".join(errors),
        })
    return records


# ---------------------------------------------------------------------------
# Databricks Files API upload
# ---------------------------------------------------------------------------


def upload_to_volume(
    workspace_host: str,
    token: str,
    volume_path: str,
    filename: str,
    body: bytes,
) -> str:
    """PUT a file to a Unity Catalog volume via the Files API."""
    full_path = f"{volume_path.rstrip('/')}/{filename}"
    url = f"{workspace_host.rstrip('/')}/api/2.0/fs/files{full_path}?overwrite=true"
    resp = http.request(
        "PUT",
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream",
        },
        body=body,
        timeout=60,
    )
    if resp.status not in (200, 204):
        raise RuntimeError(
            f"Files API PUT {full_path} failed ({resp.status}): {resp.data.decode()}"
        )
    return f"{workspace_host}{full_path}"


def main() -> int:
    # Single environment per run. The workflow invokes this once per GitHub
    # environment (dev, prod); the vars resolve to that environment's own
    # account, workspace, and catalog. Auth is GitHub OIDC federation — the
    # workflow passes a Databricks-audience OIDC token, no stored secret.
    account_id = os.environ.get("DATABRICKS_ACCOUNT_ID")
    client_id = os.environ.get("DATABRICKS_CLIENT_ID")
    oidc_token = os.environ.get("DATABRICKS_OIDC_TOKEN")
    workspace_host = os.environ.get("DATABRICKS_HOST")
    catalog = os.environ.get("DATABRICKS_METRICS_CATALOG")
    account_label = os.environ.get("ACCOUNT_LABEL", "unknown")

    missing = [
        name
        for name, val in [
            ("DATABRICKS_ACCOUNT_ID", account_id),
            ("DATABRICKS_CLIENT_ID", client_id),
            ("DATABRICKS_OIDC_TOKEN", oidc_token),
            ("DATABRICKS_HOST", workspace_host),
            ("DATABRICKS_METRICS_CATALOG", catalog),
        ]
        if not val
    ]
    if missing:
        print(f"Missing required env vars: {', '.join(missing)}", file=sys.stderr)
        return 1

    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"Authenticating to {account_label} account ({account_id}) via GitHub OIDC")
    token = get_account_token(account_id, client_id, oidc_token)
    records = collect_account_metrics(account_id, account_label, token, timestamp)

    if not records:
        print("No records collected")
        return 0

    now = datetime.now(UTC)
    filename = f"metrics-{now.strftime('%Y%m%dT%H%M%SZ')}.jsonl"
    body = "\n".join(json.dumps(r, ensure_ascii=False) for r in records).encode("utf-8")

    uri = upload_to_volume(
        workspace_host, token, collection_path(catalog), filename, body
    )
    print(f"Uploaded {len(records)} workspace records to {uri}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
