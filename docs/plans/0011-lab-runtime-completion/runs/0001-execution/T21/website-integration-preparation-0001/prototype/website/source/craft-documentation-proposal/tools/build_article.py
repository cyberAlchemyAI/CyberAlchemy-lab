#!/usr/bin/env python3
"""Build the local article and offline SVG figures from craft-model.md."""
from pathlib import Path
from html import escape
import hashlib
import json
import re
import shutil
import textwrap
import os

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
FIGURES = ASSETS / 'figures'
FIGURES.mkdir(parents=True, exist_ok=True)
KEP_SOURCE = ROOT.parent / 'governance-lab-series' / 'assets' / 'kep'
(ASSETS / 'kep').mkdir(exist_ok=True)
for name in ['design-system.css', 'cyberalchemy-lab-logo-light-v2.svg', 'cyberalchemy-orb-frozen.webp']:
    shutil.copy2(KEP_SOURCE / name, ASSETS / 'kep' / name)

PALETTE = {
    'neutral': ('#f7f4ed', '#a49b8c', '#242322'),
    'blue': ('#eef4fb', '#6488b6', '#17395f'),
    'orange': ('#fff3e9', '#c68455', '#703a1a'),
    'purple': ('#f5f0fa', '#9c83b5', '#4e366b'),
    'green': ('#edf6ef', '#77a585', '#235439'),
    'red': ('#fff0f0', '#bd7d87', '#7d2435'),
}


class Diagram:
    def __init__(self, width, height, title, description):
        self.width, self.height = width, height
        self.title, self.description = title, description
        self.nodes, self.edges, self.labels = [], [], []

    def node(self, x, y, w, h, lines, tone='neutral', shape='rect'):
        fill, stroke, ink = PALETTE[tone]
        if shape == 'diamond':
            points = f'{x+w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}'
            shape_html = f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
        elif shape == 'store':
            shape_html = f'<rect x="{x}" y="{y+12}" width="{w}" height="{h-24}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
            shape_html += f'<ellipse cx="{x+w/2}" cy="{y+h-12}" rx="{w/2}" ry="12" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
            shape_html += f'<rect x="{x+1}" y="{y+h-27}" width="{w-2}" height="15" fill="{fill}"/>'
            shape_html += f'<ellipse cx="{x+w/2}" cy="{y+12}" rx="{w/2}" ry="12" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
        else:
            shape_html = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
        wrapped = []
        for i, line in enumerate(lines):
            # Bold titles have wider glyphs. Body lines keep the original
            # wrapping so narrow nodes gain no unnecessary extra rows.
            wrap_width=max(16,int((w-28)/(9.8 if i==0 else 7.5)))
            for part in textwrap.wrap(line, wrap_width, break_long_words=False, break_on_hyphens=False):
                wrapped.append((part, i == 0))
        center_y = y + h/2 + (6 if shape == 'store' else 0)
        start_y = center_y - (len(wrapped)-1)*11 + 5
        text = ''.join(f'<text x="{x+w/2}" y="{start_y+i*22}" text-anchor="middle" fill="{ink}" font-size="{16 if bold else 15}" font-weight="{600 if bold else 400}">{escape(line)}</text>' for i, (line, bold) in enumerate(wrapped))
        self.nodes.append(f'<g>{shape_html}{text}</g>')
        return (x, y, w, h)

    def edge(self, points, label=None, at=None, dashed=False):
        d = 'M ' + ' L '.join(f'{x},{y}' for x,y in points)
        dash = ' stroke-dasharray="6 5"' if dashed else ''
        self.edges.append(f'<path d="{d}" fill="none" stroke="#817a70" stroke-width="1.6" stroke-linejoin="round" marker-end="url(#arrow)"{dash}/>')
        if label:
            x, y = at
            w = max(54, len(label)*8.4+24)
            self.labels.append(f'<g><rect x="{x-w/2}" y="{y-15}" width="{w}" height="30" rx="4" fill="#fffdf8"/><text x="{x}" y="{y+5}" text-anchor="middle" font-size="16" fill="#514c46">{escape(label)}</text></g>')

    def save(self, path):
        content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(self.title)}</title><desc id="desc">{escape(self.description)}</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#817a70"/></marker></defs>
