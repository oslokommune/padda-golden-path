#!/usr/bin/env python3
"""Generate nav section for Notion pages (fetched via API if configured)."""

import os
import re
from collections.abc import Iterable
from pathlib import Path

try:
    from ruamel.yaml import YAML

    def load_yaml(stream):
        yaml = YAML()
        yaml.preserve_quotes = True
        return yaml.load(stream)

    def dump_yaml(data, stream):
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.width = 4096
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.dump(data, stream)

except ImportError:
    import functools
    import types

    import yaml

    def load_yaml(stream):
        import mermaid2  # noqa: F401 - needed for yaml python/name tags

        return yaml.full_load(stream)

    class PythonNameDumper(yaml.SafeDumper):
        """Allow emitting python/name tags when ruamel.yaml is unavailable."""

    def _represent_python_name(dumper, obj):
        module = getattr(obj, "__module__", None)
        name = getattr(obj, "__name__", None)
        if isinstance(obj, functools.partial):
            module = getattr(obj.func, "__module__", module)
            name = name or getattr(obj.func, "__name__", None)
        if module and name:
            tag = f"tag:yaml.org,2002:python/name:{module}.{name}"
            return yaml.nodes.ScalarNode(tag=tag, value="")
        return dumper.represent_scalar("tag:yaml.org,2002:str", str(obj))

    PythonNameDumper.add_representer(types.FunctionType, _represent_python_name)
    PythonNameDumper.add_representer(functools.partial, _represent_python_name)

    def dump_yaml(data, stream):
        yaml.dump(
            data,
            stream,
            Dumper=PythonNameDumper,
            default_flow_style=False,
            allow_unicode=True,
        )


docs_dir = Path("docs")
mkdocs_file = Path("mkdocs.yml")
notion_dir = Path(os.getenv("NOTION_OUTPUT_DIR", docs_dir / "notion"))
notion_index = notion_dir / "index.md"

NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
NOTION_PAGE_IDS = [
    p.strip() for p in os.getenv("NOTION_PAGE_IDS", "").split(",") if p.strip()
]
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")

# Lazy import requests to avoid failures when env vars are not set
requests = None
if NOTION_API_TOKEN and NOTION_PAGE_IDS:
    import requests  # type: ignore


def format_title(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").title()


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return slug or "page"


def plain_text(rich_text: list[dict]) -> str:
    parts: list[str] = []
    for item in rich_text:
        text = item.get("plain_text", "")
        ann = item.get("annotations", {}) or {}
        if ann.get("code"):
            text = f"`{text}`"
        if ann.get("bold"):
            text = f"**{text}**"
        if ann.get("italic"):
            text = f"*{text}*"
        if ann.get("strikethrough"):
            text = f"~~{text}~~"
        if item.get("href"):
            text = f"[{text}]({item['href']})"
        parts.append(text)
    return "".join(parts)


def fetch_blocks(session, block_id: str) -> list[dict]:
    blocks: list[dict] = []
    start_cursor = None
    while True:
        params = {"page_size": 100}
        if start_cursor:
            params["start_cursor"] = start_cursor
        resp = session.get(
            f"https://api.notion.com/v1/blocks/{block_id}/children",
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        blocks.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        start_cursor = data.get("next_cursor")
    return blocks


def fetch_page_title(session, page_id: str) -> str:
    resp = session.get(f"https://api.notion.com/v1/pages/{page_id}", timeout=30)
    resp.raise_for_status()
    data = resp.json()
    properties = data.get("properties", {}) or {}
    for prop in properties.values():
        if prop.get("type") == "title":
            title_rich = prop.get("title", [])
            if title_rich:
                return plain_text(title_rich)
    return page_id


def render_blocks(session, blocks: Iterable[dict], indent: int = 0) -> list[str]:
    lines: list[str] = []
    for block in blocks:
        block_type = block.get("type")
        data = block.get(block_type, {})
        prefix = "  " * indent
        text = plain_text(data.get("rich_text", []))

        if block_type in {"heading_1", "heading_2", "heading_3"}:
            level = {"heading_1": "#", "heading_2": "##", "heading_3": "###"}[
                block_type
            ]
            lines.append(f"{level} {text}".rstrip())
        elif block_type == "paragraph":
            if text:
                lines.append(prefix + text)
            lines.append("")
        elif block_type == "bulleted_list_item":
            lines.append(f"{prefix}- {text}")
        elif block_type == "numbered_list_item":
            lines.append(f"{prefix}1. {text}")
        elif block_type == "to_do":
            checked = data.get("checked", False)
            lines.append(f"{prefix}- [{'x' if checked else ' '}] {text}")
        elif block_type == "quote":
            lines.append(f"{prefix}> {text}")
        elif block_type == "callout":
            emoji = data.get("icon", {}).get("emoji", "💡")
            lines.append(f"{prefix}> {emoji} {text}")
        elif block_type == "code":
            language = data.get("language") or ""
            lines.append(f"{prefix}```{language}".rstrip())
            lines.append(data.get("rich_text", [{}])[0].get("plain_text", ""))
            lines.append(f"{prefix}```")
        elif block_type == "toggle":
            lines.append(f"{prefix}- {text}")
        elif block_type == "divider":
            lines.append(f"{prefix}---")
        else:
            if text:
                lines.append(f"{prefix}{text}")

        if block.get("has_children"):
            child_blocks = fetch_blocks(session, block["id"])
            lines.extend(render_blocks(session, child_blocks, indent + 1))

        if block_type in {
            "bulleted_list_item",
            "numbered_list_item",
            "to_do",
            "callout",
            "toggle",
        }:
            lines.append("")
    return lines


def fetch_notion_pages() -> list[tuple[str, Path]]:
    if not (NOTION_API_TOKEN and NOTION_PAGE_IDS):
        return []
    if requests is None:
        print("requests is not available; skipping Notion fetch.")
        return []

    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    })

    written: list[tuple[str, Path]] = []
    notion_dir.mkdir(parents=True, exist_ok=True)

    for page_id in NOTION_PAGE_IDS:
        try:
            title = fetch_page_title(session, page_id)
            slug = slugify(title)
            blocks = fetch_blocks(session, page_id)
            md_lines = render_blocks(session, blocks)
            path = notion_dir / f"{slug}.md"
            path.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
            written.append((title, path))
        except Exception as exc:  # pragma: no cover - best effort logging
            print(f"Failed to fetch Notion page {page_id}: {exc}")
    if written:
        print("Fetched Notion pages:")
        for title, path in written:
            print(f"- {title} -> {path}")
    else:
        print("No Notion pages were fetched.")
    return written


