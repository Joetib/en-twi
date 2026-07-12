"""Data loading and splitting utilities for English-Twi parallel corpora."""

import json
import os
from pathlib import Path

from datasets import Dataset, DatasetDict


def load_parallel_corpus(path: str) -> Dataset:
    """Load a parallel English-Twi corpus from a JSON file.

    Expects records of the form ``{"english": str, "twi": str}``. Leading and
    trailing whitespace is stripped from both sides because the source data
    contains many records with stray padding (e.g. " Oh Jehovah Keep ..."),
    which would otherwise produce off-by-one tokenization artifacts. Records
    where either side is empty after stripping are dropped.
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    english, twi = [], []
    for rec in raw:
        en = (rec.get("english") or "").strip()
        tw = (rec.get("twi") or "").strip()
        if en and tw:
            english.append(en)
            twi.append(tw)

    return Dataset.from_dict({"english": english, "twi": twi})


def make_splits(
    ds: Dataset,
    *,
    seed: int = 42,
    val_size: int = 3000,
    test_size: int = 3000,
    test_indices_out: str | None = "results/test_indices.json",
) -> DatasetDict:
    """Deterministic shuffle and slice into train / validation / test.

    The shuffle uses the given seed, so re-running produces identical splits.
    Test indices (positions in the *shuffled* dataset) are written to
    ``test_indices_out`` so the held-out set is documented for the paper.
    """
    shuffled = ds.shuffle(seed=seed)
    n = len(shuffled)
    if val_size + test_size >= n:
        raise ValueError(
            f"val_size + test_size ({val_size + test_size}) must be < dataset size ({n})"
        )

    test = shuffled.select(range(test_size))
    val = shuffled.select(range(test_size, test_size + val_size))
    train = shuffled.select(range(test_size + val_size, n))

    if test_indices_out is not None:
        out_path = Path(test_indices_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "seed": seed,
                    "shuffle_then_select": True,
                    "test_range": [0, test_size],
                    "val_range": [test_size, test_size + val_size],
                    "train_range": [test_size + val_size, n],
                    "total": n,
                },
                f,
                indent=2,
            )

    return DatasetDict({"train": train, "validation": val, "test": test})


def subsample_train(ds: DatasetDict, max_train: int | None, *, seed: int = 42) -> DatasetDict:
    """Optionally cap the train split (used for M1 smoke tests and quick runs)."""
    if max_train is None or max_train >= len(ds["train"]):
        return ds
    return DatasetDict(
        {
            "train": ds["train"].shuffle(seed=seed).select(range(max_train)),
            "validation": ds["validation"],
            "test": ds["test"],
        }
    )
