# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

The portfolio serves three layered audiences. A visitor should self-select into the right depth within five seconds, then get richer content if they stay.

- **Primary: technical recruiters and hiring managers in Germany and the EU.** Scanning a GitHub profile README or landing on iankitkumar.in during a sourcing pass. They want a fast yes/no on fit: location, eligibility, stack, seniority, contact.
- **Secondary: software and AI engineering hiring managers.** Dig past the first fold for evidence of scope, scale, and recent work. Want credible claims, easy access to deeper material, and a sense of whether the candidate can ship.
- **Tertiary: peers in DevOps, SRE, MLOps, and AI-engineering communities.** Visiting for reasons other than hiring: project interest, voice, taste, conversation starters.

Decision shape the design must protect: the first five seconds answer the recruiter's question; the rest serves managers and peers without contradicting the first impression.

## Product Purpose

Ankit Kumar's personal site and GitHub profile presence. It communicates an **infrastructure engineer transitioning into software and AI engineering**, anchored in real Splunk, Azure, AWS, Terraform, MCP, and AI-powered security work, and routes interested visitors to the right follow-up surface (resume, GitHub, LinkedIn, blog).

Success looks like: a recruiter or manager can confirm fit (Pune, relocating to Germany, EU Blue Card eligible, Splunk multi-site + Azure + AWS + Terraform + MCP, comfortable with software and AI engineering crossover) from the profile alone, without needing to ask. Failure looks like: a visitor leaves unsure of location, eligibility, or how to make contact.

## Positioning

Layered, with a deliberate order:

1. **Infrastructure engineer → software & AI engineering.** This is the lead. The "becoming" arrow is the brand. Built on real production ownership at Wolters Kluwer (Splunk multi-site, Azure, Terraform, CI/CD) and real software/AI work in the open (MCP servers, AI-assisted Splunk tooling, ML security research).
2. **Reliability + operability in the bones.** Defined RPO/RTO, audit-ready telemetry, change control that doesn't fight the team. These are the boring skills that matter in production and that the new direction inherits, not replaces.
3. **One identity, three surfaces.** The career arc is the story; each surface renders it in its own idiom — the profile card in a terminal register, the portfolio site in a typographic register, the blog in its own theme. The claim set and the voice stay identical.

Mechanism: the visible artifacts are a system-summary card and a long-form profile page. Both imply a practitioner who ships and documents, which is the brand.

## Operating Context

- Visitor path: search or LinkedIn → iankitkumar.in (deeper) → GitHub / LinkedIn / email contact. The portfolio is the routing surface, not the destination.
- Three products serve the same identity. They are designed to read as one person across GitHub, the personal domain, and the blog.
- Static, content-driven, no backend. Every fact lives in a content collection; any unverifiable claim carries a `confirm: true` flag rendered as a `verify` badge.

## Surfaces

The product ships across three repos. They share the audience, positioning, evidence, principles, and brand commitments above. They differ in stack, output, and operating constraints. The durable product truth lives in this file; the per-surface detail lives in each repo's PRODUCT.md so each surface can stay in lockstep without duplication.

### Surface 1 — GitHub profile card (terminal register)

- **Repo**: `github.com/i-ankitkumar/i-ankitkumar`
- **Stack**: Python 3.12 + Pillow (chafa is CI-only, for the ASCII cache)
- **Output**: `dark_mode.svg` and `light_mode.svg`, ~110 KB each, well under GitHub's 250 KB profile-image cap
- **Where it renders**: GitHub profile README (img tag, `?v=4` cache-buster)
- **CI**: GitHub Actions cron `30 6 * * *` and on push of `config.json`, `scripts/**`, `assets/portrait.png`, or the workflow file. Generated artifacts are committed back to the repo
- **Local override**: `assets/portrait.png` overrides the GitHub avatar for the face crop. The auto-refresh must not silently replace it
- **Customization point**: `config.json` (bio rows, contact links, window title). The generator and SVGs are derived; edit the generator and the config, not the SVGs
- **Visual register**: the terminal/CLI idiom is the binding aesthetic for this surface. Monospace, a window chrome bar, and key/value rows are the brand here and are not replaced by the portfolio site's typographic register
- **Card content rules** (binding, added 2026-11-01):
  - **No cosplay fields.** Nothing is labelled `OS`, `Uptime`, `Host`, `Kernel`, or `Shell`. Those labels were a neofetch costume: "Uptime: 8 years" was a GitHub account age, not career tenure, and "Kernel: Cloud · Automation" was not a kernel. A row that cannot be verified as its label claims is a defect.
  - **Every row is a verified fact from `career-ops/cv.md`** — role, focus, stack, cloud, AI practice, scale, impact, certs, location. No value claim, no marketing copy.
  - **The value column is a fixed grid.** The key column is sized to the longest label so every value starts on the same x. Ragged value alignment was a visible defect of the previous card.
  - **The photo is duotoned**, not full colour, so the portrait sits inside the palette instead of fighting it. Dark theme ramps shadows to the card background; light theme ramps ink to soft paper. A negative-looking light-theme photo is a defect.
  - **The card answers the recruiter's question, the README carries the argument.** The card is the five-second read; the README is the depth. They must not duplicate each other.
