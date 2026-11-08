"""Build the isolated preview; never write the maintained website or its dist."""
from pathlib import Path
from html import escape,unescape
from html.parser import HTMLParser
from markdown_it import MarkdownIt
import re,json,shutil,hashlib,os
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DIST=ROOT/'website/dist'
SITE=HERE/'site'
COPY=json.loads((HERE/'copy.json').read_text())
MD=MarkdownIt('commonmark',{'html':False}).enable('table')
GITHUB='https://github.com/cyberAlchemyAI/CyberAlchemy-lab'
LAB='governance-lab-series/'
CANDIDATES={
 'CMP':LAB+'campaign-comparison.html','EVO':LAB+'campaign-comparison.html#even-the-rules-need-a-way-to-grow',
 'REP':LAB+'customer-reply.html','HAND':LAB+'sales-handoff.html','TEAM':LAB+'team-examples.html',
 'TEAM-01':LAB+'customer-reply.html','TEAM-02':LAB+'sales-handoff.html','TEAM-03':LAB+'campaign-comparison.html',
 'TEAM-04':LAB+'guides/finance-discrepancy.html','TEAM-05':LAB+'guides/onboarding.html','TEAM-06':LAB+'guides/contract-history.html',
 'TEAM-07':LAB+'guides/supplier-comparison.html','TEAM-08':LAB+'guides/research-decision.html','TEAM-09':LAB+'guides/suspicious-activity.html',
 'TEAM-10':LAB+'guides/software-change.html','BRAIN':LAB+'company-brain.html','MODEL':LAB+'governance-lab-reference.html',
 'AGENT':LAB+'resume-agent-work.html','NORTH':LAB+'incident-walkthrough.html','LEARN':LAB+'governance-lab-reference.html#learning',
 'CRAFT':'craft-documentation-proposal/craft-model.html','CRAFT-03':'craft-documentation-proposal/craft-model.html#architecture',
 'CRAFT-06':'craft-documentation-proposal/craft-model.html#capacity','CRAFT-08':'craft-documentation-proposal/craft-model.html#current-scope',
 'SRC':LAB+'source-and-status.html','RES':LAB+'research.html','CON':GITHUB,'REF':LAB+'lab-reference-library.html',
 'RUN':LAB+'runtime-overview.html','EVENT':LAB+'hackathon.html','ST':LAB+'start-here.html'}
for key in COPY:
 for family in ['CMP','EVO','BRAIN','MODEL','AGENT','NORTH','LEARN','SRC','RES','CON','CRAFT','TEAM']:
  if key.startswith(family+'-') and key not in CANDIDATES:CANDIDATES[key]=CANDIDATES[family]
ROUTES={
 LAB+'campaign-comparison.html':['CMP-01','CMP-02','CMP-03','EVO-01','EVO-02'],
 LAB+'customer-reply.html':['REP'],LAB+'sales-handoff.html':['HAND'],
 LAB+'company-brain.html':['BRAIN-01','BRAIN-02','BRAIN-03','BRAIN-04','BRAIN-05','BRAIN-06'],
 LAB+'source-and-status.html':['SRC-01','CON-01'],LAB+'research.html':['RES-01'],
 LAB+'governance-lab-reference.html':['MODEL-01','LEARN-01','LEARN-02'],
 LAB+'incident-walkthrough.html':['NORTH-01'],
 LAB+'governance-authority.html':['MODEL-02'],LAB+'governance-provenance.html':['MODEL-03'],LAB+'governance-lifecycle.html':['MODEL-04'],
 LAB+'resume-agent-work.html':['AGENT-01','AGENT-02'],
 'craft-documentation-proposal/craft-model.html':[f'CRAFT-{i:02}' for i in range(1,9)]}
for i,slug in [(4,'finance-discrepancy'),(5,'onboarding'),(6,'contract-history'),(7,'supplier-comparison'),(8,'research-decision'),(9,'suspicious-activity'),(10,'software-change')]:ROUTES[LAB+f'guides/{slug}.html']=[f'TEAM-{i:02}']
EXAMPLE_ROUTES={LAB+'campaign-comparison.html',LAB+'customer-reply.html',LAB+'sales-handoff.html'}|{r for r in ROUTES if '/guides/' in r}
BUILT={};PRESERVED={}

def rel(route,target):
 if target.startswith(('http:','https:','mailto:')):return target
 path,sep,frag=target.partition('#')
 result=os.path.relpath(path, str(Path(route).parent)).replace(os.sep,'/')
 return result+('#'+frag if sep else '')
def slug(text):return re.sub(r'[^\w\s-]','',text.lower()).strip().replace(' ','-')
def prefix(route):return '../'*len(Path(route).parent.parts)
def icon(name):
 shapes={'github':'<path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-4a3.4 3.4 0 0 0-1-2.6c3.3-.4 6.8-1.6 6.8-7.4a5.8 5.8 0 0 0-1.6-4 5.4 5.4 0 0 0-.1-4s-1.3-.4-4.1 1.5a14.3 14.3 0 0 0-7.5 0C5.7-.4 4.4 0 4.4 0a5.4 5.4 0 0 0-.1 4A5.8 5.8 0 0 0 2.7 8c0 5.8 3.5 7 6.8 7.4A3.4 3.4 0 0 0 8.5 18v4"/>','search':'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>','theme':'<path d="M20 14a8 8 0 0 1-10-10 8 8 0 1 0 10 10Z"/>'}
 return f'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">{shapes.get(name,shapes["search"])}</svg>'

