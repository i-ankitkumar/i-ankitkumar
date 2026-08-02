#!/usr/bin/env python3
"""Generate Andrew6rant-style neofetch profile SVGs (dark + light)."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

from ascii_from_avatar import image_to_ascii, save_ascii_cache

ROOT = Path(__file__).resolve().parents[1]

THEMES = {
    "dark": {
        "bg": "#161b22",
        "fg": "#c9d1d9",
        "key": "#ffa657",
        "value": "#a5d6ff",
        "cc": "#616e7f",
        "add": "#3fb950",
        "del": "#f85149",
        "ascii": "#c9d1d9",
        "title": "#8b949e",
        "dot_r": "#ff5f56",
        "dot_y": "#ffbd2e",
        "dot_g": "#27c93f",
        "bar": "#21262d",
    },
    "light": {
        "bg": "#ffffff",
        "fg": "#24292f",
        "key": "#953800",
        "value": "#0550ae",
        "cc": "#8c959f",
        "add": "#1a7f37",
        "del": "#cf222e",
        "ascii": "#24292f",
        "title": "#57606a",
        "dot_r": "#ff5f56",
        "dot_y": "#ffbd2e",
        "dot_g": "#27c93f",
        "bar": "#f6f8fa",
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
    url = "https://github.com/i-ankitkumar.png?size=400"
    urllib.request.urlretrieve(url, dest)


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


def dotted_row(label: str, value: str, width: int = 48) -> tuple[str, str, str]:
    """Return (label, dots, value) padded to approximate neofetch width."""
    prefix = f"{label}:"
    room = max(3, width - len(prefix) - len(value))
    dots = " " + ("." * room) + " "
    return label, dots, value


def render_info_lines(cfg: dict, stats: dict) -> list[tuple[str, str]]:
    """List of (kind, payload) where kind is header|rule|section|row|blank."""
    lines: list[tuple[str, str]] = []
    user_at = cfg["user_at_host"]
    lines.append(("header", user_at))
    lines.append(("rule", "─" * max(28, len(user_at) + 8)))

    bio = dict(cfg["bio"])
    bio["Uptime"] = stats.get("uptime", bio.get("Uptime", ""))
    # Keep a stable order
    order = [
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
    ]
    for key in order:
        if key in bio and bio[key]:
            lines.append(("row", json.dumps({"label": key, "value": str(bio[key])})))

    lines.append(("blank", ""))
    lines.append(("section", "Contact"))
    for label, value in cfg["contact"].items():
        lines.append(("row", json.dumps({"label": label, "value": value})))

    lines.append(("blank", ""))
    lines.append(("section", "GitHub Stats"))
    repos = stats.get("public_repos", 0)
    stars = stats.get("stars", 0)
    followers = stats.get("followers", 0)
    commits = stats.get("commits_year")
    repo_line = f"{repos} | Stars: {stars}"
    lines.append(("row", json.dumps({"label": "Repos", "value": repo_line})))
    if commits is not None:
        commit_line = f"{commits:,} | Followers: {followers}"
        lines.append(("row", json.dumps({"label": "Commits", "value": commit_line})))
    else:
        lines.append(
            ("row", json.dumps({"label": "Followers", "value": str(followers)}))
        )
    return lines


def build_svg(mode: str, ascii_lines: list[str], cfg: dict, stats: dict) -> str:
    t = THEMES[mode]
    font_size = 13
    line_h = 18
    pad = 16
    char_w = 7.8  # conservative advance so values don't clip
    ascii_x = pad
    ascii_y0 = 52
    info_x = pad + len(ascii_lines[0]) * char_w + 28
    width = max(1050, int(info_x + 580))
    height = int(ascii_y0 + max(len(ascii_lines), 26) * line_h + pad + 4)

    # ASCII block
    ascii_tspans = []
    for i, line in enumerate(ascii_lines):
        y = ascii_y0 + i * line_h
        ascii_tspans.append(
            f'<tspan x="{ascii_x}" y="{y}">{esc(line)}</tspan>'
        )

    # Info block
    info_lines = render_info_lines(cfg, stats)
    info_parts = []
    y = ascii_y0
    col_width = 54

    for kind, payload in info_lines:
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
            info_parts.append(
                f'<tspan x="{info_x}" y="{y}" class="cc">{esc(payload)}</tspan>'
            )
            y += line_h
            continue
        if kind == "section":
            info_parts.append(
                f'<tspan x="{info_x}" y="{y}" class="cc">- </tspan>'
                f'<tspan class="key">{esc(payload)}</tspan>'
            )
            y += line_h
            continue
        if kind == "row":
            data = json.loads(payload)
            label, dots, value = dotted_row(data["label"], data["value"], col_width)
            # Nested labels: Languages.Stack → two key spans
            if "." in label:
                a, b = label.split(".", 1)
                label_xml = (
                    f'<tspan class="key">{esc(a)}</tspan>'
                    f'<tspan class="cc">.</tspan>'
                    f'<tspan class="key">{esc(b)}</tspan>'
                )
            else:
                label_xml = f'<tspan class="key">{esc(label)}</tspan>'
            info_parts.append(
                f'<tspan x="{info_x}" y="{y}" class="cc">. </tspan>'
                f"{label_xml}"
                f'<tspan class="cc">:</tspan>'
                f'<tspan class="cc">{esc(dots)}</tspan>'
                f'<tspan class="value">{esc(value)}</tspan>'
            )
            y += line_h

    height = max(height, int(y + pad + 8))
    title = f"{cfg['username']} / README.md"

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace"
     font-size="{font_size}px" role="img"
     aria-label="{esc(cfg['display_name'])} — neofetch-style GitHub profile">
  <title>{esc(cfg['display_name'])} · GitHub Profile</title>
  <style><![CDATA[
    .key {{ fill: {t['key']}; }}
    .value {{ fill: {t['value']}; }}
    .cc {{ fill: {t['cc']}; }}
    text, tspan {{ white-space: pre; }}
  ]]></style>
  <rect width="100%" height="100%" rx="12" fill="{t['bg']}"/>
  <rect width="100%" height="36" rx="12" fill="{t['bar']}"/>
  <rect y="20" width="100%" height="16" fill="{t['bar']}"/>
  <circle cx="22" cy="18" r="5" fill="{t['dot_r']}"/>
  <circle cx="40" cy="18" r="5" fill="{t['dot_y']}"/>
  <circle cx="58" cy="18" r="5" fill="{t['dot_g']}"/>
  <text x="{width / 2}" y="22" text-anchor="middle" fill="{t['title']}" font-size="12px">{esc(title)}</text>

  <text x="{ascii_x}" y="{ascii_y0}" fill="{t['ascii']}" xml:space="preserve">
    {''.join(ascii_tspans)}
  </text>

  <text x="{info_x}" y="{ascii_y0}" fill="{t['fg']}" xml:space="preserve">
    {''.join(info_parts)}
  </text>
</svg>
'''


def main() -> None:
    cfg = load_config()
    (ROOT / "cache").mkdir(exist_ok=True)
    (ROOT / "assets").mkdir(exist_ok=True)

    avatar = ROOT / "assets" / "portrait.png"
    if not avatar.exists():
        avatar = ROOT / "assets" / "avatar.png"
    if cfg.get("ascii", {}).get("source"):
        candidate = ROOT / cfg["ascii"]["source"]
        if candidate.exists():
            avatar = candidate
    # Keep avatar.png in sync for Actions that refresh from GitHub — but prefer portrait when present
    if avatar.name == "portrait.png":
        ensure_avatar(ROOT / "assets" / "avatar.png")  # still refresh github avatar copy
    else:
        ensure_avatar(avatar)

    w = int(cfg.get("ascii", {}).get("width", 48))
    h = int(cfg.get("ascii", {}).get("height", 30))
    ascii_lines = image_to_ascii(avatar, width=w, height=h)
    # Pad lines to equal width
    max_w = max(len(l) for l in ascii_lines)
    ascii_lines = [l.ljust(max_w) for l in ascii_lines]
    save_ascii_cache(ascii_lines, ROOT / "cache" / "ascii.txt")

    stats = load_stats()

    for mode, filename in (("dark", "dark_mode.svg"), ("light", "light_mode.svg")):
        svg = build_svg(mode, ascii_lines, cfg, stats)
        (ROOT / filename).write_text(svg, encoding="utf-8")
        print(f"Wrote {filename} ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
