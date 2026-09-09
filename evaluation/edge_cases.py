"""Edge-case image generation for AITC-04 (robustness).

The Test Plan asks for "10-15 poor quality images (blurred, low contrast,
cropped)". Rather than hand-collecting them, derive them deterministically
from the evaluation subset so the case is reproducible and every degradation
has a clean original to compare against.

Degradations applied (roughly in increasing severity):
    blur         Gaussian blur, radius scaled to image width
    low_contrast contrast crushed toward mid-grey, plus a brightness lift
    cropped      a chunk of the panoramic arch cut away
    dark         heavy under-exposure
    noisy        additive uniform pixel noise
"""

from __future__ import annotations

import os

DEGRADATIONS = ["blur", "low_contrast", "cropped", "dark", "noisy"]


def _apply(image, kind: str):
    from PIL import Image, ImageEnhance, ImageFilter

    if kind == "blur":
        radius = max(3.0, image.width / 250.0)
        return image.filter(ImageFilter.GaussianBlur(radius=radius))

    if kind == "low_contrast":
        faded = ImageEnhance.Contrast(image).enhance(0.25)
        return ImageEnhance.Brightness(faded).enhance(1.15)

    if kind == "cropped":
        # Cut the right third away, keeping the panoramic aspect plausible.
        return image.crop((0, 0, int(image.width * 0.66), image.height))

    if kind == "dark":
        return ImageEnhance.Brightness(image).enhance(0.30)

    if kind == "noisy":
        import numpy as np

        array = np.array(image.convert("RGB")).astype(np.int16)
        rng = np.random.default_rng(seed=0)
        noise = rng.integers(-45, 46, size=array.shape, dtype=np.int16)
        return Image.fromarray(np.clip(array + noise, 0, 255).astype("uint8"))

    raise ValueError(f"unknown degradation: {kind}")


def generate(source_paths: list[str], output_dir: str, limit: int = 15) -> list[dict]:
    """Write degraded variants of `source_paths` into `output_dir`.

    Cycles through the degradation kinds so the batch always covers all of
    them, and stops at `limit` images (the Test Plan asks for 10-15).
    """
    from PIL import Image

    os.makedirs(output_dir, exist_ok=True)
    generated: list[dict] = []

    for index, source in enumerate(source_paths):
        if len(generated) >= limit:
            break
        kind = DEGRADATIONS[index % len(DEGRADATIONS)]
        stem = os.path.splitext(os.path.basename(source))[0]
        destination = os.path.join(output_dir, f"{stem}.{kind}.png")

        with Image.open(source) as handle:
            _apply(handle.convert("RGB"), kind).save(destination)

        generated.append({"path": destination, "source": source, "degradation": kind})

    return generated
