#!/usr/bin/env python3
"""Generate guides/index.md and update navigation in mkdocs.yml automatically."""

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
    import yaml

    def load_yaml(stream):
        return yaml.safe_load(stream)

    def dump_yaml(data, stream):
        yaml.safe_dump(data, stream, default_flow_style=False, allow_unicode=True)


docs_dir = Path("docs")
guides_dir = docs_dir / "guides"
index_file = guides_dir / "index.md"
mkdocs_file = Path("mkdocs.yml")

if not guides_dir.exists():
    print(f"Guides directory not found: {guides_dir}")
    exit(1)

# Collect all subdirectories and files (excluding images)
exclude_dirs = {"images"}
content_lines = ["# Guider", ""]
content_lines.append(
    "Her listes alle guider som er tilgjengelige innenfor respektive område."
)
content_lines.append("")

subdirs = [d for d in guides_dir.iterdir() if d.is_dir() and d.name not in exclude_dirs]
subdirs.sort()

# Build navigation structure for guides
guides_nav = [{"Guider": "guides/index"}]

for subdir in subdirs:
    # Get directory name (capitalize first letter)
    dir_name = subdir.name.replace("-", " ").replace("_", " ").title()
    content_lines.append(f"## {dir_name}")
    content_lines.append("")

    md_files = sorted(subdir.glob("*.md"))
    if md_files:
        content_lines.append("")

        # Build navigation for this subdirectory
        subdir_nav_items = []
        for md_file in md_files:
            # Get file name without extension
            file_name = md_file.stem.replace("-", " ").replace("_", " ").title()
            # Create relative path for markdown links (from guides directory)
            rel_path = f"{subdir.name}/{md_file.name}"
            # Create full path for navigation
            nav_path = f"guides/{subdir.name}/{md_file.stem}"
            content_lines.append(f"- [{file_name}]({rel_path})")
            subdir_nav_items.append({file_name: nav_path})

        if len(subdir_nav_items) == 1:
            guides_nav.append({
                dir_name: subdir_nav_items[0][list(subdir_nav_items[0].keys())[0]]
            })
        else:
            guides_nav.append({dir_name: subdir_nav_items})

        content_lines.append("")

# Write the generated index content
index_file.write_text("\n".join(content_lines), encoding="utf-8")
print(f"Generated {index_file}")

# Update navigation in mkdocs.yml
if mkdocs_file.exists():
    with open(mkdocs_file, encoding="utf-8") as f:
        config = load_yaml(f)

    if config and "nav" in config:
        nav = config["nav"]
        for i, item in enumerate(nav):
            if isinstance(item, dict) and "Guides" in item:
                nav[i] = {"Guides": guides_nav}
                break
            elif isinstance(item, str) and item == "Guides":
                nav[i] = {"Guides": guides_nav}
                break
        with open(mkdocs_file, "w", encoding="utf-8") as f:
            dump_yaml(config, f)
        print(f"Updated navigation in {mkdocs_file}")
    else:
        print(f"Warning: Could not find 'nav' section in {mkdocs_file}")
else:
    print(f"Warning: {mkdocs_file} not found")
