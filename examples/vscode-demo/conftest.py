"""Pytest helpers for the VS Code demo project (mirrors sample_job setup)."""

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from pathlib import Path

import pytest

try:
    from databricks.connect import DatabricksSession
    from databricks.sdk import WorkspaceClient
    from pyspark.sql import SparkSession
except ImportError as exc:  # pragma: no cover - depends on dev setup
    raise ImportError(
        "Test dependencies not found.\n\nRun tests using 'uv run pytest'. "
        "See http://docs.astral.sh/uv to learn more about uv."
    ) from exc


def _ensure_src_on_path() -> None:
    """Add the local src/ directory to sys.path for pytest runs."""
    project_root = Path(__file__).resolve().parent
    src_dir = project_root / "src"
    if src_dir.exists():
        sys.path.insert(0, str(src_dir))


_ensure_src_on_path()


def enable_fallback_compute() -> None:
    """Enable serverless compute if no Databricks Connect target is configured."""
    conf = WorkspaceClient().config
    if conf.serverless_compute_id or conf.cluster_id or os.environ.get("SPARK_REMOTE"):
        return

    url = "https://docs.databricks.com/dev-tools/databricks-connect/cluster-config"
    print("☁️ no compute specified, falling back to serverless compute", file=sys.stderr)
    print(f"  see {url} for manual configuration", file=sys.stderr)

    os.environ["DATABRICKS_SERVERLESS_COMPUTE_ID"] = "auto"


@contextmanager
def allow_stderr_output(config: pytest.Config):
    """Temporarily disable pytest output capture."""
    capman = config.pluginmanager.get_plugin("capturemanager")
    if capman:
        with capman.global_and_fixture_disabled():
            yield
    else:
        yield


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest session just like sample_job."""
    with allow_stderr_output(config):
        enable_fallback_compute()

        if hasattr(DatabricksSession.builder, "validateSession"):
            DatabricksSession.builder.validateSession().getOrCreate()
        else:
            DatabricksSession.builder.getOrCreate()


@pytest.fixture(scope="session")
def spark() -> SparkSession:
    """Provide a SparkSession fixture for tests."""
    return DatabricksSession.builder.getOrCreate()
