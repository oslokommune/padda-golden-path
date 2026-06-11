"""Collect platform metrics from all Databricks workspaces.

Connects to both the dev and prod Databricks accounts via GitHub OIDC
federation, enumerates workspaces, and for each workspace counts jobs,
pipelines, and tables grouped by medallion tier (bronze / silver / gold /
n/a). A table's tier comes from tier keywords in its own name (English or
Norwegian); tables without one inherit the tier of their schema; everything
else is "na". Results are uploaded as JSONL to a Unity Catalog volume so the
Databricks Auto Loader in the platform_metrics bundle can ingest them.

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
import re
import sys
import urllib.parse
from datetime import UTC, datetime

import urllib3

http = urllib3.PoolManager(retries=urllib3.Retry(total=3, backoff_factor=0.5))

ACCOUNTS_HOST = "https://accounts.cloud.databricks.com"

# Medallion tier keywords, English and Norwegian. Matched as whole tokens of
# the identifier (split on non-alphanumerics), so "bronze_default" and
# "salg_gull" match while "resolver" does not match "solv".
MEDALLION_TIERS: dict[str, tuple[str, ...]] = {
    "bronze": ("bronze", "bronse"),
    "silver": ("silver", "sølv", "solv", "soelv"),
    "gold": ("gold", "gull"),
}
TIER_NA = "na"  # tables with no tier keyword in table or schema name

# Vendor/system catalogs that say nothing about platform usage.
SKIPPED_CATALOGS = ("system", "__databricks_internal", "hive_metastore", "samples")

_IDENTIFIER_TOKENS = re.compile(r"[^a-z0-9æøå]+")


def medallion_tier(name: str) -> str | None:
    """Medallion tier signalled by an identifier's name, or None.

    The first tier (in bronze -> silver -> gold order) with a keyword present
    as a whole token wins, so e.g. "bronze_to_gold_sync" counts as bronze.
    """
    tokens = set(_IDENTIFIER_TOKENS.split(name.lower()))
    for tier, keywords in MEDALLION_TIERS.items():
        if tokens.intersection(keywords):
            return tier
    return None


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


def _get_uc_paginated(
    url: str, token: str, items_key: str, params: dict | None = None
) -> list:
    """Paginate a Unity Catalog list endpoint, including BROWSE-only objects.

    ``include_browse=true`` matters: the collector SP typically holds BROWSE
    (not USE) on other teams' catalogs, and without the flag the API silently
    omits everything the SP can only browse — which reads as "zero tables".
    """
    all_items: list = []
    page_params: dict = {
        **(params or {}),
        "max_results": "100",
        "include_browse": "true",
    }
    while True:
        data = _get(url, token, page_params)
        all_items.extend(data.get(items_key, []))
        next_token = data.get("next_page_token")
        if not next_token:
            break
        page_params["page_token"] = next_token
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


def _list_directory(workspace_url: str, token: str, path: str) -> list[dict]:
    """List a volume directory via the Files API (paginated)."""
    entries: list = []
    params: dict = {"page_size": "1000"}
    url = f"{workspace_url}/api/2.0/fs/directories{path}"
    while True:
        data = _get(url, token, params)
        entries.extend(data.get("contents", []))
        next_token = data.get("next_page_token")
        if not next_token:
            break
        params["page_token"] = next_token
    return entries


def count_tables_by_tier(
    workspace_url: str, token: str, errors: list[str]
) -> dict[str, int | None]:
    """Count tables per medallion tier, plus data-product volume folders.

    All schemas in all user catalogs are inventoried (not just schemas with a
    tier keyword). Per table, the tier is resolved as:
    1. tier keyword in the table's own name (English or Norwegian), else
    2. the tier inherited from its schema's name, else
    3. "na".
    The "total" entry is the sum of all four groups. Views, materialized
    views, and streaming tables count too — they are the medallion artifacts
    DLT produces. Each catalog's ``information_schema`` is skipped so its
    system views don't inflate the n/a group.

    Volume folders: some teams ship data products as FOLDERS in a volume
    (e.g. dig_eksempelteam_prod_green.gold_default's volume). Every volume in
    every schema is inventoried; each top-level folder is counted into
    ``silver_folders`` / ``gold_folders`` with the usual tier resolution:
    folder name, else volume name, else the schema's tier. Folders resolving
    to bronze/na are not data products and are skipped. Listing folders is a
    DATA-plane read: it requires USE CATALOG + USE SCHEMA + READ VOLUME,
    granted catalog-wide by padda-iac.

    Counts are None when they could not be fully collected, so a transient
    failure is not silently reported as zero. Because an object name can
    override its container's tier, a failed schema or catalog listing makes
    every count unknown; a failed volume/folder listing only nullifies the
    two folder counts (table counts stay). Failures are appended to
    ``errors``.
    """
    counts: dict[str, int] = {tier: 0 for tier in (*MEDALLION_TIERS, TIER_NA)}
    folder_counts: dict[str, int] = {"silver_folders": 0, "gold_folders": 0}
    all_unknown = dict.fromkeys((*counts, "total", *folder_counts))
    tables_incomplete = False
    folders_incomplete = False
    try:
        catalogs = _get_uc_paginated(
            f"{workspace_url}/api/2.1/unity-catalog/catalogs", token, "catalogs"
        )
    except RuntimeError as exc:
        print(f"  Warning: could not list catalogs for {workspace_url}: {exc}")
        errors.append(f"catalogs: {exc}")
        return all_unknown

    for catalog in catalogs:
        catalog_name = catalog["name"]
        if catalog_name in SKIPPED_CATALOGS:
            continue
        try:
            schemas = _get_uc_paginated(
                f"{workspace_url}/api/2.1/unity-catalog/schemas",
                token,
                "schemas",
                {"catalog_name": catalog_name},
            )
        except RuntimeError as exc:
            errors.append(f"schemas[{catalog_name}]: {exc}")
            tables_incomplete = True
            folders_incomplete = True
            continue

        for schema in schemas:
            if schema["name"] == "information_schema":
                continue
            schema_tier = medallion_tier(schema["name"])
            try:
                tables = _get_uc_paginated(
                    f"{workspace_url}/api/2.1/unity-catalog/tables",
                    token,
                    "tables",
                    {"catalog_name": catalog_name, "schema_name": schema["name"]},
                )
            except RuntimeError as exc:
                errors.append(f"tables[{catalog_name}.{schema['name']}]: {exc}")
                tables_incomplete = True
                continue
            for table in tables:
                tier = medallion_tier(table.get("name", "")) or schema_tier or TIER_NA
                counts[tier] += 1

            schema_full = f"{catalog_name}.{schema['name']}"
            try:
                volumes = _get_uc_paginated(
                    f"{workspace_url}/api/2.1/unity-catalog/volumes",
                    token,
                    "volumes",
                    {"catalog_name": catalog_name, "schema_name": schema["name"]},
                )
            except RuntimeError as exc:
                errors.append(f"volumes[{schema_full}]: {exc}")
                folders_incomplete = True
                continue
            for volume in volumes:
                volume_name = volume.get("name", "")
                volume_tier = medallion_tier(volume_name) or schema_tier
                path = f"/Volumes/{catalog_name}/{schema['name']}/{volume_name}"
                try:
                    entries = _list_directory(workspace_url, token, path)
                except RuntimeError as exc:
                    errors.append(f"folders[{schema_full}.{volume_name}]: {exc}")
                    folders_incomplete = True
                    continue
                for entry in entries:
                    if not entry.get("is_directory"):
                        continue
                    tier = medallion_tier(entry.get("name", "")) or volume_tier
                    if tier in ("silver", "gold"):
                        folder_counts[f"{tier}_folders"] += 1

    result: dict[str, int | None] = (
        dict.fromkeys((*counts, "total"))
        if tables_incomplete
        else {**counts, "total": sum(counts.values())}
    )
    result.update(
        dict.fromkeys(folder_counts)
        if tables_incomplete or folders_incomplete
        else folder_counts
    )
    return result


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
        table_counts = count_tables_by_tier(workspace_url, account_token, errors)

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
            "num_na_tables": table_counts[TIER_NA],
            "num_tables": table_counts["total"],
            # Data products shipped as folders in silver/gold-tier volumes.
            "num_silver_volume_folders": table_counts["silver_folders"],
            "num_gold_volume_folders": table_counts["gold_folders"],
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
