"""
Module Clustering clustering kanji or fitting an estimator
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import logging
import progressbar
import pickle
from preprocessing import ndarray_of

progressbar.streams.wrap_stderr()
logging.basicConfig(level=logging.INFO)


def kanji_jis_daiichisuijun() -> list:
    kanji_list = []
    for first in range(0xB0A0, 0xCFA0 + 0x100, 0x100):
        last = first + 0x10 * 6
        for code in range(first, last):
            if code > 0xCFD3 or not character_present(code):
                continue
            byte = int.to_bytes(code, byteorder='big', length=2)
            char = byte.decode('euc_jisx0213', errors='ignore')
            kanji_list.append(char)

    logging.debug(kanji_list)

    return kanji_list


def character_present(code: int) -> bool:
    divisor = 0x100

    return code % divisor not in [0xA0, 0xFF]


def extract_feature() -> np.ndarray:
    feature = np.array(
        [ndarray_of(char)
            for char in progressbar.progressbar(kanji_jis_daiichisuijun())])

    feature = feature.reshape(feature.shape[0], -1)

    return feature


def create_fitted_estimator(n_clusters: int = 100) -> (KMeans, pd.DataFrame):
    logging.info("extracting feature values...")
    feature = extract_feature()

    logging.info("fitting an estimator with k-means clustering...")
    estimator = KMeans(n_clusters=n_clusters).fit(feature)
    logging.info("successfully fitted the estimator.")

    labels = pd.Series(estimator.labels_, name='label')

    df = pd.concat(
        [pd.Series(
            kanji_jis_daiichisuijun(),
            name="character"), labels], axis=1)

    logging.debug("""The estimator dataframe:
%s
    """, df)

    return estimator, df


def store_estimator():
    estimator, df = create_fitted_estimator()

    with open('estimator/JIS_level-1_kanji_set.pkl', 'wb') as f:
        pickle.dump((estimator, df), f)