<rect width="100%" height="100%" fill="#fffdf8"/>
<g font-family="Helvetica Neue, Arial, sans-serif">{''.join(self.edges)}{''.join(self.nodes)}{''.join(self.labels)}</g></svg>'''
        path.write_text(content)


def draw(number, title, description):
    if number == 1:
        d = Diagram(880, 350, title, description)
        d.node(20, 45, 175, 100, ['New request'], 'orange')
        d.node(240, 45, 175, 100, ['Convenient local patch'], 'orange')
        d.node(460, 45, 175, 100, ['Copied rules', 'or entangled responsibilities'], 'red')
        d.node(680, 45, 180, 100, ['Harder next change', 'More investigation and coordination'], 'red')
        d.node(455, 220, 260, 85, ['Pressure for another workaround'], 'red')
        for start,end in [(195,240),(415,460),(635,680)]:
            d.edge([(start,95),(end,95)])
        d.edge([(770,145),(770,263),(715,263)])
        d.edge([(455,263),(328,263),(328,145)])
    elif number == 2:
        d = Diagram(880, 370, title, description)
        d.node(320, 20, 240, 60, ['13 active backend roles'])
        cards = [(20, 'Structural', ['Entity', 'Value Object', 'Enum'], 'blue'), (240, 'Behavioral', ['Operation · Query', 'Calculation · Rule', 'Policy · Workflow'], 'orange'), (460, 'Connective', ['Interface', 'Event', 'Mapping'], 'purple'), (680, 'Lifecycle', ['State Machine'], 'green')]
        for x,label,roles,tone in cards:
            d.node(x, 155, 180, 175, [label]+roles, tone)
            d.edge([(440,80),(440,115),(x+90,115),(x+90,155)])
    elif number == 3:
        d = Diagram(900, 550, title, description)
        d.node(20, 165, 170, 100, ['Domain definitions'], 'blue')
        d.node(230, 165, 180, 100, ['Project model', 'Concepts, contracts and relationships'], 'blue')
        d.node(450, 165, 160, 100, ['Model validation', 'Checks selected inputs'], 'orange')
        d.node(680, 165, 180, 100, ['Compiler'], 'orange')
        d.node(440, 20, 180, 100, ['Architecture profile', 'Composition constraints'], 'blue')
        d.node(680, 20, 180, 100, ['Selected realizations', 'Implementation forms'], 'orange')
        d.node(660, 360, 200, 125, ['Source-code artifacts', 'Bindings to inputs and selections'])
        d.node(375, 360, 215, 125, ['Target observations', 'Inspection and evaluation'])
        d.node(30, 360, 265, 125, ['Project State', 'Governed records of results', 'Performed or pending work'])
        d.edge([(190,215),(230,215)])
        d.edge([(410,215),(450,215)])
        d.edge([(610,215),(680,215)], 'valid input', (645,195))
        d.edge([(530,120),(530,165)])
        d.edge([(770,120),(770,165)])
        d.edge([(770,265),(770,360)])
        d.edge([(660,423),(590,423)])
        d.edge([(375,423),(295,423)])
    elif number == 4:
        d = Diagram(620, 585, title, description)
        d.node(160, 20, 300, 80, ['Supplied capacity snapshot'], 'blue')
        d.node(140, 150, 340, 140, ['Within capacity?', 'requested_units <', 'available_units'], 'orange', 'diamond')
        d.node(50, 360, 200, 70, ['Accept'], 'green')
        d.node(370, 360, 200, 70, ['Reject'], 'red')
        d.node(160, 490, 300, 75, ['Return the decision', 'State unchanged'], 'blue')
        d.edge([(310,100),(310,150)])
        d.edge([(310,290),(310,325),(150,325),(150,360)], 'True', (150,324))
        d.edge([(310,290),(310,325),(470,325),(470,360)], 'False', (470,324))
        d.edge([(150,430),(150,462),(310,462),(310,490)])
        d.edge([(470,430),(470,462),(310,462),(310,490)])
    elif number == 5:
        d = Diagram(880, 390, title, description)
        d.node(20, 35, 200, 100, ['Within capacity', 'Rule'], 'orange')
        d.node(335, 35, 210, 100, ['Classify capacity', 'Calculation'], 'orange')
        d.node(660, 35, 200, 100, ['Capacity snapshot', 'Entity'], 'blue')
        d.node(315, 265, 250, 90, ['Capacity decision', 'Enum: Accept or Reject'], 'blue')
        d.edge([(335,85),(220,85)], 'calls Rule', (277,64), True)
        d.edge([(545,85),(660,85)], 'input type', (602,64), True)
        d.edge([(440,135),(440,265)], 'result type', (440,200), True)
    elif number == 6:
        d = Diagram(920, 350, title, description)
        d.node(300, 20, 320, 70, ['Selected capacity implementation'])
        cards = [(20,'Model validation',['Declarations and','connections consistent?']), (250,'Artifact verification',['Target matches the','selected implementation?']), (480,'Behavioral evaluation',['Execution produces','expected decisions?']), (710,'Completion review',['Which required actions','were actually performed?'])]
        for x,name,lines in cards:
            d.node(x,180,190,145,[name]+lines,'blue')
            d.edge([(460,90),(460,130),(x+95,130),(x+95,180)])
    elif number == 7:
        d = Diagram(840, 680, title, description)
        d.node(280, 20, 280, 75, ['New business requirement'])
        d.node(30,155,345,70,['Allow equality'],'orange')
        d.node(465,155,345,70,['Reserve capacity'],'purple')
        d.node(30,275,345,90,['Revise meaning','Definition and Rule predicate'],'orange')
        d.node(465,275,345,90,['Add reservation responsibility','State owner, writes and failures'],'purple')
        d.node(30,420,345,90,['Revise expected','boundary outcomes'],'orange')
        d.node(465,420,345,90,['Specify coordinated check and mutation','For overlapping requests'],'purple')
        d.node(230,575,380,85,['Review the successor model','Compile supported contracts','Collect new evidence'])
        for x in [202.5,637.5]:
            d.edge([(420,95),(420,125),(x,125),(x,155)])
            d.edge([(x,225),(x,275)])
            d.edge([(x,365),(x,420)])
            d.edge([(x,510),(x,540),(420,540),(420,575)])
    elif number == 8:
        d = Diagram(850, 550, title, description)
        d.node(20,45,180,135,['Agent session A','Ephemeral worker','Session memory'],'orange')
        d.node(350,35,470,155,['Durable project state','Definitions and design selections','Artifacts, observations and open work'],'neutral','store')
        d.node(350,270,210,75,['New Context View','Task-relevant selection'],'blue')
        d.node(610,270,210,75,['New Ontology View','Concepts and connections'],'blue')
        d.node(450,425,270,105,['Agent session B','Ephemeral worker','New session memory'],'orange')
        d.edge([(200,113),(350,113)], 'governed write', (275,112))
        for x in [455,715]:
            d.edge([(585,190),(585,230),(x,230),(x,270)])
            d.edge([(x,345),(x,385),(585,385),(585,425)])
    else:
        d = Diagram(880, 395, title, description)
        d.node(240,20,400,100,['A particular subject and version','Definition, model, artifact or work record'])
        cards=[(20,'Authority',['Governing meanings and rules','Permissions and scope'],'orange'), (315,'Provenance',['Inputs and producing actions','Relevant observations'],'purple'), (610,'Lifecycle',['Current state','Permitted transitions'],'green')]
        for x,name,lines,tone in cards:
            d.node(x,215,250,150,[name]+lines,tone)
            d.edge([(440,120),(440,165),(x+125,165),(x+125,215)])
    return d


source = (ROOT/'craft-model.md').read_text()
version = re.search(r'Version ([\d.]+)', source).group(1)
article = source.split('\n## Editorial notes for iteration')[0]
prefix, body = article.split('\n## 1. ', 1)
intro = '\n\n'.join(part for part in prefix.strip().split('\n\n') if not part.startswith(('#', '>')))
body = '## 1. '+body
figure_records = []


def replace_figure(match):
    code, number, caption = match.groups()
    number = int(number)
    title = re.search(r'accTitle: (.+)',code).group(1)
    description = re.search(r'accDescr: (.+)',code).group(1)
    filename = f'figure-{number:02d}.svg'
    diagram = draw(number,title,description)
    diagram.save(FIGURES/filename)
    (FIGURES/f'figure-{number:02d}.mmd').write_text(code)
    figure_records.append({'number':number,'title':title,'description':description,'filename':filename})
    minimum = 500 if number == 4 else 720
    return f'''<figure class="article-figure" id="figure-{number}" aria-labelledby="figure-caption-{number}">
