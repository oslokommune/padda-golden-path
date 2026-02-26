# CLAUDE-Zensical.md

Branch plan and TODO tracking for the `zensical` branch — migrating documentation from MkDocs to Zensical.

## Why

MkDocs is no longer actively maintained. Zensical is the successor to Material for MkDocs, built by the same team. It offers Rust-accelerated builds, better search, incremental updates, and active development.

## Approach

Incremental migration: get a working Zensical skeleton first, keep the old MkDocs setup in place, then remove it once Zensical is fully functional.

## Key decisions

- **Config**: Use `zensical.toml` (native format) rather than `mkdocs.yml` compatibility mode.
- **CSS**: Write fresh CSS with tokens extracted from the latest Punkt version. Do NOT reuse CSS from the existing MkDocs setup. No npm dependency on `@oslokommune/punkt-css`.
- **Excalidraw**: Replace with Mermaid diagrams. Zensical has native Mermaid support.
- **Oslo visual identity**: Follow designmanual.oslo.kommune.no. Use styles from punkt.oslo.kommune.no (tokens/variables only, not the full component library).

## TODO

### Phase 1: Working skeleton
- [x] Create CLAUDE-Zensical.md (this file)
- [x] Install Zensical (`uv add --dev zensical`) — v0.0.23
- [x] Extract fresh Punkt design tokens (`docs/zensical-stylesheets/punkt-tokens.css`)
- [x] Create `zensical.toml` with site config, navigation, extensions, and Oslo theme
- [x] Create Oslo theme CSS (`docs/zensical-stylesheets/oslo-theme.css`)
- [x] Verify `zensical serve` runs locally and docs render correctly
- [x] Fix rendering issues (TOML icon parsing, Google Fonts disabled)

### Phase 2: Feature parity
- [ ] Convert `docs/mkdocs_extension/generate_guides_index.py` to standalone pre-build script
- [ ] Convert `docs/mkdocs_extension/generate_listof_bundles.py` to standalone pre-build script
- [ ] Convert `docs/mkdocs_extension/generate_notion_nav.py` to standalone pre-build script
- [x] Replace Excalidraw diagram `dataflyt_sye` with Mermaid (Punkt-colored, flowchart TD)
- [ ] Replace remaining Excalidraw diagrams with Mermaid equivalents
- [ ] Verify mkdocstrings (Python API docs) works in Zensical
- [ ] Verify glightbox / image handling

### Phase 3: Cleanup
- [ ] Remove MkDocs dependencies from `pyproject.toml`
- [ ] Remove `mkdocs.yml` and `mkdocs.local.yml`
- [ ] Update CI/CD workflow (`.github/workflows/pages.yml`) to use `zensical build`
- [ ] Update CI/CD workflow (`.github/workflows/pr.yaml`) if docs validation is needed
- [ ] Update `README.md` with new commands
- [ ] Update `CLAUDE.md` with new commands
- [ ] Refine CSS to use Zensical-native selectors where possible

### Phase 4: Enhancements
- [ ] Explore Zensical-native search (Disco) improvements
- [ ] Evaluate Zensical module system when available
- [ ] Consider migrating remaining Material template overrides to Zensical components