- **What this surface does NOT do**: it does not host the portfolio, host a CV PDF, or run an interactive terminal. It is the static identity card

### Surface 2 — Live site at iankitkumar.in

- **Repo**: `github.com/i-ankitkumar/iankitkumar.in`
- **Stack**: Astro 5 + TypeScript + plain CSS. No framework runtime shipped; content collections drive every fact
- **Output**: static HTML/CSS, one bundle of inline theme/IO JS, no analytics
- **Hosting**: Cloudflare Pages, project name `iankitkumar-in`, branch `main`
- **Deploy**: `npx wrangler pages deploy dist --project-name=iankitkumar-in --branch=main --commit-dirty=true` (CF Pages Git integration also wired)
- **Local dev**: `npm install && npm run dev` (Astro at `localhost:4321`); `npm run build` produces `dist/`; `npm run preview` serves the built site
- **Customization point**: `src/content/` collections (`experiences/`, `projects/`, `certs/`, `experiments/`, `tools/`). Every visible fact has frontmatter; the schema is the source of truth
- **Visual register**: monochrome precision. Geist and Geist Mono, a near-black ink on white, one blue accent, shadow-as-border instead of CSS borders, generous whitespace. Three type weights only (400 read, 500 interact, 600 announce) and aggressive negative tracking at display sizes
- **What this surface does NOT do**: it does not host the blog (separate repo), generate the SVG cards (Surface 1), or run a backend. All interactivity is client-side JS (theme toggle, scroll-reveal)

### Surface 3 — Blog at blog.iankitkumar.in (separate repo, not in this workspace)

- **Repo**: `github.com/i-ankitkumar/blog.iankitkumar.in`
- **Stack**: Astro + Tailwind + Content Collections, theme `Brutal` (ElianCodes)
- **Hosting**: Cloudflare Pages, project name `blog-iankitkumar-in`
- **Customization point**: Markdown in `src/data/blog/`
- **What this surface does NOT do**: it is a writing surface, not an identity surface. It carries no bio, no contact, no certs. Neither the portfolio's typographic register nor the profile card's terminal register applies to the blog theme; the blog is allowed to feel like a blog. PRODUCT.md applies only in the parts that don't conflict (audience, voice, evidence)

## Capabilities and Constraints

**Capabilities (confirmed):**

- Generates a dark-theme and a light-theme SVG in lockstep from a single `config.json`.
- Pulls live GitHub stats into `cache/stats.json` during regen.
- Renders an ASCII art side from a local portrait (face crop), with GitHub avatar as a fallback.
- Auto-refreshes on a nightly cron and on relevant pushes; no manual sync needed.
- Rendered surface is the same set of files for the GitHub profile card, and is consumed by iankitkumar.in and the blog as the shared identity layer.

**Constraints (binding):**

- Every claim is verifiable and must remain so. Cert list (Terraform Associate, AZ-104, RHCSA, AZ-900, AI-900, AZ-400 in progress), language levels (German A2, English C1, Hindi native), and EU Blue Card eligibility are factual. Future design work must not invent additional certs, client logos, testimonials, employers, or metrics.
- SVGs must stay under GitHub's 250 KB profile-image cap. Current size is 120 KB; any growth plan needs to defend its bytes.
- Dark and light themes must move together. Changing one without the other is a defect.
- `config.json` is the source of truth for all visible copy. Editing the SVGs by hand is wrong; editing the generator is right.
- EU Blue Card eligibility is a legal status. Stating it weakly to avoid legal concern is a failure; stating it correctly is the job.
- Generated artifacts (`dark_mode.svg`, `light_mode.svg`, `cache/stats.json`, `cache/ascii.txt`, `assets/face.jpg`) are committed and tracked; the `avatar.png` cache is allowed to be refreshed.
- Monospace and the GitHub-style dark palette are part of this surface's brand. A pivot of the card itself to a sans-serif / SaaS-template look would be a rebrand, not a redesign. The portfolio site at iankitkumar.in runs a separate monochrome-precision register; that does not license the card to follow it.

