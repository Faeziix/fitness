"""Second half of the migration: lift prose sections into MDX, verbatim.
Only structural wrappers are rewritten — no sentence is touched."""
import re, os, html

M = open('marathon-16-week-plan.html').read()
S = open('strength-plan.html').read()

def between(src, a, b):
    i = src.index(f'<h2>{a}</h2>')
    j = src.index(f'<h2>{b}</h2>') if b else len(src)
    chunk = src[i:j]
    # a trailing section may carry the document's own wrapper closers; drop them
    chunk = re.sub(r'<script>.*?</script>', '', chunk, flags=re.S)
    depth, cut = 0, len(chunk)
    for m in re.finditer(r'<(/?)div\b[^>]*>', chunk):
        depth += -1 if m.group(1) else 1
        if depth < 0:
            cut = m.start()
            break
    return chunk[:cut]

def convert(body):
    """HTML section -> MDX body. Notes become <Note>, video grids become <VideoGrid>."""
    body = re.sub(r'^<h2>.*?</h2>\s*', '', body, flags=re.S)
    body = re.sub(r'^\s*<p class="kicker">(.*?)</p>\s*', '', body, flags=re.S)

    VAR = {'note--stop': 'stop', 'note--caution': 'caution', 'note--go': 'go', 'note--accent': 'accent'}
    def note(m):
        cls = m.group(1)
        inner = m.group(2)
        variant = next((v for k, v in VAR.items() if k in cls), None)
        lab = re.search(r'<span class="label">(.*?)</span>', inner, re.S)
        inner = re.sub(r'<span class="label">.*?</span>\s*', '', inner, flags=re.S)
        attrs = ''
        if variant:
            attrs += f' variant="{variant}"'
        if lab:
            attrs += ' label="%s"' % html.unescape(re.sub(r'<[^>]+>', '', lab.group(1))).strip().replace('"', '&quot;')
        return f'<Note{attrs}>\n{inner.strip()}\n</Note>\n'
    body = re.sub(r'<div class="note([^"]*)">(.*?)</div>\s*(?=<|\Z)', note, body, flags=re.S)

    # video grids are rendered from data, not inlined
    body = re.sub(r'<p class="kicker">[^<]*demonstrated[^<]*</p>\s*', '', body)
    body = re.sub(r'<p class="kicker">Watch each one[^<]*</p>\s*', '', body)
    # video grids render from data on the program pages, never inline in prose
    while '<div class="vids">' in body:
        i = body.index('<div class="vids">')
        depth, j = 0, i
        for m in re.finditer(r'<(/?)div\b[^>]*>', body[i:]):
            depth += -1 if m.group(1) else 1
            if depth == 0:
                j = i + m.end()
                break
        body = body[:i] + body[j:]
    # MDX is JSX: void elements must self-close
    body = re.sub(r'<(img|br|hr|input)\b([^>]*?)/?>', r'<\1\2 />', body)

    body = re.sub(r'<div class="prose">\s*(.*?)\s*</div>', r'\1', body, flags=re.S)
    body = re.sub(r'</?section>', '', body)
    body = re.sub(r'<h4>(.*?)</h4>', r'### \1', body, flags=re.S)
    body = re.sub(r'<h3>(.*?)</h3>', r'### \1', body, flags=re.S)
    body = re.sub(r'\n[ \t]+', '\n', body)
    body = re.sub(r'\n{3,}', '\n\n', body)
    return body.strip()


# The 'About these videos' note in the source describes the old file:// architecture
# (disk-opened pages, a python3 -m http.server workaround, blank offline tiles). It is
# rewritten by hand in the-knee.mdx; do not re-import it verbatim from the original.

ART = [
    dict(slug='honest-framing', order=1,
         title='What these plans are honest about',
         eyebrow='Read once', explains='marathon',
         standfirst='What sixteen weeks of running and a strength block will and will not deliver.',
         parts=[('The running plan', between(M, 'What this plan is honest about', 'The on-ramp')),
                ('The strength plan', between(S, 'What this plan is honest about', 'The knee'))]),
    dict(slug='the-knee', order=2,
         title='The knee', eyebrow='Right lateral · working diagnosis ITB', explains='hip-block',
         standfirst='The thing you actually asked about — what the pattern fits, what it does not, and what to do about it.',
         parts=[(None, between(S, 'The knee', 'The daily hip block'))]),
    dict(slug='how-strength-fits', order=3,
         title='How strength fits the running week', eyebrow='Wednesday and Friday', explains='strength',
         standfirst='The two slots the marathon plan already reserved, and why heavy legs never go on Friday.',
         parts=[(None, between(S, 'How strength fits the running week', 'Session A — Wednesday'))]),
    dict(slug='fuel', order=4,
         title='Fuel', eyebrow='The part that decides the last 10 km', explains='marathon',
         standfirst='Race fuelling, and what training in the heat does to it.',
         parts=[(None, between(M, 'Fuel', "When it doesn't go to plan"))]),
    dict(slug='eating-for-two-goals', order=5,
         title='Eating for two goals at once', eyebrow='Front-load the fat loss, then stop', explains='strength',
         standfirst='Where the deficit lives, and why it has to close by week 8.',
         parts=[(None, between(S, 'Eating for two goals at once', 'Baseline, this week'))]),
    dict(slug='how-to-progress', order=6,
         title='How to progress', eyebrow='Four rules', explains='strength',
         standfirst='They replace guessing.',
         parts=[(None, between(S, 'How to progress', 'Eating for two goals at once'))]),
    dict(slug='when-it-doesnt-go-to-plan', order=7,
         title="When it doesn't go to plan", eyebrow='It won’t, and that’s accounted for', explains='marathon',
         standfirst='Missed weeks, illness, and the sessions that are worth rescuing.',
         parts=[(None, between(M, "When it doesn't go to plan", 'After this'))]),
    dict(slug='after-the-race', order=8,
         title='After the race', eyebrow='Where it actually gets built', explains='marathon',
         standfirst='Where the sub-3 lives, and where "strong athlete" gets built.',
         parts=[('After this — the running side', between(M, 'After this', None)),
                ('After the race — the strength side', between(S, 'After the race', None))]),
]

os.makedirs('src/content/articles', exist_ok=True)
for a in ART:
    chunks = []
    for heading, body in a['parts']:
        c = convert(body)
        if heading:
            chunks.append(f'## {heading}\n\n{c}')
        else:
            chunks.append(c)
    fm = (
        '---\n'
        f"title: {a['title']!r}\n"
        f"eyebrow: {a['eyebrow']!r}\n"
        f"standfirst: {a['standfirst']!r}\n"
        f"order: {a['order']}\n"
        f"explains: {a['explains']!r}\n"
        '---\n\n'
        'import Note from \'../../components/Note.astro\';\n\n'
    )
    open(f"src/content/articles/{a['slug']}.mdx", 'w').write(fm + '\n\n'.join(chunks) + '\n')
    print(a['slug'], len('\n\n'.join(chunks)))
