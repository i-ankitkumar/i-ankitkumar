#!/usr/bin/env python3
"""Generate the terminal-register profile card SVGs (dark + light).

Layout: window chrome / duotone face crop on the left / aligned key-value
panel on the right. Every visible string comes from config.json; the stats
rows come from cache/stats.json.

Design rules (see PRODUCT.md, Surface 1):
- Terminal / CLI register is binding: monospace, GitHub-style palette, key/value rows.
- No cosplay fields. Nothing labelled OS / Uptime / Kernel / Shell.
- The value column is a fixed grid so values align down the card.
- Duotone photo, so the portrait sits inside the palette instead of fighting it.
- Both themes move together. Both must clear WCAG AA on the key/value text.
"""

from __future__ import annotations

import base64
import json
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ascii_from_avatar import (  # noqa: E402
    _face_crop,
    card_face_crop,
    image_to_ascii,
    save_ascii_cache,
)

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "bar": "#161b22",
        "frame": "#30363d",
        "fg": "#c9d1d9",
        "key": "#ffa657",
        "value": "#a5d6ff",
        "cc": "#768390",
        "title": "#8b949e",
        "dot_r": "#ff5f56",
        "dot_y": "#ffbd2e",
        "dot_g": "#27c93f",
        # duotone: shadows -> card background, highlights -> soft ink
        "duo_shadow": (13, 17, 23),
        "duo_highlight": (201, 209, 217),
    },
    "light": {
        "bg": "#ffffff",
        "bar": "#f6f8fa",
        "frame": "#d0d7de",
        "fg": "#24292f",
        "key": "#953800",
        "value": "#0550ae",
        "cc": "#6e7781",
        "title": "#57606a",
        "dot_r": "#ff5f56",
        "dot_y": "#ffbd2e",
        "dot_g": "#27c93f",
        # duotone on a light card: ink shadows into soft paper highlights
        "duo_shadow": (31, 35, 40),
        "duo_highlight": (233, 237, 242),
    },
}

# geometry
BAR_H = 38
PAD = 24
PHOTO_MIN = 260
LABEL_CHARS = 13  # minimum width of the key column, in characters
CHAR_W = 7.9  # monospace advance at font-size 13
FONT_SIZE = 13
LINE_H = 21


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def ensure_avatar(dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000:
        return
    urllib.request.urlretrieve("https://github.com/i-ankitkumar.png?size=400", dest)


def load_config() -> dict:
    return json.loads((ROOT / "config.json").read_text(encoding="utf-8"))


def load_stats() -> dict:
    path = ROOT / "cache" / "stats.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "public_repos": 10,
        "stars": 0,
        "followers": 3,
        "uptime": "8 years",
        "commits_year": None,
    }


