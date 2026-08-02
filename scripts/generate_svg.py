#!/usr/bin/env python3
"""Generate Andrew6rant-style neofetch profile SVGs (dark + light).

Left: identifiable face crop photo (ASCII from busy photos rarely reads).
Right: classic neofetch dotted key/value panel.
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
from ascii_from_avatar import _face_crop, image_to_ascii, save_ascii_cache  # noqa: E402

THEMES = {
    "dark": {
        "bg": "#161b22",
        "fg": "#c9d1d9",
        "key": "#ffa657",
        "value": "#a5d6ff",
        "cc": "#616e7f",
        "title": "#8b949e",
        "dot_r": "#ff5f56",
        "dot_y": "#ffbd2e",
        "dot_g": "#27c93f",
        "bar": "#21262d",
        "frame": "#30363d",
    },
    "light": {
        "bg": "#ffffff",
        "fg": "#24292f",
        "key": "#953800",
        "value": "#0550ae",
        "cc": "#8c959f",
        "title": "#57606a",
        "dot_r": "#ff5f56",
        "dot_y": "#ffbd2e",
        "dot_g": "#27c93f",
        "bar": "#f6f8fa",
        "frame": "#d0d7de",
    },
}


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


def prepare_face_jpg(src: Path, out: Path, size: int = 400) -> Path:
    img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    img = _face_crop(img)
    w, h = img.size
    side = min(w, h)
    img = img.crop(
        ((w - side) // 2, (h - side) // 2, (w - side) // 2 + side, (h - side) // 2 + side)
    )
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(1.12)
    img = ImageEnhance.Color(img).enhance(1.05)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="JPEG", quality=88, optimize=True)
    return out


def dotted_row(label: str, value: str, width: int = 48) -> tuple[str, str, str]:
    prefix = f"{label}:"
    room = max(3, width - len(prefix) - len(value))
    return label, " " + ("." * room) + " ", value


def render_info_lines(cfg: dict, stats: dict) -> list[tuple[str, str]]:
    lines: list[tuple[str, str]] = []
    user_at = cfg["user_at_host"]
    lines.append(("header", user_at))
    lines.append(("rule", "─" * max(28, len(user_at) + 8)))
    bio = dict(cfg["bio"])
    bio["Uptime"] = stats.get("uptime", bio.get("Uptime", ""))
    for key in [
        "OS",
        "Uptime",
        "Host",
        "Kernel",
        "Shell",
        "Languages.Stack",
        "Languages.Cloud",
        "Languages.Data",
        "Focus",
        "Location",
    ]:
        if bio.get(key):
            lines.append(("row", json.dumps({"label": key, "value": str(bio[key])})))
    lines.append(("blank", ""))
    lines.append(("section", "Contact"))
    for label, value in cfg["contact"].items():
        lines.append(("row", json.dumps({"label": label, "value": value})))
    lines.append(("blank", ""))
    lines.append(("section", "GitHub Stats"))
    repos, stars, followers = (
        stats.get("public_repos", 0),
        stats.get("stars", 0),
        stats.get("followers", 0),
    )
    commits = stats.get("commits_year")
    lines.append(("row", json.dumps({"label": "Repos", "value": f"{repos} | Stars: {stars}"})))
    if commits is not None:
        lines.append(
            (
                "row",
                json.dumps(
                    {"label": "Commits", "value": f"{commits:,} | Followers: {followers}"}
                ),
            )
        )
    else:
        lines.append(("row", json.dumps({"label": "Followers", "value": str(followers)})))
    return lines


def build_svg(mode: str, face_b64: str, cfg: dict, stats: dict) -> str:
    t = THEMES[mode]
    font_size, line_h, pad = 14, 19, 16
    photo, photo_x, photo_y = 360, pad + 8, 52
    info_x = photo_x + photo + 36
    width = int(info_x + 540)
    title = f"{cfg['username']} / README.md"

    info_parts, y, col_width = [], photo_y + 8, 50
    for kind, payload in render_info_lines(cfg, stats):
        if kind == "blank":
            y += line_h // 2
            continue
        if kind == "header":
            info_parts.append(
                f'<tspan x="{info_x}" y="{y}" fill="{t["fg"]}" font-weight="700">{esc(payload)}</tspan>'
            )
            y += line_h
            continue
        if kind == "rule":
            info_parts.append(f'<tspan x="{info_x}" y="{y}" class="cc">{esc(payload)}</tspan>')
            y += line_h
            continue
        if kind == "section":
            info_parts.append(
                f'<tspan x="{info_x}" y="{y}" class="cc">- </tspan><tspan class="key">{esc(payload)}</tspan>'
            )
            y += line_h
            continue
        data = json.loads(payload)
        label, dots, value = dotted_row(data["label"], data["value"], col_width)
        if "." in label:
            a, b = label.split(".", 1)
            label_xml = (
                f'<tspan class="key">{esc(a)}</tspan><tspan class="cc">.</tspan>'
                f'<tspan class="key">{esc(b)}</tspan>'
            )
        else:
            label_xml = f'<tspan class="key">{esc(label)}</tspan>'
        info_parts.append(
            f'<tspan x="{info_x}" y="{y}" class="cc">. </tspan>{label_xml}'
            f'<tspan class="cc">:</tspan><tspan class="cc">{esc(dots)}</tspan>'
            f'<tspan class="value">{esc(value)}</tspan>'
        )
        y += line_h

    height = max(int(photo_y + photo + pad + 24), int(y + pad + 8))
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{width}" height="{height}"
     font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
     font-size="{font_size}px" role="img"
     aria-label="{esc(cfg['display_name'])} — neofetch-style GitHub profile">
  <title>{esc(cfg['display_name'])} · GitHub Profile</title>
  <style><![CDATA[
    .key {{ fill: {t['key']}; }}
    .value {{ fill: {t['value']}; }}
    .cc {{ fill: {t['cc']}; }}
    text, tspan {{ white-space: pre; }}
  ]]></style>
  <defs>
    <clipPath id="faceClip">
      <rect x="{photo_x}" y="{photo_y}" width="{photo}" height="{photo}" rx="12" ry="12"/>
    </clipPath>
  </defs>
  <rect width="100%" height="100%" rx="12" fill="{t['bg']}"/>
  <rect width="100%" height="36" rx="12" fill="{t['bar']}"/>
  <rect y="20" width="100%" height="16" fill="{t['bar']}"/>
  <circle cx="22" cy="18" r="5" fill="{t['dot_r']}"/>
  <circle cx="40" cy="18" r="5" fill="{t['dot_y']}"/>
  <circle cx="58" cy="18" r="5" fill="{t['dot_g']}"/>
  <text x="{width/2}" y="22" text-anchor="middle" fill="{t['title']}" font-size="12px">{esc(title)}</text>
  <rect x="{photo_x-1}" y="{photo_y-1}" width="{photo+2}" height="{photo+2}" rx="13"
        fill="none" stroke="{t['frame']}" stroke-width="1"/>
  <image x="{photo_x}" y="{photo_y}" width="{photo}" height="{photo}"
         clip-path="url(#faceClip)" preserveAspectRatio="xMidYMid slice"
         href="data:image/jpeg;base64,{face_b64}"
         xlink:href="data:image/jpeg;base64,{face_b64}"/>
  <text x="{info_x}" y="{photo_y+8}" fill="{t['fg']}" xml:space="preserve">
    {''.join(info_parts)}
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

    face = prepare_face_jpg(portrait, ROOT / "assets" / "face.jpg", size=400)
    face_b64 = base64.b64encode(face.read_bytes()).decode("ascii")

    try:
        w = int(cfg.get("ascii", {}).get("width", 52))
        h = int(cfg.get("ascii", {}).get("height", 28))
        save_ascii_cache(image_to_ascii(portrait, width=w, height=h), ROOT / "cache" / "ascii.txt")
    except Exception as exc:  # noqa: BLE001
        print(f"warn: ascii cache skipped: {exc}")

    stats = load_stats()
    for mode, name in (("dark", "dark_mode.svg"), ("light", "light_mode.svg")):
        (ROOT / name).write_text(build_svg(mode, face_b64, cfg, stats), encoding="utf-8")
        print(f"Wrote {name} ({(ROOT / name).stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
