#!/usr/bin/env python3
"""Convert portrait/avatar image to dense ASCII (tuned for high-contrast headshots)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# Neofetch-style ramp — good midtone separation for face + fabric
RAMP = " .,:;irsXA253hMHGS#9B&@"


def _subject_crop(img: Image.Image) -> Image.Image:
    """
    Bust crop optimized for waist-up portraits:
    - keep head, sunglasses, shoulders, polo
    - trim sparse shutter/wall sides that become noisy columns in ASCII
    """
    w, h = img.size
    left = int(w * 0.16)
    right = int(w * 0.84)
    top = int(h * 0.01)
    bottom = int(h * 0.70)
    return img.crop((left, top, right, bottom))


def _percentile_stretch(g: Image.Image, lo_p: float = 0.02, hi_p: float = 0.98) -> Image.Image:
    px = sorted(g.getdata())
    n = len(px)
    lo = px[int(n * lo_p)]
    hi = px[max(lo + 1, int(n * hi_p))]
    scale = 255.0 / (hi - lo)
    return g.point(lambda v: max(0, min(255, int((v - lo) * scale))))


def _center_weight(g: Image.Image, strength: float = 0.22) -> Image.Image:
    """Slightly darken edges so background shutters don't dominate."""
    w, h = g.size
    # Build a simple radial-ish vertical vignette via pixel loop on a small map
    vig = Image.new("L", (w, h))
    cx, cy = w / 2, h * 0.42
    rx, ry = w * 0.55, h * 0.62
    pix = vig.load()
    for y in range(h):
        for x in range(w):
            nx = (x - cx) / rx
            ny = (y - cy) / ry
            d = (nx * nx + ny * ny) ** 0.5
            # 255 center → darker edges
            fall = max(0.0, min(1.0, d))
            pix[x, y] = int(255 * (1.0 - strength * fall * fall))
    return Image.composite(g, Image.new("L", (w, h), 0), vig)


def image_to_ascii(path: Path, width: int = 48, height: int = 30) -> list[str]:
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    img = _subject_crop(img)
    g = img.convert("L")

    g = _percentile_stretch(g)
    g = ImageEnhance.Contrast(g).enhance(1.85)
    g = ImageEnhance.Brightness(g).enhance(1.06)
    g = _center_weight(g, strength=0.28)
    # Keep shirt ribbing / shutter grain readable
    g = g.filter(ImageFilter.UnsharpMask(radius=1.15, percent=145, threshold=2))

    g = g.resize((width, height), Image.Resampling.LANCZOS)
    pixels = list(g.getdata())
    n = len(RAMP) - 1
    lines: list[str] = []
    for y in range(height):
        row = []
        for x in range(width):
            # Dark → dense glyph (portrait on dark terminal bg)
            val = 255 - pixels[y * width + x]
            idx = max(0, min(n, int(val / 255 * n + 0.5)))
            row.append(RAMP[idx])
        lines.append("".join(row))
    return lines


def save_ascii_cache(lines: list[str], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    # Prefer dedicated portrait if present
    avatar = root / "assets" / "portrait.png"
    if not avatar.exists():
        avatar = root / "assets" / "avatar.png"
    lines = image_to_ascii(avatar)
    save_ascii_cache(lines, root / "cache" / "ascii.txt")
    for line in lines:
        print(line)
