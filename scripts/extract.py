"""One-off migration: lift structured data out of the original HTML into YAML.
Kept in the repo as the provenance record for src/data/*.yaml."""
import re, html, json, sys

M = open('marathon-16-week-plan.html').read()
S = open('strength-plan.html').read()

ZONE = {'ze': 'easy', 'zm': 'mp', 'zh': 'threshold', 'zx': 'max'}

def tokens(cell):
    """Turn a table cell into an ordered list of text / zone-chip tokens."""
    out = []
    for part in re.split(r'(<span class="z z\w">.*?</span>)', cell, flags=re.S):
        if not part.strip():
            continue
        z = re.match(r'<span class="z (z\w)">(.*?)</span>', part, re.S)
        if z:
            out.append({'zone': ZONE[z.group(1)], 'label': strip(z.group(2))})
        else:
            t = strip(part)
            if t and t != '—':
                out.append({'text': t})
    return out

def strip(x):
    x = re.sub(r'<[^>]+>', '', x)
    return html.unescape(x).replace(' ', ' ').strip()

def cell(c):
    """Split '9 · T 3×8 min' into km plus trailing detail tokens."""
    plain = strip(c)
    if plain in ('—', ''):
        return {'rest': True}
    m = re.match(r'^(\d+)\s*(?:·|\+)?\s*(.*)$', plain)
    km = int(m.group(1)) if m and m.group(1) else None
    det = tokens(c)
    # drop the leading bare number from the detail tokens
    if det and det[0].get('text', '').startswith(str(km)):
        rest = det[0]['text'][len(str(km)):].lstrip(' ·')
        if rest:
            det[0] = {'text': rest}
        else:
            det = det[1:]
    return {'km': km, 'detail': det} if km is not None else {'text': plain, 'detail': det}

def rows(section, table_index=0):
    tables = re.findall(r'<tbody>(.*?)</tbody>', section, re.S)
    return re.findall(r'<tr([^>]*)>(.*?)</tr>', tables[table_index], re.S)

def cells(tr):
    return re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)

# ---------------------------------------------------------------- weeks
weeks = []
onramp = M[M.index('<h2>The on-ramp</h2>'):M.index('<h2>Your paces</h2>')]
for attrs, tr in rows(onramp):
    c = cells(tr)
    weeks.append({
        'id': 'onramp-' + strip(c[0]).lower(),
        'label': strip(c[0]),
        'phase': 'On-ramp',
        'block': 0,
        'isDown': 'down' in attrs,
        'km': int(strip(c[6])),
        'days': {'mon': cell(c[1]), 'tue': cell(c[2]), 'wed': cell(c[3]),
                 'thu': {'rest': True}, 'fri': {'rest': True},
                 'sat': cell(c[4]), 'sun': cell(c[5])},
    })

plan = M[M.index('<h2>The plan</h2>'):M.index('<h2>The quality sessions in full</h2>')]
PHASES = {1: 'Base', 2: 'Build', 3: 'Specific', 4: 'Peak and taper'}
for ti in range(4):
    for attrs, tr in rows(plan, ti):
        c = cells(tr)
        blk = int(re.search(r'data-block="(\d)"', attrs).group(1))
        tot = strip(c[6])
        weeks.append({
            'id': 'w' + strip(c[0]),
            'label': strip(c[0]),
            'phase': PHASES[blk],
            'block': blk,
            'isDown': 'down' in attrs,
            'isMilestone': 'milestone' in attrs,
            'km': int(re.match(r'\d+', tot).group(0)),
            'kmLabel': tot,
            'days': {'mon': cell(c[1]), 'tue': cell(c[2]), 'wed': {'rest': True},
                     'thu': cell(c[3]), 'fri': {'rest': True},
                     'sat': cell(c[4]), 'sun': cell(c[5])},
        })

# ---------------------------------------------------------------- paces
paces = []
pc = M[M.index('<h2>Your paces</h2>'):M.index('<h2>The week</h2>')]
for attrs, tr in rows(pc):
    c = cells(tr)
    paces.append({'id': 'g' + strip(c[0]).replace(':', ''), 'goal': strip(c[0]),
                  'mp': strip(c[1]), 'easy': strip(c[2]), 'threshold': strip(c[3]),
                  'predicted10k': strip(c[4]), 'isMilestone': 'milestone' in attrs})

# ------------------------------------------------------- quality sessions
qs = []
q = M[M.index('<h2>The quality sessions in full</h2>'):M.index('<h2>Fuel</h2>')]
for i, (attrs, tr) in enumerate(rows(q)):
    c = cells(tr)
    qs.append({'id': 'q%d' % i, 'weeks': strip(c[0]), 'session': strip(c[1]),
               'work': tokens(c[2]), 'why': strip(c[3])})

