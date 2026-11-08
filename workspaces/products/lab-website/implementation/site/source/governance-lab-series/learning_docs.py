"""Source-bound reading paths in the shared static documentation shell."""
from html import escape
import hashlib
import math
import re

from build_site_search import Document
from governance_series import bind_incident
from lab_visual_language import bind_model_icons


PAGES = [
    ('incident-walkthrough', 'Follow an incident', 'A guided investigation from the customer report to evidence, a proposed repair and the next owner decision.'),
    ('concept-comparisons', 'Compare the concepts', 'Distinguish the meanings, records, work, evidence and agent views used throughout CyberAlchemy Lab and Craft.'),
]


def render(root, catalog):
    shell = (root / 'templates/start-here.html.in').read_text()
    definitions = {d['term']: d for d in catalog['definitions']}
    outputs = {}
    for key, title, description in PAGES:
        content = bind_model_icons(bind_incident(root, (root / f'templates/{key}.html.in').read_text()))
        for term, definition in definitions.items():
            slug = re.sub(r'[^a-z0-9]+', '-', definition['identity'].lower()).strip('-')
            content = content.replace('{{DEF:' + term + '}}', 'lab-reference-library.html#def-' + slug)
        document = Document(content)
        sections = document.root.all(lambda n: n.tag == 'section' and n.attrs.get('id'))
        headings = [section.first(lambda n: n.tag == 'h2') for section in sections]
        assert all(headings), 'Every reading-path section needs a heading'
        toc = ''.join(f'<a href="#{escape(section.attrs["id"])}">{escape(heading.text())}</a>'
                      for section, heading in zip(sections, headings))
        minutes = math.ceil(len(re.findall(r"\b[\w’'-]+\b", document.root.text())) / 220)
        content = content.replace('{{READING_TIME}}', str(minutes))
        page = shell.replace('<title>Start here · CyberAlchemy Lab</title>', f'<title>{title} · CyberAlchemy Lab</title>')
        page = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{escape(description)}">', page)
        page = page.replace('href="#start-here"', f'href="#{key}"').replace('Skip to the introduction', 'Skip to the article')
        page = page.replace('data-site-start aria-current="page"', 'data-site-start')
        page = page.replace(f'href="{key}.html" data-site-learning="{key}"', f'href="{key}.html" data-site-learning="{key}" aria-current="page"')
        page = re.sub(r'<article id="start-here".*?</article>', f'<article id="{key}" class="start-content" tabindex="-1">{content}</article>', page, flags=re.S)
        page = re.sub(r'(<details class="docs-toc" id="start-toc"><summary>On this page</summary><nav aria-label="Headings on this page">).*?(</nav></details>)', lambda m: m[1] + toc + m[2], page, flags=re.S)
        page = page.replace('{{READING_TIME}}', str(minutes))
        assert '{{' not in page, (key, 'Unresolved reading-path placeholder')
        outputs[key + '.html'] = page
    metadata = {
        'schema_version': 'editorial-learning-paths/v1', 'authority_effect': 'none',
        'pages': list(outputs), 'scope': 'Explanatory reading paths; no new definition, admission, implementation or customer result.',
        'source_bindings': [{'source': name, 'sha256': hashlib.sha256((root / name).read_bytes()).hexdigest()}
                            for name in ['research/catalog.json', 'research/incident-extraction-case.json',
                                         '../craft-documentation-proposal/craft-model.md']],
        'diagram_meanings': ['Numbered steps show explanatory order, not an admitted relation.',
                             'Record links use only the ordered endpoint signatures declared in the captured catalog.',
                             'Session handoff selects durable Project State through newly checked views; it transfers no session memory or permission.'],
        'case_limits': ['Identifier coverage only; cause, wider impact and recovery remain unresolved.',
                        'Revision 8 is proposed; owner review and any later adoption, deployment or closure are conditional.',
                        'Calculation returns a value without reserving capacity; an Operation owns a separate state change.'],
    }
    return outputs, metadata
