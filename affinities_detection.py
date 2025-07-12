"""Module AffinitiesDetection detect affinities of given kanji character."""

import pickle
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from kanji_types import KanjiSet
from preprocessing import ndarray_of


def get_affinities(character: str, kanji_set: KanjiSet) -> NDArray[np.str_]:
    """Get characters with similar visual features to the input character.

    Args:
        character: The kanji character to find affinities for.
        kanji_set: The kanji set to use ('jis_level_1' or 'jis_level_2').

    Returns:
        Array of kanji characters that are visually similar.

    """
    with Path(f"estimator/{kanji_set}.pkl").open("rb") as f:
        estimator, df = pickle.load(f)  # noqa: S301

    predicted_labels = estimator.predict(ndarray_of(character).reshape(1, -1))

    label = predicted_labels[0]

    affinities: NDArray[np.str_] = df.loc[df["label"] == label, "character"].values

    return affinities