# ---------------------------------------------------------------- videos
vids = {}
for m in re.finditer(r'<div class="vids">(.*?)\n    </div>\n', S, re.S):
    head = strip(re.findall(r'<h2>(.*?)</h2>', S[:m.start()], re.S)[-1])
    for v in re.finditer(r'<div class="vid( vid--out)?" data-yt="([^"]+)">(.*?)</div>', m.group(1), re.S):
        b = v.group(3)
        vids[v.group(2)] = {
            'group': head,
            'youtube': v.group(2),
            'name': strip(re.search(r'<span class="t">(.*?)</span>', b, re.S).group(1)),
            'channel': strip(re.search(r'<span class="src">(.*?)</span>', b, re.S).group(1)),
            'cue': re.search(r'<span class="cue">(.*?)</span>', b, re.S).group(1).strip(),
            'withdrawn': bool(v.group(1)),
        }

json.dump({'weeks': weeks, 'paces': paces, 'quality': qs, 'videos': vids},
          open('/tmp/claude-1000/-home-faezix-Personal-fitness/22467268-b324-41bc-aa4c-a10aa059209b/scratchpad/extract.json', 'w'), indent=1, ensure_ascii=False)
print(f"weeks={len(weeks)} paces={len(paces)} quality={len(qs)} videos={len(vids)}")

# ------------------------------------------------ strength dose per week
dose = S[S.index('<h2>The dose across nineteen weeks</h2>'):S.index('<h2>How to progress</h2>')]
SESS = {'': 3, 's2': 2, 's1': 1, 's0': 0}
bars = re.findall(r'<div class="b\s*(s\d)?"\s*title="([^"]+)"><i style="height:(\d+)%"></i></div>', dose)
lookup = {}
for cls, title, h in bars:
    key = title.split(' · ')[0].replace('On-ramp ', 'onramp-').replace('Week ', 'w').lower()
    key = 'w16' if 'race week' in title.lower() and key == 'w16' else key
    lookup[key] = {'sessions': SESS[cls or ''], 'note': title}
for w in weeks:
    d = lookup.get(w['id'])
    w['strength'] = d['sessions'] if d else 3
    if d:
        w['strengthNote'] = d['note'].split(' · ', 2)[-1]

# ---------------------------------------------- strength session tables
def session(name, endmark):
    sec = S[S.index('<h2>%s</h2>' % name):S.index(endmark)]
    out = []
    for i, (attrs, tr) in enumerate(rows(sec)):
        c = cells(tr)
        z = re.search(r'class="z (z\w)"', c[0])
        out.append({
            'id': '%s-%d' % (name.split()[1].lower(), i),
            'name': strip(c[0]),
            'intensity': ZONE[z.group(1)] if z else None,
            'why': c[1].strip(),
            'early': strip(c[2]), 'mid': strip(c[3]), 'late': strip(c[4]), 'rest': strip(c[5]),
        })
    return out

sessA = session('Session A — Wednesday', '<p class="kicker">Session A, demonstrated')
sessB = session('Session B — Friday', '<p class="kicker">Session B, demonstrated')

# ------------------------------------------------------------ hip block
hip = S[S.index('<h2>The daily hip block</h2>'):S.index('<p class="kicker">Watch each one')]
hipRows = []
for i, (attrs, tr) in enumerate(rows(hip)):
    c = cells(tr)
    hipRows.append({'id': 'hip-%d' % i, 'name': strip(c[0]),
                    'early': strip(c[1]), 'mid': strip(c[2]), 'late': strip(c[3]),
                    'why': c[4].strip()})

# ----------------------------------------------------------- baselines
base = S[S.index('<h2>Baseline, this week</h2>'):S.index('<p class="kicker">The baseline tests, demonstrated')]
baselines = []
for i, (attrs, tr) in enumerate(rows(base)):
    c = cells(tr)
    baselines.append({'id': 'b%d' % i, 'test': strip(c[0]), 'how': c[1].strip(), 'good': c[2].strip()})

json.dump({'weeks': weeks, 'paces': paces, 'quality': qs, 'videos': vids,
           'sessionA': sessA, 'sessionB': sessB, 'hip': hipRows, 'baselines': baselines},
          open('/tmp/claude-1000/-home-faezix-Personal-fitness/22467268-b324-41bc-aa4c-a10aa059209b/scratchpad/extract.json', 'w'), indent=1, ensure_ascii=False)
print(f"sessionA={len(sessA)} sessionB={len(sessB)} hip={len(hipRows)} baselines={len(baselines)}")
print("strength per week:", [(w['id'], w['strength']) for w in weeks])
