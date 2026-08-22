# Project: Fitness

## Overview
- **Type**: Personal training site — Today dashboard, Programs, Articles, Video library, Archive
- **Stack**: Astro 7 (static), MDX, `@vite-pwa/astro`, plain CSS with design tokens, `cva` for note variants
- **Package Manager**: bun
- **Started**: August 2026 · migrated from single-file HTML to Astro 22 Aug 2026

## Athlete profile
- 71 kg. Returning runner, previously fast (18:59 5K, 153 km month in 2020), detrained.
- Training for a **first marathon** on `marathon-16-week-plan.html` — 5 runs/week, peak 66 km, longest 30 km.
- Currently: **on-ramp week B** (week A completed as of 15 Aug 2026). ~19 weeks to race day.
- Based in the UAE — August–October training defaults to treadmill or pre-05:30 outdoor runs.
- Goals beyond the marathon: become a genuinely strong athlete, reduce body fat, hold/build calisthenics (pull-ups, dips, push-ups).

### Open injury file
- **Right lateral knee pain** — location re-confirmed by the athlete 22 Aug 2026 as the *outer* side of the knee, not the kneecap. Not sharp, runnable, worst walking afterwards. Presentation most consistent with ITB syndrome; not clinically assessed.
- Separate, older file: **anterior knee pain in deep squat with audible noise** (from `3-month-training-plan.md`). Treat as a distinct issue.
- **Positive Renne test (22 Aug 2026):** single-leg semi-squat on the right sharpens the pain. Double-leg standing does not. Supports the ITB working diagnosis and confirms the problem is load tolerance under single-leg control.
- Consequence: squat-pattern work stays partial-range and single-leg-biased; hip abductor work is a daily fixture.
- **Single-leg step-down removed from the daily hip block from 22 Aug 2026** — it is the provocative movement itself. Reintroduce ~5 Sept at the lowest step height. The other five hip-block movements are knee-neutral and continue unchanged.
- Wednesday step-ups stay below the prescribed 30–40 cm box height until the squat test is quiet.
- **Short-cycle progress marker:** five slow single-leg semi-squats each morning, scored 0–10 on the right. Responds faster than the after-run ache and needs no equipment.
- Running is capped, not stopped: repeat on-ramp week B, hold the long run at 9 km. The metric that matters for this condition is **the distance at which the pain arrives** — if onset moves earlier week on week, cut volume regardless of how mild it feels.

### Transient left-foot numbness (22 Aug 2026)
- Mid-run, did not resolve on loosening laces, eased with continued running, gone afterwards. Treated as lace/dorsal pressure, not pathology. First move is skip-lacing + shoe-size check. Escalate if it recurs on three consecutive runs after that change.

## Architecture Decisions
- **One document per plan, self-contained.** No shared stylesheet, no assets, no external requests — each file must open from disk or a phone with zero dependencies. The design tokens are duplicated into each file deliberately.
  - **One deliberate exception, requested 22 Aug 2026:** `strength-plan.html` embeds YouTube demonstrations, so it references `i.ytimg.com`, `www.youtube-nocookie.com` and `www.youtube.com`. Opened from disk the tiles are real thumbnails and a tap opens YouTube; served over http the videos play inline. Offline the tiles blank out and every word, table and number still renders. Do not extend this to any other asset or document.
- **Design tokens only, never hardcoded colour.** See `docs/design-system.md`.
- Plans are written in kilometres and in prose that states its own reasoning, so a plan can be re-read months later and still explain why it is shaped that way.

## Preferences & Rules
- **Honesty over encouragement.** State what a plan will and will not deliver, including where two goals genuinely conflict (e.g. marathon volume vs. hypertrophy vs. calorie deficit). Do not soften physiology.
- Distinguish clearly between well-evidenced claims, reasonable inference, and speculation. Never present a diagnosis as settled — describe the pattern and name the differentials.
- Every prescription carries a *why* column or sentence. No exercise appears without a reason.
- Give hard stop-criteria and escalation triggers for anything injury-related.
- Prefer minimum effective dose when two training goals compete.

## Patterns & Conventions
- Filenames and slugs: kebab-case, descriptive, no dates.
- Page skeleton: `<Crumb>` → `<Masthead>` → `.statbar` → `<JumpList>` → sections.
- Tables are the primary content vehicle; each carries a `.kicker` subtitle stating scope.
- Callouts use `<Note variant>`: `stop` (hard stop), `caution` (risk), `go` (green light), `accent` (emphasis).
- **Hard stop-criteria travel with the prescription**, never off to an article.
- Prose is capped at `.prose` (68ch); tables live inside `<Scroller>`.
- **Read data collections only through `ordered()`** (`src/lib/data.ts`) — the `file()` loader sorts by id, which puts `w10` before `w2`.
- Movements get a facade video card derived from `exercises.yaml`. Run `bun run verify:videos` before shipping.
- **Update `src/data/current.ts` whenever the athlete's week or open flags change**, and keep it in step with the injury file above.

