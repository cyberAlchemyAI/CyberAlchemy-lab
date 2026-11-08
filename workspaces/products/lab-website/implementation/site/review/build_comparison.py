#!/usr/bin/env python3
"""Render the opening-text sample in three editorial versions."""
from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parent
VARIANTS = [('original', 'current', 'Current text'),
            ('revised', 'revised', 'Concise'),
            ('editorial', 'editorial', 'Natural editorial')]
FORBIDDEN = [
    'can', 'may', 'just', 'that', 'very', 'really', 'literally', 'actually',
    'certainly', 'probably', 'basically', 'could', 'maybe', 'delve', 'embark',
    'enlightening', 'esteemed', 'shed light', 'craft', 'crafting', 'imagine',
    'realm', 'game-changer', 'unlock', 'discover', 'skyrocket', 'abyss',
    'not alone', 'in a world where', 'revolutionize', 'disruptive', 'utilize',
    'utilizing', 'dive deep', 'tapestry', 'illuminate', 'unveil', 'pivotal',
    'intricate', 'elucidate', 'hence', 'furthermore', 'however', 'harness',
    'exciting', 'groundbreaking', 'cutting-edge', 'remarkable', 'it',
    'remains to be seen', 'glimpse into', 'navigating', 'landscape', 'stark',
    'testament', 'in summary', 'in conclusion', 'moreover', 'boost',
    'skyrocketing', 'opened up', 'powerful', 'inquiries', 'ever-evolving',
]


def text_markup(row, key):
    chunks = row[key].split('\n\n')
    if row['role'] in {'heading', 'subheading'}:
        tag = 'h3' if row['role'] == 'heading' else 'h4'
        return f'<{tag}>{escape(row[key])}</{tag}>'
    if row['role'] == 'definition':
        return '<blockquote>' + ''.join('<p>' + escape(p) + '</p>' for p in chunks) + '</blockquote>'
    return ''.join('<p>' + escape(p) + '</p>' for p in chunks)


def words(value):
    return len(re.findall(r"\b[\w]+(?:[’'-][\w]+)*\b", value))


def build():
    data = json.loads((ROOT / 'opening-style-sample.json').read_text())
    rows = [row for section in data['sections'] for row in section['rows']]
    for row in rows:
        if row['role'] == 'definition' and any(row[key] != row['original'] for key, _, _ in VARIANTS):
            raise ValueError('The exact formal definition must retain its wording.')
        value = row['revised']
        violations = [phrase for phrase in FORBIDDEN if re.search(r'(?<!\w)' + re.escape(phrase) + r'(?!\w)', value, re.I)]
        if any(c in value for c in ['—', ';', '*', '#']):
            violations.append('excluded punctuation')
        if re.search(r'not just|in closing|in conclusion', value, re.I):
            violations.append('excluded construction')
        if violations:
            raise ValueError(f"{row['id']}: {violations}")
    original_words = sum(words(row['original']) for row in rows)
    revised_words = sum(words(row['revised']) for row in rows)
    editorial_words = sum(words(row['editorial']) for row in rows)
    reduction = round((1 - revised_words / original_words) * 100)
    sections = []
    for section in data['sections']:
        pairs = []
        for row in section['rows']:
            same = len({row[key] for key, _, _ in VARIANTS}) == 1
            passages = ''.join(f'<div class="passage {css}" data-version="{css}" aria-label="{label}"><span class="mobile-label">{label}</span>{text_markup(row, key)}</div>' for key, css, label in VARIANTS)
            pairs.append(f'''<div class="pair" id="{escape(row['id'])}" data-identical="{str(same).lower()}">
{passages}
</div>''')
        sections.append(f'''<section id="{escape(section['id'])}" aria-labelledby="{escape(section['id'])}-title">
<div class="section-heading"><span>{len(sections) + 1:02}</span><h2 id="{escape(section['id'])}-title">{escape(section['label'])}</h2></div>
{''.join(pairs)}</section>''')
    links = ''.join(f'<a href="#{escape(section["id"])}">{escape(section["label"])}</a>' for section in data['sections'])
    html = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light"><title>Opening sections | Writing comparison | CyberAlchemy Lab</title>
