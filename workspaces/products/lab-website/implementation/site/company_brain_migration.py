"""Consolidate the approved conceptual introduction, preserving legacy entry links."""
from html import escape
import hashlib
import json
import math
from pathlib import Path
import re
import sys

HOME_TARGETS = {
    'hero-title': ('#paper-hero-title', 'The Lab introduction'),
    'home-example-title': ('#model', 'The incident example'),
    'lab': ('company-brain.html#company-knowledge', 'How the company brain works'),
    'lab-title': ('company-brain.html#company-knowledge', 'How the company brain works'),
    'company-brain-map-title': ('company-brain.html#company-brain-map-title', 'The company brain role map'),
    'brain-map-detail': ('company-brain.html#brain-map-detail', 'People, agents and project knowledge'),
    'knowledge-cycle-title': ('company-brain.html#knowledge-cycle-title', 'Knowledge, work and decisions'),
    'how': ('company-brain.html#governed-work', 'Knowledge that can guide work'),
    'how-title': ('company-brain.html#governed-work', 'Knowledge that can guide work'),
    'continuity': ('company-brain.html#agent-memory', 'What the next agent inherits'),
    'continuity-title': ('company-brain.html#agent-memory', 'What the next agent inherits'),
    'craft': ('#paper-craft', 'Craft and the Lab'),
    'craft-title': ('#paper-craft', 'Craft and the Lab'),
    'explore': ('#paper-explore', 'Explore the Lab'),
    'explore-title': ('#paper-explore', 'Explore the Lab'),
    'lab-home': ('company-brain.html#company-brain', 'The company brain introduction'),
    'company-brain-background': ('company-brain.html#company-brain', 'The company brain introduction'),
}
INTRO_TARGETS = {
    'organize-knowledge': ('company-brain.html#company-knowledge', 'Knowledge and work'),
    'definitions-first': ('company-brain.html#definitions-first', 'Meanings, formats and records'),
    'three-questions': ('company-brain.html#governed-work', 'Three governance questions'),
    'purpose-and-work': ('company-brain.html#purpose-and-work', 'Purpose and work'),
    'agent-continuity': ('company-brain.html#agent-memory', 'Agent continuity'),
    'craft-in-the-lab': ('company-brain.html#craft-in-the-lab', 'Craft in the Lab'),
    'choose-your-path': ('#reading-paths', 'Choose a reading path'),
}


def section(text, identity):
    match = re.search(r'<section\b[^>]*id="' + re.escape(identity) + r'"[^>]*>.*?</section>', text, re.S)
    if not match:
        raise ValueError('Missing migration source section: ' + identity)
    return match[0]


def add_before_end(block, extra):
    return block.rsplit('</section>', 1)[0] + extra + '</section>'


def fragment_links(mapping):
    # Each old fragment is a real visible destination without JavaScript.
    # Normal reading does not expose a competing legacy menu.
    return '\n'.join(f'<p class="migration-link" id="{identity}" data-migrated-to="{escape(href, quote=True)}">'
                     f'This material is now in <a href="{escape(href, quote=True)}">{escape(label)}</a>.</p>'
                     for identity, (href, label) in mapping.items())


def local_outline(labels):
    links = ''.join(f'<a href="#{identity}">{escape(label)}</a>' for identity, label in labels)
    return '<aside class="docs-local-nav" aria-label="On this page"><details class="docs-toc" id="start-toc"><summary>On this page</summary><nav aria-label="Headings on this page">' + links + '</nav></details></aside>'