## Learnings & Corrections
- ❌ Assuming a prior plan still applies → ✅ The 3-month strength plan was written while running was *off the table* for knee reasons. It is not compatible with 66 km/week and must not be layered on top of the marathon plan unmodified.
- ❌ Putting heavy lower-body work on Friday because the marathon plan says "rest + strength" → ✅ Friday is ~18 h before the Saturday long run; peak soreness lands on the most important session of the week. All heavy leg work goes on Wednesday.
- ❌ Copying exercise GIFs from MuscleWiki/ExRx/Jefit into a document → ✅ They are copyrighted. Link or embed from the source; never copy the media. Openly-licensed alternatives were checked — wger is CC-BY-SA but holds only sparse static line art.
- ❌ Assuming a YouTube embed works in a document opened from disk → ✅ It does not. `file://` gives the page no origin, so the player returns Error 153; the same iframe plays fine over `http://`. Verified 22 Aug 2026 by rendering both. The handler branches on `location.protocol`: inline iframe when served, open YouTube when opened from disk. Never test an embed only over a local server.
- ❌ Embedding 29 live YouTube iframes directly → ✅ Each pulls megabytes of player JS and would make the page unusable on a phone. Use the facade pattern: thumbnail in a button, iframe injected on click.
- ❌ Hand-drawing SVG stick figures to illustrate exercises → ✅ Rejected by the athlete as unusable. A crude figure is worse than none because it invites copying bad form. Link to verified physiotherapist-led video demonstrations instead; see `docs/design-system.md`.
- ❌ Attributing the lateral knee pain to never having done mobility work → ✅ The cause is a load-vs-capacity mismatch: aerobic ambition returned at 2020 levels while fascia, tendon and hip musculature stayed detrained. Stretching does not prevent running injuries (consistently null in trials, including RCTs in runners), and for ITB specifically the "tight band needs lengthening" premise is mechanistically wrong. Do not add a mobility routine that competes with the 6-minute hip block for adherence.
- ❌ Recommending IT band stretching or foam-rolling the band → ✅ The band is dense fascia anchored to the femur and the pain source is the compressed fat pad beneath it. Roll TFL, vastus lateralis and glutes; strengthen hip abductors.
- ❌ Rewriting the knee section on a self-reported diagnosis label ("I think it's runner's knee") → ✅ Act on the *location*, not the label. The athlete named PFPS on 22 Aug 2026 and then corrected to lateral within the same session; the document was rewritten and reverted for nothing. Confirm which structure hurts — one finger on the sorest spot — before changing any prescription.
- ❌ Treating lateral and anterior knee pain as interchangeable because both are called "runner's knee" → ✅ ITB and PFPS share the stairs-down provocation but need different work: ITB is hip-abductor-led, PFPS needs quad loading through a pain-free range. Discriminators: prolonged-sitting ache and patellar-edge tenderness (PFPS), predictable-distance shutdown and tenderness 2–3 cm above the joint line (ITB).
- ❌ Duplicating the token block into every document → ✅ The two inline stylesheets silently drifted: `letter-spacing: 0.14em` vs `0.13em`, a dropped `font-variant-numeric: tabular-nums`, and two incompatible naming schemes (`.b1–.b4` vs `.s0–.s3`) for the same chart colours. Duplicated tokens do not stay in sync by good intentions.
- ❌ Hand-computing chart bar heights and column counts → ✅ Both are derived from the data now. The hand-written `height:N%` values happened to be correct, but `--bar-cols` had to be changed in two places per file and nothing checked that the chart agreed with the table.
- ❌ Asserting summary figures ("Total volume 772 km") → ✅ Derive them. The first derived total came out 730 because week 16's 42.2 km race leg lived only inside a display string; modelling `raceKm` explicitly fixed both the number and the gap it revealed.
- ❌ Assuming `getCollection` preserves file order → ✅ It sorts by id, so `w10` lands before `w2` and every table and chart scrambles silently. Every row carries `seq`; read through `ordered()`.
- ❌ Rewriting prose by hand during the migration → ✅ Migrate it with a script and then diff sentence-by-sentence against the originals. The first hand-written pass silently truncated the "The trap" note and dropped nine other blocks, including all four block commentaries and the whole strength phase table.
- ❌ Running a calorie deficit through peak marathon weeks → ✅ Deficit is front-loaded to the base/build phases and closes by week 8; low energy availability at 55–66 km/week is a bone-stress-injury route.

## Component Registry
See `docs/design-system.md`. `BaseLayout`, `Masthead`, `Crumb`, `JumpList`, `CardGrid`, `Note`, `Scroller`, `Zone`, `Detail`, `WeekGrid`, `VolumeChart`, `VideoGrid`, `Why`, `SiteNav`.

## Current State
Astro site, 16 routes. `bun run dev` · `bun run build` · `bun run verify:videos`.

- `/` — Today dashboard, driven by `src/data/current.ts`.
- `/programs/marathon/`, `/programs/strength/`, `/programs/hip-block/` — the active plans.
- `/articles/` — 8 pieces carrying all the reasoning.
- `/library/videos/` — all 29 demonstrations, verified.
- `/archive/` — the four original documents, unchanged, each still standalone.

The original `.html`/`.md` files remain in the repo root as the migration source of truth and are copied into `public/archive/`. `scripts/extract.py` and `scripts/extract-articles.py` are the one-off migration scripts, kept as provenance for every number and sentence on the site.

### Next
- **Deploy.** Not yet hosted. Before the first production deploy: turn on Vercel Deployment Protection (password or SSO) — this site is a documented injury file and `noindex` alone is not access control. `noindex, nofollow` is already set in `BaseLayout`.
- Retest and log the eight baseline numbers, including the new single-leg semi-squat score and hip extension.
- **Measure ankle dorsiflexion (knee-to-wall, <10 cm = restricted) and hip extension (Thomas-test position).** These are the only two "mobility" items with a defensible link to running injury; treat any finding as a secondary contributor, not the cause.
- Currently on **on-ramp week B, repeating it** rather than progressing to C, until the after-run ache shrinks.
- Re-evaluate the knee at week 4 of the hip block. If unchanged, escalate to clinical assessment — update this file with any diagnosis.
