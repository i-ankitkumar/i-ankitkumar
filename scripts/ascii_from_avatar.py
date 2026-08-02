#!/usr/bin/env python3
"""Portrait helpers + optional ASCII cache for the neofetch card."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"


def _face_crop(img: Image.Image) -> Image.Image:
    """Tight face crop so identity fills the frame (Andrew-style framing)."""
    w, h = img.size
    if h >= w * 1.15:
        # Tall portrait (sunglasses waist-up shot)
        return img.crop((int(w * 0.20), int(h * 0.01), int(w * 0.80), int(h * 0.50)))
    side = min(w, h)
    left = (w - side) // 2
    top = max(0, (h - side) // 2 - int(side * 0.05))
    return img.crop((left, top, left + side, min(h, top + side)))


def _preprocess(path: Path) -> Image.Image:
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    img = _face_crop(img)
    w, h = img.size
    side = min(w, h)
    img = img.crop(((w - side) // 2, (h - side) // 2, (w - side) // 2 + side, (h - side) // 2 + side))
    g = img.convert("L")
    px = sorted(g.getdata())
    n = len(px)
    lo, hi = px[int(n * 0.03)], px[int(n * 0.97)]
    if hi > lo:
        g = g.point(lambda v, lo=lo, hi=hi: max(0, min(255, int((v - lo) * 255 / (hi - lo)))))
    g = ImageEnhance.Contrast(g).enhance(1.55)
    g = ImageEnhance.Sharpness(g).enhance(1.35)
    g = g.filter(ImageFilter.GaussianBlur(radius=0.6))
    g = g.filter(ImageFilter.UnsharpMask(radius=1.6, percent=160, threshold=2))
    return g


def _via_chafa(img_path: Path, cols: int, rows: int) -> list[str] | None:
    chafa = shutil.which("chafa")
    if not chafa:
        return None
    face = _preprocess(img_path)
    tmp = img_path.parent / "_face_tmp.png"
    face.save(tmp)
    try:
        proc = subprocess.run(
            [
                chafa,
                "-f",
                "symbols",
                "-s",
                f"{cols}x{rows}",
                "-c",
                "none",
                "--symbols",
                "ascii",
                "--font-ratio",
                "0.5",
                str(tmp),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        raw = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", proc.stdout)
        lines = [ln.rstrip("\n") for ln in raw.splitlines() if ln.strip() != ""]
        if not lines:
            return None
        width = max(len(l) for l in lines)
        return [l.ljust(width)[:width] for l in lines][:rows]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    finally:
        if tmp.exists():
            tmp.unlink()


def _via_pillow(path: Path, cols: int, rows: int) -> list[str]:
    g = _preprocess(path).resize((cols, rows), Image.Resampling.LANCZOS)
    pixels = list(g.getdata())
    n = len(RAMP) - 1
    lines: list[str] = []
    for y in range(rows):
        row = []
        for x in range(cols):
            val = 255 - pixels[y * cols + x]
            q = int((val / 255) * 8 + 0.5) / 8.0
            row.append(RAMP[max(0, min(n, int(q * n)))])
        lines.append("".join(row))
    return lines


def image_to_ascii(path: Path, width: int = 52, height: int = 28) -> list[str]:
    lines = _via_chafa(path, width, height) or _via_pillow(path, width, height)
    w = max(len(l) for l in lines)
    return [l.ljust(w)[:w] for l in lines]


def save_ascii_cache(lines: list[str], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    src = root / "assets" / "portrait.png"
    if not src.exists():
        src = root / "assets" / "avatar.png"
    lines = image_to_ascii(src)
    save_ascii_cache(lines, root / "cache" / "ascii.txt")
    for line in lines:
        print(line)
