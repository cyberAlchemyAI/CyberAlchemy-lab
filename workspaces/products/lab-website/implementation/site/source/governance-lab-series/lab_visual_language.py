"""Shared editorial icons and colors; these do not change Lab record semantics."""
from html import escape


CONCEPTS = {
    'intent': {'label': 'Intent', 'icon': 'compass', 'color': '#805616', 'console_color': '#d5b072'},
    'product': {'label': 'Product', 'icon': 'briefcase', 'color': '#31547a', 'console_color': '#9ab9e4'},
    'project': {'label': 'Project', 'icon': 'folder', 'color': '#23665f', 'console_color': '#85c3b6'},
    'work': {'label': 'Work', 'icon': 'hammer', 'color': '#b94812', 'console_color': '#eaa176'},
    'agent': {'label': 'Actors & agents', 'icon': 'robot', 'color': '#5c55b8', 'console_color': '#bcb4ff'},
}

# Original 24-unit geometry matches the system map, including supporting roles.
ICONS = {
    'compass': '<circle cx="12" cy="12" r="9"/><path d="m16 8-2.5 5.5L8 16l2.5-5.5Z"/>',
    'briefcase': '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V4h8v3M3 12c6 3 12 3 18 0M12 11v4"/>',
    'folder': '<path d="M3 7V5h7l2 3h9v12H3Z"/>',
    'hammer': '<path d="m14 4 6 6-3 3-6-6Zm-3 3-7 7 3 3 7-7M3 21l4-4"/>',
    'robot': '<rect x="4" y="6" width="16" height="15" rx="3"/><path d="M12 2v4M1 12h3m16 0h3M8 11v2m8-2v2M9 17h6"/>',
    'target': '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    'link': '<path d="m10 7 2-2a5 5 0 0 1 7 7l-2 2M14 17l-2 2a5 5 0 0 1-7-7l2-2m1 6 8-8"/>',
    'wrench': '<path d="M14 4a6 6 0 0 0-6 8L3 17a2.8 2.8 0 0 0 4 4l5-5a6 6 0 0 0 8-6l-4 3-4-4Z"/>',
    'clipboard': '<path d="M8 5H4v17h16V5h-4"/><rect x="8" y="2" width="8" height="5" rx="2"/><path d="M8 12h8M8 17h6"/>',
    'archive': '<path d="M3 3h18v5H3ZM5 8v13h14V8M9 12h6M10 16h4"/>',
    'memory': '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 9h10M7 13h7M7 17h4"/>',
    'bulb': '<path d="M8 15a7 7 0 1 1 8 0v3H8Zm1 7h6M9 18h6M12 10v8"/>',
}

NODE_CONCEPTS = {
    'purpose': 'intent', 'intent': 'intent', 'resolution': 'intent',
    'product': 'product', 'capability': 'product', 'realization': 'product',
    'project': 'project', 'goal': 'project', 'project-state': 'project',
    'work-system': 'work', 'work': 'work', 'implementation': 'work',
    'agent-session': 'agent', 'actor': 'agent', 'profile': 'agent',
    'assignment': 'agent', 'instance': 'agent', 'delegation': 'agent',
    'memory': 'agent', 'tool': 'agent', 'action': 'agent',
}

ICON_BINDINGS = {
    'INTENT': ('intent', 'compass'), 'INTENT_RESOLUTION': ('intent', 'target'),
    'PRODUCT': ('product', 'briefcase'), 'PRODUCT_CAPABILITY': ('product', 'target'),
    'CAPABILITY_BINDING': ('product', 'link'), 'IMPLEMENTATION': ('work', 'wrench'),
    'PROJECT': ('project', 'folder'), 'GOAL': ('project', 'target'),
    'WORK': ('work', 'hammer'), 'AGENT': ('agent', 'robot'),
    'AGENT_ASSIGNMENT': ('agent', 'clipboard'), 'PROJECT_STATE': ('project', 'archive'),
    'SESSION_MEMORY': ('agent', 'memory'), 'AGENT_REFLECTION': ('agent', 'bulb'),
    'TOOLS': ('agent', 'wrench'),
}


def model_icon(concept, glyph=None):
    glyph = glyph or CONCEPTS[concept]['icon']
    return (f'<svg class="lab-icon" data-model-icon="{escape(concept)}" '
            'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            f'aria-hidden="true" focusable="false">{ICONS[glyph]}</svg>')


def bind_model_icons(content):
    for name, (concept, glyph) in ICON_BINDINGS.items():
        content = content.replace('{{' + name + '_ICON}}', model_icon(concept, glyph))
    return content


def svg_glyph(concept, x, y, glyph=None):
    glyph = glyph or CONCEPTS[concept]['icon']
    return (f'<g class="model-svg-icon" data-model-glyph="{concept}" '
            f'transform="translate({x},{y})" aria-hidden="true">{ICONS[glyph]}</g>')


def model_styles(scope=':root'):
    tokens = ''.join(f'--lab-model-{key}:{value["color"]};' for key, value in CONCEPTS.items())
    console_tokens = ''.join(f'--lab-model-{key}:{value["console_color"]};' for key, value in CONCEPTS.items())
    rules = '\n'.join(
        f'[data-model-concept="{key}"]{{ --model-color:var(--lab-model-{key}); --smap-color:var(--lab-model-{key}); }}'
        for key in CONCEPTS)
    return f'''/* Generated from lab_visual_language.py. */
{scope}{{{tokens}}}
[data-theme="console"]{{{console_tokens}}}
{rules}
.lab-icon, .diagram svg.lab-icon {{ display:block; width:1.375rem; height:1.375rem; min-width:0; flex-shrink:0; fill:none; stroke:currentColor; stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round; }}
.model-heading {{ display:flex; align-items:center; gap:.75rem; }}
.model-heading > .lab-icon {{ color:var(--model-color); }}
.model-heading > span {{ min-width:0; }}
.model-svg-node > rect, .model-svg-project > rect {{ fill:color-mix(in srgb,var(--model-color) 7%,var(--ds-surface)); stroke:var(--model-color); }}
.model-svg-node > .node-title, .model-svg-project > .node-title {{ fill:var(--model-color); }}
.model-svg-node > .model-svg-small-title {{ font-size:15px; }}
.model-svg-icon {{ color:var(--model-color); fill:none; stroke:currentColor; stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round; }}
.model-svg-session > .session-boundary {{ fill:color-mix(in srgb,var(--model-color) 4%,var(--ds-surface)); stroke:var(--model-color); }}
.model-svg-session > .small-label {{ fill:var(--model-color); }}
@media(forced-colors:active) {{
  [data-model-concept] {{ --model-color:CanvasText; --smap-color:CanvasText; }}
  .model-svg-node > rect, .model-svg-project > rect, .model-svg-session > .session-boundary {{ fill:Canvas; stroke:CanvasText; }}
}}
'''
