/**
 * The one hand-maintained file on the site.
 * Everything on the Today page derives from it — update `week` and the rest follows.
 * Source of truth for the athlete's state is CLAUDE.md; keep the two in step.
 */
export const current = {
  /** must match an `id` in weeks.yaml */
  week: 'onramp-b',
  repeating: true,
  note: 'Holding the long run at 9 km until the after-run ache shrinks. Repeating week B rather than progressing to C.',
  raceDate: '2026-12-27',

  /** Open injury/monitoring flags, surfaced on Today. */
  flags: [
    {
      text: 'Right lateral knee — ITB working diagnosis, positive Renne test 22 Aug 2026. Not clinically assessed.',
      article: 'the-knee',
    },
    {
      text: 'Single-leg step-down withdrawn from the hip block. Reintroduce ~5 Sept at a 10 cm step.',
      article: 'the-knee',
    },
    {
      text: 'Wednesday step-ups stay below the prescribed 30–40 cm box until the squat test is quiet.',
      article: 'the-knee',
    },
    {
      text: 'Score five slow single-leg semi-squats on the right each morning, 0–10. It moves before the after-run ache does.',
      article: 'the-knee',
    },
    {
      text: 'Left-foot numbness — skip-lacing and a shoe-size check. Escalate if it recurs on three consecutive runs after that change.',
      article: 'the-knee',
    },
    {
      text: 'Re-evaluate at week 4 of the hip block. If unchanged, escalate to clinical assessment.',
      article: 'the-knee',
    },
  ],
} as const;
