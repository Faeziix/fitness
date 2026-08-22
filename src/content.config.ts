import { defineCollection } from 'astro:content';
import { glob, file } from 'astro/loaders';
import { z } from 'astro/zod';

const ZONES = ['easy', 'mp', 'threshold', 'max'] as const;

const detailToken = z.union([
  z.object({ text: z.string() }),
  z.object({ zone: z.enum(ZONES), label: z.string() }),
]);

const day = z.union([
  z.object({ rest: z.literal(true) }),
  z.object({
    km: z.number().min(0).max(60).optional(),
    text: z.string().optional(),
    detail: z.array(detailToken).default([]),
  }),
]);

const weeks = defineCollection({
  loader: file('./src/data/weeks.yaml'),
  schema: z.object({
    seq: z.number(),
    label: z.string(),
    phase: z.string(),
    block: z.number().min(0).max(4),
    km: z.number().min(0).max(100),
    raceKm: z.number().optional(),
    kmLabel: z.string().optional(),
    isDown: z.boolean().default(false),
    isMilestone: z.boolean().default(false),
    strength: z.number().min(0).max(3),
    strengthNote: z.string().optional(),
    days: z.object({
      mon: day, tue: day, wed: day, thu: day, fri: day, sat: day, sun: day,
    }),
  }),
});

const exercises = defineCollection({
  loader: file('./src/data/exercises.yaml'),
  schema: z.object({
    seq: z.number(),
    group: z.enum(['knee-tests', 'hip-block', 'session-a', 'session-b', 'baseline']),
    groupLabel: z.string(),
    youtube: z.string().regex(/^[\w-]{11}$/, 'not a YouTube id'),
    name: z.string(),
    channel: z.string(),
    cue: z.string(),
    withdrawn: z.boolean().default(false),
  }),
});

const strengthSessions = defineCollection({
  loader: file('./src/data/strength-sessions.yaml'),
  schema: z.object({
    seq: z.number(),
    session: z.enum(['A', 'B', 'hip']),
    name: z.string(),
    intensity: z.enum(ZONES).nullable().default(null),
    intensityLabel: z.string().nullable().default(null),
    why: z.string(),
    early: z.string(),
    mid: z.string(),
    late: z.string(),
    rest: z.string().nullable().default(null),
  }),
});

const qualitySessions = defineCollection({
  loader: file('./src/data/quality-sessions.yaml'),
  schema: z.object({
    seq: z.number(),
    weeks: z.string(),
    session: z.string(),
    work: z.array(detailToken),
    why: z.string(),
  }),
});

const paces = defineCollection({
  loader: file('./src/data/paces.yaml'),
  schema: z.object({
    seq: z.number(),
    goal: z.string(),
    mp: z.string(),
    easy: z.string(),
    threshold: z.string(),
    predicted10k: z.string(),
    isMilestone: z.boolean().default(false),
  }),
});

const baselines = defineCollection({
  loader: file('./src/data/baselines.yaml'),
  schema: z.object({ seq: z.number(), test: z.string(), how: z.string(), good: z.string() }),
});

const blockNotes = defineCollection({
  loader: file('./src/data/block-notes.yaml'),
  schema: z.object({ seq: z.number(), block: z.number().min(1).max(4), body: z.string() }),
});

const dosePhases = defineCollection({
  loader: file('./src/data/dose-phases.yaml'),
  schema: z.object({
    seq: z.number(), phase: z.string(), weeks: z.string(), running: z.string(),
    lifts: z.string(), doing: z.string(), eating: z.string(),
  }),
});

const articles = defineCollection({
  loader: glob({ base: './src/content/articles', pattern: '**/*.mdx' }),
  schema: z.object({
    title: z.string(),
    eyebrow: z.string(),
    standfirst: z.string(),
    order: z.number(),
    explains: z.string().optional(),
  }),
});

export const collections = {
  weeks, exercises, strengthSessions, qualitySessions,
  paces, baselines, blockNotes, dosePhases, articles,
};
