#!/usr/bin/env bash
# Update the GitHub profile bio + location for i-ankitkumar.
#
# Why this is a script and not a one-liner:
#   The `gh` token on this machine has scopes 'gist, read:org, repo,
#   workflow'. Updating the profile bio (PATCH /user) needs the 'user'
#   scope, which requires an interactive OAuth refresh. So this script
#   does the refresh itself and then the update — you do not have to
#   paste anything into chat.
#
# What it changes:
#   bio      "DevOps & Cloud Engineer — Azure/AWS, Terraform, Linux,
#             Splunk. Mumbai, India → Germany."
#         -> "Infrastructure Engineer → Software & AI Engineering —
#             Splunk, Azure, AWS, Terraform, MCP. Pune, India →
#             Germany."
#   location "India" -> "Pune, India"
#
# Why: the site and the CV both say Pune, and the old bio said Mumbai.
# The relocation target stays at country level ("Germany") on purpose —
# Heidelberg is partner-linked and the portfolio product truth treats
# relocation specifics as needing sign-off before they go public.

set -euo pipefail

NEW_BIO='Infrastructure Engineer → Software & AI Engineering — Splunk, Azure, AWS, Terraform, MCP. Pune, India → Germany.'
NEW_LOCATION='Pune, India'

echo "=== 1/3 checking the current profile"
CURRENT_BIO="$(gh api user --jq '.bio' 2>/dev/null || echo '<unreadable>')"
echo "current bio: ${CURRENT_BIO}"

if gh api user --jq '.bio' >/dev/null 2>&1; then
  SCOPES="$(curl -sS -H "Authorization: token $(gh auth token)" -I https://api.github.com/user 2>/dev/null \
    | tr -d '\r' | grep -i '^x-oauth-scopes:' | cut -d: -f2- | xargs)"
  case ",${SCOPES}," in
    *,user,*)
      echo "token already has the 'user' scope"
      ;;
    *)
      echo
      echo "=== 2/3 granting the 'user' scope (opens a browser)"
      gh auth refresh -h github.com -s user
      ;;
  esac
else
  echo
  echo "=== 2/3 granting the 'user' scope (opens a browser)"
  gh auth refresh -h github.com -s user
fi

echo
echo "=== 3/3 applying the update"
gh api --method PATCH user \
  -f bio="$NEW_BIO" \
  -f location="$NEW_LOCATION" \
  --jq '{name: .name, bio: .bio, location: .location}'

echo
echo "Done. Verify at https://github.com/i-ankitkumar (the sidebar bio)."
