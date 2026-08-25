"""Collect AWS cost per cost-allocation tag from Cost Explorer.

Queries the current AWS account's Cost Explorer (daily granularity, lookback
window with overlap) in two breakdowns:

  team_process — TAG:CostTeam x TAG:CostProcess (the core allocation view)
  service_team — DIMENSION:SERVICE x TAG:CostTeam (what services cost per team)

and uploads the rows as JSONL to the environment's Unity Catalog landing
volume, next to the workspace_inventory and dora collections. Because the
lookback windows of consecutive runs overlap (late-arriving cost data means
recent days keep changing), the downstream silver table must deduplicate on
(account, breakdown, date, cost_team, cost_process, service) keeping the
latest collection_timestamp — same pattern as dora_events.

Untagged usage surfaces as tag value "untagged"; costs only carry tag values
for usage after the tags were activated as cost-allocation tags in AWS Billing.

Auth: AWS credentials come ambient from aws-actions/configure-aws-credentials
(GitHub OIDC -> metrics-cost-reader role, read-only Cost Explorer). The upload
uses a Databricks account token federated from the workflow's OIDC token
(RFC 8693 token exchange), same as collect_platform_metrics.py.
"""

import json
import os
import sys
import urllib.parse
from datetime import UTC, datetime, timedelta

import boto3
import urllib3

http = urllib3.PoolManager(retries=urllib3.Retry(total=3, backoff_factor=0.5))

ACCOUNTS_HOST = "https://accounts.cloud.databricks.com"

# Landing convention: /Volumes/<catalog>/landing_default/platform_events/<collection>/
LANDING_SCHEMA = "landing_default"
LANDING_VOLUME = "platform_events"
COLLECTION = "aws_cost"  # this collector's subdirectory

# Cost Explorer is a global API served only from us-east-1.
CE_REGION = "us-east-1"
CE_METRICS = ["UnblendedCost", "AmortizedCost"]
TAG_TEAM = "CostTeam"
TAG_PROCESS = "CostProcess"
DEFAULT_LOOKBACK_DAYS = 14


def collection_path(catalog: str) -> str:
    """Volume directory this collector uploads to."""
    return f"/Volumes/{catalog}/{LANDING_SCHEMA}/{LANDING_VOLUME}/{COLLECTION}"


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
            f"Databricks token exchange failed ({resp.status}): {resp.data.decode()}"
        )
    return json.loads(resp.data)["access_token"]


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


def _tag_value(raw: str) -> str:
    """Strip the "CostTeam$" prefix from a tag group key; empty value = untagged."""
    value = raw.split("$", 1)[1] if "$" in raw else raw
    return value or "untagged"


def query_cost(
    ce,
    start: str,
    end: str,
    breakdown: str,
    group_by: list[dict],
    account_label: str,
    aws_account_id: str,
    collected_at: str,
) -> list[dict]:
    """One paginated GetCostAndUsage query, flattened to JSONL-ready rows."""
    records: list[dict] = []
    next_token = None
    while True:
        kwargs = {
            "TimePeriod": {"Start": start, "End": end},
            "Granularity": "DAILY",
            "Metrics": CE_METRICS,
            "GroupBy": group_by,
        }
        if next_token:
            kwargs["NextPageToken"] = next_token
        resp = ce.get_cost_and_usage(**kwargs)
        for day in resp.get("ResultsByTime", []):
            date = day["TimePeriod"]["Start"]
            estimated = bool(day.get("Estimated", False))
            for group in day.get("Groups", []):
                keys = group["Keys"]
                metrics = group["Metrics"]
                record = {
                    "breakdown": breakdown,
                    "date": date,
                    "account": account_label,
                    "aws_account_id": aws_account_id,
                    "cost_team": None,
                    "cost_process": None,
                    "service": None,
                    "unblended_cost": float(metrics["UnblendedCost"]["Amount"]),
                    "amortized_cost": float(metrics["AmortizedCost"]["Amount"]),
                    "currency": metrics["UnblendedCost"]["Unit"],
                    "estimated": estimated,
                    "collection_timestamp": collected_at,
                }
                if breakdown == "team_process":
                    record["cost_team"] = _tag_value(keys[0])
                    record["cost_process"] = _tag_value(keys[1])
                else:  # service_team
                    record["service"] = keys[0] or "unknown"
                    record["cost_team"] = _tag_value(keys[1])
                records.append(record)
        next_token = resp.get("NextPageToken")
        if not next_token:
            return records


def main() -> int:
    # Single environment per run. The workflow invokes this once per GitHub
    # environment (dev, prod); the vars resolve to that environment's own
    # Databricks account and catalog, and the ambient AWS credentials to that
    # environment's AWS account.
    account_id = (os.environ.get("DATABRICKS_ACCOUNT_ID") or "").strip()
    client_id = (os.environ.get("DATABRICKS_CLIENT_ID") or "").strip()
    oidc_token = (os.environ.get("DATABRICKS_OIDC_TOKEN") or "").strip()
    workspace_host = (os.environ.get("DATABRICKS_HOST") or "").strip()
    catalog = (os.environ.get("DATABRICKS_METRICS_CATALOG") or "").strip()
    account_label = (os.environ.get("ACCOUNT_LABEL") or "unknown").strip()

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

    try:
        lookback_days = max(
            1, int(os.environ.get("LOOKBACK_DAYS", DEFAULT_LOOKBACK_DAYS))
        )
    except ValueError:
        print("LOOKBACK_DAYS must be an integer", file=sys.stderr)
        return 1

    now = datetime.now(UTC)
    collected_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    # End is exclusive in Cost Explorer, so today's (partial) data is excluded.
    end = now.date().isoformat()
    start = (now.date() - timedelta(days=lookback_days)).isoformat()

    aws_account_id = boto3.client("sts").get_caller_identity()["Account"]
    ce = boto3.client("ce", region_name=CE_REGION)

    print(
        f"Collecting AWS cost for account {aws_account_id} ({account_label}), "
        f"{start} to {end} (exclusive)"
    )
    records = query_cost(
        ce,
        start,
        end,
        "team_process",
        [
            {"Type": "TAG", "Key": TAG_TEAM},
            {"Type": "TAG", "Key": TAG_PROCESS},
        ],
        account_label,
        aws_account_id,
        collected_at,
    )
    records += query_cost(
        ce,
        start,
        end,
        "service_team",
        [
            {"Type": "DIMENSION", "Key": "SERVICE"},
            {"Type": "TAG", "Key": TAG_TEAM},
        ],
        account_label,
        aws_account_id,
        collected_at,
    )

    if not records:
        print("No cost records returned")
        return 0

    print(
        f"Authenticating to {account_label} Databricks account "
        f"({account_id}) via GitHub OIDC"
    )
    token = get_account_token(account_id, client_id, oidc_token)

    filename = f"aws-cost-{now.strftime('%Y%m%dT%H%M%SZ')}.jsonl"
    body = "\n".join(json.dumps(r, ensure_ascii=False) for r in records).encode("utf-8")
    uri = upload_to_volume(
        workspace_host, token, collection_path(catalog), filename, body
    )
    print(f"Uploaded {len(records)} cost records to {uri}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
