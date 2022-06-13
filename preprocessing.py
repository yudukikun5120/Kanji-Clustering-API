"""
Module Preprocessing providing functions which need in preprocessing
"""

import numpy as np
from PIL import Image, ImageFont, ImageDraw


def ndarray_of(character: str) -> np.ndarray:
    font = 'fonts/NotoSansJP-Regular.otf'
    size = 64
    font = ImageFont.truetype(font=font, size=size)
    xy = (0, 0)

    image = Image.new(mode='RGB', size=(size, size))
    draw = ImageDraw.Draw(image)
    draw.text(xy=xy, text=character, font=font)

    return np.array(image)
