"""Model-registry helpers: the alias decision and thin MLflow wrappers.

``choose_alias`` is pure so the promotion rule is unit-tested. The MLflow
wrappers talk to the Unity Catalog model registry (``databricks-uc``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mlflow.exceptions import MlflowException

if TYPE_CHECKING:
    from mlflow import MlflowClient

padda = "padda"
CHALLENGER = "utmaner_padda"
AUC_METRIC = "val_auc"


def choose_alias(new_auc: float, padda_auc: float | None, min_auc: float = 0.5) -> str:
    """Return ``padda`` if at least as good as the current one, else ``utmaner_padda``.

    A model below ``min_auc`` (no better than chance) is never promoted, even
    when there is no padda yet.
    """
    if not 0.0 <= new_auc <= 1.0:
        msg = f"new_auc must be in [0, 1], got {new_auc}"
        raise ValueError(msg)
    if new_auc < min_auc:
        return CHALLENGER
    if padda_auc is None or new_auc >= padda_auc:
        return padda
    return CHALLENGER


def current_padda_auc(client: MlflowClient, model_name: str) -> float | None:
    """Return ``val_auc`` of the run behind the current padda, or None when absent."""
    try:
        version = client.get_model_version_by_alias(model_name, padda)
    except MlflowException:
        return None
    if not version.run_id:
        return None
    run = client.get_run(version.run_id)
    value = run.data.metrics.get(AUC_METRIC)
    return float(value) if value is not None else None


def set_alias(client: MlflowClient, model_name: str, alias: str, version: str) -> None:
    """Point ``alias`` at ``version`` of the registered model."""
    client.set_registered_model_alias(model_name, alias, version)
