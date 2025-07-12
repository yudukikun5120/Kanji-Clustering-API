"""Unit tests for Kanji clustering API."""

from unittest.mock import MagicMock, mock_open, patch

import numpy as np
import pandas as pd

from .affinities_detection import get_affinities
from .clustering import kanji_group, store_estimator

# Constants for expected values
JIS_LEVEL_1_COUNT = 2965
EXPECTED_AFFINITY_COUNT = 3


def test_kanji_jis_daiichisuijun() -> None:
    """Test that JIS Level 1 kanji group has the expected number of characters."""
    result_length = len(kanji_group("jis_level_1"))
    if result_length != JIS_LEVEL_1_COUNT:
        msg = f"Expected {JIS_LEVEL_1_COUNT} characters, got {result_length}"
        raise AssertionError(msg)


@patch("kanji_clustering_api.clustering.Path")
@patch("kanji_clustering_api.clustering.pickle.dump")
@patch("kanji_clustering_api.clustering.create_fitted_estimator")
def test_store_estimator(
    mock_create_fitted_estimator: MagicMock,
    mock_pickle_dump: MagicMock,
    mock_path: MagicMock,
) -> None:
    """Test that estimators can be created and stored for both JIS levels."""
    # Mock the create_fitted_estimator to return dummy data
    mock_estimator = MagicMock()
    mock_df = pd.DataFrame({"character": ["あ", "い"], "label": [0, 1]})
    mock_create_fitted_estimator.return_value = (mock_estimator, mock_df)

    # Mock the file opening
    mock_file = mock_open()
    mock_path.return_value.open.return_value.__enter__ = mock_file
    mock_path.return_value.open.return_value.__exit__ = MagicMock()

    # Test storing estimator
    store_estimator("jis_level_1")

    # Verify the function was called
    mock_create_fitted_estimator.assert_called_once_with("jis_level_1")
    mock_pickle_dump.assert_called_once()


@patch("kanji_clustering_api.affinities_detection.Path")
@patch("kanji_clustering_api.affinities_detection.pickle.load")
@patch("kanji_clustering_api.affinities_detection.ndarray_of")
def test_affinities(
    mock_ndarray_of: MagicMock,
    mock_pickle_load: MagicMock,
    mock_path: MagicMock,
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

    mock_pickle_load.return_value = (mock_estimator, mock_df)

    # Mock ndarray_of to return a dummy array
    mock_ndarray_of.return_value = np.zeros((64, 64, 3))

    # Mock file opening
    mock_file = mock_open()
    mock_path.return_value.open.return_value = mock_file()

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
