#!/usr/bin/env python3
"""Convert GitHub avatar image to dense ASCII portrait lines."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# Classic neofetch-style ramp (dark → light ink on dark bg after invert)
RAMP = " .:-=+*#%@"


def _face_crop(img: Image.Image) -> Image.Image:
    """
    Heuristic head/shoulders crop.
    GitHub avatars that are full-body outdoor shots need a tight upper crop
    so ASCII reads as a portrait (Andrew6rant-style), not scene noise.
    """
    w, h = img.size
    # Prefer upper-central square covering roughly head + torso
    crop_h = int(h * 0.58)
    crop_w = crop_h
    left = max(0, (w - crop_w) // 2)
    top = int(h * 0.02)
    if top + crop_h > h:
        top = max(0, h - crop_h)
    if left + crop_w > w:
        left = max(0, w - crop_w)
    return img.crop((left, top, left + crop_w, top + crop_h))


def image_to_ascii(path: Path, width: int = 46, height: int = 24) -> list[str]:
    img = Image.open(path).convert("RGB")
    img = ImageOps.exif_transpose(img)
    img = _face_crop(img)
    img = img.convert("L")

    img = ImageEnhance.Contrast(img).enhance(1.85)
    img = ImageEnhance.Brightness(img).enhance(1.08)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=140, threshold=2))
    img = img.resize((width, height), Image.Resampling.LANCZOS)

    pixels = list(img.getdata())
    lines: list[str] = []
    n = len(RAMP) - 1
    for y in range(height):
        row = []
        for x in range(width):
            # Dark areas → denser glyphs
            val = 255 - pixels[y * width + x]
            idx = int(val / 255 * n + 0.5)
            idx = max(0, min(n, idx))
            row.append(RAMP[idx])
        lines.append("".join(row))
    return lines


def save_ascii_cache(lines: list[str], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    avatar = root / "assets" / "avatar.png"
    lines = image_to_ascii(avatar)
    save_ascii_cache(lines, root / "cache" / "ascii.txt")
    for line in lines:
        print(line)
