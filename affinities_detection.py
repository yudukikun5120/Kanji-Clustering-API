"""
Module AffinitiesDetection detect affinities of given kanji character
"""

import numpy as np
import pickle
from preprocessing import ndarray_of


def get_affinities(character: str, set: str) -> np.ndarray:
    # predicted_image = np.array(io.imread(
    # "")).reshape(1, -1)
    with open(f"estimator/{set}.pkl", "rb") as f:
        estimator, df = pickle.load(f)

    predicted_labels = estimator.predict(ndarray_of(character).reshape(1, -1))

    label = predicted_labels[0]

    affinities = df.loc[df["label"] == label, "character"].values

    return affinities
