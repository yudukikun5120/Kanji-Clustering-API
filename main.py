import numpy as np
import pandas as pd
from PIL import Image, ImageFont, ImageDraw
from sklearn.cluster import KMeans
import logging
import progressbar

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


def ndarray_of(character: str) -> np.ndarray:
    font = 'fonts/NotoSansJP-Regular.otf'
    size = 64
    font = ImageFont.truetype(font=font, size=size)
    xy = (0, 0)

    image = Image.new(mode='RGB', size=(size, size))
    draw = ImageDraw.Draw(image)
    draw.text(xy=xy, text=character, font=font)

    return np.array(image)


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


def predict_label(character: str) -> int:
    # predicted_image = np.array(io.imread(
    # "")).reshape(1, -1)
    estimator, df = create_fitted_estimator()

    predicted_labels = estimator.predict(
        ndarray_of(character).reshape(1, -1))

    affinities = [df.loc[df['label'] == label, 'character'].values
                  for label in predicted_labels]

    return affinities
