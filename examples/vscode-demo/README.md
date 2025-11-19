# vscode-demo

Example project used to demonstrate:

- VS Code + Databricks extension
- Running notebooks (.py with `# %%`)
- Using `uv` for dependencies
- Building a Python wheel
- Deploying with a Databricks bundle
- Relying on Databricks runtime dependencies

## Quick start

```bash
cd examples/vscode-demo

# Create / reuse a uv environment and run tests
uv run pytest

# Build wheel
uv build --wheel

```

## Local Databricks Connect debugging

When running notebooks or the CLI locally (e.g., via the Databricks VS Code
extension), install and configure [Databricks Connect](https://docs.databricks.com/dev-tools/databricks-connect.html):

1. Install into this project’s environment (e.g. `uv add databricks-connect` or
   `uv run --project examples/vscode-demo pip install databricks-connect`).
2. Configure it (`databricks-connect configure` or set `DATABRICKS_*` env vars).
3. Re-run `uv run --project examples/vscode-demo pytest` or your notebook.

If Databricks Connect is missing, local notebook execution raises a helpful error
with a link to the setup guide.