**Deliberately undecided (do not invent in future work):**

- Specific employers and project names beyond what is already in `config.json`.
- A written bio longer than what the card carries today.
- Testimonials, case studies, or press.
- Pricing / availability windows / response-time SLAs.
- A native iOS or Android app. The portfolio is web-only.

## Brand Commitments

- **Terminal / CLI aesthetic is binding.** The profile card is the identity, not a decoration. Future work preserves the form factor (window chrome, monospace, aligned key/value pairs, duotone portrait) unless the user explicitly reopens the brand. The *content* of the card is free to change; the *form* is not.
- **Real name and identity.** "Ankit Kumar", handle `i-ankitkumar`, host label `ankit@kumar` (as rendered by `config.json` -> `user_at_host`). These are the brand; fictional personas are not.
- **Honest voice.** No marketing copy. If a statement is a fact (cert, level, eligibility), it is stated as a fact. If it is a value claim, it is softened or omitted.
- **Dark theme is the default.** Light theme exists for the visitors who need it, not as a co-equal brand.

## Evidence on Hand

- `config.json` — drives every visible label, both themes, contact links.
- `assets/portrait.png` — local face source for the duotone crop (do not silently overwrite).
- `assets/face_dark.jpg`, `assets/face_light.jpg` — generated duotone portraits, one per theme.
- `cache/stats.json`, `cache/ascii.txt` — generated by the workflow; reflect live GitHub state at last regen.
- `dark_mode.svg`, `light_mode.svg` — current visible artifacts, ~110 KB each.
- `scripts/preview_readme.py` — renders README.md through the GitHub markdown API and screenshots it in both themes. Use it to review a README change without pushing.
- Live surfaces: `github.com/i-ankitkumar` (profile README), `iankitkumar.in` (deeper site), `blog.iankitkumar.in` (writing).
- Verified certs: Terraform Associate, AZ-104, RHCSA (active); AZ-400 (in progress); AZ-900, AI-900 (held, expired).
- Self-reported language levels: German A2, English C1, Hindi (native).
- Contact links present in `config.json`: Portfolio, Blog, GitHub, LinkedIn.
- Scale facts quoted on the card and README, all traceable to `career-ops/cv.md`: 20,000+ endpoints under upgrade automation, 2,500+ subscriptions scanned for tech debt, index provisioning turnaround 3-5 days → 10-15 min, 35% Azure cost reduction, IDS_using_MLP accuracy 98.10% binary / 97.62% multi-class.

**Absences future work must not fabricate:** case studies, named employers beyond the current role, named clients, named scale (requests/sec, user counts, cost savings), testimonials, conference talks, awards, press.

## Product Principles

1. **Factual over flattering.** Every claim is verifiable. The design's job is to surface real evidence, not to persuade with invented detail.
2. **Skim-first, depth-on-demand.** The first five seconds must answer the recruiter's question. Richer content only appears when the visitor wants more, and never contradicts the first impression.
3. **One identity, three surfaces.** GitHub profile, iankitkumar.in, and blog must read as the same person. The claim set and the voice are the spine; each surface renders them in its own register.
4. **Generated, not hand-edited.** The SVGs are a build output. Editing them by hand is wrong; editing `config.json` and the generator is right. The discipline is what makes the work feel real instead of faked.
5. **Quiet wins on the noise floor.** This is a personal profile, not a marketing site. Restraint is the move; the terminal aesthetic reads as intentional precisely because it doesn't shout.

## Accessibility & Inclusion

- Both themes must meet WCAG AA contrast for the key/value text in the card. Current dark theme: bg `#0d1117`, key `#ffa657`, value `#a5d6ff`, leader/comment `#768390`. Light theme: bg `#ffffff`, key `#953800`, value `#0550ae`, leader/comment `#6e7781`. Any palette change must defend all pairs against AA (4.5:1 for body text, 3:1 for large text). The leader-dot colour used to be `#616e7f` (3.65:1 on dark) and failed AA body text; it is now `#768390` (4.88:1).
- When the SVG is consumed standalone (not as a README inline), it must include `<title>` and `<desc>` elements so screen readers can announce what the card is.
- Copy is in English at a C1 register. Avoid marketing-style superlatives; favor plain, factual phrasing. Visitors whose first language is not English should not need to fight the copy.
- The portrait is decorative. A visitor using a screen reader or `prefers-reduced-motion` should still get the key/value content from the SVG. The `<desc>` element names the role and location so the standalone card announces the essentials.
- No flashing or motion in the card itself. Any animation added later must respect `prefers-reduced-motion`.
