"""Editorial reading paths, rendered only into the isolated preview."""
from html import escape
import hashlib
import json
import re
import runpy

PATHS = [
    {
        'slug': 'understand-lab', 'title': 'Understand the Lab',
        'description': 'Connect meaning, purpose and work before exploring the model in detail.',
        'steps': [
            ('Start with the overview', 'See how saved meanings, work and evidence give a project continuity.', 'governance-lab-reference.html#start', 'Read the overview'),
            ('Follow one investigation', 'Use the fictional Northstar export incident to see the responsibilities in context.', 'incident-walkthrough.html', 'Follow the incident'),
            ('Explore the connections', 'Choose a view in the system map and inspect the concepts behind the investigation.', 'governance-lab-reference.html#system-map', 'Open the system map'),
        ],
    },
    {
        'slug': 'investigate-incident', 'title': 'Investigate an incident',
        'description': 'Follow a report through evidence, assessment and the owner’s next review.',
        'steps': [
            ('Understand the reported problem', 'Follow the Northstar case from the customer’s report to a scoped investigation.', 'incident-walkthrough.html', 'Read the walkthrough'),
            ('Examine the saved records', 'Inspect the Work, observations and evidence specimens used in the example.', 'record-examples.html#example-work', 'Inspect the examples'),
            ('Prepare the assessment', 'Bring the criterion, evidence and limits together for an accountable decision.', 'prepare-incident-assessment.html', 'Read the practical guide'),
        ],
    },
    {
        'slug': 'read-record', 'title': 'Read a record',
        'description': 'Find the exact meaning, check its standing and follow its supporting sources.',
        'steps': [
            ('Learn the library’s structure', 'Distinguish meanings, formats, connections and captured acceptance status.', 'lab-reference-library.html#library-reading-guide', 'Read the library guide'),
            ('Inspect a complete specimen', 'Keep identity, selected format, scope and evidence visible while reading.', 'read-record.html', 'Read the practical guide'),
            ('Find the exact contract', 'Search the captured definitions and open an entry for its full statement and sources.', 'lab-reference-library.html#catalog-definitions', 'Browse the definitions'),
        ],
    },
    {
        'slug': 'prepare-definition', 'title': 'Prepare a definition',
        'description': 'State a meaning and its boundaries, then assemble the material for review.',
        'steps': [
            ('Understand what a definition governs', 'Separate accepted meaning from a record’s format, permission and lifecycle state.', 'governance-lab-reference.html#records', 'Read about meanings and records'),
            ('Prepare the candidate', 'Work through meaning, explanatory voices, sources and review obligations.', 'prepare-definition.html', 'Read the practical guide'),
            ('Compare with a complete example', 'Inspect the criterion specimen and its explicit boundaries before seeking owner review.', 'record-examples.html#example-definition', 'Inspect the definition specimen'),
        ],
    },
    {
        'slug': 'resume-agent-work', 'title': 'Resume agent work',
        'description': 'Recover project knowledge, refresh the views and recheck permission to continue.',
        'steps': [
            ('Understand the session boundary', 'See what belongs to a temporary agent session and what persists in Project State.', 'governance-lab-reference.html#agent', 'Read about agent continuity'),
            ('Rebuild the task context', 'Recover durable material, check freshness and establish the current authority envelope.', 'resume-agent-work.html', 'Read the practical guide'),
            ('Inspect the session specimen', 'Examine the assignment, views and session envelope used in the fictional example.', 'record-examples.html#example-agent-session', 'Inspect the session specimen'),
        ],
    },
    {
        'slug': 'explore-craft', 'title': 'Explore Craft',
        'description': 'Follow an explicit software model from a capacity criterion to supported construction.',
        'steps': [
            ('Meet the software model', 'See the responsibilities and scope of Craft within the Lab.', '../craft-documentation-proposal/craft-model.html#craft-overview', 'Read the Craft overview'),
            ('Follow the capacity example', 'Distinguish a condition, derived value, retrieval and state change in the worked example.', '../craft-documentation-proposal/craft-model.html#definition', 'Open the worked example'),
            ('Understand the governance boundary', 'Read how software design and generated outputs connect to Lab records and owner decisions.', '../craft-documentation-proposal/craft-model.html#governance', 'Read how Craft fits into the Lab'),
        ],
    },
]

