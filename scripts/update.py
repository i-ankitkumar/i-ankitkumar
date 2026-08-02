#!/usr/bin/env python3
"""Download avatar, fetch stats, regenerate profile SVGs."""

from __future__ import annotations

import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent


def run(script: str) -> None:
    cmd = [sys.executable, str(SCRIPTS / script)]
    print("+", " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(ROOT))


def refresh_avatar() -> None:
    """Keep GitHub avatar cached, but never overwrite a local portrait.png."""
    dest = ROOT / "assets" / "avatar.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = "https://github.com/i-ankitkumar.png?size=400"
    print(f"Downloading {url}")
    urllib.request.urlretrieve(url, dest)
    portrait = ROOT / "assets" / "portrait.png"
    if portrait.exists():
        print(f"Using local portrait for ASCII: {portrait}")
    else:
        print("No portrait.png — ASCII will use GitHub avatar")


def main() -> None:
    refresh_avatar()
    run("fetch_stats.py")
    run("generate_svg.py")
    print("Done.")


if __name__ == "__main__":
    main()
