#!/usr/bin/env python3
"""Render README.md the way GitHub does, for visual review.

Uses the GitHub markdown API (gfm mode, repo context) so tables, badges and
headings match what a visitor actually sees, then screenshots it with
headless Chromium in both colour schemes.

Usage: python3 scripts/preview_readme.py [--out /tmp]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CSS = """
body{margin:0;background:#0d1117;color:#c9d1d9;
     font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;
     font-size:16px;line-height:1.5}
.wrap{max-width:1012px;margin:0 auto;padding:32px}
.markdown img{max-width:100%}
.markdown table{border-collapse:collapse;margin:16px 0;display:block;overflow:auto;width:max-content;max-width:100%}
.markdown th,.markdown td{border:1px solid #30363d;padding:6px 13px}
.markdown tr:nth-child(2n){background:#161b22}
.markdown h2{border-bottom:1px solid #30363d;padding-bottom:.3em;margin-top:24px}
.markdown h1,.markdown h3{margin-top:24px}
.markdown hr{border:0;border-top:1px solid #30363d;margin:24px 0}
.markdown a{color:#a5d6ff;text-decoration:none}
.markdown a:hover{text-decoration:underline}
.markdown code{background:#21262d;padding:.2em .4em;border-radius:6px;font-size:85%}
.markdown p{margin:16px 0}
.markdown blockquote{border-left:.25em solid #30363d;padding:0 1em;color:#8b949e;margin:0 0 16px}
.markdown ul{margin:16px 0;padding-left:2em}
.markdown li{margin:.25em 0}
.light{background:#ffffff;color:#1f2328}
.light .markdown tr:nth-child(2n){background:#f6f8fa}
.light .markdown th,.light .markdown td{border-color:#d1d9e0}
.light .markdown h2{border-color:#d1d9e0}
.light .markdown hr{border-color:#d1d9e0}
.light .markdown a{color:#0969da}
.light .markdown code{background:#eff1f3}
.light .markdown blockquote{border-color:#d1d9e0;color:#59636e}
"""


def github_markdown(md: str, context: str) -> str:
    req = urllib.request.Request(
        "https://api.github.com/markdown",
        data=json.dumps({"text": md, "mode": "gfm", "context": context}).encode(),
        headers={
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "profile-readme-preview",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode()


def absolutise(html: str) -> str:
    """Point relative ./refs at the local repo so the card renders."""
    html = html.replace('src="./', f'src="file://{ROOT}/')
    html = html.replace('srcset="./', f'srcset="file://{ROOT}/')
    return html


def build_html(md: str, out_dir: Path) -> tuple[Path, Path]:
    body = absolutise(github_markdown(md, "i-ankitkumar/i-ankitkumar"))
    page = (
        "<!doctype html><meta charset=utf-8>"
        f"<style>{CSS}</style>"
        f'<div class=wrap><div class=markdown>{body}</div></div>'
    )
    dark = out_dir / "readme_dark.html"
    light = out_dir / "readme_light.html"
    dark.write_text(page, encoding="utf-8")
    light.write_text(page.replace('class=wrap', 'class="wrap light"'), encoding="utf-8")
    return dark, light


def shoot(html: Path, png: Path, height: int = 2400) -> None:
    subprocess.run(
        [
            "chromium",
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            "--allow-file-access-from-files",
            f"--window-size=1150,{height}",
            f"--screenshot={png}",
            str(html),
        ],
        check=True,
        capture_output=True,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    md = (ROOT / "README.md").read_text(encoding="utf-8")
    dark_html, light_html = build_html(md, out)
    shoot(dark_html, out / "readme_dark.png")
    shoot(light_html, out / "readme_light.png")
    print(f"dark:  {out / 'readme_dark.png'}")
    print(f"light: {out / 'readme_light.png'}")


if __name__ == "__main__":
    main()