<link rel="icon" type="image/svg+xml" href="../source/governance-lab-series/assets/kep/cyberalchemy-lab-logo-light-v2.svg">
<link rel="stylesheet" href="../source/governance-lab-series/assets/kep/design-system.css">
<style>
:root{--paper:#fdfaf3;--ink:#282725;--muted:#66635e;--line:#d6d1c6;--accent:#a51b33;--new:#17706a;--editorial:#655080;--font:var(--ds-font-ui,system-ui,sans-serif)}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:130px}body{margin:0;color:var(--ink);background:var(--paper);font-family:var(--font)}
a{color:inherit;text-underline-offset:4px}button,input{font:inherit}button{cursor:pointer}button:focus-visible,a:focus-visible,input:focus-visible{outline:3px solid var(--new);outline-offset:4px}
.skip{position:fixed;top:-100px;left:20px;background:var(--ink);color:white;padding:12px;z-index:10}.skip:focus{top:16px}
.topbar{max-width:1680px;margin:auto;padding:27px 32px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;gap:24px}.topbar img{display:block;width:155px;height:auto}.topbar a:last-child{font-size:13px;color:var(--muted)}
.intro{max-width:1680px;margin:auto;padding:58px 32px 36px}.eyebrow{text-transform:uppercase;font-size:11px;letter-spacing:.15em;color:var(--accent);margin:0 0 15px}h1{font-family:var(--ds-font-display,Georgia,serif);font-weight:400;font-size:clamp(36px,5vw,58px);line-height:1.12;letter-spacing:-.025em;margin:0 0 22px}
.statistics{display:flex;gap:28px;flex-wrap:wrap;color:var(--muted);font-size:13px;margin:0}.statistics span:nth-child(2){color:var(--new)}.statistics span:last-child{color:var(--editorial)}
.controls{position:sticky;top:0;z-index:5;background:var(--paper);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}.control-inner{max-width:1680px;margin:auto;display:flex;align-items:center;justify-content:space-between;gap:24px;padding:17px 32px}.view-controls{display:flex;gap:5px;flex-wrap:wrap}.view-controls button{background:transparent;border:0;padding:9px 14px;color:var(--muted);border-radius:2px;font-size:13px}.view-controls button[aria-pressed="true"]{background:var(--ink);color:white}.hide-control{display:flex;align-items:center;gap:9px;font-size:12px;color:var(--muted)}.hide-control input{width:17px;height:17px;accent-color:var(--new)}
.layout{display:grid;grid-template-columns:150px minmax(0,1fr);gap:30px;max-width:1680px;margin:auto;padding:38px 32px 80px}.section-nav{position:sticky;top:100px;align-self:start}.section-nav a{display:block;font-size:12px;line-height:1.6;padding:11px 0;text-decoration:none;color:var(--muted)}.section-nav a[aria-current="location"]{color:var(--accent)}.comparison{min-width:0}
.column-heads{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));margin:0 0 12px;font-size:12px;letter-spacing:.08em;text-transform:uppercase}.column-heads span{padding:0 20px 15px}.column-heads span:nth-child(2){color:var(--new)}.column-heads span:last-child{color:var(--editorial)}
.section-heading{display:flex;gap:17px;align-items:baseline;border-top:1px solid var(--line);padding-top:26px;margin:12px 0 24px}.section-heading>span{font-size:11px;color:var(--accent)}h2{font-size:15px;line-height:1.4;margin:0;font-weight:600}
.pair{display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}.passage{padding:8px 20px 23px;font-size:16px;line-height:1.85;min-width:0;overflow-wrap:break-word}.revised,.editorial{border-left:1px solid var(--line)}.passage p{margin:0 0 16px}.passage p:last-child{margin-bottom:0}.passage h3{font-family:var(--ds-font-display,Georgia,serif);font-size:30px;font-weight:400;line-height:1.25;margin:0 0 8px}.passage h4{font-size:17px;line-height:1.5;margin:0 0 8px;font-weight:600}.passage blockquote{margin:0;padding:0 0 0 18px;border-left:2px solid var(--new);font-size:15px}.editorial blockquote{border-color:var(--editorial)}.mobile-label{display:none}
body:not([data-view="both"]) .pair{display:block;border:0;margin-bottom:0}body[data-view="current"] .passage:not(.current),body[data-view="revised"] .passage:not(.revised),body[data-view="editorial"] .passage:not(.editorial){display:none}body:not([data-view="both"]) .column-heads{display:none}body:not([data-view="both"]) .passage{max-width:700px;border:0;padding-left:0;padding-right:0}
body[data-hide-identical="true"] .pair[data-identical="true"]{display:none}footer{border-top:1px solid var(--line);max-width:1680px;margin:auto;padding:22px 32px 34px;color:var(--muted);font-size:12px;display:flex;justify-content:space-between;gap:24px}
@media(max-width:1300px){.layout{grid-template-columns:135px 1fr;gap:24px}.passage{font-size:15px;padding-left:16px;padding-right:16px}.column-heads span{padding-left:16px;padding-right:16px}}
@media(max-width:1050px){html{scroll-padding-top:160px}.topbar,.intro,.control-inner{padding-left:22px;padding-right:22px}.intro{padding-top:38px}.control-inner{align-items:flex-start;flex-direction:column;gap:12px;padding-top:12px;padding-bottom:12px}.layout{display:block;padding:22px 22px 50px}.section-nav{position:static;display:flex;flex-wrap:wrap;gap:0 18px;border-bottom:1px solid var(--line);margin-bottom:28px;padding-bottom:12px}.column-heads{display:none}.pair{display:block;border-bottom:1px solid var(--line);margin-bottom:18px}.passage,.revised,.editorial{padding:12px 0 20px;border:0;font-size:16px}.revised,.editorial{padding-top:14px}.mobile-label{display:block;font-size:10px;color:var(--muted);letter-spacing:.08em;text-transform:uppercase;margin-bottom:9px}.revised .mobile-label{color:var(--new)}.editorial .mobile-label{color:var(--editorial)}.passage h3{font-size:27px}.topbar img{width:135px}.statistics{gap:10px 20px}footer{padding-left:22px;padding-right:22px;flex-wrap:wrap}body:not([data-view="both"]) .mobile-label{display:none}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{.controls,.section-nav,.topbar a:last-child,.skip,footer{display:none}.layout{display:block;padding:0}.intro{padding:0 0 20px}.column-heads{display:grid}.pair{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));break-inside:avoid;border:0}.passage{font-size:9pt;padding-right:12px}.revised,.editorial{padding-left:12px;border-left:1px solid var(--line)}.editorial{padding-right:0}.mobile-label{display:none}.section-heading{break-after:avoid}h1{font-size:27pt}.passage h3{font-size:16pt}}
</style></head>
<body data-view="both" data-hide-identical="false"><a class="skip" href="#comparison">Skip to comparison</a>
<header class="topbar"><a href="../dist/index.html" aria-label="CyberAlchemy Lab home"><img src="../source/governance-lab-series/assets/kep/cyberalchemy-lab-logo-light-v2.svg" alt="CyberAlchemy Lab" width="470" height="110"></a><a href="__SOURCE__">Read the guide ↗</a></header>
<div class="intro"><p class="eyebrow">Writing comparison</p><h1>Opening sections</h1><p class="statistics"><span>Current text: __ORIGINAL__ words</span><span>Concise: __REVISED__ words</span><span>Natural editorial: __EDITORIAL__ words</span></p></div>
<div class="controls"><div class="control-inner"><div class="view-controls" role="group" aria-label="Reading view"><button type="button" data-view="both" aria-pressed="true">All three</button><button type="button" data-view="current" aria-pressed="false">Current only</button><button type="button" data-view="revised" aria-pressed="false">Concise only</button><button type="button" data-view="editorial" aria-pressed="false">Editorial only</button></div><label class="hide-control"><input type="checkbox" id="hide-identical">Hide identical passages</label></div></div>
<div class="layout"><nav class="section-nav" aria-label="Sections">__LINKS__</nav><main class="comparison" id="comparison"><div class="column-heads"><span>Current text</span><span>Concise</span><span>Natural editorial</span></div>__SECTIONS__</main></div>
<footer><span>CyberAlchemy Lab</span><a href="#comparison">Back to comparison ↑</a></footer>
<script>
for(const button of document.querySelectorAll('[data-view] button[data-view]')){
  button.addEventListener('click',()=>{
    document.body.dataset.view=button.dataset.view;
    for(const sibling of document.querySelectorAll('button[data-view]'))sibling.setAttribute('aria-pressed',String(sibling===button));
  });
}
document.getElementById('hide-identical').addEventListener('change',event=>{document.body.dataset.hideIdentical=String(event.target.checked);});
const links=[...document.querySelectorAll('.section-nav a')];
if('IntersectionObserver' in window){
  const observer=new IntersectionObserver(entries=>{
    for(const entry of entries)if(entry.isIntersecting){for(const link of links){if(link.hash==='#'+entry.target.id)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current');}}
  },{rootMargin:'-100px 0px -60% 0px'});
  document.querySelectorAll('main section').forEach(section=>observer.observe(section));
}
</script></body></html>'''
    for key, value in {'SOURCE': escape(data['source']), 'ORIGINAL': str(original_words),
                       'REVISED': str(revised_words), 'EDITORIAL': str(editorial_words),
                       'LINKS': links, 'SECTIONS': ''.join(sections)}.items():
        html = html.replace('__' + key + '__', value)
    output = ROOT / 'opening-style-comparison.html'
    output.write_text(html, encoding='utf-8')
    print(json.dumps({'output': str(output), 'rows': len(rows), 'original_words': original_words,
                      'revised_words': revised_words, 'reduction_percent': reduction,
                      'editorial_words': editorial_words,
                      'revised_style_rules': 'pass'}))


if __name__ == '__main__':
    build()
