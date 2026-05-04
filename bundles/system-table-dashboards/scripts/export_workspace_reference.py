#!/usr/bin/env python3
"""Export or verify workspace display-name mappings for the dashboard bundle."""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path


DEFAULT_ACCOUNT_HOST = "https://accounts.cloud.databricks.com/"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "data" / "workspace_reference.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write data/workspace_reference.csv from the Databricks account API, "
            "or verify that the existing CSV matches account workspace names."
        )
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="CSV path to write or check. Defaults to bundle data/workspace_reference.csv.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the CSV instead of writing it.",
    )
    parser.add_argument(
        "--account-host",
        default=os.getenv("DATABRICKS_ACCOUNT_HOST", DEFAULT_ACCOUNT_HOST),
        help="Databricks account console host.",
    )
    parser.add_argument(
        "--account-id",
        default=os.getenv("DATABRICKS_ACCOUNT_ID"),
        help="Databricks account ID. Can also be set with DATABRICKS_ACCOUNT_ID.",
    )
    parser.add_argument(
        "--profile",
        default=os.getenv("DATABRICKS_CONFIG_PROFILE"),
        help=(
            "Databricks CLI profile to use for account authentication. Can also "
            "be set with DATABRICKS_CONFIG_PROFILE."
        ),
    )
    parser.add_argument(
        "--client-id",
        default=os.getenv("DATABRICKS_CLIENT_ID"),
        help="Account service principal client ID. Can also be set with DATABRICKS_CLIENT_ID.",
    )
    parser.add_argument(
        "--client-secret",
        default=os.getenv("DATABRICKS_CLIENT_SECRET"),
        help=(
            "Account service principal client secret. Can also be set with "
            "DATABRICKS_CLIENT_SECRET."
        ),
    )
    return parser.parse_args()


def account_client(args: argparse.Namespace):
    try:
        from databricks.sdk import AccountClient
    except ImportError as exc:
        raise SystemExit(
            "databricks-sdk is required. Install it locally with: "
            "python -m pip install databricks-sdk"
        ) from exc

    if args.profile:
        if not args.account_id:
            raise SystemExit(
                "Missing required --account-id when using --profile. "
                "The profile must authenticate to the account console, not a workspace."
            )
        return AccountClient(
            host=args.account_host,
            account_id=args.account_id,
            profile=args.profile,
        )

    missing = [
        name
        for name, value in {
            "--account-id": args.account_id,
            "--client-id": args.client_id,
            "--client-secret": args.client_secret,
        }.items()
        if not value
    ]
    if missing:
        raise SystemExit(
            f"Missing required account credentials: {', '.join(missing)}. "
            "Alternatively pass --profile for an account-authenticated CLI profile."
        )

    return AccountClient(
        host=args.account_host,
        account_id=args.account_id,
        client_id=args.client_id,
        client_secret=args.client_secret,
    )


def list_workspace_rows(client) -> list[dict[str, str]]:
    rows = [
        {
            "workspace_id": str(workspace.workspace_id),
            "workspace_name": workspace.workspace_name or str(workspace.workspace_id),
        }
        for workspace in client.workspaces.list()
    ]
    return sorted(rows, key=lambda row: row["workspace_id"])


def explain_databricks_error(exc: Exception) -> SystemExit:
    message = str(exc)
    if "Invalid Token" in message or "invalid_token" in message:
        return SystemExit(
            "Databricks account API rejected the token as invalid.\n"
            "\n"
            "Check that you are using account-level authentication, not a "
            "workspace-only token/client:\n"
            "- --account-id must be the Databricks account ID.\n"
            "- --client-id and --client-secret must belong to an account service "
            "principal with permission to list account workspaces.\n"
            "- If using --profile, the profile must authenticate against "
            "https://accounts.cloud.databricks.com/.\n"
            "\n"
            "You can also maintain data/workspace_reference.csv manually with "
            "columns: workspace_id,workspace_name."
        )

    return SystemExit(f"Failed to list Databricks account workspaces: {message}")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["workspace_id", "workspace_name"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} workspace mappings to {path}")


def read_csv(path: Path) -> dict[str, str]:
    if not path.exists():
        raise SystemExit(f"CSV does not exist: {path}")

    workspace_names = {}
    with path.open(newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        required_columns = {"workspace_id", "workspace_name"}
        if not required_columns.issubset(reader.fieldnames or []):
            raise SystemExit(
                f"{path} must contain columns: workspace_id, workspace_name"
            )

        for row in reader:
            workspace_id = row["workspace_id"].strip()
            workspace_name = row["workspace_name"].strip()
            if not workspace_id:
                continue
            if (
                workspace_id in workspace_names
                and workspace_names[workspace_id] != workspace_name
            ):
                raise SystemExit(
                    f"{path} has conflicting names for workspace_id {workspace_id}"
                )
            workspace_names[workspace_id] = workspace_name

    return workspace_names


def check_csv(path: Path, expected_rows: list[dict[str, str]]) -> None:
    actual = read_csv(path)
    expected = {row["workspace_id"]: row["workspace_name"] for row in expected_rows}

    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    mismatched = sorted(
        workspace_id
        for workspace_id in set(actual) & set(expected)
        if actual[workspace_id] != expected[workspace_id]
    )

    if missing or extra or mismatched:
        for workspace_id in missing:
            print(f"missing: {workspace_id},{expected[workspace_id]}")
        for workspace_id in extra:
            print(f"extra: {workspace_id},{actual[workspace_id]}")
        for workspace_id in mismatched:
            print(
                "mismatch: "
                f"{workspace_id}, csv={actual[workspace_id]!r}, "
                f"account={expected[workspace_id]!r}"
            )
        raise SystemExit(1)

    print(f"CSV is up to date: {path}")


def main() -> int:
    args = parse_args()
    try:
        rows = list_workspace_rows(account_client(args))
    except Exception as exc:
        raise explain_databricks_error(exc) from None

    if args.check:
        check_csv(args.output, rows)
    else:
        write_csv(args.output, rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
