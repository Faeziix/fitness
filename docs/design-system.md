# Design system — the training site

The plans are an [Astro](https://astro.build) static site. Pages ship as plain HTML with **no framework runtime**: the only JavaScript on a page is ~575 bytes of inlined script (theme toggle + video facade) plus the service-worker registration. There is no React, no hydration, no client bundle.

The single-self-contained-file rule that governed the original documents is **retired**. Those originals live unchanged in `public/archive/` and still open standalone.

## Layout

```
src/
  styles/tokens.css      the token block, defined three times
  styles/base.css        typography, tables, notes, charts, video cards
  styles/shell.css       nav, breadcrumb, jump list, cards, Why links
  components/            the component registry (below)
  layouts/BaseLayout.astro
  content.config.ts      Zod schemas for every collection
  content/articles/*.mdx prose
  data/*.yaml            all training data
  data/current.ts        the one hand-edited file
  lib/data.ts            ordered() — the only way to read a collection
scripts/
  extract.py             one-off migration from the original HTML (provenance)
  extract-articles.py    one-off prose migration
  verify-videos.ts       checks every YouTube id against oEmbed
```

## Rules

1. **Never hardcode a colour, font or size.** Everything resolves through a custom property.
2. **Every token is defined three times**: bare `:root` (light), `@media (prefers-color-scheme: dark)` guarded as `:root:not([data-theme="light"])`, and `:root[data-theme="dark"]`. A token defined only inside a media query is a bug.
3. `body` always paints an explicit `var(--ground)`.
4. Tables never overflow the page — they live inside `<Scroller>` and carry `min-width`.
5. Prose is capped at `.prose { max-width: 68ch }`. Tables and grids run full width.
6. **Read collections only through `ordered()`** (`src/lib/data.ts`). See "Ordering" below.

## Tokens

### Surfaces and ink
| Token | Role |
|---|---|
| `--ground` | Page background |
| `--surface` | Cards, note backgrounds, even table rows |
| `--surface-2` | Inset elements, `code`, muted bars |
| `--ink` | Primary text, headings, top rules |
| `--ink-2` | Secondary prose, standfirst, table sub-detail |
| `--ink-3` | Eyebrows, kickers, table headers, disabled/dash |
| `--rule` | Hairlines, grid gaps |
| `--rule-strong` | Emphasised borders, default note border |

### Semantic
| Pair | Meaning |
|---|---|
| `--accent` / `--accent-ink` / `--accent-soft` | Emphasis, highlighted rows, block 2 |
| `--go` / `--go-soft` | Green light, expectation setting, block 3 |
| `--caution` / `--caution-soft` | Risk, reduced dose, block 1 |
| `--stop` / `--stop-soft` | Hard stop criteria, race day, block 4 |

`--accent-ink` is the accessible-on-surface variant; use it for text and `--accent` for fills and borders.

### Intensity scale
`--easy` / `--mp` / `--hard` / `--max`, each with a `-soft` background. Rendered by `<Zone>` as `.z` chips (`.ze`, `.zm`, `.zh`, `.zx`). Used for run pace zones and lift intensity.

### Type
- `--font-display` — Helvetica Neue stack. Headings only, uppercase, 700–800, negative tracking.
- `--font-body` — Iowan Old Style / Charter serif. All prose.
- `--font-mono` — system mono. Eyebrows, kickers, table content, stat labels, numerals.
- Scale `--step-0` (1.0625rem) to `--step-4` (3.25rem). Reduced at 620px.

Numeric content always sets `font-variant-numeric: tabular-nums`.

## Components

| Component | Use |
|---|---|
| `<BaseLayout>` | `title`, `description`, `section`. Owns `<head>`, nav, and the anti-FOUC script |
| `<Masthead>` | `eyebrow` + `h1` + `standfirst` |
| `<Crumb>` | Breadcrumb trail on inner pages |
| `<JumpList>` | "On this page" chip row for long program pages |
| `<CardGrid>` | Directory grids on the index pages |
| `<Note>` | `variant`: default / `stop` / `caution` / `go` / `accent`, plus `label`. Uses `cva` |
| `<Scroller>` | Wraps every table; `min` sets `min-width` |
| `<Zone>` | Pace / intensity chip |
| `<Detail>` | Renders a token array (text + zone chips) from the data |
| `<WeekGrid>` | Seven-day grid. `markToday` adds the client-side highlight |
| `<VolumeChart>` | Derives column count and bar heights from the weeks passed in |
| `<VideoGrid>` | Facade video cards + the delegated click handler |
| `<Why>` | Link from a prescription out to the article explaining it |
| `.statbar` / `.stat` | Headline figures, auto-fitting grid |
| `.steps` | Counter-numbered list with ringed markers |
| `.closer` | Final block; last `<p>` renders as a large uppercase directive |
| `tr[data-block="0..4"]` | Coloured left edge marking block membership |
| `tr.down` / `tr.milestone` | Down weeks (italic, muted) and highlighted rows |

### Charts derive their own shape

`<VolumeChart>` takes `weeks[]` and computes the column count (`--bar-cols`) and every bar height from `Math.max(...km)`. The originals hardcoded both, in two places per file that had to change in lockstep; that class of bug is now structurally impossible.

Bar and legend classes are semantic and shared: `.b--caution`, `.b--accent`, `.b--go`, `.b--stop`, `.b--muted`, plus `.b--down` which fades a bar without changing its colour. The originals used two incompatible schemes (`.b1–.b4` and `.s0–.s3`) and the marathon legend did not describe its own bars.

`colourBy="block"` colours by training block, matching the table row edges and the legend. `colourBy="strength"` colours by strength-session count.

### Ordering — important

The `file()` loader returns entries **sorted by id**, which puts `w10` before `w2`. Every YAML row therefore carries an explicit `seq`, and every read goes through `ordered()` in `src/lib/data.ts`. Never call `getCollection` directly for a data collection.

## Content model

| Collection | Source | Holds |
|---|---|---|
| `weeks` | `weeks.yaml` | All 20 weeks: `km`, `block`, `isDown`, `strength`, `days.{mon..sun}` |
| `exercises` | `exercises.yaml` | Every movement: `youtube`, `channel`, `cue`, `group`, `withdrawn` |
| `strengthSessions` | `strength-sessions.yaml` | Sessions A, B and the hip block |
| `qualitySessions` | `quality-sessions.yaml` | The Tuesday sessions |
| `paces` | `paces.yaml` | The target-time pace table |
| `baselines` | `baselines.yaml` | The eight baseline tests |
| `blockNotes` | `block-notes.yaml` | The commentary under each block table |
| `dosePhases` | `dose-phases.yaml` | The strength phase table |
| `articles` | `content/articles/*.mdx` | The eight explanatory pieces |

`exercises.yaml` is the **single source for every video**. The library page, both session tables and the hip block all derive from it — `withdrawn: true` mutes a card everywhere at once.

`src/data/current.ts` is the only hand-edited file. Update `week` and the Today page follows.

## Demonstration videos

### The facade pattern — required
Never place a live `<iframe>` in the markup. Each card ships a still thumbnail inside a `<button>`; `<VideoGrid>`'s delegated handler swaps it for an iframe on the tap that starts playback.

A YouTube iframe pulls megabytes of player JavaScript *each*, and the site carries 29. The facade also means YouTube sets no cookies until the reader chooses to watch. Players are created against `youtube-nocookie.com`. The thumbnail has an `error` handler that removes it, so a failed image degrades to a plain tile rather than a broken-image icon.

### Rules
- **Verify every id before shipping.** `bun run verify:videos` checks all of them against oEmbed and fails the run on a dead id or a channel that does not match the card.
- **Name the channel.** The reader judges the source before spending two minutes.
- **Match the source to the stakes.** Injury and rehab movements get physiotherapist-led channels.
- **Pick the specific variant prescribed** — the knee-version Copenhagen, not the full-length one.
- Keep the `a.go` escape hatch so the video is reachable if the embed is blocked.
- One video per movement.

### The offline exception
Three external hosts are permitted and no others: `i.ytimg.com`, `www.youtube-nocookie.com`, `www.youtube.com`. There are no external fonts and no CDNs. A Workbox `StaleWhileRevalidate` rule caches thumbnails, so offline the tiles now survive — better than the originals, where they went blank. The player itself needs signal by design and is never precached.

## Offline

`@vite-pwa/astro` with `registerType: 'autoUpdate'`. Two configuration traps, both load-bearing:

- **`trailingSlash: 'always'` is mandatory.** The integration derives precache URLs from it. With Astro's default `'ignore'` it stores `/programs/marathon` while every link points at `/programs/marathon/`; the lookup misses and offline silently serves nothing but the home page.
- **Never list a file in both `globPatterns` and `includeAssets`.** The two produce conflicting revisions for the same URL and Workbox refuses the whole precache at install — so nothing is cached at all.

With `build.format: 'directory'`, the integration maps any `.html` to its *parent directory*. Standalone HTML files sharing one folder therefore collide. Each archived document lives in its own directory (`public/archive/<name>/index.html`) for this reason.

## Responsive
Single breakpoint at `620px`: type scale steps down, tables bleed to the viewport edge via negative inline margin on `.scroller`, chart height and gaps reduce, and the nav bar scrolls horizontally. Overflow on `.sitenav-in` is safe because it is a *child* of the sticky element — never put `overflow: hidden` on an ancestor of `.sitenav`, which would silently kill `position: sticky`.

## Accessibility
- `:focus-visible` outline uses `--accent` at 2px with 3px offset.
- Colour is never the sole carrier of meaning — every `.note` variant has a text `.label`, every bar has a `title`, every intensity chip has a word in it.
- The Today page renders all seven days into the DOM; script only promotes one, so it reads correctly with JavaScript off.
