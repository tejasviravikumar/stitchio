"""Garment foreground segmentation with rembg, imported only when used."""
import io

import numpy as np
from PIL import Image


def garment_mask(image_bytes: bytes) -> np.ndarray:
    """Return a boolean (height, width) mask; True marks garment pixels."""
    from rembg import remove

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    mask = remove(image, only_mask=True)
    return np.asarray(mask) > 127