def resolve(ref,route):
 ref=ref.strip();m=re.search(r'`([^`]+\.html(?:#[^`]+)?)`',ref)
 if m:return rel(route,m[1] if '/' in m[1] else LAB+m[1])
 for key in sorted(CANDIDATES,key=len,reverse=True):
  if re.match(re.escape(key)+r'(?:\b|\s|/|$)',ref):return rel(route,CANDIDATES[key])
 if 'capacity chapter' in ref.lower():return rel(route,CANDIDATES['CRAFT-06'])
 for key in sorted(CANDIDATES,key=len,reverse=True):
  if re.search(r'\b'+re.escape(key)+r'\b',ref):return rel(route,CANDIDATES[key])
 if 'craft' in ref.lower():return rel(route,CANDIDATES['CRAFT'])
 return rel(route,CANDIDATES['MODEL'])

def rendered(keys,route):
 source='\n\n'.join(COPY[k] for k in keys if k in COPY)
 # Implementation directions stay in the copy deck rather than the reader's guide.
 source=source.replace(' Preserve quoted text exactly in any later implementation.','')
 source=re.sub(r'^(?:Page title|Description|Eyebrow|Breadcrumb):[^\n]*\n?', '',source,flags=re.M)
 # Resolve each authored action independently; do not consume another bold action.
 source=re.sub(r'\*\*([^*\n]+)\*\*\s*→\s*([^\n;]+)',lambda m:f'[{m[1]}]({resolve(m[2],route)})',source)
 labels={'NORTH':'Follow Northstar','REP':'Prepare a reply','HAND':'Inspect the handoff','CRAFT':'Explore Craft','CMP':'Follow the campaign','TEAM-04':'Trace the discrepancy','TEAM-07':'Inspect the supplier comparison','TEAM-08':'Build a research brief','TEAM-09':'Examine the alert'}
 def multiple(m):
  keys=re.findall(r'[A-Z]+(?:-\d{2})?',m[1]);return ' · '.join(f'[{labels.get(key,"Open guide")}]({resolve(key,route)})' for key in keys if key in CANDIDATES)
 source=re.sub(r'→\s*((?:[A-Z]+(?:-\d{2})?\s*/\s*)+[A-Z]+(?:-\d{2})?)',multiple,source)
 source=re.sub(r'→\s*(TEAM-\d{2}|CMP|REP|HAND|BRAIN|CRAFT|MODEL|RUN|SRC|RES|CON|NORTH|AGENT|LEARN|REF|EVENT|ST)\b',lambda m:f'→ [Open guide]({resolve(m[1],route)})',source)
 for text,target in [('Search the docs','#preview-search'),('open the reference',rel(route,CANDIDATES['REF'])),('check the runtime',rel(route,CANDIDATES['RUN']))]:
  source=source.replace('**'+text+'**',f'[{text}]({target})')
 source=re.sub(r'(?m)^#{1,3}\s+(?:CMP|H|ST|EVO|TEAM)-\d{2}.*\n','',source)
 html=MD.render(source)
 # Editorial shorthand resolves to the retained subject, never an unrelated fallback.
 for label,target in [('Inspect the system map',LAB+'governance-lab-reference.html#system-map'),('Open the continuation guide',LAB+'resume-agent-work.html#maintained-detail'),('Inspect the maintained model and exact excerpts','craft-documentation-proposal/craft-model.html#maintained-detail'),('Read the current Craft model','craft-documentation-proposal/craft-model.html#maintained-detail'),('Explore the research collection',LAB+'research.html#research'),('Follow the robot-learning series','robot-learning-series/robot-learning-series.html'),('Open the selected source map',LAB+'source-and-status.html#inspect'),('Read how this edition was assembled',LAB+'source-and-status.html#inspect')]:
  html=re.sub(r'<a href="[^"]+">'+re.escape(label)+r'</a>',lambda m:'<a href="'+escape(rel(route,target),quote=True)+'">'+label+'</a>',html)
 count=0
 def heads(m):
  nonlocal count
  level=int(m[1]);text=m[2];plain=re.sub('<[^>]+>','',text);sid=slug(plain)
  if level==1:
   count+=1
   if count>1:level=2
  return f'<h{level} id="{escape(sid,quote=True)}">{text}</h{level}>'
 html=re.sub(r'<h([123])>(.*?)</h\1>',heads,html,flags=re.S)
 def table_labels(m):
  table=m[0];headers=[unescape(re.sub('<[^>]+>','',x)) for x in re.findall(r'<th[^>]*>(.*?)</th>',table,re.S)]
  def row_labels(row):
   i=0
   def cell(cell):
    nonlocal i
    label=headers[i] if i<len(headers) else 'Value';i+=1
    return '<td role="cell" data-label="'+escape(label,quote=True)+'">'+cell[1]+'</td>'
   return '<tr role="row">'+re.sub(r'<td>(.*?)</td>',cell,row[1],flags=re.S)+'</tr>'
  table=re.sub(r'<tr>(.*?)</tr>',row_labels,table,flags=re.S)
  table=table.replace('<th>','<th role="columnheader" scope="col">')
  return table.replace('<table>','<table role="table" class="metrics-table">')
 html=re.sub(r'<table>.*?</table>',table_labels,html,flags=re.S)
 html=html.replace('<table role="table"','<div class="table-region" role="region" aria-label="Comparison table" tabindex="0"><table role="table"').replace('</table>','</table></div>')
 html=re.sub(r'<p>(\s*(?:<a [\s\S]*?</a>[\s;·]*)+)</p>',r'<p class="action-row">\1</p>',html)
 return html

