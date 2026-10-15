"""Verified diagram corrections shared by the maintained website."""
import re

DIAGRAMS = {
    'figure-evidence-chain': ('evidence-chain.svg', 'the evidence chain'),
    'figure-admission-and-histories': ('admission-and-histories.svg', 'admission and histories'),
    'figure-meaning-shape-record': ('meaning-shape-record.svg', 'meaning, format and record'),
    'figure-records-and-ontology': ('records-and-ontology.svg', 'records and their ontology view'),
    'figure-agent-session': ('agent-session.svg', 'the agent session'),
}


def wrap_map_titles(text):
    # Keep the node rectangle, connections, description and subtitle unchanged.
    text = re.sub(
        r'(<text\b[^>]*id="smap-agent-assignment-title"[^>]*>)<tspan[^>]*>Agent Assignment\s*</tspan>',
        r'\1<tspan x="646" y="278">Agent </tspan><tspan x="646" y="298">Assignment</tspan>', text)
    text = re.sub(r'(<text\b[^>]*id="smap-agent-assignment-title"[^>]*><tspan x="646" y="278">)Agent(</tspan>)',
                  r'\1Agent \2', text)
    return re.sub(
        r'(<text\b[^>]*id="smap-overview-records-title"[^>]*>)<tspan[^>]*>Governed records\s*</tspan>',
        r'\1<tspan x="646" y="278">Governed </tspan><tspan x="646" y="298">records</tspan>', text)


def apply_visual_fixes(text, page, favicon, search_count):
    text = re.sub(r'<link\b[^>]*rel="icon"[^>]*>',
                  lambda _: f'<link rel="icon" type="image/svg+xml" href="{favicon}">', text)
    if page == 'index.html':
        text = re.sub(r'(<dt data-search-entry-count>)\d+', lambda m: m[1] + str(search_count), text)
    if page != 'governance-lab-series/governance-lab-reference.html':
        return text
    text = wrap_map_titles(text)
    for identity, (asset, label) in DIAGRAMS.items():
        help_id = identity + '-view-help'
        if f'id="{help_id}"' in text:
            continue
        pattern = rf'(<figure\b[^>]*id="{identity}"[^>]*>)(<div class="diagram-shell"[^>]*>)'
        tools = (f'<div class="diagram-view-tools"><span id="{help_id}">'
                 'Scroll horizontally to read the full diagram.</span>'
                 f'<a href="assets/{asset}" target="_blank" rel="noopener">Open full size'
                 f'<span class="site-search-sr-only">: {label} (new tab)</span>'
                 '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14"/></svg></a></div>')
        text = re.sub(pattern, lambda m: m[1] + tools + m[2][:-1] + f' aria-describedby="{help_id}">', text, count=1)
    return text
