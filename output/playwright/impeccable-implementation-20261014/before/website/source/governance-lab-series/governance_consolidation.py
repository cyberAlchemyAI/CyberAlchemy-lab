"""Preserve legacy governance URLs while the guide owns the explanations."""
from html import escape
import json
import re

from build_site_search import Document, clean


ROUTES = {'authority': 'governance', 'provenance': 'evidence', 'lifecycle': 'change'}
LEGACY_IDS = 'research/governance-legacy-sections.json'


def guide_additions(root):
    context = (root / 'templates/governance-authority-context.html.in').read_text().replace('{{SOURCES_AUTHORITY}}', '')
    authority = (root / 'templates/governance-authority-additions.html.in').read_text().replace('{{AUTHORITY_CONTEXT}}', context)
    return {'GOVERNANCE_AUTHORITY_ADDITIONS': authority,
            'GOVERNANCE_PROVENANCE_ADDITIONS': (root / 'templates/governance-provenance-additions.html.in').read_text(),
            'GOVERNANCE_LIFECYCLE_CONTINUITY': (root / 'templates/governance-lifecycle-continuity.html.in').read_text()}


def redirects(root, guide):
    document = Document(guide)
    ids = {n.attrs['id'] for n in document.root.all(lambda n: 'id' in n.attrs)}
    headings = {clean(n.text()): n.attrs['id'] for n in document.root.all(lambda n: n.tag in ['h2', 'h3'] and n.attrs.get('id'))}
    legacy = json.loads((root / LEGACY_IDS).read_text())
    special = {
        'incident-case': 'opening-incident-case-title', 'incident-case-heading': 'opening-incident-case-title',
        'authority-surfaces-title': 'authority-surfaces', 'authority-agent-title': 'authority-agent',
        'provenance-definition': 'opening-provenance-definition-title', 'provenance-definition-heading': 'opening-provenance-definition-title',
        'provenance-agent-title': 'provenance-agent',
        'lifecycle-definition': 'opening-lifecycle-definition-title', 'lifecycle-definition-heading': 'opening-lifecycle-definition-title',
        'kinds-of-change-title': 'kinds-of-change', 'lifecycle-agent': 'docs-change-heading-4', 'lifecycle-agent-title': 'docs-change-heading-4',
        'authority-export-definition-title': 'opening-export-definition-title',
        'series-lifecycle-lenses-title': 'opening-incident-lenses-title',
        'lens-authority-visual': 'opening-export-definition-title', 'authority-visual-title': 'opening-export-definition-title',
        'lens-provenance-visual': 'opening-provenance-example-title', 'provenance-visual-title': 'opening-provenance-example-title',
        'lens-lifecycle-visual': 'opening-lifecycle-example-title', 'lifecycle-visual-title': 'opening-lifecycle-example-title',
    }
    # Numbered headings were local to each former article. Route them to the
    # matching explanation, even when the guide uses a different heading.
    section_overrides = {
        'authority': {
            'authority-agent': 'opening-authority-example-title',
            'authority-agent-title': 'opening-authority-example-title',
            'docs-part-heading-5': 'opening-authority-example-title',
            'docs-part-heading-6': 'authority-agent',
        },
        'provenance': {
            'provenance-agent': 'opening-provenance-example-title',
            'provenance-agent-title': 'opening-provenance-example-title',
            'docs-part-heading-5': 'docs-evidence-heading-2',
            'docs-part-heading-6': 'docs-evidence-heading-3',
            'docs-part-heading-8': 'provenance-agent',
        },
        'lifecycle': {
            'docs-part-heading-5': 'docs-change-heading-2',
            'docs-part-heading-6': 'docs-change-heading-3',
            'docs-part-heading-7': 'docs-change-heading-3',
        },
    }
    pages, metadata = {}, []
    for key, route in ROUTES.items():
        filename = 'governance-' + key + '.html'
        mapping = {}
        for record in legacy['pages'][filename]['anchors']:
            old = record['id']
            mapped = section_overrides[key].get(old) or special.get(old)
            if old.startswith('series-') and old.endswith('-case-title'):
                mapped = 'opening-incident-case-title'
            if old.startswith('series-') and old.endswith(('-definition-title', '-example-title')):
                mapped = old.replace('series-', 'opening-', 1)
            if old == 'top' or old == 'governance-part':
                mapped = route
            if old == 'further-title':
                mapped = route
            if not mapped and old in ids:
                mapped = old
            if not mapped:
                mapped = headings.get(record.get('text', '')) or special.get(record.get('section_id')) or record.get('section_id')
            if mapped not in ids:
                mapped = route
            mapping[old] = mapped
        assert all(target in ids for target in mapping.values()), filename
        title = key.capitalize() + ' in the Lab guide'
        target = 'governance-lab-reference.html#' + route
        encoded = json.dumps(mapping, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
        pages[filename] = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} · CyberAlchemy Lab</title><link rel="canonical" href="{target}"><meta name="robots" content="noindex">
<link rel="stylesheet" href="assets/kep/design-system.css">
<script>
(() => {{
  const sections = {encoded};
  let fragment; try {{ fragment = decodeURIComponent(location.hash.slice(1)); }} catch {{ fragment = ''; }}
  const destination = new URL('governance-lab-reference.html', location.href);
  destination.search = location.search;
  destination.hash = Object.prototype.hasOwnProperty.call(sections, fragment) ? sections[fragment] : '{route}';
  location.replace(destination.href);
}})();
</script><noscript><meta http-equiv="refresh" content="1; url={target}"></noscript>
<style>body{{margin:0;padding:3rem 1.5rem;font:1rem/1.7 var(--ds-font-ui);color:var(--ds-ink);background:var(--ds-canvas)}}main{{max-width:38rem;margin:auto}}h1{{font-size:1.5rem}}a{{color:var(--ds-accent)}}</style>
</head><body><main><h1>{escape(title)}</h1><p>This topic is now part of the guide.</p><p><a href="{target}">Continue to {key} →</a></p></main></body></html>
'''
        metadata.append({'legacy_page': filename, 'destination': target, 'section_map': mapping,
                         'fallback': route, 'query_handling': 'Preserved', 'history_handling': 'replace',
                         'without_javascript': 'Timed redirect and manual link to the guide chapter.'})
    return pages, metadata
