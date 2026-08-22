/**
 * Verifies every YouTube id in src/data/exercises.yaml against the oEmbed
 * endpoint. A live video returns title + channel; a dead one 404s.
 *
 * The design-system rule "verify every id before shipping it" is a discipline
 * until it is a check. Run with: bun run verify:videos
 */
import { parse } from 'yaml';

type Exercise = { id: string; name: string; youtube: string; channel: string };

const raw = await Bun.file('src/data/exercises.yaml').text();
const exercises = parse(raw) as Exercise[];

const strip = (s: string) =>
  s.replace(/&middot;|·/g, ' ').replace(/[’‘']/g, "'").replace(/\s+/g, ' ').trim().toLowerCase();

let failed = 0;
let mismatched = 0;

const results = await Promise.all(
  exercises.map(async (e) => {
    const url = `https://www.youtube.com/oembed?format=json&url=https://www.youtube.com/watch?v=${e.youtube}`;
    try {
      const res = await fetch(url);
      if (!res.ok) return { e, ok: false, reason: `HTTP ${res.status}` };
      const data = (await res.json()) as { title: string; author_name: string };
      const claimed = strip(e.channel).split(' ')[0];
      const actual = strip(data.author_name);
      return { e, ok: true, title: data.title, author: data.author_name, matches: actual.includes(claimed) };
    } catch (err) {
      return { e, ok: false, reason: String(err) };
    }
  }),
);

for (const r of results) {
  if (!r.ok) {
    failed++;
    console.error(`DEAD     ${r.e.youtube}  ${r.e.name} — ${r.reason}`);
  } else if (!r.matches) {
    mismatched++;
    console.warn(`CHANNEL? ${r.e.youtube}  ${r.e.name} — claims "${r.e.channel}", oEmbed says "${r.author}"`);
  } else {
    console.log(`ok       ${r.e.youtube}  ${r.e.name}`);
  }
}

console.log(`\n${results.length} checked · ${failed} dead · ${mismatched} channel mismatches`);
if (failed > 0) process.exit(1);
