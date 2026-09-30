"""PyTorch model for room availability.

The network is a stock ``torch.nn.Sequential``: a ``BatchNorm1d`` that
normalises raw features using running statistics learned during training, two
hidden layers, and a ``Sigmoid`` so the output is a probability. Using only
stock layers matters: the pickled model references ``torch.nn`` classes, so it
loads wherever torch is installed (batch job, serving endpoint, laptop) with
no custom code on the path.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from numpy.typing import NDArray
from sklearn.metrics import roc_auc_score
from torch import nn

FloatArray = NDArray[np.float32]

MIN_BATCH_ROWS = 2  # BatchNorm needs more than one row in train mode


@dataclass(frozen=True)
class TrainParams:
    """Hyper-parameters for ``train_model``."""

    epochs: int = 40
    lr: float = 0.005
    batch_size: int = 256
    seed: int = 0


def build_model(n_features: int, hidden: int = 32, seed: int = 0) -> nn.Sequential:
    """Return an untrained network for ``n_features`` numeric inputs."""
    torch.manual_seed(seed)
    return nn.Sequential(
        nn.BatchNorm1d(n_features),
        nn.Linear(n_features, hidden),
        nn.ReLU(),
        nn.Linear(hidden, hidden // 2),
        nn.ReLU(),
        nn.Linear(hidden // 2, 1),
        nn.Sigmoid(),
    )


def train_model(
    model: nn.Sequential,
    x: FloatArray,
    y: FloatArray,
    params: TrainParams | None = None,
) -> list[float]:
    """Train in place with shuffled mini-batches and return the mean loss per epoch."""
    params = params or TrainParams()
    torch.manual_seed(params.seed)
    features = torch.from_numpy(np.asarray(x, dtype="float32"))
    target = torch.from_numpy(np.asarray(y, dtype="float32")).reshape(-1, 1)
    optimiser = torch.optim.Adam(model.parameters(), lr=params.lr)
    loss_fn = nn.BCELoss()
    losses: list[float] = []
    n = len(features)
    for _ in range(params.epochs):
        model.train()
        permutation = torch.randperm(n)
        total = 0.0
        for start in range(0, n, params.batch_size):
            idx = permutation[start : start + params.batch_size]
            if len(idx) < MIN_BATCH_ROWS:
                continue
            optimiser.zero_grad()
            loss = loss_fn(model(features[idx]), target[idx])
            loss.backward()
            optimiser.step()
            total += loss.item() * len(idx)
        losses.append(total / n)
    model.eval()
    return losses


def predict_proba(model: nn.Sequential, x: FloatArray) -> FloatArray:
    """Return the booked probability per row as a flat float32 array."""
    model.eval()
    with torch.no_grad():
        out = model(torch.from_numpy(np.asarray(x, dtype="float32")))
    return np.asarray(out.reshape(-1).numpy(), dtype="float32")


def evaluate(model: nn.Sequential, x: FloatArray, y: FloatArray) -> dict[str, float]:
    """Return ``auc`` and ``accuracy`` (threshold 0.5) on the given rows."""
    probs = predict_proba(model, x)
    labels = np.asarray(y, dtype="float32")
    return {
        "auc": float(roc_auc_score(labels, probs)),
        "accuracy": float(((probs >= 0.5) == (labels >= 0.5)).mean()),
    }
