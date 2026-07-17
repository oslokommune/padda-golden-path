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

# Run tests (requires Databricks authentication, see below)
uv run pytest

# Build wheel
uv build --wheel
```

## Running tests locally

The tests run against Databricks via [Databricks
Connect](https://docs.databricks.com/dev-tools/databricks-connect.html), which
is declared as a dev dependency — `uv run pytest` installs it automatically.
You do need workspace authentication:

1. Log in with the Databricks CLI (`databricks auth login`) if you haven't
   already.
2. Point the tests at your profile and run them:

   ```bash
   DATABRICKS_CONFIG_PROFILE=<profile-name> uv run pytest
   ```

If no cluster is configured for Databricks Connect, the test setup falls back
to serverless compute automatically.