class Extract(HTMLParser):
 def __init__(self):super().__init__();self.start=None;self.depth=0;self.parts=[];self.ids=[];self.title=[];self.skip=0;self.text=[];self.h1=False
 def handle_starttag(self,t,a):
  d=dict(a)
  if d.get('id'):self.ids.append(d['id'])
  if t in ('script','style','nav','aside','header','footer'):self.skip+=1
  if t=='h1':self.h1=True
 def handle_endtag(self,t):
  if t in ('script','style','nav','aside','header','footer'):self.skip=max(0,self.skip-1)
  if t=='h1':self.h1=False
 def handle_data(self,d):
  if self.h1:self.title.append(d)
  if not self.skip and d.strip():self.text.append(d.strip())

def original_article(route):
 source=(DIST/route)
 if not source.exists():return ''
 raw=source.read_text()
 # The model's explorer precedes its article. Retain its complete main region.
 if route==LAB+'governance-lab-reference.html':
  m=re.search(r'<main\b[^>]*>',raw);end=raw.rfind('</main>')
  return raw[m.end():end] if m and end>=m.end() else ''
 m=re.search(r'<article\b[^>]*>',raw)
 if m:
  # Existing selected pages have one principal article; keep all contents/IDs intact.
  end=raw.rfind('</article>')
  chunk=raw[m.end():end] if end>=m.end() else ''
 else:
  m=re.search(r'<main\b[^>]*>',raw);end=raw.rfind('</main>');chunk=raw[m.end():end] if m and end>=m.end() else ''
 # Scripts from existing figures remain present, but page-level repeated navigation does not.
 return chunk

def template_links(raw,route):
 def target(m):
  value=m[1];return escape(rel(route,LAB+value[5:] if value.startswith('@LAB@') else value[6:]),quote=True)
 return re.sub(r'@(?:LAB|ROOT)@[^"\s<>]+',lambda m:target([None,m[0]]),raw)

def header(route,home=False):
 raw=(HERE/('templates/header-home.html' if home else 'templates/header-docs.html')).read_text()
 search='''<div class="docs-search" data-enhancement><label class="sr-only" for="preview-search">Search all documentation</label>'''+icon('search')+'''<input id="preview-search" type="search" placeholder="Search docs" autocomplete="off" aria-controls="preview-search-results" aria-expanded="false"><kbd>/</kbd><div id="preview-search-results" data-search-panel hidden><div class="search-panel-head"><strong>Search the documentation</strong><div class="search-panel-actions"><button type="button" data-search-clear>Clear search</button><button type="button" data-search-dismiss aria-label="Dismiss search suggestions">Close</button></div></div><label for="search-scope">Search in</label><select id="search-scope"><option value="all">All docs</option><option>Introductions</option><option>Practical guides</option><option>Craft</option><option>Runtime</option><option>Reference</option></select><p role="status" aria-live="polite" data-search-status>Enter a term to begin.</p><ul data-search-list></ul><button data-search-retry type="button" hidden>Try again</button><a href="@LAB@lab-reference-library.html">Browse the docs</a></div></div>'''
 raw=raw.replace('@SEARCH@',search)
 return '<a class="'+('skip' if home else 'skip-link')+'" href="#main-content">Skip to content</a>'+template_links(raw,route)

def footer(route):
 raw=(HERE/'templates/footer.html').read_text()
 raw+='<div class="preview-note"><span>Local content preview · Live visual identity</span><a href="@LAB@preview-options.html">Compare documentation entrances</a></div>'
 return template_links(raw,route)

def navigation_standing(route,target):
 if route==target:return ' aria-current="page"'
 if target==LAB+'team-examples.html' and route in EXAMPLE_ROUTES:return ' aria-current="location"'
 if target==LAB+'start-here.html' and route in {LAB+'start-'+k+'.html' for k in 'abc'}:return ' aria-current="location"'
 return ''

def breadcrumb(route,title):
 parts=[('<a href="'+rel(route,CANDIDATES['ST'])+'">Docs</a>')]
 if route in EXAMPLE_ROUTES:
  parts.append('<a href="'+rel(route,CANDIDATES['TEAM'])+'">Practical guides</a>')
  topic=next((g[0] for g in GUIDES if CANDIDATES[g[3]]==route),title)
  parts.append('<span>'+escape(topic)+'</span>')
 else:parts.append('<span>'+escape(title)+'</span>')
 return '<nav class="breadcrumb" aria-label="Breadcrumb">'+('<span aria-hidden="true">/</span>'.join(parts))+'</nav>'

