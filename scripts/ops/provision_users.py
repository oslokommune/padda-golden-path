"""Provision Databricks account users into a single account group.

Additive and idempotent: creates the user and the group if missing, ensures
group membership, and never removes anything. Dry-run by default; pass --apply
to write. Select the target account with --profile (SDK unified auth).

# Example:
#   DATABRICKS_ACCOUNT_ID= paddapaddapadda uv run --extra tools \
#     python scripts/ops/provision_users.py \
#       --profile prod-acct \
#       --user store.padda@oslo.kommune.no --user lille.padda@oslo.kommune.no \
#       --group DS-DIG_PADDA_WORKSPACE_ADMINS \
#       --apply
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass

from databricks.sdk import AccountClient
from databricks.sdk.service import iam

ACCOUNT_ID = os.environ.get("DATABRICKS_ACCOUNT_ID")


@dataclass
class GroupOutcome:
    name: str
    action: str  # "existed" | "created" | "would-create"
    group_id: str | None


@dataclass
class UserOutcome:
    user_name: str
    user_action: str  # "existed" | "created" | "would-create" | "failed"
    membership_action: str  # "added" | "already-member" | "would-add" | "skipped"
    error: str | None = None


def find_group(client: AccountClient, name: str):
    return next(iter(client.groups.list(filter=f'displayName eq "{name}"')), None)


def ensure_group(client: AccountClient, name: str, apply: bool) -> GroupOutcome:
    group = find_group(client, name)
    if group is not None:
        return GroupOutcome(name, "existed", group.id)
    if not apply:
        return GroupOutcome(name, "would-create", None)
    created = client.groups.create(display_name=name)
    return GroupOutcome(name, "created", created.id)


def find_user(client: AccountClient, user_name: str):
    return next(iter(client.users.list(filter=f'userName eq "{user_name}"')), None)


def ensure_user(
    client: AccountClient, user_name: str, apply: bool
) -> tuple[str | None, str]:
    user = find_user(client, user_name)
    if user is not None:
        return user.id, "existed"
    if not apply:
        return None, "would-create"
    display_name = user_name.split("@", 1)[0]
    created = client.users.create(user_name=user_name, display_name=display_name)
    return created.id, "created"


def group_member_ids(client: AccountClient, group_id: str) -> set[str]:
    group = client.groups.get(id=group_id)
    return {m.value for m in (group.members or [])}


def decide_membership(
    client: AccountClient,
    group: GroupOutcome,
    user_id: str | None,
    member_ids: set[str],
    apply: bool,
) -> str:
    # Group or user does not exist yet (dry-run create) -> only a future add.
    if group.group_id is None or user_id is None:
        return "would-add"
    if user_id in member_ids:
        return "already-member"
    if not apply:
        return "would-add"
    client.groups.patch(
        id=group.group_id,
        operations=[
            iam.Patch(op=iam.PatchOp.ADD, path="members", value=[{"value": user_id}])
        ],
        schemas=[iam.PatchSchema.URN_IETF_PARAMS_SCIM_API_MESSAGES_2_0_PATCH_OP],
    )
    member_ids.add(user_id)
    return "added"


def provision(
    client: AccountClient,
    user_names: list[str],
    group_name: str,
    apply: bool,
) -> tuple[GroupOutcome, list[UserOutcome]]:
    group = ensure_group(client, group_name, apply)
    member_ids = group_member_ids(client, group.group_id) if group.group_id else set()
    results: list[UserOutcome] = []
    for user_name in user_names:
        try:
            user_id, user_action = ensure_user(client, user_name, apply)
            membership_action = decide_membership(
                client, group, user_id, member_ids, apply
            )
            results.append(UserOutcome(user_name, user_action, membership_action))
        except Exception as exc:  # report the failure and continue with the rest
            results.append(UserOutcome(user_name, "failed", "skipped", error=str(exc)))
    return group, results


def compute_exit_code(results: list[UserOutcome]) -> int:
    return 1 if any(r.user_action == "failed" for r in results) else 0


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Add Databricks account users to a group (create if missing).",
    )
    parser.add_argument(
        "--user",
        action="append",
        dest="users",
        required=True,
        metavar="EMAIL",
        help="User to provision (repeatable).",
    )
    parser.add_argument(
        "--group", required=True, help="Target account group displayName."
    )
    parser.add_argument(
        "--profile",
        default=None,
        help="Databricks config profile (account-level). Default: SDK unified auth.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform changes. Without it, runs a dry-run.",
    )
    parser.add_argument(
        "--yes", action="store_true", help="Skip the interactive prod confirmation."
    )
    return parser


def make_client(profile: str | None) -> AccountClient:
    return AccountClient(profile=profile) if profile else AccountClient()


def is_prod(client: AccountClient) -> bool:
    return client.config.account_id == ACCOUNT_ID


def confirm_prod(client: AccountClient, apply: bool, yes: bool, input_fn=input) -> bool:
    if apply and is_prod(client) and not yes:
        prompt = (
            f"About to APPLY to PROD account {client.config.account_id}."
            " Type 'yes' to continue: "
        )
        answer = input_fn(prompt)
        return answer.strip() == "yes"
    return True


def render(group: GroupOutcome, results: list[UserOutcome], apply: bool) -> str:
    lines = [] if apply else ["DRY-RUN (no --apply)"]
    lines.append(f"group  {group.name}  : {group.action}")
    for r in results:
        detail = f"{r.user_action} / {r.membership_action}"
        if r.error:
            detail += f"  ERROR: {r.error}"
        lines.append(f"user   {r.user_name}  : {detail}")
    created = sum(1 for r in results if r.user_action in ("created", "would-create"))
    added = sum(1 for r in results if r.membership_action in ("added", "would-add"))
    failed = sum(1 for r in results if r.user_action == "failed")
    summary = (
        f"Summary: {len(results)} users"
        f" · {created} create · {added} add · {failed} failed"
    )
    lines.append(summary)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    client = make_client(args.profile)
    if not client.config.account_id:
        print(
            "Error: resolved credentials are not account-level (no account_id). "
            "Use an account-level profile/host (accounts.cloud.databricks.com).",
            file=sys.stderr,
        )
        return 2
    if not confirm_prod(client, args.apply, args.yes):
        print("Aborted.")
        return 2
    group, results = provision(client, args.users, args.group, args.apply)
    print(render(group, results, args.apply))
    return compute_exit_code(results)


if __name__ == "__main__":
    sys.exit(main())