def duotone_face(src: Path, out: Path, theme: str, size: int = 420) -> Path:
    """Crop to the face, then map luminance onto a two-colour ramp.

    The ramp keeps the portrait inside the card palette: dark theme fades the
    shadows into the card, light theme fades the highlights into the paper.
    """
    t = THEMES[theme]
    img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    img = card_face_crop(img)
    w, h = img.size
    side = min(w, h)
    img = img.crop(((w - side) // 2, (w - side) // 2, (w - side) // 2 + side, (w - side) // 2 + side))
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(1.14)

    gray = ImageOps.grayscale(img)
    gray = ImageOps.autocontrast(gray, cutoff=1)
    shadow, highlight = t["duo_shadow"], t["duo_highlight"]
    luts = []
    for c in range(3):
        luts.append(
            gray.point(
                [int(shadow[c] + (highlight[c] - shadow[c]) * (i / 255.0)) for i in range(256)]
            )
        )
    duo = Image.merge("RGB", luts)

    out.parent.mkdir(parents=True, exist_ok=True)
    duo.save(out, format="JPEG", quality=90, optimize=True)
    return out


def build_rows(cfg: dict) -> list[tuple[str, str, str]]:
    """Right-column rows as (kind, key, value). kind: row | section | blank | header | rule."""
    rows: list[tuple[str, str, str]] = []
    rows.append(("header", "", cfg["user_at_host"]))
    rows.append(("rule", "", ""))
    for key, value in cfg["bio"].items():
        rows.append(("row", key, str(value)))
    rows.append(("blank", "", ""))
    rows.append(("section", "Contact", ""))
    for label, value in cfg["contact"].items():
        rows.append(("row", label, value))
    return rows


def build_stat_rows(stats: dict) -> list[tuple[str, str]]:
    """Left-column rows, under the photo.

    Only signals a recruiter cannot read off GitHub's own chrome stay here.
    The repo count is deliberately absent: GitHub prints it in the tab bar
    directly above the card, and a card counter that disagrees with the
    platform's own number (the nav counts differently from the API) reads
    as a bug. The contribution count is kept because the heatmap further
    down the profile is a shape, not a figure.
    """
    rows: list[tuple[str, str]] = []
    commits = stats.get("commits_year")
    if commits is not None:
        rows.append(("Commits", f"{commits:,} · last 12 months"))
    return rows


def build_svg(mode: str, photo_b64: str, cfg: dict, stats: dict) -> str:
    t = THEMES[mode]
    rows = build_rows(cfg)
    stat_rows = build_stat_rows(stats)

    photo_x = PAD
    photo_y = BAR_H + 26

    # Pass 1: how tall is the right column? The photo is sized to match it,
    # so the card has no dead space under the portrait and the two columns
    # read as one panel instead of a photo with a gap beneath it.
    right_h = 0
    for kind, _, _ in rows:
        right_h += LINE_H // 2 if kind == "blank" else LINE_H

    # the stats block sits under the photo; reserve its height
    stat_block_h = (len(stat_rows) * LINE_H) + (32 if stat_rows else 0)
    photo_h = int(max(PHOTO_MIN, min(right_h - stat_block_h, 360)))

    info_x = photo_x + photo_h + 44
    label_x = info_x + 10
    # the key column is as wide as the longest label, so every value starts
    # on the same x no matter how long its label is
    label_col = max(
        [len(key) for kind, key, _ in rows if kind == "row"]
        + [len(label) for label, _ in stat_rows]
        + [LABEL_CHARS]
    )
    value_x = label_x + (label_col + 2) * CHAR_W

    widest = 0
    for kind, key, value in rows:
        if kind == "row":
            widest = max(widest, len(value))
    width = int(value_x + widest * CHAR_W + PAD)
    width = max(width, 900)

    parts: list[str] = []
    y = photo_y + 2
    for kind, key, value in rows:
        if kind == "blank":
            y += LINE_H // 2
            continue
        if kind == "header":
            parts.append(
                f'<tspan x="{info_x}" y="{y}" fill="{t["fg"]}" font-weight="600">{esc(value)}</tspan>'
            )
            y += LINE_H
            continue
        if kind == "rule":
            rule_w = int(width - info_x - PAD)
            parts.append(
                f'<rect x="{info_x}" y="{y - 11}" width="{rule_w}" height="1" fill="{t["frame"]}"/>'
            )
            y += LINE_H
            continue
        if kind == "section":
            parts.append(
                f'<tspan x="{info_x}" y="{y}" fill="{t["cc"]}">—</tspan>'
                f'<tspan x="{info_x + 16}" fill="{t["key"]}" font-weight="600">{esc(key)}</tspan>'
            )
            y += LINE_H
            continue
        # row: label in the key column, dotted leader fills the gap, value
        # starts on a single fixed x so every value lines up down the card.
        label = key if len(key) <= label_col else key[: label_col - 1] + "…"
        dot_start = label_x + len(label) * CHAR_W + 10
        dot_room = int((value_x - dot_start - 12) / CHAR_W)
        dots = "." * max(1, dot_room)
        parts.append(
            f'<tspan x="{label_x}" y="{y}" fill="{t["key"]}">{esc(label)}</tspan>'
            f'<tspan x="{dot_start}" y="{y}" fill="{t["cc"]}">{esc(dots)}</tspan>'
            f'<tspan x="{value_x}" y="{y}" fill="{t["value"]}">{esc(value)}</tspan>'
        )
        y += LINE_H

    # left column: stats under the photo
    stat_y = photo_y + photo_h + 32
    stat_parts: list[str] = []
    for label, value in stat_rows:
        value_start = photo_x + photo_h - len(value) * CHAR_W
        dot_start = photo_x + len(label) * CHAR_W + 10
        dot_room = int((value_start - dot_start - 14) / CHAR_W)
        stat_parts.append(
            f'<tspan x="{photo_x}" y="{stat_y}" fill="{t["key"]}">{esc(label)}</tspan>'
            f'<tspan x="{dot_start}" y="{stat_y}" fill="{t["cc"]}">{esc("." * max(1, dot_room))}</tspan>'
            f'<tspan x="{value_start}" y="{stat_y}" fill="{t["value"]}">{esc(value)}</tspan>'
        )
        stat_y += LINE_H

    height = max(photo_y + photo_h + PAD, int(y + 6), int(stat_y + 6))
    title = cfg.get("window_title", f"{cfg['username']} / README.md")

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{width}" height="{height}" viewBox="0 0 {width} {height}"
     font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace"
     font-size="{FONT_SIZE}px" role="img"
     aria-label="{esc(cfg['display_name'])} — GitHub profile">
  <title>{esc(cfg['display_name'])} — GitHub Profile</title>
  <desc>{esc(cfg['display_name'])}. {esc(cfg.get('bio', {}).get('Role', ''))}. Based in {esc(cfg.get('bio', {}).get('Location', ''))}.</desc>
  <style><![CDATA[
    .key {{ fill: {t['key']}; }}
    .value {{ fill: {t['value']}; }}
    .cc {{ fill: {t['cc']}; }}
    text, tspan {{ white-space: pre; }}
  ]]></style>
  <defs>
    <clipPath id="faceClip">
      <rect x="{photo_x}" y="{photo_y}" width="{photo_h}" height="{photo_h}" rx="10" ry="10"/>
    </clipPath>
  </defs>
  <rect width="100%" height="100%" rx="10" fill="{t['bg']}"/>
  <rect width="100%" height="{BAR_H}" rx="10" fill="{t['bar']}"/>
  <rect y="{BAR_H - 14}" width="100%" height="14" fill="{t['bar']}"/>
  <circle cx="20" cy="19" r="5" fill="{t['dot_r']}"/>
  <circle cx="37" cy="19" r="5" fill="{t['dot_y']}"/>
  <circle cx="54" cy="19" r="5" fill="{t['dot_g']}"/>
  <text x="{width / 2}" y="23" text-anchor="middle" fill="{t['title']}" font-size="12px">{esc(title)}</text>
  <rect x="{photo_x - 1}" y="{photo_y - 1}" width="{photo_h + 2}" height="{photo_h + 2}" rx="11"
        fill="none" stroke="{t['frame']}" stroke-width="1"/>
  <image x="{photo_x}" y="{photo_y}" width="{photo_h}" height="{photo_h}"
         clip-path="url(#faceClip)" preserveAspectRatio="xMidYMid slice"
         href="data:image/jpeg;base64,{photo_b64}"
         xlink:href="data:image/jpeg;base64,{photo_b64}"/>
  <text x="{info_x}" y="{photo_y + 2}" fill="{t['fg']}" xml:space="preserve">
    {''.join(parts)}
  </text>
  <text x="{photo_x}" y="{photo_y + photo_h + 32}" fill="{t['fg']}" xml:space="preserve">
    {''.join(stat_parts)}
  </text>
</svg>
'''


def main() -> None:
    cfg = load_config()
    (ROOT / "cache").mkdir(exist_ok=True)
    (ROOT / "assets").mkdir(exist_ok=True)

    portrait = ROOT / "assets" / "portrait.png"
    if not portrait.exists():
        ensure_avatar(ROOT / "assets" / "avatar.png")
        portrait = ROOT / "assets" / "avatar.png"
    else:
        ensure_avatar(ROOT / "assets" / "avatar.png")

    try:
        w = int(cfg.get("ascii", {}).get("width", 52))
        h = int(cfg.get("ascii", {}).get("height", 28))
        save_ascii_cache(image_to_ascii(portrait, width=w, height=h), ROOT / "cache" / "ascii.txt")
    except Exception as exc:  # noqa: BLE001
        print(f"warn: ascii cache skipped: {exc}")

    stats = load_stats()
    for mode, name in (("dark", "dark_mode.svg"), ("light", "light_mode.svg")):
        photo = duotone_face(portrait, ROOT / f"assets/face_{mode}.jpg", mode)
        photo_b64 = base64.b64encode(photo.read_bytes()).decode("ascii")
        (ROOT / name).write_text(build_svg(mode, photo_b64, cfg, stats), encoding="utf-8")
        size = (ROOT / name).stat().st_size
        print(f"Wrote {name} ({size:,} bytes)")
        if size > 250_000:
            raise SystemExit(f"{name} exceeds GitHub's 250 KB profile-image cap")


if __name__ == "__main__":
    main()
