# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

The portfolio serves three layered audiences. A visitor should self-select into the right depth within five seconds, then get richer content if they stay.

- **Primary: technical recruiters in Germany.** Scanning the GitHub profile README or landing on iankitkumar.in during a sourcing pass. They want a fast yes/no on fit: location, eligibility, stack, seniority, contact.
- **Secondary: DevOps / SRE hiring managers.** Will dig past the first fold for evidence of scope, scale, and recent work. Want credible claims and easy access to deeper material (blog, GitHub, LinkedIn).
- **Tertiary: peers in the DevOps and MLOps community.** Visiting for reasons other than hiring: project interest, terminal aesthetic, conversation starters. Care about voice, taste, and what is worth talking about.

Decision shape the design must protect: the first five seconds answer the recruiter's question; the rest serves managers and peers without contradicting the first impression.

## Product Purpose

Ankit Kumar's personal site and GitHub profile presence. It communicates a DevOps / Cloud / MLOps identity and the current open-to-DevOps/SRE-in-Germany status at a glance, and it routes interested visitors to the right follow-up surface (blog, GitHub, LinkedIn).

Success looks like: a recruiter or manager can confirm fit (Germany-bound, EU Blue Card eligible, RHCSA + Terraform Associate + Azure, comfortable with MLOps crossover) from the profile alone, without needing to ask. Failure looks like: a visitor leaves unsure of location, eligibility, or how to make contact.

## Positioning

Layered, with a deliberate order:

1. **Germany-bound DevOps engineer with EU Blue Card eligibility.** This is the lead. Anchored by verified certs (RHCSA, Terraform Associate, AZ-104, AZ-900, AI-900) and real language claims (German A1, English C1).
2. **MLOps crossover as a differentiator.** A DevOps engineer also fluent in Pandas, NumPy, TensorFlow, Keras is rare; it widens the role space from pure platform engineering into ML platform / MLOps work.
3. **Terminal / CLI aesthetic as deliberate brand choice.** The neofetch-style card is the visual identity. A neighboring portfolio can copy any single layer; the combination of (1) + (2) dressed in (3) is the actual position.

Mechanism: the visible artifact is a system-summary card (neofetch), not a marketing page. The format implies a sysadmin, which is the brand.

## Operating Context

- Visitor path: GitHub profile (avatar / README) → iankitkumar.in (deeper) → blog.iankitkumar.in (writing) → LinkedIn / GitHub / email contact. The portfolio is the routing surface, not the destination; each surface answers a different depth of the same question.
- Two products serve the same identity, see `## Surfaces` below. They are designed to read as one person across GitHub, the personal domain, and the blog.
- No build pipeline, no bundler, no framework on either surface. Both are static and config-driven so a content change is a single-file edit and a deploy.

## Surfaces

The product ships across two repos and a third separate one. They share the audience, positioning, evidence, principles, and brand commitments above. They differ in stack, output, and operating constraints. The durable product truth lives in this file; the per-surface detail lives here so the two repos can stay in lockstep without duplication.

### Surface 1 — GitHub profile cards (neofetch SVGs)

- **Repo**: `github.com/i-ankitkumar/i-ankitkumar`
- **Stack**: Python 3.12 + Pillow + chafa (chafa is CI-only)
- **Output**: `dark_mode.svg` and `light_mode.svg`, ~120 KB each, well under GitHub's 250 KB profile-image cap
- **Where it renders**: GitHub profile README (img tag), and as a fallback art element on iankitkumar.in
- **CI**: GitHub Actions cron `30 6 * * *` and on push of `config.json`, `scripts/**`, `assets/portrait.png`, or the workflow file. Generated artifacts are committed back to the repo
- **Local override**: `assets/portrait.png` overrides the GitHub avatar for the ASCII side. The auto-refresh must not silently replace it
- **Customization point**: `config.json` (bio, contact, ascii source). The generator and SVGs are derived; edit the generator and the config, not the SVGs
- **What this surface does NOT do**: it does not host a blog, host a CV PDF, or run an interactive terminal. It is the static identity card

### Surface 2 — Live site at iankitkumar.in

