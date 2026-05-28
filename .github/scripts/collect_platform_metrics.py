"""Collect platform metrics from all Databricks workspaces.

Connects to both the dev and prod Databricks accounts via GitHub OIDC
federation, enumerates workspaces, and for each workspace counts jobs,
pipelines, and tables by medallion layer (bronze / silver / gold).
Results are uploaded as JSONL to a Unity Catalog volume so the Databricks
Auto Loader in the platform_metrics bundle can ingest them.

No AWS hop — auth to storage is GitHub → Databricks OIDC federation.

Required environment variables:
  DEV_OIDC_TOKEN          GitHub OIDC JWT with audience = dev account ID
  PROD_OIDC_TOKEN         GitHub OIDC JWT with audience = prod account ID
  DATABRICKS_HOST         Workspace host the volume lives in
  VOLUME_PATH             /Volumes/<catalog>/<schema>/<volume>/<subdir>/

The DEV OIDC token doubles as the upload credential — the catalog the
volume sits in is owned by the dev account.
"""

import json
import os
import sys
from datetime import datetime, timezone

import urllib3

http = urllib3.PoolManager(retries=urllib3.Retry(total=3, backoff_factor=0.5))

ACCOUNTS_HOST = "https://accounts.cloud.databricks.com"
MEDALLION_KEYWORDS = ("bronze", "silver", "gold")

DEV_ACCOUNT_ID = "00000000-0000-0000-0000-000000000001"
PROD_ACCOUNT_ID = "00000000-0000-0000-0000-000000000002"


# ---------------------------------------------------------------------------
# Databricks OIDC token exchange
# ---------------------------------------------------------------------------

def get_account_token(account_id: str, github_oidc_token: str) -> str:
    """Exchange a GitHub OIDC JWT for a Databricks account-level token."""
    url = f"{ACCOUNTS_HOST}/oidc/accounts/{account_id}/v1/token"
    resp = http.request(
        "POST",
        url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body=(
            "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer"
            f"&assertion={github_oidc_token}"
            "&scope=all-apis"
        ),
        timeout=30,
    )
    if resp.status != 200:
        raise RuntimeError(f"OIDC token exchange failed ({resp.status}): {resp.data.decode()}")
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


def count_jobs(workspace_url: str, token: str) -> int:
    """Count all jobs in a workspace."""
    try:
        jobs = _get_paginated(f"{workspace_url}/api/2.1/jobs/list", token, "jobs")
        return len(jobs)
    except RuntimeError as exc:
        print(f"  Warning: could not list jobs for {workspace_url}: {exc}")
        return -1


def count_pipelines(workspace_url: str, token: str) -> int:
    """Count all DLT pipelines in a workspace."""
    try:
        pipelines = _get_paginated(f"{workspace_url}/api/2.0/pipelines", token, "statuses")
        return len(pipelines)
    except RuntimeError as exc:
        print(f"  Warning: could not list pipelines for {workspace_url}: {exc}")
        return -1


def count_tables_by_medallion(workspace_url: str, token: str) -> dict[str, int]:
    """Count tables grouped by medallion layer (bronze/silver/gold)."""
    counts = {layer: 0 for layer in MEDALLION_KEYWORDS}
    try:
        catalogs = _get(f"{workspace_url}/api/2.1/unity-catalog/catalogs", token).get("catalogs", [])
    except RuntimeError as exc:
        print(f"  Warning: could not list catalogs for {workspace_url}: {exc}")
        return counts

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
        except RuntimeError:
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
            except RuntimeError:
                continue
    return counts


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
        num_jobs = count_jobs(workspace_url, account_token)
        num_pipelines = count_pipelines(workspace_url, account_token)
        table_counts = count_tables_by_medallion(workspace_url, account_token)

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
        raise RuntimeError(f"Files API PUT {full_path} failed ({resp.status}): {resp.data.decode()}")
    return f"{workspace_host}{full_path}"


def main() -> int:
    dev_oidc_token = os.environ.get("DEV_OIDC_TOKEN")
    prod_oidc_token = os.environ.get("PROD_OIDC_TOKEN")
    workspace_host = os.environ.get("DATABRICKS_HOST")
    volume_path = os.environ.get("VOLUME_PATH")

    missing = [
        name
        for name, val in [
            ("DEV_OIDC_TOKEN", dev_oidc_token),
            ("PROD_OIDC_TOKEN", prod_oidc_token),
            ("DATABRICKS_HOST", workspace_host),
            ("VOLUME_PATH", volume_path),
        ]
        if not val
    ]
    if missing:
        print(f"Missing required env vars: {', '.join(missing)}", file=sys.stderr)
        return 1

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"Authenticating to dev account ({DEV_ACCOUNT_ID}) via OIDC")
    dev_token = get_account_token(DEV_ACCOUNT_ID, dev_oidc_token)
    print(f"Authenticating to prod account ({PROD_ACCOUNT_ID}) via OIDC")
    prod_token = get_account_token(PROD_ACCOUNT_ID, prod_oidc_token)

    all_records: list[dict] = []
    for account_id, label, token in [
        (DEV_ACCOUNT_ID, "dev", dev_token),
        (PROD_ACCOUNT_ID, "prod", prod_token),
    ]:
        try:
            records = collect_account_metrics(account_id, label, token, timestamp)
            all_records.extend(records)
        except Exception as exc:
            print(f"Error collecting from {label} account: {exc}")

    if not all_records:
        print("No records collected")
        return 0

    now = datetime.now(timezone.utc)
    filename = f"metrics-{now.strftime('%Y%m%dT%H%M%SZ')}.jsonl"
    body = "\n".join(json.dumps(r, ensure_ascii=False) for r in all_records).encode("utf-8")

    # Volume lives in the dev catalog — use the dev token for upload.
    uri = upload_to_volume(workspace_host, dev_token, volume_path, filename, body)
    print(f"Uploaded {len(all_records)} workspace records to {uri}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