def navtree(route):
 groups={'Getting started':[('Start here','start-here.html'),('Practical examples','team-examples.html'),('The company brain','company-brain.html')],'Follow the work':[('Campaign and meaning','campaign-comparison.html'),('A customer reply','customer-reply.html'),('A sales handoff','sales-handoff.html'),('Northstar incident','incident-walkthrough.html')],'How it develops':[('The model','governance-lab-reference.html'),('Authority','governance-authority.html'),('Provenance','governance-provenance.html'),('Lifecycle','governance-lifecycle.html'),('Learning','governance-lab-reference.html#learning'),('Fresh agent sessions','resume-agent-work.html')],'Go deeper':[('Exact reference','lab-reference-library.html'),('Build and run','runtime-overview.html'),('Research','research.html'),('Source and status','source-and-status.html')]}
 out='<aside class="site-tree article-tree start-sidebar"><details class="article-contents" open data-browse><summary>Browse documentation</summary><nav aria-label="Documentation">'
 for label,links in groups.items():
  out+=f'<div class="tree-group"><strong>{label}</strong>'
  for text,t in links:
   target=LAB+t;current=navigation_standing(route,target);out+=f'<a href="{escape(rel(route,target),quote=True)}"{current}>{text}</a>'
  out+='</div>'
 out+=f'<a class="tree-craft" href="{rel(route,CANDIDATES["CRAFT"])}"'+navigation_standing(route,CANDIDATES['CRAFT'])+'>Explore Craft</a></nav></details></aside>'
 return out

def outline(body):
 headings=re.findall(r'<h2 id="([^"]+)">(.*?)</h2>',body,re.S)
 if not headings:return ''
 return '<aside class="page-outline docs-local-nav"><details class="docs-toc" open data-outline><summary>On this page</summary><nav aria-label="Page contents">'+''.join(f'<a href="#{sid}">{re.sub("<[^>]+>","",text)}</a>' for sid,text in headings)+'</nav></details></aside>'

def shell(route,title,body,home=False):
 pr=prefix(route)
 boot="try{let t=localStorage.getItem('cyberalchemy-paper-theme')||localStorage.getItem('ob-preview-theme');document.documentElement.dataset.theme=t||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light')}catch(e){}"
 if home:
  files=['assets/kep/design-system.css','assets/hackathon-d0b010b0be1b.css','assets/paper-crimson/home.css','assets/paper-crimson/palette.css','assets/paper-crimson/migration.css','assets/diagram-reading.css']
 else:
  files=['assets/kep/design-system.css','assets/lab-docs.css','assets/lab-model-visuals.css','assets/start-here.css','assets/learning-docs.css','assets/practical-docs.css','assets/site-search.css','assets/site-typography.css','assets/paper-crimson/appearance.css']
  if 'class="docs-layout"' not in body:
   inner=re.sub(r'^<main[^>]*>|</main>$','',body)
   body='<main id="main-content" class="docs-layout">'+navtree(route)+'<article class="article-body start-content"><div class="copy-content">'+inner+'</div></article>'+outline(inner)+'</main>'
 if not home and '<aside class="page-outline' not in body:body=body.replace('class="docs-layout"','class="docs-layout docs-layout--without-outline"')
 styles=''.join('<link rel="stylesheet" href="'+escape(rel(route,LAB+f),quote=True)+'">' for f in files)
 classes='paper-home ob-preview' if home else 'site-document ob-preview'
 attrs='' if home else ' data-edition="article" data-docs-enhanced="intro"'
 frame='page-frame' if home else 'site-frame'
 return f'''<!doctype html><html lang="en" data-site-design="paper" data-palette="paper" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{escape(title)} · Local preview</title><script>{boot}</script><link rel="icon" href="{pr}governance-lab-series/assets/paper-crimson/favicon.svg">{styles}<link rel="stylesheet" href="{pr}preview-assets/preview.css"></head><body class="{classes}"{attrs}><div class="{frame}">{header(route,home)}{body}{footer(route)}</div><script>window.PREVIEW_ROOT={json.dumps(pr)};</script><script src="{pr}preview-assets/preview.js" defer></script></body></html>'''

def write(route,raw):
 p=SITE/route;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(raw);BUILT[route]=hashlib.sha256(raw.encode()).hexdigest()