ARROW = '<svg class="docs-card-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14"/></svg>'


def path_cards():
    cards = []
    for path in PATHS:
        cards.append(f'<a class="docs-path-card" href="path-{path["slug"]}.html"><strong>{escape(path["title"])}{ARROW}</strong><span>{escape(path["description"])}</span><small>{len(path["steps"])} reading steps</small></a>')
    return '<nav class="docs-card-grid docs-path-grid" aria-label="Choose a reading path">' + ''.join(cards) + '</nav>'


def apply_docs_preview(current, target):
    template = (current / 'governance-lab-series/start-here.html').read_text()
    home = template
    home = re.sub(r'<nav class="start-quick-path".*?</nav>\s*', '', home, count=1, flags=re.S)
    home = home.replace('Begin with the ideas behind knowledge and work in the Lab, then follow the parts you need in more detail.', 'Choose what you want to understand or do. Each reading path connects the explanations, examples and practical guides you need.')
    home = home.replace('5 minute read · No prior knowledge of the Lab required', 'New to the Lab? Start with “Understand the Lab,” or read the introduction below.')
    section = '<section id="reading-paths" class="docs-path-picker" aria-labelledby="reading-paths-title"><h2 id="reading-paths-title">What would you like to do?</h2>' + path_cards() + '</section>'
    home = home.replace('<section id="organize-knowledge"', section + '<section id="organize-knowledge"', 1)
    home = home.replace('<a href="#organize-knowledge">Knowledge and work</a>', '<a href="#reading-paths">Choose a reading path</a><a href="#organize-knowledge">Knowledge and work</a>', 1)
    (target / 'governance-lab-series/start-here.html').write_text(home)
    for path in PATHS:
        name = f'path-{path["slug"]}.html'
        title = escape(path['title'])
        steps = []
        toc = []
        for i, (heading, description, href, action) in enumerate(path['steps'], 1):
            toc.append(f'<a href="#step-{i}">{i}. {escape(heading)}</a>')
            steps.append(f'''<li><details class="docs-reading-step" id="step-{i}" data-step="{i}" open>
<summary><span class="docs-step-number">{i}</span><span class="docs-step-title">{escape(heading)}</span><span class="docs-step-state" data-step-state aria-hidden="true"></span></summary>
<div class="docs-step-body"><p>{escape(description)}</p><div class="docs-step-actions"><a href="{escape(href, quote=True)}">{escape(action)}{ARROW}</a><button type="button" data-mark-read aria-pressed="false" hidden>Mark as read<span class="site-search-sr-only">: {escape(heading)}</span></button></div></div>
</details></li>''')
        article = f'''<article id="reading-path" class="start-content docs-reading-path" tabindex="-1" data-reading-path="{path['slug']}">
<header class="start-masthead"><a class="docs-all-paths" href="start-here.html#reading-paths">Back to all reading paths</a><h1>{title}</h1><p class="start-deck">{escape(path['description'])}</p><p class="start-reading-time">{len(steps)} reading steps · Open the linked docs at your own pace.</p></header>
<div class="docs-reading-progress" hidden><p role="status" aria-live="polite" aria-atomic="true" data-reading-status>0 of {len(steps)} steps read</p><span data-reading-storage>Reading progress is saved in this browser.</span></div>
<ol class="docs-reading-steps" aria-label="Reading steps">{''.join(steps)}</ol>
<div class="docs-path-end"><a href="start-here.html#reading-paths">Choose another reading path</a><button type="button" data-reset-reading hidden>Reset reading progress</button></div>
<noscript><p>All reading steps and documentation links are available. Enable JavaScript to save reading progress in this browser.</p></noscript></article>'''
        page = re.sub(r'<article id="start-here".*?</article>', lambda _: article, template, count=1, flags=re.S)
        page = re.sub(r'<aside class="docs-local-nav".*?</aside>', '<aside class="docs-local-nav" aria-label="On this path"><details class="docs-toc" id="start-toc"><summary>On this path</summary><nav aria-label="Reading steps">' + ''.join(toc) + '</nav></details></aside>', page, count=1, flags=re.S)
        page = page.replace('<title>Start here · CyberAlchemy Lab</title>', f'<title>{title} · CyberAlchemy Lab</title>')
        page = page.replace('content="Start here · CyberAlchemy Lab"', f'content="{title} · CyberAlchemy Lab"')
        page = re.sub(r'(<meta (?:name|property)="(?:description|og:description)" content=")[^"]*', lambda m: m[1] + escape(path['description'], quote=True), page)
        page = page.replace('href="start-here.html" data-site-start aria-current="page"', 'href="start-here.html" data-site-start')
        page = page.replace('href="#start-here"', 'href="#reading-path"').replace('Skip to the introduction', 'Skip to the reading path')
        page = page.replace('<link rel="canonical" href="start-here.html">', f'<link rel="canonical" href="{name}">')
        page = page.replace('<body ', f'<body data-preview-reading-path="{path["slug"]}" ', 1)
        (target / 'governance-lab-series' / name).write_text(page)


