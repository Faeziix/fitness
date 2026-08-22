import { getCollection } from 'astro:content';

/**
 * The file() loader returns entries sorted by id, which puts w10 before w2.
 * Every read goes through here so ordering can never be forgotten at a call site.
 */
export async function ordered<C extends 'weeks' | 'paces' | 'qualitySessions' | 'baselines' | 'exercises' | 'strengthSessions' | 'blockNotes' | 'dosePhases'>(
  collection: C,
) {
  const entries = await getCollection(collection);
  return entries
    .map((e) => ({ id: e.id, ...(e.data as any) }))
    .sort((a, b) => a.seq - b.seq);
}