def collect_pages():
    if not notion_dir.exists():
        return [], []

    pages_for_nav = []
    index_entries = []

    def page_title(path: Path) -> str:
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.startswith("#"):
                    return line.lstrip("#").strip()
        except OSError:
            pass
        return format_title(path.stem)

    for path in sorted(notion_dir.rglob("*.md")):
        if path.name == "index.md":
            continue
        rel_parts = path.relative_to(notion_dir).parts
        nav_path = Path("notion") / Path(*rel_parts)
        title = page_title(path)
        index_entries.append((title, Path(*rel_parts)))
        if len(rel_parts) == 1:
            pages_for_nav.append({title: nav_path.as_posix()})
        else:
            section = format_title(rel_parts[0])
            section_entry = next(
                (
                    entry
                    for entry in pages_for_nav
                    if isinstance(entry, dict) and section in entry
                ),
                None,
            )
            if section_entry is None:
                section_entry = {section: []}
                pages_for_nav.append(section_entry)
            section_entry[section].append({title: nav_path.as_posix()})
    return pages_for_nav, index_entries


def upsert_nav(nav, notion_pages):
    existing_idx = next(
        (
            i
            for i, item in enumerate(nav)
            if isinstance(item, dict) and "Notion-sider" in item
        ),
        None,
    )

    if notion_pages:
        notion_entry = {"Notion-sider": ["notion/index.md", *notion_pages]}
        if existing_idx is not None:
            nav[existing_idx] = notion_entry
        else:
            nav.append(notion_entry)
    else:
        if existing_idx is not None:
            nav.pop(existing_idx)


def write_index(index_entries):
    if not index_entries:
        if notion_index.exists():
            notion_index.unlink()
        return
    notion_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Notion-sider", "", "Oversikt over innhold hentet fra Notion.", ""]
    for title, rel_path in index_entries:
        lines.append(f"- [{title}]({rel_path.as_posix()})")
    notion_index.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {notion_index}")


if mkdocs_file.exists():
    with open(mkdocs_file, encoding="utf-8") as f:
        config = load_yaml(f)

    fetch_notion_pages()
    nav_pages, index_entries = collect_pages()
    write_index(index_entries)
    if config and "nav" in config:
        upsert_nav(config["nav"], nav_pages)
        with open(mkdocs_file, "w", encoding="utf-8") as f:
            dump_yaml(config, f)
        if nav_pages:
            print(f"Updated navigation with {len(nav_pages)} Notion page entries")
        else:
            print("No Notion pages found; removed Notion-sider from nav if present.")
    else:
        print(f"Warning: Could not find 'nav' section in {mkdocs_file}")
else:
    print(f"Warning: {mkdocs_file} not found")
