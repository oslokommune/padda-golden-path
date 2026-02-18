#!/usr/bin/env python3
"""
SAT workspace setup — runs locally to configure workspace_configs.csv.

Calls the Databricks Accounts API (unreachable from SRA/isolated clusters)
to discover workspaces and test connections, then writes the config that the
SAT bundle jobs need at runtime.

Usage:
    # All workspaces in the account (auto-discover):
    python setup_workspaces.py --account-id <ACCOUNT_ID>

    # Specific workspaces only:
    python setup_workspaces.py --account-id <ACCOUNT_ID> \
        --workspace-ids 2727440053493594 1234567890123456

    # Skip connection tests (faster, marks all as connected):
    python setup_workspaces.py --account-id <ACCOUNT_ID> --skip-connection-test

    # Override Databricks host for accounts API (e.g. GovCloud):
    python setup_workspaces.py --account-id <ACCOUNT_ID> \
        --accounts-host https://accounts.cloud.databricks.us

Prerequisites:
    pip install databricks-sdk

Authentication:
    Uses standard Databricks unified auth (env vars, ~/.databrickscfg, or CLI).
    Needs account-level credentials. Set one of:
      - DATABRICKS_HOST + DATABRICKS_TOKEN (account-level PAT)
      - DATABRICKS_HOST + DATABRICKS_CLIENT_ID + DATABRICKS_CLIENT_SECRET (OAuth SP)
      - Databricks CLI profile: databricks auth login --account-id <ACCOUNT_ID>
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Optional

from databricks.sdk import AccountClient, WorkspaceClient
from databricks.sdk.config import Config


CONFIGS_DIR = Path(__file__).parent / "configs"
OUTPUT_CSV = CONFIGS_DIR / "workspace_configs.csv"

CSV_COLUMNS = [
    "workspace_id",
    "deployment_url",
    "workspace_name",
    "workspace_status",
    "sso_enabled",
    "scim_enabled",
    "vpc_peering_done",
    "object_storage_encrypted",
    "table_access_control_enabled",
    "connection_test",
    "analysis_enabled",
]


def get_account_client(
    account_id: str,
    accounts_host: Optional[str] = None,
) -> AccountClient:
    """Create an account-level Databricks client."""
    kwargs = {"account_id": account_id}
    if accounts_host:
        kwargs["host"] = accounts_host
    return AccountClient(**kwargs)


def list_workspaces(
    acct_client: AccountClient,
    workspace_ids: Optional[list[str]] = None,
) -> list[dict]:
    """Fetch workspaces from the Accounts API."""
    print("Fetching workspaces from Accounts API...")
    all_ws = list(acct_client.workspaces.list())
    print(f"  Found {len(all_ws)} workspace(s) in account")

    workspaces = []
    for ws in all_ws:
        if ws.workspace_status_message and "RUNNING" not in str(ws.workspace_status):
            continue
        if workspace_ids and str(ws.workspace_id) not in workspace_ids:
            continue
        workspaces.append(ws)

    if workspace_ids:
        found = {str(ws.workspace_id) for ws in workspaces}
        missing = set(workspace_ids) - found
        if missing:
            print(f"  WARNING: Workspace IDs not found: {missing}")

    print(f"  Selected {len(workspaces)} running workspace(s)")
    return workspaces


def test_workspace_connection(deployment_url: str) -> bool:
    """Test connectivity to a workspace by listing Spark versions."""
    try:
        ws_url = f"https://{deployment_url}"
        ws_client = WorkspaceClient(host=ws_url)
        ws_client.clusters.spark_versions()
        return True
    except Exception as e:
        print(f"    Connection failed: {e}")
        return False


def build_workspace_row(ws, cloud_type: str, connection_test: bool) -> dict:
    """Build a CSV row dict from a workspace object."""
    return {
        "workspace_id": str(ws.workspace_id),
        "deployment_url": ws.deployment_name,
        "workspace_name": ws.workspace_name,
        "workspace_status": str(ws.workspace_status).replace("WorkspaceStatus.", ""),
        "sso_enabled": str(cloud_type in ("azure", "gcp")),
        "scim_enabled": "False",
        "vpc_peering_done": "False",
        "object_storage_encrypted": "True",
        "table_access_control_enabled": "False",
        "connection_test": str(connection_test),
        "analysis_enabled": "True",
    }


def detect_cloud_type(deployment_name: str) -> str:
    """Detect cloud from deployment URL pattern."""
    if ".azuredatabricks." in deployment_name:
        return "azure"
    elif ".gcp.databricks." in deployment_name:
        return "gcp"
    return "aws"


def write_csv(rows: list[dict]) -> None:
    """Write workspace config CSV."""
    CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWritten {len(rows)} workspace(s) to {OUTPUT_CSV}")


def main():
    parser = argparse.ArgumentParser(
        description="SAT workspace setup — discover and configure workspaces for SAT analysis.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--account-id",
        required=True,
        help="Databricks Account ID (UUID from Account Console)",
    )
    parser.add_argument(
        "--workspace-ids",
        nargs="+",
        default=None,
        help="Only include these workspace IDs (space-separated). "
        "Omit to include all running workspaces.",
    )
    parser.add_argument(
        "--skip-connection-test",
        action="store_true",
        help="Skip workspace connection tests (marks all as connected)",
    )
    parser.add_argument(
        "--accounts-host",
        default=None,
        help="Accounts API host URL (default: auto-detect from auth config). "
        "Override for GovCloud: https://accounts.cloud.databricks.us",
    )
    args = parser.parse_args()

    # 1. Connect to Accounts API
    acct_client = get_account_client(args.account_id, args.accounts_host)

    # 2. List workspaces
    workspaces = list_workspaces(acct_client, args.workspace_ids)
    if not workspaces:
        print("ERROR: No workspaces found. Check account ID and credentials.")
        sys.exit(1)

    # 3. Test connections and build rows
    rows = []
    for ws in workspaces:
        deployment_url = ws.deployment_name
        cloud_type = detect_cloud_type(deployment_url or "")
        print(f"\n  [{ws.workspace_id}] {ws.workspace_name} ({deployment_url})")

        if args.skip_connection_test:
            connected = True
            print("    Connection test: SKIPPED (--skip-connection-test)")
        else:
            print("    Testing connection...", end=" ", flush=True)
            connected = test_workspace_connection(deployment_url)
            status = "OK" if connected else "FAILED"
            print(status)

        rows.append(build_workspace_row(ws, cloud_type, connected))

    # 4. Write CSV
    write_csv(rows)

    # 5. Summary
    connected_count = sum(1 for r in rows if r["connection_test"] == "True")
    print(f"\nSummary: {connected_count}/{len(rows)} workspace(s) connected")
    print("\nNext steps:")
    print("  databricks bundle deploy --target dev")
    print("  databricks bundle run sat_initializer --target dev")


if __name__ == "__main__":
    main()
