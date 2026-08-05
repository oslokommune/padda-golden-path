"""Collect DORA events from the current GitHub repo.

Fetches PRs merged in the lookback window and computes the two DORA
signals derivable from GitHub alone:

  * deployment: every merge to the default branch is one deployment
  * lead_time_seconds: time from the PR's first commit to merge_commit

Uploads JSONL to a Unity Catalog volume so the Databricks Auto Loader in
the platform_metrics bundle (in padda-databrikker) can ingest it.

Designed to be copied unchanged to each platform repo's
.github/scripts/ directory. Each repo's workflow handles its own merged
PRs — no cross-repo token plumbing.

Auth: GitHub OIDC federation (RFC 8693 token-exchange). The workflow mints an
OIDC token with the Databricks account as audience and passes it in; client_id
selects the collector SP, whose federation policy in padda-iac authorizes the
exchange. No stored secret.

Single environment per run. The workflow runs this once per GitHub environment
(dev, prod); each run uploads the repo's events to that environment's own
landing volume. Only the catalog varies the path — the rest follows
LANDING_SCHEMA / LANDING_VOLUME / COLLECTION below.

Required environment variables:
  GITHUB_TOKEN                Workflow's built-in token (default in GH Actions)
  GITHUB_REPOSITORY           Set automatically by GitHub Actions
  DATABRICKS_ACCOUNT_ID       Databricks account ID for this environment
  DATABRICKS_CLIENT_ID        Collector SP application id (selects the SP; not secret)
  DATABRICKS_OIDC_TOKEN       GitHub OIDC JWT (audience = the account ID)
  DATABRICKS_HOST             Workspace host hosting this environment's volume
  DATABRICKS_METRICS_CATALOG  Catalog (padda_dev_green / dig_databrikker_stage_green)
"""

import json
import os
import sys
from datetime import UTC, datetime, timedelta

import urllib3

http = urllib3.PoolManager(retries=urllib3.Retry(total=3, backoff_factor=0.5))

GITHUB_API = "https://api.github.com"
ACCOUNTS_HOST = "https://accounts.cloud.databricks.com"

DEFAULT_LOOKBACK_DAYS = 7

# Landing-zone layout (same convention as collect_platform_metrics.py). One
# volume per environment, one subdirectory per collection. Only the catalog
# varies per environment.
#   /Volumes/<catalog>/<LANDING_SCHEMA>/<LANDING_VOLUME>/<COLLECTION>/
LANDING_SCHEMA = "landing_default"
LANDING_VOLUME = "platform_events"
COLLECTION = "dora"  # this collector's subdirectory


def collection_path(catalog: str) -> str:
    """Landing-volume path for this collection in the given catalog."""
    return f"/Volumes/{catalog}/{LANDING_SCHEMA}/{LANDING_VOLUME}/{COLLECTION}"


# ---------------------------------------------------------------------------
# GitHub OIDC -> Databricks token federation (RFC 8693 token-exchange)
# ---------------------------------------------------------------------------


def get_databricks_token(account_id: str, client_id: str, oidc_token: str) -> str:
    """Federate a GitHub OIDC token into a Databricks account-level token.

    RFC 8693 token exchange: the GitHub Actions OIDC JWT is the subject_token;
    client_id selects the collector SP, whose federation policy in padda-iac
    authorizes the exchange. No stored secret.
    """
    import urllib.parse

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
# GitHub helpers
# ---------------------------------------------------------------------------


def _gh_get(url: str, token: str, params: dict | None = None) -> dict | list:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    resp = http.request("GET", url, headers=headers, timeout=30)
    if resp.status != 200:
        raise RuntimeError(f"GET {url} failed ({resp.status}): {resp.data.decode()}")
    return json.loads(resp.data.decode())


def fetch_merged_prs(repo: str, since_iso: str, token: str) -> list[dict]:
    """List PRs merged on/after since_iso, sorted by merge time descending."""
    query = f"repo:{repo}+is:pr+is:merged+merged:>={since_iso}"
    url = f"{GITHUB_API}/search/issues?q={query}&per_page=100&sort=updated&order=desc"
    data = _gh_get(url, token)
    return data.get("items", [])


def fetch_pr_detail(repo: str, number: int, token: str) -> dict:
    return _gh_get(f"{GITHUB_API}/repos/{repo}/pulls/{number}", token)