def article_page(route,keys):
 content=rendered(keys,route)
 title_match=re.search(r'<h1[^>]*>(.*?)</h1>',content,re.S)
 title=re.sub('<[^>]+>','',title_match[1]) if title_match else keys[0]
 note='<p class="example-standing"><strong>About this example.</strong> This is a fictional walkthrough. Its sample inputs and outputs explain how work could be described; they are not records from an executed integration. <a href="'+rel(route,CANDIDATES['SRC'])+'">Source and status</a>.</p>' if route in EXAMPLE_ROUTES else ''
 if note and title_match:content=content[:title_match.end()]+note+content[title_match.end():]
 if route==LAB+'campaign-comparison.html':
  content=content.replace('<h2 id="the-old-report-keeps-its-history">',campaign_diagram()+'<h2 id="the-old-report-keeps-its-history">')
 if route.endswith('craft-model.html'):
  content='<span id="craft-overview" class="legacy-anchor"></span>'+content
  for alias,heading in [('capacity','four-passes-five-doesnt-the-requirement-decides'),('architecture-introduction','here-the-blueprint-runs-the-factory'),('current-scope','open-the-factory-doors-look-at-whats-inside-today')]:
   content=content.replace(f'<h2 id="{heading}">',f'<span id="{alias}" class="legacy-anchor"></span><h2 id="{heading}">')
 if route==LAB+'governance-lab-reference.html':
  content=content.replace('<h2 id="your-last-mistake-doesnt-need-to-become-company-policy">','<span id="learning" class="legacy-anchor"></span><h2 id="your-last-mistake-doesnt-need-to-become-company-policy">')
  content=content.replace('href="governance-lab-reference.html#learning">Inspect the existing learning model','href="#learning-maintained">Inspect the existing learning model')
 preserved=original_article(route)
 if route==LAB+'governance-lab-reference.html':preserved=preserved.replace('id="learning"','id="learning-maintained"')
 if route==LAB+'incident-walkthrough.html':content=content.replace('href="incident-walkthrough.html">Follow the maintained incident','href="#maintained-detail">Follow the maintained incident')
 if preserved:
  PRESERVED[route]=True
  # Preserve detailed historical explanations, exact statements, code and old anchors.
  # They remain inspectable, without duplicating the new front-door narrative by default.
  content+='<section class="maintained-source"><details id="maintained-detail"><summary>Read the maintained detailed article and exact examples</summary><div class="retained-reading">'+preserved+'</div></details></section>'
 original=(DIST/route)
 if original.exists():
  a=Extract();a.feed(original.read_text());b=Extract();b.feed(content)
  missing=set(a.ids)-set(b.ids)-{'main-content','preview-search'}
  # Non-article legacy anchors retain the original complete page as their exact subject.
  aliases=''.join(f'<span id="{escape(i,quote=True)}" class="legacy-anchor" data-legacy-anchor></span>' for i in sorted(missing))
  content=aliases+content
 body='<main id="main-content" class="docs-layout">'+navtree(route)+'<article class="article-body">'+breadcrumb(route,title)+'<div class="prose copy-content">'+content+'</div></article>'+outline(rendered(keys,route))+'</main>'
 write(route,shell(route,title,body))

def campaign_diagram():
 labels=[('Q1 · selected meaning','Business email + demo request'),('R1 · completed comparison','12 / 15 qualified under Q1'),('Q2 · proposed successor','Add a target-segment assessment'),('R2 · proposed assessment','New counts remain pending')]
 shapes=[]
 for i,(label,description) in enumerate(labels):
  y=12+i*98
  shapes.append(f'<g data-diagram-node aria-label="{escape(label+": "+description,quote=True)}"><rect x="8" y="{y}" width="264" height="78" rx="3" fill="var(--surface)" stroke="var(--line)"/><text x="20" y="{y+29}" fill="var(--ink)" font-size="15">{escape(label)}</text><text x="20" y="{y+54}" fill="var(--muted)" font-size="12">{escape(description)}</text></g>')
 edges='<defs><marker id="meaning-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 10 5 0 10Z" fill="var(--accent)"/></marker></defs><path d="M34 110V90" fill="none" stroke="var(--accent)" stroke-width="1.5" marker-end="url(#meaning-arrow)"/><text x="46" y="103" font-size="11" fill="var(--muted)">R1 uses Q1</text><path d="M34 306V286" fill="none" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="3 2" marker-end="url(#meaning-arrow)"/><text x="46" y="299" font-size="11" fill="var(--muted)">proposed Q2 basis</text><path d="M8 205H272" stroke="var(--line)" stroke-dasharray="3 4"/>'
 return '<figure data-diagram data-diagram-title="One meaning, two versions"><h3>One meaning, two versions.</h3><svg width="280" height="404" viewBox="0 0 280 404" role="group" aria-label="R1 retains Q1. Q2 and R2 remain proposed, with no new counts.">'+edges+''.join(shapes)+'</svg><button type="button" data-enhancement data-expand-diagram>Expand diagram</button><figcaption>R1 keeps its Q1 basis. The dashed pair is proposed: R2 needs its own assessment after the applicable Q2 decisions. These are separate subjects, not one approval ladder.</figcaption></figure>'

GUIDES=[
 ('Marketing','The dashboard is smiling. Should you be?','Examine a campaign, the meaning behind its numbers, and what happens when that meaning changes.','CMP','marketing','software retail services'),
 ('Customer support','The customer has already told your company this story.','Recover the history and prepare a reply with its unanswered questions still visible.','REP','support','software retail services'),
 ('Sales and customer success',"A promise shouldn't disappear at the handoff.",'Carry the accepted commitment, its conditions, and the next dependency into delivery.','HAND','sales','software services'),
 ('Finance and operations','The totals disagree. Follow the rows.','Reconcile selected records and keep the unexplained remainder open.','TEAM-04','finance','retail services manufacturing finance'),
 ('People and onboarding',"A first week shouldn't depend on finding the right person online.",'Prepare a role-specific starting pack with dated sources and accountable owners.','TEAM-05','people','software retail services manufacturing finance'),
 ('Legal and contract operations','Which version of the promise did everyone accept?','Compare supplied revisions and the approval evidence before assessing an obligation.','TEAM-06','legal','software retail services manufacturing finance'),
 ('Procurement','The cheapest offer still needs to meet the brief.','Compare supplied offers against the requirements you selected.','TEAM-07','procurement','retail services manufacturing'),
 ('Research and strategy','A confident answer still owes you its sources.','Follow claims to their sources and retain competing explanations.','TEAM-08','research','software retail services manufacturing finance'),
 ('Risk and investigations','An alert is the beginning of a question.','Examine the signal, its alternatives, and a proposed escalation.','TEAM-09','risk','retail finance'),
 ('Engineering','Who remembers why this thing works?','Recover intended behavior and follow the selected construction.','TEAM-10','engineering','software manufacturing')]

