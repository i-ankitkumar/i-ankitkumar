#!/usr/bin/env python3
"""Fetch GitHub profile stats (REST + optional GraphQL with token)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USERNAME = "i-ankitkumar"


def _get_json(url: str, token: str | None = None) -> dict | list:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-profile-readme",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _graphql(query: str, variables: dict, token: str) -> dict:
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": f"{USERNAME}-profile-readme",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]


def account_uptime(created_at: str) -> str:
    created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    years = now.year - created.year
    months = now.month - created.month
    days = now.day - created.day
    if days < 0:
        months -= 1
        # rough previous month days
        days += 30
    if months < 0:
        years -= 1
        months += 12
    parts = []
    if years:
        parts.append(f"{years} year" + ("s" if years != 1 else ""))
    if months:
        parts.append(f"{months} month" + ("s" if months != 1 else ""))
    if days or not parts:
        parts.append(f"{days} day" + ("s" if days != 1 else ""))
    return ", ".join(parts)


def fetch_stats(username: str = USERNAME) -> dict:
    token = os.environ.get("ACCESS_TOKEN") or os.environ.get("GITHUB_TOKEN")

    user = _get_json(f"https://api.github.com/users/{username}", token)
    repos = []
    page = 1
    while True:
        batch = _get_json(
            f"https://api.github.com/users/{username}/repos?per_page=100&page={page}&type=owner",
            token,
        )
        if not isinstance(batch, list) or not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    stars = sum(r.get("stargazers_count", 0) for r in repos)
    public_repos = user.get("public_repos", len(repos))
    followers = user.get("followers", 0)

    commits = None
    if token:
        try:
            # Last ~1 year window is limited by API; also get totalContributions this year
            q = """
            query($login: String!) {
              user(login: $login) {
                contributionsCollection {
                  contributionCalendar { totalContributions }
                }
              }
            }
            """
            data = _graphql(q, {"login": username}, token)
            commits = data["user"]["contributionsCollection"]["contributionCalendar"][
                "totalContributions"
            ]
        except Exception as exc:  # noqa: BLE001
            print(f"warn: graphql contributions failed: {exc}")

    stats = {
        "username": username,
        "name": user.get("name") or username,
        "public_repos": public_repos,
        "stars": stars,
        "followers": followers,
        "following": user.get("following", 0),
        "uptime": account_uptime(user["created_at"]),
        "created_at": user["created_at"],
        "commits_year": commits,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    return stats


def main() -> None:
    cache = ROOT / "cache"
    cache.mkdir(exist_ok=True)
    try:
        stats = fetch_stats()
    except urllib.error.HTTPError as exc:
        print(f"warn: fetch failed ({exc}); keeping previous cache if any")
        existing = cache / "stats.json"
        if existing.exists():
            return
        stats = {
            "username": USERNAME,
            "name": "Ankit Kumar",
            "public_repos": 10,
            "stars": 0,
            "followers": 3,
            "following": 5,
            "uptime": "8 years",
            "commits_year": None,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    (cache / "stats.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