- **Repo**: `github.com/i-ankitkumar/iankitkumar.in`
- **Stack**: Plain static HTML / CSS / JS, config-driven. No build step, no bundler
- **Template**: Forked and adapted from [`LucidAkshay/operator-portfolio`](https://github.com/LucidAkshay/operator-portfolio) (MIT). Template attribution lives in the footer; keep it
- **Output**: `index.html` (11 KB) + `style.css` (58 KB) + `script.js` (34 KB) + `config.js` (14 KB) + `assets/photo.jpg` (234 KB) + `assets/favicon.svg` + `assets/resume.pdf` + `assets/og-preview.png`
- **Hosting**: Cloudflare Pages, project name `iankitkumar-in`, branch `main`
- **Deploy**: `wrangler pages deploy . --project-name=iankitkumar-in --branch=main --commit-dirty=true`
- **Local dev**: `python3 -m http.server 5173` (any static server works; no build)
- **Customization point**: `config.js` (bio, experience, projects, certs, links). Most page content renders from that file
- **What this surface does NOT do**: it does not host a blog (separate repo, see below), it does not generate the SVGs (Surface 1), it does not run a backend. All interactivity is client-side JS

### Surface 3 — Blog at blog.iankitkumar.in (separate repo)

- **Repo**: `github.com/i-ankitkumar/blog.iankitkumar.in`
- **Stack**: Astro + Tailwind + Content Collections, theme `Brutal` (ElianCodes)
- **Hosting**: Cloudflare Pages, project name `blog-iankitkumar-in`
- **Customization point**: Markdown in `src/data/blog/`
- **What this surface does NOT do**: it is a writing surface, not an identity surface. The terminal aesthetic does not apply to the blog theme; the blog is allowed to feel like a blog. PRODUCT.md applies only in the parts that don't conflict (audience, voice, evidence)

## Capabilities and Constraints

**Capabilities (confirmed):**

- Generates a dark-theme and a light-theme SVG in lockstep from a single `config.json`.
- Pulls live GitHub stats into `cache/stats.json` during regen.
- Renders an ASCII art side from a local portrait (face crop), with GitHub avatar as a fallback.
- Auto-refreshes on a nightly cron and on relevant pushes; no manual sync needed.
- Rendered surface is the same set of files for GitHub profile, iankitkumar.in, and blog.

**Constraints (binding):**

- Every claim is verifiable and must remain so. Cert list (RHCSA, Terraform Associate, AZ-104, AZ-900, AI-900), language levels (German A1, English C1), and EU Blue Card eligibility are factual. Future design work must not invent additional certs, client logos, testimonials, employers, or metrics.
- SVGs must stay under GitHub's 250 KB profile-image cap. Current size is 120 KB; any growth plan needs to defend its bytes.
- Dark and light themes must move together. Changing one without the other is a defect.
- `config.json` is the source of truth for all visible copy. Editing the SVGs by hand is wrong; editing the generator is right.
- EU Blue Card eligibility is a legal status. Stating it weakly to avoid legal concern is a failure; stating it correctly is the job.
- Generated artifacts (`dark_mode.svg`, `light_mode.svg`, `cache/stats.json`, `cache/ascii.txt`, `assets/face.jpg`) are committed and tracked; the `avatar.png` cache is allowed to be refreshed.
- Monospace and the GitHub-style dark palette are part of the brand. A pivot to a sans-serif / SaaS-template look would be a rebrand, not a redesign.

**Deliberately undecided (do not invent in future work):**

- Specific employers and project names beyond what is already in `config.json`.
- A written bio longer than what the card carries today.
- Testimonials, case studies, or press.
- Pricing / availability windows / response-time SLAs.
- A native iOS or Android app. The portfolio is web-only.

## Brand Commitments

- **Terminal / CLI aesthetic is binding.** The neofetch card is the identity, not a decoration. Future work preserves the form factor (system-summary style, monospace, key/value pairs, ASCII side) unless the user explicitly reopens the brand.
- **Real name and identity.** "Ankit Kumar", handle `i-ankitkumar`, host label `ankit@ops`. These are the brand; fictional personas are not.
- **Honest voice.** No marketing copy. If a statement is a fact (cert, level, eligibility), it is stated as a fact. If it is a value claim, it is softened or omitted.
- **Dark theme is the default.** Light theme exists for the visitors who need it, not as a co-equal brand.

## Evidence on Hand

- `config.json` — drives every visible label, both themes, contact links.
- `assets/portrait.png` — local face source for the ASCII side (do not silently overwrite).
- `cache/stats.json`, `cache/ascii.txt` — generated by the workflow; reflect live GitHub state at last regen.
- `dark_mode.svg`, `light_mode.svg` — current visible artifacts, ~120 KB each.
- Live surfaces: `github.com/i-ankitkumar` (profile README), `iankitkumar.in` (deeper site), `blog.iankitkumar.in` (writing).
- Verified certs: RHCSA, Terraform Associate, AZ-104, AZ-900, AI-900.
- Self-reported language levels: German A1, English C1.
- Contact links present in `config.json`: GitHub, LinkedIn, Twitter, YouTube, Instagram.

**Absences future work must not fabricate:** case studies, named employers beyond the current role, named clients, named scale (requests/sec, user counts, cost savings), testimonials, conference talks, awards, press.

## Product Principles

1. **Factual over flattering.** Every claim is verifiable. The design's job is to surface real evidence, not to persuade with invented detail.
2. **Skim-first, depth-on-demand.** The first five seconds must answer the recruiter's question. Richer content only appears when the visitor wants more, and never contradicts the first impression.
3. **One identity, three surfaces.** GitHub profile, iankitkumar.in, and blog must read as the same person. The terminal aesthetic is the spine that holds them together.
4. **Generated, not hand-edited.** The SVGs are a build output. Editing them by hand is wrong; editing `config.json` and the generator is right. The discipline is what makes the work feel real instead of faked.
5. **Quiet wins on the noise floor.** This is a personal profile, not a marketing site. Restraint is the move; the terminal aesthetic reads as intentional precisely because it doesn't shout.

## Accessibility & Inclusion

- Both themes must meet WCAG AA contrast for the key/value text in the card. Current dark theme: bg `#161b22`, key `#ffa657`, value `#a5d6ff`. Light theme: bg `#ffffff`, key `#953800`, value `#0550ae`. Any palette change must defend both pairs against AA (4.5:1 for body text, 3:1 for large text).
- When the SVG is consumed standalone (not as a README inline), it must include `<title>` and `<desc>` elements so screen readers can announce what the card is.
- Copy is in English at a C1 register. Avoid marketing-style superlatives; favor plain, factual phrasing. Visitors whose first language is not English should not need to fight the copy.
- The ASCII side is decorative. A visitor using a screen reader or `prefers-reduced-motion` should still get the key/value content from the SVG.
- No flashing or motion in the card itself. Any animation added later must respect `prefers-reduced-motion`.