def apply(stage):
    lab = Path(stage) / 'governance-lab-series'
    sys.path.insert(0, str(lab))
    from build_site_search import Document, clean
    original = {name: (lab / name).read_text() for name in ['index.html', 'start-here.html', 'company-brain.html']}
    intro, company, old_home = original['start-here.html'], original['company-brain.html'], original['index.html']
    knowledge = section(company, 'company-knowledge')
    role_map = re.search(r'<figure class="company-brain-map".*?</figure>', old_home, re.S)[0].replace('href="#lab"', 'href="#company-knowledge"')
    # Distinct introductory responsibilities stay with the conceptual model.
    knowledge = add_before_end(knowledge, role_map)
    definitions = section(intro, 'definitions-first')
    definitions = definitions.replace('Begin with what the words mean', 'Meanings, formats and records')
    governed = section(company, 'governed-work')
    # Meaning/record representation is introduced once in the preceding section.
    governed = re.sub(r'<p>.*?</p>', '', governed, count=1, flags=re.S)
    lenses = re.search(r'<dl class="start-lenses">.*?</dl>', section(intro, 'three-questions'), re.S)[0]
    # Keep both the general questions and their concrete, scoped example.
    old_lenses = re.search(r'<dl class="article-lenses">.*?</dl>', governed, re.S)[0]
    questions = re.findall(r'<dd>(.*?)</dd>', old_lenses, re.S)
    index = iter(questions)
    lenses = re.sub(r'<dd>', lambda _: '<dd>' + next(index) + ' ', lenses)
    governed = governed.replace(old_lenses, lenses)
    purpose_paragraph = re.findall(r'<p>.*?</p>', governed, re.S)[-1]
    governed = governed.replace(purpose_paragraph, '')
    cycle = re.search(r'<figure class="brain-knowledge-cycle".*?</figure>', old_home, re.S)[0]
    governed = add_before_end(governed, cycle)
    purpose = section(intro, 'purpose-and-work')
    purpose = re.sub(r'<p>.*?</p>', lambda _: purpose_paragraph, purpose, count=1, flags=re.S)
    incident = section(company, 'incident')
    # Identifier coverage is not value accuracy, permission, cause or recovery.
    coverage = re.findall(r'<p>.*?</p>', definitions, re.S)[1]
    definitions = definitions.replace(coverage, '')
    incident = add_before_end(incident, coverage + '<p><a href="governance-lab-reference.html#opening-incident-case-title">Inspect the case in the technical guide</a>.</p>')
    memory = section(company, 'agent-memory')
    source_memory = re.findall(r'<p>.*?</p>', section(intro, 'agent-continuity'), re.S)
    existing_memory = re.findall(r'<p>.*?</p>', memory, re.S)
    memory = memory.replace(existing_memory[0], source_memory[1])
    # State the enduring comparison once; the existing learning paragraph below
    # already explains later use, benefit evidence and the limit on improvement claims.
    comparison = source_memory[-1].replace(' A saved lesson can also be examined through later use and benefit evidence.', '')
    memory = memory.replace(existing_memory[1], source_memory[0] + '<p>If a view expires, refresh it or pause. Continuing requires usable context and current permission.</p>' + comparison)
    craft = section(intro, 'craft-in-the-lab')
    # The previous short process points remain linked to their detailed owners.
    governed = add_before_end(governed, '<p class="concept-further">Explore <a href="governance-lab-reference.html#governance">authority and meaning</a>, <a href="governance-lab-reference.html#evidence">provenance and evidence</a>, <a href="governance-lab-reference.html#change">lifecycle and change</a>, or <a href="resume-agent-work.html">continuing agent work</a>.</p>')
    body = ''.join([section(company, 'continuity'), knowledge, definitions, governed, purpose, incident, memory, craft, section(company, 'alignment'), section(company, 'begin')])
    masthead = re.search(r'<header class="product-masthead.*?</header>', company, re.S)[0]
    masthead = masthead.replace('class="product-masthead page-width"', 'class="start-masthead"')
    masthead = masthead.replace('Why we are building it', 'Understand the Lab')
    minutes = max(1, math.ceil(len(clean(Document(body).root.text()).split()) / 220))
    masthead = re.sub(r'<p class="article-meta">.*?</p>', f'<p class="article-meta">{minutes} minute read · Conceptual introduction</p>', masthead, flags=re.S)
    article = '<article id="company-brain" class="start-content company-brain-guide" tabindex="-1">' + masthead + body + '</article>'
    # Adopt the existing docs shell, including runtime navigation and portable search.
    page = re.sub(r'<article id="start-here".*?</article>', lambda _: article, intro, count=1, flags=re.S)
    page = page.replace('href="#start-here"', 'href="#company-brain"').replace('Skip to the introduction', 'Skip to the company brain introduction')
    page = page.replace('<body ', '<body class="research-site" ', 1)
    for pattern in [r'<title>.*?</title>', r'<meta name="description"[^>]*>', r'<meta property="og:(?:title|description|url)"[^>]*>', r'<link rel="canonical"[^>]*>']:
        values = re.findall(pattern, company, re.S)
        if values:
            page = re.sub(pattern, '', page, flags=re.S)
            page = page.replace('</head>', '\n'.join(values) + '\n</head>', 1)
    labels = [('continuity','The continuity problem'),('company-knowledge','The company brain'),('definitions-first','Meanings and records'),('governed-work','Governance and change'),('purpose-and-work','Purpose and work'),('incident','An incident, examined'),('agent-memory','Agent continuity'),('craft-in-the-lab','Craft in the Lab'),('alignment','The alignment question'),('begin','Where to begin')]
    page = re.sub(r'<aside class="docs-local-nav".*?</aside>', local_outline(labels), page, count=1, flags=re.S)
    page = page.replace('href="start-here.html" data-site-start aria-current="page"', 'href="start-here.html" data-site-start')
    page = page.replace('</head>', '<link rel="stylesheet" href="assets/paper-crimson/migration.css"><link rel="stylesheet" href="assets/company-brain-map.css"><script src="assets/company-brain-map.js" defer></script></head>', 1)
    (lab / 'company-brain.html').write_text(page)
    # A short entry hub with a single primary task chooser.
    picker = section(intro, 'reading-paths')
    utilities = '<section id="direct-lookup" aria-labelledby="direct-lookup-title"><h2 id="direct-lookup-title">Go straight to a reference</h2><nav class="docs-direct-links" aria-label="Direct documentation links">' + ''.join(f'<a href="{href}">{label}</a>' for href, label in [
        ('company-brain.html#company-knowledge','How the company brain works'),
        ('lab-reference-library.html#catalog-definitions','Exact definitions'),
        ('lab-reference-library.html#library-reading-guide','How to read the library'),
        ('governance-lab-reference.html#system-map','System map'),
        ('concept-comparisons.html','Compare the concepts'),
        ('lab-reference-library.html#articles-library','Expanded explanations')]) + '</nav></section>'
    intro_targets = dict(INTRO_TARGETS)
    old_intro = Document(intro).by_id('start-here')
    surviving = set(Document(picker + utilities).ids) | {'start-here'}
    for node in old_intro.all(lambda n:'id' in n.attrs):
        identity = node.attrs['id']
        if identity in surviving or identity in intro_targets:
            continue
        parent = node
        while parent and not(parent.tag=='section' and parent.attrs.get('id') in INTRO_TARGETS):
            parent = parent.parent
        if parent:
            intro_targets[identity] = INTRO_TARGETS[parent.attrs['id']]
    hub = '<article id="start-here" class="start-content docs-entry-hub" tabindex="-1"><header class="start-masthead"><p class="docs-breadcrumb">CyberAlchemy Lab / Getting started</p><h1>Start here</h1><p class="start-deck">Choose a path for the work you want to understand. Each path links the relevant explanations, examples and guides.</p><p class="start-reading-time">Six reading paths · No prior knowledge of the Lab required</p></header>' + picker + utilities + fragment_links(intro_targets) + '</article>'
    hub_page = re.sub(r'<article id="start-here".*?</article>', lambda _: hub, intro, count=1, flags=re.S)
    hub_page = re.sub(r'<aside class="docs-local-nav".*?</aside>', local_outline([('reading-paths','Choose a reading path'),('direct-lookup','Direct lookup')]), hub_page, count=1, flags=re.S)
    hub_page = hub_page.replace('</head>', '<link rel="stylesheet" href="assets/paper-crimson/migration.css"><script src="assets/paper-crimson/migrated-fragments.js" defer></script></head>', 1)
    (lab / 'start-here.html').write_text(hub_page)
    # A per-block ledger makes intentional consolidation reviewable.
    mappings = {
        'index.html': {'lab':'company-brain.html#company-knowledge','how':'company-brain.html#governed-work','continuity':'company-brain.html#agent-memory','craft':'company-brain.html#craft-in-the-lab','explore':'index.html#paper-explore'},
        'start-here.html': {identity: href for identity, (href, _) in INTRO_TARGETS.items()}}
    ledger = []
    for name in ['index.html','start-here.html']:
        doc = Document(original[name]);root = doc.by_id('lab-home' if name=='index.html' else 'start-here')
        for n in root.all(lambda n:n.tag in ['p','h1','h2','h3','dt','dd','li','figcaption']):
            text = clean(n.text())
            if not text:continue
            parent = n
            while parent and not(parent.tag=='section' and parent.attrs.get('id')):parent=parent.parent
            identity = parent.attrs['id'] if parent else 'opening'
            destination = mappings[name].get(identity, 'index.html' if name=='index.html' else 'start-here.html')
            # Navigation copy is consolidated into the six paths and utility links.
            if identity=='reading-paths':destination='start-here.html#reading-paths'
            ledger.append({'source':name,'section':identity,'text':text,'destination':destination,'disposition':'relocated or reconciled with canonical explanation','snapshot':'migrations/company-brain-20261014/'+name+'.snapshot'})
    snapshots = Path(__file__).parent / 'migrations/company-brain-20261014'
    snapshot_hashes = {file.name: hashlib.sha256(file.read_bytes()).hexdigest() for file in sorted(snapshots.glob('*.snapshot'))}
    receipt = {'snapshots': snapshot_hashes, 'schema_version':'company-brain-consolidation/v1','authority_effect':'none','home_fragments':{k:v[0] for k,v in HOME_TARGETS.items()},'intro_fragments':{k:v[0] for k,v in intro_targets.items()},'ledger':ledger,'reading_minutes':minutes,
               'preservation':'Unique meanings, caveats and destinations retained; duplicate public copy consolidated. Exact original pages are retained as source-side snapshots outside site search.'}
    (lab/'research/company-brain-migration.json').write_text(json.dumps(receipt,indent=2)+'\n')
    # Keep introductory source bindings but describe their canonical consumer.
    metadata_path = lab/'research/start-here-model.json'
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text());metadata['purpose']='Choose one of six task-based reading paths; conceptual primer consolidated into company-brain.html.';metadata['conceptual_owner']='company-brain.html';metadata['conceptual_reading_minutes']=minutes;metadata['reading_minutes']=1;metadata['reading_words']=len(clean(Document(hub).root.text()).split());metadata_path.write_text(json.dumps(metadata,indent=2)+'\n')
    return receipt