def team_page():
 route=LAB+'team-examples.html';intro=rendered(['TEAM-00'],route);intro=intro.split('<div class="table-region"',1)[0]
 filters='''<div class="directory-filters" data-enhancement><div><label for="department-filter">Department</label><select id="department-filter"><option value="all">All departments</option>'''+''.join(f'<option value="{g[4]}">{g[0]}</option>' for g in GUIDES)+'''</select></div><div><label for="industry-filter">Industry</label><select id="industry-filter"><option value="all">All industries</option><option value="software">Software / SaaS</option><option value="retail">Retail / commerce</option><option value="services">Professional services</option><option value="manufacturing">Manufacturing / logistics</option><option value="finance">Financial-services operations</option></select></div><button id="clear-filters" type="button">Clear filters</button></div><p data-directory-count role="status">10 guides</p>'''
 cards='<div class="cards guide-grid">'+''.join(f'<a class="destination-card guide-card" data-departments="{dep}" data-industries="{ind}" href="{rel(route,CANDIDATES[key])}"><span class="card-domain">{department}</span><h2>{title}</h2><p>{desc}</p><span class="card-action">Open guide <span aria-hidden="true">↗</span></span></a>' for department,title,desc,key,dep,ind in GUIDES)+'</div><p data-directory-empty hidden>No guides match these filters. Clear the filters to see all guides.</p>'
 body='<main id="main-content" class="directory-page section"><div class="prose">'+intro+'</div><section data-directory aria-label="Practical guide directory">'+filters+cards+'</section><section class="section prose">'+rendered(['TEAM-11'],route)+'</section></main>'
 write(route,shell(route,'Practical examples for your team',body))

def start_pages():
 for kind,key in [('a','ST-A'),('b','ST-B'),('c','ST-C')]:
  route=LAB+f'start-{kind}.html';body=rendered(['ST-01',key,'ST-02'],route)
  chooser='<nav class="entrance-chooser" aria-label="Compare documentation entrances">'+''.join(f'<a href="start-{k}.html"'+(' aria-current="page"' if k==kind else '')+f'>{label}</a>' for k,label in [('a','Problem first'),('b','Team / task first'),('c','Story first')])+'</nav>'
  chooser+='<p class="comparison-note">Local comparison · these are alternate entrances into the same guides and model.</p>'
  cards='<div class="cards">'+''.join(f'<a class="destination-card" href="{rel(route,CANDIDATES[k])}"><h2>{title}</h2><p>{desc}</p><span class="card-action">Open example ↗</span></a>' for title,desc,k in [('The campaign','A meaning, a comparison, and a proposed successor.','CMP'),('The reply','Sources, uncertainty, and accountable continuation.','REP'),('The handoff','A commitment with its conditions intact.','HAND')])+'</div>'
  if kind=='b':
   table=re.search(r'<div class="table-region"[^>]*><table.*?</table></div>',body,re.S)
   if table:
    task_cards=[]
    rows=re.findall(r'<tr[^>]*>(.*?)</tr>',table[0],re.S)
    for row in rows:
     cells=re.findall(r'<td[^>]*>(.*?)</td>',row,re.S)
     if len(cells)!=3:continue
     href=re.search(r'href="([^"]+)"',cells[2]);label=unescape(re.sub('<[^>]+>','',cells[2])).split('→')[0].strip()
     if href:task_cards.append('<a class="destination-card docs-path-card" href="'+href[1]+'"><h3>'+cells[0]+'</h3><p>'+cells[1]+'</p><span class="card-action">'+escape(label)+' ↗</span></a>')
    body=body[:table.start()]+'<div class="cards docs-card-grid">'+''.join(task_cards)+'</div>'+body[table.end():]
   cards=''
  # Keep the familiar breadcrumb and heading first; comparison is secondary context.
  boundary=body.find('<h2 ')
  if boundary>=0:body=body[:boundary]+chooser+body[boundary:]
  else:body+=chooser
  chooser='<nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">CyberAlchemy Lab</a><span>/</span><span>Getting started</span></nav>'
  paths='<section class="reading-paths"><h2 id="reading-paths">Keep a direct path</h2><div class="cards">'
  for name,label in [('understand-lab','Understand the Lab'),('investigate-incident','Investigate an incident'),('read-record','Read a record'),('prepare-definition','Prepare a definition'),('resume-agent-work','Resume agent work'),('explore-craft','Explore Craft')]:paths+=f'<a class="destination-card" href="path-{name}.html"><h3>{label}</h3><span>Open reading path ↗</span></a>'
  paths+='</div></section>'
  legacy='<span id="docs-search-input" class="legacy-anchor"></span><span id="start-here" class="legacy-anchor"></span><span id="start-browse" class="legacy-anchor"></span><span id="start-toc" class="legacy-anchor"></span>'
  alias_groups={'reading-paths':['reading-paths-title','choose-your-path','choose-your-path-title','direct-lookup','direct-lookup-title','organize-knowledge','definitions-first','three-questions','purpose-and-work','agent-continuity','craft-in-the-lab','agent-continuity-title','craft-in-the-lab-title','definitions-first-title','organize-knowledge-title','purpose-and-work-title','three-questions-title']}
  for target,ids in alias_groups.items():
   paths=paths.replace('<h2 id="'+target+'">',''.join('<span id="'+i+'" class="legacy-anchor"></span>' for i in ids)+'<h2 id="'+target+'">')
  main='<main id="main-content" class="section start-page">'+legacy+chooser+'<div class="prose">'+body+'</div>'+cards+paths+'</main>'
  write(route,shell(route,'Start here · '+kind.upper(),main))
 # The recommended working preview opens task-first. A/B/C remains visible and selectable.
 raw=(SITE/(LAB+'start-b.html')).read_text().replace('href="start-here.html" aria-current="location"','href="start-here.html" aria-current="page"');write(LAB+'start-here.html',raw)
 route=LAB+'preview-options.html'
 body='<main id="main-content" class="section prose"><h1>Choose your way into the Lab.</h1><p>This local preview implements the proposed design and copy. The same campaign, guides, and exact reference are available from each entrance.</p><div class="cards">'+''.join(f'<a class="destination-card" href="start-{k}.html"><h2>{label}</h2><p>{desc}</p><span>Explore this entrance ↗</span></a>' for k,label,desc in [('a','Start with a problem','Choose where the work comes apart.'),('b','Find your team’s work','Choose a familiar task or department.'),('c','Follow a story','Watch a comparison lead to a challenged meaning.')])+'</div><p><a href="index.html">Return to the homepage</a></p></main>'
 write(route,shell(route,'Compare documentation entrances',body))