<div class="figure-tools"><span>Figure {number:02d}</span><a class="diagram-open" href="assets/figures/{filename}" data-title="{escape(title,quote=True)}">Open diagram <span aria-hidden="true">↗</span></a></div>
<div class="diagram-scroll" role="region" tabindex="0" aria-label="{escape(title,quote=True)}"><img src="assets/figures/{filename}" alt="{escape(description,quote=True)}" width="{diagram.width}" height="{diagram.height}" style="--diagram-min:{minimum}px" loading="lazy" decoding="async"></div>
<p class="diagram-hint">Scroll the diagram or open it at full size.</p>
<figcaption id="figure-caption-{number}">{escape(caption)}</figcaption></figure>'''


body = re.sub(r'```mermaid\n(.*?)```\s*\*Figure (\d+)\. (.*?)\*', replace_figure, body, flags=re.S)
md = MarkdownIt('commonmark', {'html':True}).enable('table')
slugs = ['modelling','failure-causes','taxonomy','process','definition','typed-model','architecture','compilation','enforcement','evolution','agent-sessions','governance']
parts = re.split(r'(?m)^## (\d+)\. (.+)\n',body)
sections, navigation, subsection_ids = [], [], {}
for i in range(1,len(parts),3):
    number,title,text = parts[i:i+3]
    slug = slugs[int(number)-1]
    rendered = md.render(text.strip())
    table_number = 0
    def table_region(match):
        global table_number
        table_number += 1
        headings = re.findall(r'<h3[^>]*>(.*?)</h3>', rendered[:match.start()], flags=re.S)
        subject = re.sub(r'<[^>]+>', '', headings[-1]) if headings else title
        return f'<div class="table-scroll" role="region" aria-label="{escape(subject,quote=True)} table {table_number}"><table>{match[1]}</table></div>'
    rendered = re.sub(r'<table>(.*?)</table>', table_region, rendered, flags=re.S)
    rendered = re.sub(r'<pre><code class="language-([^\"]+)"',r'<pre data-language="\1"><code class="language-\1"',rendered)
    def subheading(m):
        heading = m.group(1)
        subslug = slug+'-'+re.sub(r'[^a-z0-9]+','-',re.sub(r'<[^>]+>','',heading).lower()).strip('-')
        subsection_ids[heading] = subslug
        return f'<h3 id="{subslug}">{heading}</h3>'
    rendered = re.sub(r'<h3>(.*?)</h3>',subheading,rendered)
    sections.append(f'<section class="article-section" id="{slug}" aria-labelledby="heading-{slug}"><div class="section-heading"><span class="section-number" aria-hidden="true">{int(number):02d}</span><h2 id="heading-{slug}">{escape(title)}</h2></div>{rendered}</section>')
    navigation.append(f'<li><a href="#{slug}" data-section="{slug}"><span class="toc-number">{int(number):02d}</span><span>{escape(title)}</span></a></li>')

words = len(re.findall(r'\b\w+\b', re.sub(r'```.*?```','',article,flags=re.S)))
reading_time = round(words/220)
html = f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light"><meta name="theme-color" content="#fdfaf3">
<meta name="description" content="Craft connects domain modeling, architecture and explicit code compilation. An illustrated article on its taxonomy, contracts, capacity example and agent workflows.">
<title>Craft: compiling software from explicit models</title>
<link rel="icon" type="image/svg+xml" href="assets/kep/cyberalchemy-lab-logo-light-v2.svg">
<link rel="stylesheet" href="assets/kep/design-system.css"><link rel="stylesheet" href="assets/craft-article.css">
<link rel="stylesheet" href="../governance-lab-series/assets/lab-docs.css">
<link rel="stylesheet" href="../governance-lab-series/assets/lab-craft-docs.css">
<link rel="stylesheet" href="../governance-lab-series/assets/site-search.css">
<script src="assets/craft-article.js" defer></script>
<script src="../governance-lab-series/assets/lab-craft-docs.js" defer></script>
<script src="../governance-lab-series/assets/search-engine.js" defer></script>
<script src="../governance-lab-series/assets/site-search.js" defer></script>
</head><body data-edition="craft">
<a class="skip-link" href="#article">Skip to article</a><div class="reading-progress" aria-hidden="true"></div>
<header class="topbar"><div class="topbar-inner"><a class="brand" href="../governance-lab-series/governance-lab-reference.html#start"><img src="assets/kep/cyberalchemy-lab-logo-light-v2.svg" alt="CyberAlchemy Lab" width="470" height="110"></a><span class="docs-brand-label">Knowledge &amp; work</span><nav aria-label="Main navigation"><a href="../governance-lab-series/governance-lab-reference.html#start">Overview</a><a href="../governance-lab-series/governance-lab-reference.html#governance">Guide</a><a href="../governance-lab-series/governance-lab-reference.html#system-map">System map</a><a href="../governance-lab-series/lab-reference-library.html#reference">Reference</a></nav></div></header>
<main id="top"><header class="hero"><p class="eyebrow">Craft · Software design</p><h1>Compiling software<br>from explicit models</h1><div class="hero-intro">{md.render(intro)}</div><p class="craft-example-entry"><a href="#definition">Start with the domain decision example</a></p><div class="article-meta"><span class="beta-status">In development · Preparing for closed beta</span><span>{reading_time} min read</span><span>11 October 2026</span><span>Draft {version}</span></div></header>
<div class="article-layout"><aside class="contents"><details id="article-navigation" open><summary>In this article <span aria-hidden="true">⌄</span></summary><nav aria-label="In this article"><p class="toc-label">In this article</p><ol>{''.join(navigation)}</ol></nav></details></aside>
<article id="article" tabindex="-1">{''.join(sections)}<footer class="article-footer"><p>Craft is being built within CyberAlchemy Lab.</p><a href="#top">Back to top ↑</a></footer></article></div></main>
<dialog id="diagram-dialog" aria-labelledby="dialog-title"><div class="dialog-header"><h2 id="dialog-title">Diagram</h2><button class="dialog-close" type="button" aria-label="Close diagram">Close <span aria-hidden="true">×</span></button></div><div class="dialog-image-wrap" role="region" tabindex="0" aria-label="Diagram viewport"><img id="dialog-image" src="assets/figures/figure-01.svg" alt=""></div><p class="dialog-footer"><a id="diagram-download" href="#" download>Download SVG</a></p></dialog>
</body></html>'''
(ROOT/'craft-model.html').write_text(html)
(ROOT/'article-build.json').write_text(json.dumps({'source':'craft-model.md','source_version':version,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'output':'craft-model.html','edition_date':'2026-10-11','section_count':len(sections),'figures':figure_records,'rendering':'local SVG assets; no external scripts or fonts','editorial_appendix':'retained in Markdown, omitted from article'},indent=2)+'\n')
print(f'Created craft-model.html from draft {version}: {len(sections)} sections, {len(figure_records)} SVG figures.')

# Keep the shared site index current when Craft is rebuilt on its own.
import sys
sys.path.insert(0, str(ROOT.parent / "governance-lab-series"))
from build_site_search import build as build_site_search
if os.environ.get('LAB_SITE_SKIP_SEARCH_INDEX') != '1':
    build_site_search()