def update_sidebar(raw, destination, current=False):
    def amend(match):
        aside = match[0]
        aside = re.sub(r'<a\b[^>]*href="[^"]*company-brain\.html"[^>]*>.*?</a>', '', aside, flags=re.S)
        aside = re.sub(r'(<a\b[^>]*href="[^"]*index\.html"[^>]*>)The company brain(</a>)', r'\1The Lab\2', aside)
        link = f'<a href="{destination}" data-site-research' + (' aria-current="page"' if current else '') + '>The company brain</a>'
        aside = re.sub(r'(<a\b[^>]*href="[^"]*start-here\.html"[^>]*>.*?</a>)', lambda m:m[0]+link, aside, count=1, flags=re.S)
        repository = 'https://github.com/cyberAlchemyAI/CyberAlchemy-lab'
        if repository not in aside:
            aside = aside.replace('</nav>', f'<a href="{repository}">GitHub repository</a></nav>', 1)
        return aside
    return re.sub(r'<aside\b[^>]*class="(?:[^"]*\s)?article-tree(?:\s[^"]*)?"[^>]*>.*?</aside>', amend, raw, count=1, flags=re.S)


def finalize_ledger(stage):
    """Classify consolidation against final canonical blocks, not draft markup."""
    from build_site_search import Document, clean
    from urllib.parse import urlsplit
    lab = Path(stage)/'governance-lab-series'
    path = lab/'research/company-brain-migration.json'
    receipt = json.loads(path.read_text())
    docs = {name: Document((lab/name).read_text()) for name in ['index.html','company-brain.html','start-here.html']}
    for row in receipt['ledger']:
        url = urlsplit(row['destination']);doc=docs[url.path or row['source']]
        node=doc.by_id(url.fragment) if url.fragment else doc.root
        if node is None:
            raise ValueError('Missing canonical reconciliation destination: '+row['destination'])
        exact = row['text'] in clean(node.text())
        row['disposition'] = ('kept' if (url.path or row['source'])==row['source'] else 'relocated') if exact else 'merged'
        row['rationale'] = 'Exact original explanatory text remains at the destination.' if exact else {
            'opening':'One approved homepage opening and incident example; availability and research links remain at their existing owners.',
            'lab':'The conceptual introduction and role map explain enduring project knowledge; the knowledge cycle is in #governed-work.',
            'how':'Governance questions, evidence, scoped decisions and separate change/continuation routes explain the same responsibilities.',
            'continuity':'The single detailed handoff preserves durable state, temporary instances, source-bound views, refresh/pause and learning evidence.',
            'craft':'The existing Craft primer and technical model retain pure evaluation, state change and separate authority.',
            'explore':'Destinations are consolidated into the current homepage, docs navigation and source/research pages.',
            'organize-knowledge':'The conceptual introduction describes connected knowledge; its incident section preserves the fictional case and role distinctions.',
            'three-questions':'The three lenses are combined with their existing general questions in #governed-work.',
            'choose-your-path':'The six task paths and compact direct lookup replace competing chooser descriptions.',
            'reading-paths':'The six task-based path titles, descriptions and links remain.'
        }.get(row['section'],'The canonical explanation retains the substantive distinctions; repeated framing and reading instructions are consolidated.')
    receipt['disposition_counts']={key:sum(r['disposition']==key for r in receipt['ledger']) for key in ['kept','relocated','merged']}
    path.write_text(json.dumps(receipt,indent=2)+'\n')