def fetch_default_branch(repo: str, token: str) -> str:
    return _gh_get(f"{GITHUB_API}/repos/{repo}", token)["default_branch"]


def fetch_pr_first_commit_at(repo: str, number: int, token: str) -> str | None:
    commits = _gh_get(
        f"{GITHUB_API}/repos/{repo}/pulls/{number}/commits",
        token,
        params={"per_page": "100"},
    )
    if not commits:
        return None
    timestamps = [
        c.get("commit", {}).get("author", {}).get("date")
        for c in commits
        if c.get("commit", {}).get("author", {}).get("date")
    ]
    return min(timestamps) if timestamps else None


def build_event(
    repo: str, pr: dict, first_commit_at: str | None, collection_ts: str
) -> dict:
    merged_at = pr.get("merged_at")
    lead_time_seconds = None
    if merged_at and first_commit_at:
        merge_dt = datetime.fromisoformat(merged_at.replace("Z", "+00:00"))
        first_dt = datetime.fromisoformat(first_commit_at.replace("Z", "+00:00"))
        lead_time_seconds = int((merge_dt - first_dt).total_seconds())
    return {
        "collection_timestamp": collection_ts,
        "repo": repo,
        "pr_number": pr["number"],
        "pr_title": pr.get("title", ""),
        "merged_at": merged_at,
        "first_commit_at": first_commit_at,
        "lead_time_seconds": lead_time_seconds,
        "merge_commit_sha": pr.get("merge_commit_sha"),
        "author": (pr.get("user") or {}).get("login"),
        "base_ref": (pr.get("base") or {}).get("ref"),
    }


def collect_repo(
    repo: str, since_iso: str, collection_ts: str, token: str
) -> list[dict]:
    prs = fetch_merged_prs(repo, since_iso, token)
    default_branch = fetch_default_branch(repo, token)
    events: list[dict] = []
    for pr in prs:
        detail = fetch_pr_detail(repo, pr["number"], token)
        if (detail.get("base") or {}).get("ref") != default_branch:
            continue
        first_commit_at = fetch_pr_first_commit_at(repo, pr["number"], token)
        events.append(build_event(repo, detail, first_commit_at, collection_ts))
    return events


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
    # .strip() guards against trailing whitespace/newlines in GitHub vars,
    # which otherwise corrupt the client_id / account_id sent to Databricks.
    repo = (os.environ.get("GITHUB_REPOSITORY") or "").strip()
    github_token = (os.environ.get("GITHUB_TOKEN") or "").strip()
    account_id = (os.environ.get("DATABRICKS_ACCOUNT_ID") or "").strip()
    client_id = (os.environ.get("DATABRICKS_CLIENT_ID") or "").strip()
    oidc_token = (os.environ.get("DATABRICKS_OIDC_TOKEN") or "").strip()
    workspace_host = (os.environ.get("DATABRICKS_HOST") or "").strip()
    catalog = (os.environ.get("DATABRICKS_METRICS_CATALOG") or "").strip()

    missing = [
        name
        for name, val in [
            ("GITHUB_REPOSITORY", repo),
            ("GITHUB_TOKEN", github_token),
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

    lookback_days = int(os.environ.get("LOOKBACK_DAYS", DEFAULT_LOOKBACK_DAYS))
    now = datetime.now(UTC)
    since_iso = (now - timedelta(days=lookback_days)).date().isoformat()
    collection_ts = now.strftime("%Y%m%dT%H%M%SZ")

    print(f"Collecting DORA events from {repo} (since {since_iso})", flush=True)
    events = collect_repo(repo, since_iso, collection_ts, github_token)
    print(f"  {len(events)} merged PRs", flush=True)

    if not events:
        print("Nothing to upload.")
        return 0

    body = ("\n".join(json.dumps(e, ensure_ascii=False) for e in events) + "\n").encode(
        "utf-8"
    )
    repo_slug = repo.replace("/", "_")
    filename = f"dora-{repo_slug}-{collection_ts}.jsonl"

    print(
        f"Authenticating to Databricks (account {account_id}) via GitHub OIDC",
        flush=True,
    )
    token = get_databricks_token(account_id, client_id, oidc_token)
    uri = upload_to_volume(
        workspace_host, token, collection_path(catalog), filename, body
    )
    print(f"Uploaded {len(events)} events to {uri}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