def render_runtime_diagrams(raw,route):
 manifest_path=HERE/'assets/runtime-diagrams/manifest.json'
 if not manifest_path.exists():return raw
 entry=json.loads(manifest_path.read_text())['diagrams'].get(Path(route).name)
 if not entry:return raw
 titles={'runtime-cli.html':'API candidate read sequence','runtime-local-work.html':'Local work and independent approvals','runtime-sessions.html':'Context and session lifecycle','runtime-architecture.html':'Runtime ownership and interfaces','runtime-recovery.html':'Recovery and reconciliation'}
 def diagram(m):
  source=unescape(m[1]);assert hashlib.sha256(source.encode()).hexdigest()==entry['source_sha256']
  svg=(HERE/'assets/runtime-diagrams'/entry['asset']).read_text()
  asset=rel(route,'preview-assets/runtime-diagrams/'+entry['asset']);title=titles[Path(route).name]
  return '<!--preview-runtime-diagram:start--><div class="preview-rendered-diagram" data-diagram data-diagram-title="'+title+'">'+svg+'<div class="preview-diagram-actions"><button type="button" data-expand-diagram hidden>Expand diagram</button><a href="'+asset+'">Open full-size diagram ↗</a></div></div><!--preview-runtime-diagram:end--><details data-preview-diagram-source><summary>Read diagram source</summary><pre><code class="language-mermaid">'+m[1]+'</code></pre></details>'
 raw=re.sub(r'<pre><code class="language-mermaid">(.*?)</code></pre>',diagram,raw,flags=re.S)
 camera=rel(route,'preview-assets/diagram-canvas.js')
 return raw.replace('</body>',f'<script data-preview-polish src="{camera}" defer></script></body>',1)

def patch_retained():
 # Every untouched route keeps its full original content, assets, scripts and anchors.
 for p in SITE.rglob('*.html'):
  route=str(p.relative_to(SITE))
  if route in BUILT:continue
  raw=p.read_text();back=os.path.relpath(LAB+'team-examples.html',str(Path(route).parent)).replace(os.sep,'/')
  home=os.path.relpath(LAB+'index.html',str(Path(route).parent)).replace(os.sep,'/')
  options=os.path.relpath(LAB+'preview-options.html',str(Path(route).parent)).replace(os.sep,'/')
  banner=f'<div class="local-preview-ribbon" role="note">Local preview · <a href="{home}">Homepage</a> · <a href="{back}">Practical examples</a> · <a href="{options}">Compare docs entrances</a></div>'
  raw=raw.replace('</body>',banner+'</body>',1)
  if 'class="site-document' in raw or 'site-document"' in raw:
   raw=raw.replace('<html','<html data-local-preview="polished"',1)
   style=os.path.relpath('preview-assets/retained-polish.css',str(Path(route).parent)).replace(os.sep,'/')
   script=os.path.relpath('preview-assets/retained-polish.js',str(Path(route).parent)).replace(os.sep,'/')
   raw=raw.replace('</head>',f'<link data-preview-polish rel="stylesheet" href="{style}"></head>',1)
   raw=raw.replace('</body>',f'<script data-preview-polish src="{script}" defer></script></body>',1)
   raw=render_runtime_diagrams(raw,route)
  raw=raw.replace('</head>','<meta name="robots" content="noindex,nofollow"></head>',1)
  if route==LAB+'lab-reference-library.html' and 'id="catalog-history"' not in raw:
   history='<section id="catalog-history" class="local-preview-history" style="padding:24px"><h2>Versions and record facets</h2><p>Each exact record preserves its selected version, acceptance standing, sources, and exclusions. Open a record to inspect those facets against its captured definition and format.</p><p><a href="read-record.html">Read an exact record</a> · <a href="source-and-status.html">Inspect the selected source and status</a></p></section>'
   raw=raw.replace('</main>',history+'</main>',1)
  p.write_text(raw)

