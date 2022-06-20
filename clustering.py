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


def kanji_group(set: str) -> list:
    if set == 'jis_level_1':
        first, end = 0xB0A0, 0xCFD3
    elif set == 'jis_level_2':
        first, end = 0xD0A0, 0xF4A6


    def character_present(code: int) -> bool:
        divisor = 0x100

        return (
            first <= code <= end
        ) and (
            code % divisor not in [0xA0, 0xFF]
        )

    return [
        int.to_bytes(code, byteorder='big', length=2)
        .decode('euc_jisx0213', errors='ignore')
        for first_in_block in range(first, end, 0x100)
        for code in range(first_in_block, first_in_block + 0x10 * 6)
        if character_present(code)
    ]


def extract_feature(set: str) -> np.ndarray:

    feature = np.array(
        [
            ndarray_of(char)
            for char in progressbar.progressbar(kanji_group(set))
        ])
    
    return feature.reshape(feature.shape[0], -1)


def create_fitted_estimator(set: str,
                            n_clusters: int = 100) -> (KMeans,
                                                       pd.DataFrame):
    logging.info("extracting feature values for %s...", set)
    feature = extract_feature(set)

    logging.info("fitting an estimator with k-means clustering...")
    estimator = KMeans(n_clusters=n_clusters).fit(feature)
    logging.info("successfully fitted the estimator for %s.", set)

    labels = pd.Series(estimator.labels_, name='label')

    df = pd.concat(
        [pd.Series(
            kanji_group(set),
            name="character"), labels], axis=1)

    logging.debug("""The estimator dataframe:
%s
    """, df)

    return estimator, df


def store_estimator(set: str):
    estimator, df = create_fitted_estimator(set)

    with open(f'estimator/{set}.pkl', 'wb') as f:
        pickle.dump((estimator, df), f)
