"""Collect platform metrics from all Databricks workspaces.

Connects to both the dev and prod Databricks accounts via GitHub OIDC
federation, enumerates workspaces, and for each workspace counts jobs,
pipelines, and tables by medallion layer (bronze / silver / gold).
Results are uploaded as JSONL to a Unity Catalog volume so the Databricks
Auto Loader in the platform_metrics bundle can ingest them.

No AWS hop — auth to storage is Databricks M2M client_credentials.

Auth: OIDC federation is wired in padda-iac but token exchange currently
returns TOKEN_INVALID — using M2M as workaround until that's fixed.

Required environment variables:
  DEV_CLIENT_ID         Application ID of the dev account SP
  DEV_CLIENT_SECRET     OAuth secret for the dev account SP
  PROD_CLIENT_ID        Application ID of the prod account SP
  PROD_CLIENT_SECRET    OAuth secret for the prod account SP
  DATABRICKS_HOST       Workspace host the volume lives in
  VOLUME_PATH           /Volumes/<catalog>/<schema>/<volume>/<subdir>/

The DEV token is used for the upload — the catalog hosting the volume
is in the dev account.
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

DEV_ACCOUNT_ID = "69d82905-dc92-4349-89b2-c4bf6501cb82"
PROD_ACCOUNT_ID = "5a3d7d58-a44f-4baa-b0df-5648148988d5"


# ---------------------------------------------------------------------------
# Databricks M2M client_credentials token exchange
# ---------------------------------------------------------------------------


def get_account_token(account_id: str, client_id: str, client_secret: str) -> str:
    """Exchange SP client_id + client_secret for an account-level token."""
    url = f"{ACCOUNTS_HOST}/oidc/accounts/{account_id}/v1/token"
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "scope": "all-apis",
        "client_id": client_id,
        "client_secret": client_secret,
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
            f"Token exchange failed ({resp.status}): {resp.data.decode()}"
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
    dev_client_id = os.environ.get("DEV_CLIENT_ID")
    dev_client_secret = os.environ.get("DEV_CLIENT_SECRET")
    prod_client_id = os.environ.get("PROD_CLIENT_ID")
    prod_client_secret = os.environ.get("PROD_CLIENT_SECRET")
    workspace_host = os.environ.get("DATABRICKS_HOST")
    volume_path = os.environ.get("VOLUME_PATH")

    missing = [
        name
        for name, val in [
            ("DEV_CLIENT_ID", dev_client_id),
            ("DEV_CLIENT_SECRET", dev_client_secret),
            ("DATABRICKS_HOST", workspace_host),
            ("VOLUME_PATH", volume_path),
        ]
        if not val
    ]
    if missing:
        print(f"Missing required env vars: {', '.join(missing)}", file=sys.stderr)
        return 1

    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    accounts = [(DEV_ACCOUNT_ID, "dev", dev_client_id, dev_client_secret)]
    if prod_client_id and prod_client_secret:
        accounts.append((PROD_ACCOUNT_ID, "prod", prod_client_id, prod_client_secret))
    else:
        print("PROD_CLIENT_ID/PROD_CLIENT_SECRET not set — skipping prod account")

    dev_token = None  # captured for upload

    all_records: list[dict] = []
    for account_id, label, cid, csecret in accounts:
        try:
            print(f"Authenticating to {label} account ({account_id})")
            token = get_account_token(account_id, cid, csecret)
            if label == "dev":
                dev_token = token
            records = collect_account_metrics(account_id, label, token, timestamp)
            all_records.extend(records)
        except Exception as exc:
            print(f"Error collecting from {label} account: {exc}")

    if not all_records or dev_token is None:
        print("No records collected or dev token missing")
        return 0

    now = datetime.now(UTC)
    filename = f"metrics-{now.strftime('%Y%m%dT%H%M%SZ')}.jsonl"
    body = "\n".join(json.dumps(r, ensure_ascii=False) for r in all_records).encode(
        "utf-8"
    )

    # Volume lives in the dev catalog — use the dev token for upload.
    uri = upload_to_volume(workspace_host, dev_token, volume_path, filename, body)
    print(f"Uploaded {len(all_records)} workspace records to {uri}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