def index_search():
 entries=[]
 for p in SITE.rglob('*.html'):
  route=str(p.relative_to(SITE))
  if '/research/' in route or route in {'index.html'}:continue
  if re.search(r'<meta[^>]+http-equiv=["\']?refresh',p.read_text(),re.I):continue
  parsed=Extract();parsed.feed(p.read_text());title=' '.join(parsed.title).strip() or p.stem.replace('-',' ')
  group='Reference' if '/reference/' in route else 'Craft' if route.startswith('craft-') else 'Runtime' if '/runtime-' in route else 'Practical guides' if route in EXAMPLE_ROUTES or 'team-examples' in route else 'Introductions'
  entries.append({'title':title[:220],'href':route,'group':group,'text':' '.join(parsed.text)[:16000]})
 (SITE/'preview-search.json').write_text(json.dumps({'entries':entries},ensure_ascii=False))
 return len(entries)

def fingerprint_assets():
 # Snapshot overlays must invalidate even a still-fresh, older v= URL.
 hashes={}
 for page in SITE.rglob('*.html'):
  raw=page.read_text()
  def stamped(m):
   ref=unescape(m[2]);path,sep,query=ref.partition('?')
   if path.startswith(('http:','https:','//','data:')) or not path.endswith(('.css','.js')):return m[0]
   target=(page.parent/path).resolve()
   if not target.is_relative_to(SITE.resolve()) or not target.is_file():return m[0]
   if target not in hashes:hashes[target]=hashlib.sha256(target.read_bytes()).hexdigest()[:12]
   query=re.sub(r'(?:^|&)preview_asset=[0-9a-f]+','',query).strip('&')
   return m[1]+escape(path+'?'+(query+'&' if query else '')+'preview_asset='+hashes[target],quote=True)+m[3]
  raw=re.sub(r'(<(?:link|script)\b[^>]*?\b(?:href|src)=")([^"]+)(")',stamped,raw)
  page.write_text(raw)
 return len(hashes)

def main():
 assert SITE.is_relative_to(HERE) and DIST!=SITE
 if SITE.exists():shutil.rmtree(SITE)
 shutil.copytree(DIST,SITE)
 shutil.copytree(HERE/'live-assets',SITE,dirs_exist_ok=True)
 shutil.copytree(HERE/'assets',SITE/'preview-assets',dirs_exist_ok=True)
 for route,keys in ROUTES.items():article_page(route,keys)
 team_page();start_pages()
 home=(HERE/'templates/home.html').read_text()
 write(LAB+'index.html',shell(LAB+'index.html','CyberAlchemy Lab · An open company brain',home,True))
 (SITE/'index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=governance-lab-series/index.html"><title>CyberAlchemy Lab preview</title></head><body><a href="governance-lab-series/index.html">Open the local preview</a></body></html>')
 patch_retained();search=index_search()
 # HTML-generated preserved article content needs the original figure/map styles and scripts.
 for route in PRESERVED:
  p=SITE/route;raw=p.read_text();original=(DIST/route).read_text()
  # Only retained article-specific diagram/image styles; generic legacy chrome stays isolated.
  styles=[]
  for href in re.findall(r'<link[^>]+href="([^"]+\.css(?:\?[^\"]*)?)"',original):
   if any(x in href for x in ['diagram','system-map']):styles.append(f'<link rel="stylesheet" href="{href}">')
  if styles:raw=raw.replace('</head>',''.join(styles)+'</head>')
  for src in re.findall(r'<script[^>]+src="([^"]+)"',original):
   if any(part in src for part in ['diagram-reading.js','company-brain-map.js']) or (route==LAB+'governance-lab-reference.html' and any(part in src for part in ['system-map.js','system-map-canvas.js'])):
    raw=raw.replace('</body>',f'<script src="{src}" defer></script></body>')
  p.write_text(raw)
 # Apply shared card corrections to both recomposed and retained preview pages.
 for page in SITE.rglob('*.html'):
  card_style=os.path.relpath('preview-assets/card-polish.css',str(page.relative_to(SITE).parent)).replace(os.sep,'/')
  raw=page.read_text()
  figure_style=os.path.relpath('preview-assets/retained-figures.css',str(page.relative_to(SITE).parent)).replace(os.sep,'/')
  final_style=os.path.relpath('preview-assets/final-polish.css',str(page.relative_to(SITE).parent)).replace(os.sep,'/')
  raw=raw.replace('</head>',f'<link data-preview-polish rel="stylesheet" href="{card_style}"><link data-preview-polish rel="stylesheet" href="{figure_style}"><link data-preview-polish rel="stylesheet" href="{final_style}"></head>',1)
  page.write_text(raw)
 fingerprints=fingerprint_assets()
 report={'asset_fingerprints':fingerprints,'scope':'isolated local preview','canonical_source_effect':'none','new_or_recomposed_pages':sorted(BUILT),'preserved_detailed_articles':sorted(PRESERVED),'search_entries':search,'reference_pages':len(list((SITE/LAB/'reference').glob('*.html'))),'runtime_articles':len(list((SITE/LAB).glob('runtime-*.html')))}
 (HERE/'build.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
