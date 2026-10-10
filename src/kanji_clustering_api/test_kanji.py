# Copyright (c) 2026 yudukikun5120

"""Unit tests for Kanji clustering API."""

import hashlib
import pickle
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from .affinities_detection import get_affinities
from .clustering import kanji_group, store_estimator
from .estimator_store import EstimatorIntegrityError, load_estimator
from .main import affinities, app

# Constants for expected values
JIS_LEVEL_1_COUNT = 2965
EXPECTED_AFFINITY_COUNT = 3


def test_kanji_jis_daiichisuijun() -> None:
    """Test that JIS Level 1 kanji group has the expected number of characters."""
    result_length = len(kanji_group("jis_level_1"))
    if result_length != JIS_LEVEL_1_COUNT:
        msg = f"Expected {JIS_LEVEL_1_COUNT} characters, got {result_length}"
        raise AssertionError(msg)


@patch("kanji_clustering_api.clustering.store_estimator_file")
@patch("kanji_clustering_api.clustering.create_fitted_estimator")
def test_store_estimator(
    mock_create_fitted_estimator: MagicMock,
    mock_store_file: MagicMock,
) -> None:
    """Test that estimators can be created and stored for both JIS levels."""
    # Mock the create_fitted_estimator to return dummy data
    mock_estimator = MagicMock()
    mock_df = pd.DataFrame({"character": ["あ", "い"], "label": [0, 1]})
    mock_create_fitted_estimator.return_value = (mock_estimator, mock_df)

    # Test storing estimator
    store_estimator("jis_level_1")

    # Verify the function was called
    mock_create_fitted_estimator.assert_called_once_with("jis_level_1")
    mock_store_file.assert_called_once()


@patch("kanji_clustering_api.affinities_detection.load_estimator")
@patch("kanji_clustering_api.affinities_detection.ndarray_of")
def test_affinities(
    mock_ndarray_of: MagicMock,
    mock_load_estimator: MagicMock,
) -> None:
    """Test that affinities can be retrieved for sample characters."""
    # Mock the estimator and dataframe
    mock_estimator = MagicMock()
    mock_estimator.predict.return_value = np.array([0])  # Predict label 0

    # Create a mock dataframe with some test data
    mock_df = pd.DataFrame(
        {
            "character": ["蟻", "蟷", "蜘", "蛛", "虫"],
            "label": [0, 0, 0, 1, 1],
        },
    )

    mock_load_estimator.return_value = (mock_estimator, mock_df)

    # Mock ndarray_of to return a dummy array
    mock_ndarray_of.return_value = np.zeros((64, 64, 3))

    # Test getting affinities
    result = get_affinities("蟻", "jis_level_1")

    # Verify the result contains characters with the same label
    if len(result) != EXPECTED_AFFINITY_COUNT:
        msg = f"Expected {EXPECTED_AFFINITY_COUNT} characters, got {len(result)}"
        raise AssertionError(msg)
    if "蟻" not in result:
        msg = "Expected '蟻' in result"
        raise AssertionError(msg)
    if "蟷" not in result:
        msg = "Expected '蟷' in result"
        raise AssertionError(msg)
    if "蜘" not in result:
        msg = "Expected '蜘' in result"
        raise AssertionError(msg)


@patch("kanji_clustering_api.main.get_affinities")
def test_affinities_endpoint_deduplicates_repeated_sets(
    mock_get_affinities: MagicMock,
) -> None:
    """Repeating a set name in `sets` must not call get_affinities repeatedly.

    Regression test: a client could previously repeat "jis_level_1" up to
    ~1,358 times within a single HTTP request (bounded by h11's 16 KiB
    request-line/header limit) and force an uncached pickle load plus model
    inference for each repetition, multiplying the cost of one request.
    """
    mock_get_affinities.return_value = np.array(["蟻"])

    affinities(character="蟻", sets="jis_level_1 jis_level_1 jis_level_1")

    mock_get_affinities.assert_called_once_with("蟻", "jis_level_1")


def test_load_estimator_accepts_pinned_files() -> None:
    """The committed estimator files must match the committed manifest."""
    for kanji_set in ("jis_level_1", "jis_level_2"):
        estimator, df = load_estimator(kanji_set)
        assert hasattr(estimator, "predict")  # noqa: S101
        assert {"character", "label"} <= set(df.columns)  # noqa: S101


def test_load_estimator_rejects_tampered_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A swapped pickle (even a valid one) must never be deserialized."""
    estimator_dir = tmp_path / "estimator"
    estimator_dir.mkdir()
    good = pickle.dumps(("estimator", "df"))
    (estimator_dir / "x.pkl").write_bytes(good)
    (estimator_dir / "SHA256SUMS").write_text(
        f"{hashlib.sha256(good).hexdigest()}  x.pkl\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "kanji_clustering_api.estimator_store.ESTIMATOR_DIR",
        estimator_dir,
    )
    monkeypatch.setattr(
        "kanji_clustering_api.estimator_store.MANIFEST_PATH",
        estimator_dir / "SHA256SUMS",
    )
    assert load_estimator("x") == ("estimator", "df")  # noqa: S101

    (estimator_dir / "x.pkl").write_bytes(pickle.dumps(("evil", "df")))
    with pytest.raises(EstimatorIntegrityError):
        load_estimator("x")
    (estimator_dir / "unpinned.pkl").write_bytes(good)
    with pytest.raises(EstimatorIntegrityError):
        load_estimator("unpinned")


def test_affinities_character_limited_to_one_code_point() -> None:
    """`character` must be declared as exactly one code point.

    The feature extractor renders it onto a fixed 64x64 canvas, so a longer
    string (or a newline-separated one) only adds rendering work.
    """
    parameters = app.openapi()["paths"]["/affinities"]["get"]["parameters"]
    character = next(p for p in parameters if p["name"] == "character")

    assert character["schema"]["minLength"] == 1  # noqa: S101
    assert character["schema"]["maxLength"] == 1  # noqa: S101
