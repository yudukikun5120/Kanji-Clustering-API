"""Module Clustering clustering kanji or fitting an estimator."""

import logging
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import progressbar
from sklearn.cluster import KMeans

from kanji_types import KanjiSet
from preprocessing import ndarray_of

progressbar.streams.wrap_stderr()
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def kanji_group(kanji_set: KanjiSet) -> list:
    """Get list of kanji characters for the specified JIS level.

    Args:
        kanji_set: The kanji set to retrieve ('jis_level_1' or 'jis_level_2').

    Returns:
        List of kanji characters in the specified set.

    """
    match kanji_set:
        case "jis_level_1":
            first, end = 0xB0A0, 0xCFD3
        case "jis_level_2":
            first, end = 0xD0A0, 0xF4A6

    def character_present(code: int) -> bool:
        divisor = 0x100

        return (first <= code <= end) and (code % divisor not in [0xA0, 0xFF])

    return [
        int.to_bytes(code, byteorder="big", length=2).decode(
            "euc_jisx0213",
            errors="ignore",
        )
        for first_in_block in range(first, end, 0x100)
        for code in range(first_in_block, first_in_block + 0x10 * 6)
        if character_present(code)
    ]


def extract_feature(kanji_set: KanjiSet) -> np.ndarray:
    """Extract visual features from all kanji in the specified set.

    Args:
        kanji_set: The kanji set to process ('jis_level_1' or 'jis_level_2').

    Returns:
        Feature matrix where each row represents a kanji character.

    """
    return np.array(
        [ndarray_of(char) for char in progressbar.progressbar(kanji_group(kanji_set))],
    ).reshape(len(kanji_group(kanji_set)), -1)


def create_fitted_estimator(
    kanji_set: KanjiSet,
    n_clusters: int = 100,
) -> tuple[KMeans, pd.DataFrame]:
    """Create and fit a KMeans estimator for kanji clustering.

    Args:
        kanji_set: The kanji set to cluster ('jis_level_1' or 'jis_level_2').
        n_clusters: Number of clusters for KMeans algorithm.

    Returns:
        Tuple of fitted KMeans estimator and DataFrame with character labels.

    """
    logger.info("extracting feature values for %s...", kanji_set)
    feature = extract_feature(kanji_set)

    logger.info("fitting an estimator with k-means clustering...")
    estimator = KMeans(n_clusters=n_clusters).fit(feature)
    logger.info("successfully fitted the estimator for %s.", kanji_set)

    labels = pd.Series(estimator.labels_, name="label")

    df = pd.concat(
        [pd.Series(kanji_group(kanji_set), name="character"), labels],
        axis=1,
    )

    logger.debug(
        """The estimator dataframe:
%s
    """,
        df,
    )

    return estimator, df


def store_estimator(kanji_set: KanjiSet) -> None:
    """Create and store a fitted estimator to disk.

    Args:
        kanji_set: The kanji set to process and store ('jis_level_1' or 'jis_level_2').

    """
    estimator, df = create_fitted_estimator(kanji_set)

    with Path(f"estimator/{kanji_set}.pkl").open("wb") as f:
        pickle.dump((estimator, df), f)