def extend_preview_search(current, target):
    # Reuse the site's pure compilers without invoking its website build.
    helpers = current.parent / 'source/governance-lab-series'
    compile_entries = runpy.run_path(str(helpers / 'search_features.py'))['compile_entries']
    write_payload = runpy.run_path(str(helpers / 'compressed_script.py'))['write_payload']
    assets = target / 'governance-lab-series/assets'
    original = (current / 'governance-lab-series/assets/site-search-index-fallback.js').read_text()
    payload = json.JSONDecoder().raw_decode(original.split('window.LabSiteSearchIndex=', 1)[1])[0]
    entries = [{k: v for k, v in entry.items() if k != 'prepared'} for entry in payload['entries']]
    original_count = len(entries)
    for path in PATHS:
        href = f'path-{path["slug"]}.html'
        entries.append({'id': href, 'group': 'Reading paths', 'title': path['title'], 'href': href,
                        'section': 'Guided reading', 'aliases': [],
                        'text': path['description'] + ' ' + ' '.join(' '.join(step[:2]) for step in path['steps'])})
    groups = {group: sum(entry['group'] == group for entry in entries) for group in sorted({entry['group'] for entry in entries})}
    deliveries = {}
    for name, global_name, selected in [
        ('site-search-index', 'LabSiteSearchIndex', entries),
        ('site-search-quick', 'LabSiteSearchQuick', [{**entry, 'text': entry['text'][:64]} for entry in entries]),
    ]:
        prepared, stats = compile_entries(selected)
        deliveries[name] = write_payload(assets / (name + '.js'), global_name,
                                        {'version': 1, 'entries': prepared, 'preparedStats': stats, 'groups': groups}, set_base=True)
        fallback = assets / (name + '-fallback.js')
        digest = hashlib.sha256(fallback.read_bytes()).hexdigest()[:12]
        script = assets / (name + '.js')
        script.write_text(script.read_text().replace('"' + fallback.name + '"', '"' + fallback.name + '?v=' + digest + '"'))
        deliveries[name]['script_bytes'] = script.stat().st_size
    controller = assets / 'site-search.js'
    code = controller.read_text().replace("file==='site-search-index.js'", "file.split('?')[0]==='site-search-index.js'")
    for name in ['site-search-index', 'site-search-quick']:
        digest = hashlib.sha256((assets / (name + '.js')).read_bytes()).hexdigest()[:12]
        code = code.replace("payload('" + name + ".js',", "payload('" + name + '.js?v=' + digest + "',")
    controller.write_text(code)
    receipt = {'schema_version': 'lab-preview-search/v1', 'status': 'Unpublished preview reading index',
               'original_entries_preserved': original_count, 'added_reading_paths': len(PATHS),
               'entries': len(entries), 'groups': groups, 'delivery': deliveries,
               'original_website_modified': False}
    (target / 'governance-lab-series/research/preview-reading-search.json').write_text(json.dumps(receipt, indent=2) + '\n')
