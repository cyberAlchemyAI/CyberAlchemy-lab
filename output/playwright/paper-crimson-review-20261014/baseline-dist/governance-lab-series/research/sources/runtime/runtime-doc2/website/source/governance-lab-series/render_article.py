from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json
import hashlib
import re
import math
import xml.etree.ElementTree as ET
import build_system_map
from start_here import render as render_start_here
from learning_docs import render as render_learning_docs
from practical_docs import render as render_practical_docs
from research_pages import render as render_research_pages
from diagram_label_layout import arrange_labels
from source_labels import source_title
from governance_series import PARTS as GOVERNANCE_PARTS, bind_incident, export_completeness_definition, incident_context, incident_lens_summary, lens_definition_and_example
from governance_consolidation import guide_additions, redirects as governance_redirects
from lab_visual_language import CONCEPTS, model_styles, svg_glyph, bind_model_icons

ROOT=Path(__file__).resolve().parent
(ROOT/'assets/lab-model-visuals.css').write_text(model_styles())
CAT=json.loads((ROOT/'research/catalog.json').read_text())
PACK=json.loads((ROOT/'research/context-pack.json').read_text())
CASE=json.loads((ROOT/'research/incident-extraction-case.json').read_text())
READER=json.loads((ROOT/'research/library-reader-copy.json').read_text())
REF='governance-lab-reference.html'
CATREF='lab-reference-library.html'
DIAGRAMS={}
DESIGN=json.loads((ROOT/'research/kep-design-source.json').read_text())
# Standalone SVGs obtain their foundations mechanically from the same copied KEP file.
# Scope them to svg so embedded diagrams cannot reset article or console roles.
SVG_FOUNDATIONS='svg{'+re.search(r':root\s*\{([^}]+)\}',(ROOT/DESIGN['token_source']).read_text()).group(1)+'}'

def h(v): return escape(str(v),quote=True)
def slug(v): return re.sub(r'[^a-z0-9]+','-',v.lower()).strip('-')

def text(x,y,lines,cls='label',anchor='middle',gap=23):
    if isinstance(lines,str): lines=[lines]
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">'+''.join(f'<tspan x="{x}" dy="{0 if i==0 else gap}">{h(s)}{(" " if i<len(lines)-1 else "")}</tspan>' for i,s in enumerate(lines))+'</text>'

def box(x,y,w,title,sub=None,kind='normal',height=94,concept=None,glyph=None):
    body=f'<rect x="{x}" y="{y}" width="{w}" height="{height}" rx="4" class="node {kind}"/>'
    if concept:
        title_class='node-title model-svg-small-title' if w<220 else 'node-title'
        body+=svg_glyph(concept,x+16,y+17,glyph)+text(x+52,y+34,title,title_class,'start')
    else:
        body+=text(x+w/2,y+34,title,'node-title')
    title_lines=1 if isinstance(title,str) else len(title)
    if sub:body+=text(x+w/2,y+60+max(0,title_lines-1)*23,sub,'node-sub',gap=21)
    if concept:return f'<g class="model-svg-node" data-model-concept="{concept}">{body}</g>'
    return body

def arrow(uid,x1,y1,x2,y2,label=None,dashed=False):
    body=f'<path d="M{x1},{y1} L{x2},{y2}" class="connector {"dashed" if dashed else ""}" marker-end="url(#{uid}-arrow)"/>'
    if label:body+=f'<text class="edge-label" data-connection-label="true">{h(label)}</text>'
    return '<g class="diagram-connection">'+body+'</g>'

def routed(uid,path,label=None,dashed=False):
    body=f'<path d="{path}" class="connector {"dashed" if dashed else ""}" marker-end="url(#{uid}-arrow)"/>'
    if label:body+=f'<text class="edge-label" data-connection-label="true">{h(label)}</text>'
    return '<g class="diagram-connection">'+body+'</g>'

def svg(uid,title,desc,body,height,width=1000):
    body=arrange_labels(body,width,height,font_size=16)
    style=SVG_FOUNDATIONS+'text{font-family:var(--ds-font-ui);fill:var(--ds-ink)}.node{fill:var(--ds-surface);stroke:var(--ds-border);stroke-width:1.4}.teal{fill:var(--ds-subtle);stroke:var(--ds-accent)}.blue{fill:var(--ds-canvas);stroke:var(--ds-focus)}.ochre{fill:var(--ds-subtle);stroke:var(--ds-warning)}.boundary{fill:none;stroke:var(--ds-control-border);stroke-width:1.4}.teal-boundary{fill:var(--ds-subtle);stroke:var(--ds-accent)}.blue-boundary{fill:var(--ds-subtle);stroke:var(--ds-focus)}.ochre-boundary{fill:var(--ds-subtle);stroke:var(--ds-warning)}.session-boundary{fill:var(--ds-canvas);stroke:var(--ds-control-border);stroke-dasharray:7 5}.connector{fill:none;stroke:var(--ds-muted);stroke-width:1.65}.dashed{stroke-dasharray:5 4}.node-title{font-size:20px;font-weight:600}.node-sub{font-size:16px;fill:var(--ds-muted)}.small-label{font-size:15px;font-weight:600;fill:var(--ds-muted)}.edge-label{font-size:16px;fill:var(--ds-muted)}@media(forced-colors:active){svg{--ds-ink:CanvasText;--ds-muted:CanvasText;--ds-canvas:Canvas;--ds-surface:Canvas;--ds-subtle:Canvas;--ds-border:ButtonBorder;--ds-control-border:ButtonBorder;--ds-accent:LinkText;--ds-focus:Highlight;--ds-warning:CanvasText}}'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="{uid}-title {uid}-desc"><title id="{uid}-title">{h(title)}</title><desc id="{uid}-desc">{h(desc)}</desc><style>{style}{model_styles("svg")}</style><defs><marker id="{uid}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--ds-muted)"/></marker></defs>{body}</svg>'

def figure(uid,title,desc,body,height,caption,chapter,kind='conceptual',relations=None,definitions=None,width=1000,html_body=None):
    s=svg(uid,title,desc,body,height,width)
    (ROOT/'assets'/f'{uid}.svg').write_text(s)
    DIAGRAMS[uid]={'title':title,'kind':kind,'chapter_obligation':chapter,'definitions':definitions or [],
                   'declared_relation_examples':relations or [],'caption':caption,'asset':f'assets/{uid}.svg',
                   'evidence':PACK['chapters'][chapter-1]['sources'],
                   'display_renderer':'responsive-html-flow' if html_body else 'inline-svg'}
    if html_body:
        content=html_body
    else:
        root=ET.fromstring('<g>'+body+'</g>')
        labels=[' '.join(e.itertext()) for e in root.iter('text') if e.get('class') in ['node-title','node-sub','small-label']]
        readable_nodes=''.join('<li>'+h(label)+'</li>' for label in labels)
        content=f'<div class="diagram-shell" role="region" tabindex="0" aria-label="{h(title)}. Use arrow keys to scroll horizontally.">{s}</div><details class="diagram-alternative"><summary>Read this diagram as text</summary><p>{h(desc)}</p><ul>{readable_nodes}</ul></details>'
    return f'<figure class="diagram{(" learning-figure" if html_body else "")}" id="figure-{uid}">{content}<figcaption><span class="figure-number">Figure {len(DIAGRAMS):02}</span> {h(caption)}</figcaption></figure>'

# Three independent tracks: semantic, representation and domain facts.
u='meaning-shape-record'
b=text(80,38,'Three records, three questions','small-label','start')
b+=box(45,70,280,'Definition',['What does Work mean?','A bounded unit of effort.'],'teal',125)
b+=box(360,70,280,'Artifact type',['What must a Work record contain?','Declared fields and constraints.'],'ochre',125)
b+=box(675,70,280,'One Work record',['Which investigation is this?','Investigate Northstar’s omission.'],'blue',125,concept='work')
b+=arrow(u,326,130,358,130)+arrow(u,641,130,673,130)
b+=text(185,233,'Meaning','small-label')+text(500,233,'Required format','small-label')+text(815,233,'This investigation','small-label')
F_TYPES=figure(u,'Meaning, required format and the investigation record','The definition explains what Work means. The artifact type sets the required record format. The particular Work record describes the Northstar omission investigation. The arrows explain these roles; they do not create new permitted connections.',b,270,'The definition explains Work; the type governs its record format; the instance identifies this investigation. Format conformance and owner acceptance retain their own requirements.',5,definitions=['Definition','Artifact Type','Schema','Artifact','Work'])

# Purpose, product and project are separate rows.
u='purpose-to-implementation'
b=box(45,25,300,'Intent',['Let customers obtain','their complete eligible data.'],'ochre',106,concept='intent')
b+=box(395,25,560,'Intent Resolution',['Choose a response and how to assess success.'],'normal',106,concept='intent',glyph='target')
b+=arrow(u,347,78,392,78)
b+=routed(u,'M675,133 L675,184 L140,184 L140,237')
b+=text(45,218,'PRODUCT · value offered over time','small-label','start')
for x,title,sub,concept,glyph in [(45,'Product',['Customer platform'],'product','briefcase'),(285,'Capability',['Reliable data export'],'product','target'),(525,'Binding record',['Links specific versions'],'product','link'),(765,'Implementation',['Export service revision'],'work','wrench')]:b+=box(x,239,190,title,sub,'normal',91,concept=concept,glyph=glyph)
for x in [237,477,717]:b+=arrow(u,x,284,x+46,284)
b+=text(45,388,'PROJECT · a particular effort','small-label','start')
b+=box(45,409,260,'Project',['Northstar export repair'],'normal',91,concept='project')
b+=box(370,409,260,'Goal',['Required identifiers present'],'normal',91,concept='project',glyph='target')
b+=box(695,409,260,'Work',['Investigate the omission'],'ochre',91,concept='work')
b+=arrow(u,307,454,367,454)+arrow(u,632,454,692,454)
b+=routed(u,'M825,408 L825,351 L860,351 L860,332','build and assess',dashed=True)
purpose_html=bind_incident(ROOT,(ROOT/'templates/incident-work-map.html.in').read_text())
F_PURPOSE=figure(u,'From the reported problem to the agent’s investigation job','Intent states the desired change. Intent Resolution selects a response and satisfaction test. The value column identifies the Product, Product Capability, version-specific realization binding and Implementation. The work column identifies the repair Project, Goal, investigation Work and Agent Assignment. The Incident keeps its response and closure responsibilities.',b,540,'The map pairs each general role with an illustrative record in the same incident. Reading order and grouping explain their roles; exact connections, permissions and state changes follow their own contracts.',4,definitions=['Intent','Intent Resolution','Product','Product Capability','Capability Realization Binding','Implementation','Project','Goal','Work','Agent Assignment','Incident'],html_body=purpose_html)

# A literal subset of the declared relation kind signatures, plus derived projection.
u='records-and-ontology'
b=text(48,32,'SOURCE RECORDS · particular records and permitted connections','small-label','start')
for x,title,sub in [(45,'Source · S1',['Required identifiers']),(395,'Observation v1',['Operational Observation']),(745,'Source · E12',['Saved export output'])]:b+=box(x,58,210,title,sub,'normal',94)
b+=arrow(u,392,105,258,105,'originates-from')+arrow(u,607,105,742,105,'originates-from')
b+=routed(u,'M500,154 L500,255','represent these records and connections',dashed=True)
b+='<g class="ontology-projection"><rect x="26" y="267" width="948" height="184" rx="4" class="boundary teal-boundary"/>'
b+=text(48,297,'ONTOLOGY VIEW · a graph of these selected records','small-label','start')
for x,title,sub in [(45,'Node',['Represents Source S1']),(395,'Node',['Represents the observation']),(745,'Node',['Represents Source E12'])]:b+=box(x,321,210,title,sub,'teal',90)
b+=arrow(u,392,366,258,366,'originates-from')+arrow(u,607,366,742,366,'originates-from')+'</g>'
F_ONTOLOGY=figure(u,'The incident source trail and its ontology view','Operational Observation version 1 originates from the Source records identifying snapshot S1 and output E12. The origin roles are required input and observed output. The lower graph represents the exact same subjects and connections; it does not replace them or change their standing.',b,480,'“Originates-from” is permitted from an Operational Observation to a Source. The two declared origin roles distinguish required input and observed output; exact versions and source bindings remain necessary.',5,'declared-signature illustration',relations=CASE['declared_signature_examples'][:2],definitions=['Operational Observation','Source','Typed Relation','Relation Kind','Ontology Node','Ontology Edge','Ontology View'])

# State lives outside the ephemeral machine session.
u='agent-session'
b='<g class="model-svg-project" data-model-concept="project"><rect x="36" y="30" width="928" height="131" rx="4" class="boundary blue-boundary"/>'
b+=svg_glyph('project',64,49,'archive')
b+=text(500,66,'PROJECT STATE · saved outside the agent','node-title')
b+=text(500,99,'Northstar observation · candidate revision 8 · decisions · evidence','node-sub')
b+=text(500,126,'Separate histories of changes and their acceptance','node-sub')+'</g>'
b+=box(110,211,340,'Context View 3',['Snapshot S1 · output E12 · rules','Usable at start; later expired'],'teal',109)
b+=box(550,211,340,'Ontology View',['Investigation records and source trail','from a consistent ontology cut'],'teal',109)
b+=arrow(u,280,162,280,209)+arrow(u,720,162,720,209)
b+=routed(u,'M280,322 L280,346 L500,346 L500,377')+routed(u,'M720,322 L720,346 L500,346',dashed=True)
b+='<g class="model-svg-session" data-model-concept="agent"><rect x="84" y="380" width="832" height="213" rx="4" class="boundary session-boundary"/>'
b+=svg_glyph('agent',112,398)
b+=text(500,417,'MACHINE AGENT SESSION 12 · temporary','small-label')
b+=box(114,440,235,'Agent instance',['Investigation assignment','Separate delegation'],'normal',110,concept='agent')
b+=box(383,440,235,['Actions','and tools'],['Compare identifiers','Record result and limits'],'normal',130,concept='agent',glyph='wrench')
b+='<g class="session-notes">'+box(652,440,235,['Session','Memory'],['Working notes only','Cleared on termination'],'ochre',130,concept='agent',glyph='memory')+'</g></g>'
b+=text(500,627,'Useful output → authorized recording → project records with their own standing','edge-label')
F_AGENT=figure(u,'The Northstar agent session and its durable project records','Project State retains the investigation observation, candidate revision 8, decisions and evidence. Context View 3 and an Ontology View select exact information for session 12. The temporary session binds one agent instance, its assignment, delegation, actions and working memory. View 3 later expires, requiring a checked replacement and current permission before continuing.',b,660,'The instance and working memory end with the session. The recorded investigation survives with its own standing, and later sessions obtain new checked views.',6,definitions=['Project State','Context View','Ontology View','Agent Instance','Agent Assignment','Agent Profile','Agent Capability','Principal','Agent Session','Session Memory','Delegation','Agent Action'])

# Learning reads forward through three stages, with actual use assessed separately.
u='learning-loop'
b=text(30,35,'01 · RECORD WHAT HAPPENED','small-label','start')
for x,title,sub in [(30,'Work',['Investigate incident']),(270,'Work observation',['Required rows missing']),(510,'Reflection',['Inspect adjacent batches'])]:b+=box(x,60,180,title,sub,'normal',100)
b+=arrow(u,212,110,268,110)+arrow(u,452,110,508,110)
b+=text(30,212,'02 · PROPOSE A LESSON','small-label','start')
b+=box(30,238,660,'Proposed lesson · compare adjacent batches',None,'teal',178)
b+=text(52,306,['Evidence: recorded failed run and row comparison.','Applies when data can change between batch requests.','Excludes fixed-data exports with a different integrity contract.','Predicted benefit: detect missing rows before delivery.','Contradicted if a checked export still delivers missing rows.'],'node-sub','start',22)
b+=text(30,466,'03 · EXAMINE LATER USE','small-label','start')
b+=box(30,490,290,'Lesson application',['Name the lesson version.','Record use or deliberate non-use.'],'normal',122)
b+=box(400,490,290,'Outcome assessment',['Compare the prediction with','the observed result and evidence.'],'blue',122)
b+=arrow(u,322,551,398,551)
b+=text(360,658,'Changing rules or code requires its own authorization.','edge-label')
learning_html='''<div class="learning-flow" role="group" aria-label="From an incident investigation to a proposed lesson and its later assessment">
<section class="learning-phase" aria-labelledby="learning-record-title">
<header class="learning-phase-heading"><h3 id="learning-record-title"><span class="learning-phase-number">01</span> Record what happened</h3><span class="learning-time">First episode</span></header>
<ol class="learning-sequence learning-incident">
<li class="learning-card learning-work" data-model-concept="work"><p class="learning-kind">{{WORK_ICON}}<span>Work</span></p><h4>Investigate the reported omission</h4><p>Inspect Northstar’s saved export and source snapshot.</p></li>
<li class="learning-card learning-observation"><p class="learning-kind">Operational Observation</p><h4>Required rows are missing</h4><p>Save the output and comparison evidence.</p></li>
<li class="learning-card learning-reflection" data-model-concept="agent"><p class="learning-kind">{{AGENT_REFLECTION_ICON}}<span>Reflection</span></p><h4>Inspect adjacent batches</h4><p>Record this interpretation for investigation.</p></li>
</ol></section>
<section class="learning-phase" aria-labelledby="learning-proposal-title">
<header class="learning-phase-heading"><h3 id="learning-proposal-title"><span class="learning-phase-number">02</span> Propose a lesson</h3></header>
<div class="learning-card learning-proposal"><p class="learning-kind">Operational Lesson · proposed</p><h4>Compare adjacent batches</h4>
<dl class="learning-criteria"><div><dt>Evidence</dt><dd>Recorded failed run and row comparison.</dd></div><div><dt>Applies when</dt><dd>The dataset can change between successive batch requests.</dd></div><div><dt>Exclusions</dt><dd>Fixed-data exports with a different integrity contract, and failures unrelated to batch retrieval.</dd></div><div><dt>Predicted benefit</dt><dd>Detect missing rows before delivery.</dd></div><div class="learning-falsifier"><dt>What would contradict it</dt><dd>A later export passes this check but still delivers data with required rows missing.</dd></div></dl>
</div></section>
<section class="learning-phase" aria-labelledby="learning-later-title">
<header class="learning-phase-heading"><h3 id="learning-later-title"><span class="learning-phase-number">03</span> Examine later use</h3><span class="learning-time">Later episode</span></header>
<ol class="learning-sequence learning-later">
<li class="learning-card learning-application"><p class="learning-kind">Lesson Application</p><h4>Record what was used</h4><p>Name the lesson version used in this run, or record why it was deliberately not used.</p></li>
<li class="learning-card learning-assessment"><p class="learning-kind">Lesson Outcome Assessment</p><h4>Compare prediction with result</h4><p>Did the check detect missing rows before delivery? Record the evidence and its limits.</p></li>
</ol><p class="learning-outcome">The result may support or contradict the prediction, or leave it uncertain under these conditions.</p></section>
</div>'''
F_LEARNING=figure(u,'Experience, later lesson use and assessment','Read three stages in order: record the incident investigation through an Operational Observation, propose advice for future work where data can change between batches, then record its use or deliberate non-use and assess the predicted benefit. That advice does not establish the cause or remedy of the fixed-snapshot Northstar incident. The SVG label Work observation refers to the Operational Observation record kind.',b,690,'Saving a lesson, showing it to an agent, using it and demonstrating benefit are separate facts. Changes to policies, profiles or code require their own authorization.',7,definitions=['Operational Observation','Agent Reflection','Operational Lesson','Lesson Application','Lesson Outcome Assessment','Operational Learning Cycle'],width=720,html_body=bind_model_icons(learning_html))

# One approval bundle can apply multiple independent effects atomically.
u='admission-and-histories'
b=box(40,40,240,'Specific proposal',['Records, versions and','requested changes'],'normal',111)
b+=box(380,40,240,'Decision bundle',['Independent decisions,','one review checkpoint'],'ochre',111)
b+=box(720,40,240,'Admission transaction',['Accepted record changes','applied together'],'teal',111)
b+=arrow(u,282,96,377,96,'review')+arrow(u,622,96,717,96,'authorize')
b+=routed(u,'M840,153 L840,198 L500,198 L500,222')
b+=box(280,225,440,'Updated Project State',['The saved result of the accepted changes'],'blue',95,concept='project',glyph='archive')
b+=routed(u,'M392,322 L392,350 L265,350 L265,377')
b+=routed(u,'M607,322 L607,350 L735,350 L735,377')
b+=box(40,380,450,'Change history',['What changed?','The preceding state and resulting state.'],'normal',111)
b+=box(510,380,450,'Approval history',['Why was it accepted?','Decision, authorization and applicable rules.'],'normal',111)
b+=text(500,535,'Both histories refer to the same specific change event.','edge-label')
F_ADMISSION=figure(u,'Review, acceptance and two separate histories','A specific proposal goes to a Decision Bundle for review. An authorized Admission Transaction applies the accepted record changes together and saves the updated Project State. One history records what changed; the other records why it was accepted. Both identify the same change event.',b,570,'The Lab calls these the Project Semantic Event History and Project Governance Event History. Sharing a review does not extend any decision’s permission; the transaction may apply only authorized effects.',3,definitions=['Decision','Decision Bundle','Admission Transaction','Project State','Project Semantic Event History','Project Governance Event History'])

# Evidence scope and causal explanation are separate.
u='evidence-chain'
b=text(40,31,'Northstar incident · inspect the basis of the omission claim.','small-label','start')
for x,title,sub in [(40,'Sources',['S1 + output E12','Northstar · active']),(285,'Comparison',['Required identifiers','minus output identifiers']),(530,'Evidence Set',['200 required','identifiers missing']),(775,'Assessment',['Omission confirmed','Cause unresolved'])]:b+=box(x,65,185,title,sub,'blue' if x==775 else 'normal',117)
for x in [227,472,717]:b+=arrow(u,x,121,x+56,121)
b+='<rect x="41" y="213" width="918" height="58" rx="4" class="boundary ochre-boundary"/>'
b+=text(500,250,'Showing missing rows does not yet establish why they are missing.','edge-label')
F_EVIDENCE=figure(u,'From saved inputs and output to a bounded incident assessment','Definition 1.0.0 requires every identifier selected for Northstar with status = active in snapshot S1. The illustrative saved output E12 contains 9,800 rows. Method 2 compares the actual identifier sets and finds 200 required identifiers missing. An Evidence Set supports the Failure Assessment; a Finding, if recorded, derives from that Evidence Set. Neither establishes the cause or recovery.',b,302,'The count alone is insufficient: preserve the selected identifiers, exact snapshot and output, account, filters, method and recording session. The Evidence Set supports a bounded assessment of the omission.',2,definitions=['Source','Measurement Method','Measurement Result','Operational Observation','Evidence','Evidence Set','Failure Assessment','Finding','Provenance'])

FIGURES={'FIGURE_TYPES':F_TYPES,'FIGURE_PURPOSE':F_PURPOSE,'FIGURE_ONTOLOGY':F_ONTOLOGY,'FIGURE_AGENT':F_AGENT,'FIGURE_LEARNING':F_LEARNING,'FIGURE_ADMISSION':F_ADMISSION,'FIGURE_EVIDENCE':F_EVIDENCE}

def source_details(chapters,terms):
    seen=[]
    for n in chapters:
        for p in PACK['chapters'][n-1]['sources']:
            if p not in seen:seen.append(p)
    defs=[d for t in terms for d in CAT['definitions'] if d['term']==t]
    def display_term(d):
        scope=READER['scope_labels_by_identity'].get(d['identity'])
        return d['term']+(' · '+scope if scope else '')
    dlinks=' · '.join(f'<a href="{CATREF}#def-{slug(d["identity"])}">{h(display_term(d))}</a>' for d in defs)
    citations=''.join(f'<li><a href="{h(p)}">{h(source_title(p))}</a></li>' for p in seen)
    return '<details class="source-notes"><summary>Definitions and sources</summary><p>'+dlinks+'</p><ul>'+citations+'</ul></details>'

SOURCES={
 'SOURCES_GOVERNANCE':source_details([1,2,3,6],list(dict.fromkeys(['Definition','Premise','Axiom','Invariant','Authority','Authority Claim','Authority Boundary','Governance-Axis Independence Invariant','Policy','Constitution','Provenance','Evidence','Operational Observation','Semantic Epoch','Context View','Incident','Failure Occurrence','Agent Assignment','Delegation'] + GOVERNANCE_PARTS[0]['terms'] + ['Agent Profile','Tool']))),
 'SOURCES_AUTHORITY':source_details([1],GOVERNANCE_PARTS[0]['terms']),
 'SOURCES_AUTHORITY_AGENT':source_details([6],['Agent Assignment','Delegation','Authority Claim','Agent Profile','Tool']),
 'SOURCES_PROVENANCE':source_details([2],GOVERNANCE_PARTS[1]['terms']),
 'SOURCES_LIFECYCLE':source_details([3],GOVERNANCE_PARTS[2]['terms']),
 'SOURCES_LIFECYCLE_AGENT':source_details([6],['Agent Instance','Agent Session','Session Memory','Project State','Context View','Ontology View']),
 'SOURCES_EVIDENCE':source_details([2],list(dict.fromkeys(['Source','Provenance','Measurement Method','Measurement Result','Evidence','Evidence Set','Finding','Operational Observation','Observation','Research Run','Failure Occurrence','Failure Assessment'] + GOVERNANCE_PARTS[1]['terms']))),
 'SOURCES_CHANGE':source_details([3,6],list(dict.fromkeys(['Decision Bundle','Admission Transaction','Semantic Epoch','Representation Revision','Derived Refresh','Challenge Contract','Challenge Event','Incident','Failure Assessment','Governance-Axis Independence Invariant'] + GOVERNANCE_PARTS[2]['terms'] + ['Agent Instance','Agent Session','Session Memory','Project State','Context View','Ontology View']))),
 'SOURCES_PURPOSE':source_details([4],['Product','Product Thesis','Product Capability','Capability Realization Binding','Project','Goal','Work','Coordination Context','Bounded Context','Ledger']),
 'SOURCES_RECORDS':source_details([5],['Definition','Artifact Type','Schema','Typed Relation','Typed Connection Extension Rule','Ontology Node','Ontology Edge']),
 'SOURCES_AGENT':source_details([6],['Actor','Principal','Role','Agent Profile','Agent Instance','Delegation','Agent Session','Session Memory','Tool']),
 'SOURCES_LEARNING':source_details([7],['Research Inquiry','Experiment Design','Experiment Run','Failure Mode','Failure Occurrence','Failure Assessment','Incident','Classification','Operational Learning Cycle']),
 'SOURCES_TODAY':source_details([8],['Implementation','Conformance','Review','Validation','Drift Assessment','Stable Repository'])}

LENS_VISUALS={
 'authority':{'dom_id':'lens-authority-visual','title':'What an accepted definition looks like',
              'representation':'Shared Definition structure with governing formal voice, explanatory voices, scope, boundaries and a separate illustrative owner acceptance',
              'terms':['Definition','Authority','Authority Claim','Authority Boundary']},
 'provenance':{'dom_id':'lens-provenance-visual','title':'Follow a claim back to what produced it',
               'representation':'Shared provenance definition and a concrete account/filter/snapshot trace, comparison method and bounded claim',
               'terms':['Provenance','Evidence','Measurement Method','Operational Observation']},
 'lifecycle':{'dom_id':'lens-lifecycle-visual','title':'Different things can be in different states',
              'representation':'Four independent state tracks with current and possible next states, required conditions and recorded effects; expandable Definition acceptance history',
              'terms':['Definition','Incident','Semantic Epoch','Implementation','Context View','Governance-Axis Independence Invariant']}}
for key,visual in LENS_VISUALS.items():
    visual['source_definition_bindings']=[{k:d[k] for k in ['term','ref','source','sha256']}
                                       for d in CAT['definitions'] if d['term'] in visual['terms']]
    visual['renderer']='responsive-html-cards'
    visual['page_path']=REF+'#'+{'authority':'governance','provenance':'evidence','lifecycle':'change'}[key]
    visual['dom_id']={'authority':'opening-export-definition-title','provenance':'opening-provenance-example-title','lifecycle':'opening-lifecycle-example-title'}[key]
    visual['evidence_boundary']='Illustrative records, acceptance and run; no actual admission, evidence result or connection instance is created.'

# Confirm the conceptual example uses declared relation signatures; no actual relation instance is created.
by_pred={r['predicate']:r for r in CAT['relations']}
for f in DIAGRAMS.values():
    for p in f['declared_relation_examples']:
        assert {'source_kind':p['source_kind'],'target_kind':p['target_kind']} in by_pred[p['predicate']]['allowed_endpoint_pairs']
for p in CASE['declared_signature_examples']:
    contract=by_pred[p['predicate']]
    assert {'source_kind':p['source_kind'],'target_kind':p['target_kind']} in contract['allowed_endpoint_pairs']
    assert set(contract['required_qualifier_axes']).issubset(p['qualifiers'])

template=bind_incident(ROOT,(ROOT/'templates/article.html.in').read_text())
base_style=re.search(r'<style>.*?</style>',template,re.S).group(0)
template=template.replace('{{SYSTEM_MAP}}',(ROOT/'system-map.fragment.html').read_text())
for key,value in guide_additions(ROOT).items():
    template=template.replace('{{'+key+'}}',bind_incident(ROOT,value))
template=template.replace('{{EXPORT_COMPLETENESS_DEFINITION}}',export_completeness_definition(ROOT,'opening-export-definition'))
template=template.replace('{{INCIDENT_CASE}}',incident_context(ROOT,'opening-incident-case'))
template=template.replace('{{INCIDENT_LENS_SUMMARY}}',incident_lens_summary(ROOT,'opening-incident-lenses'))
for key, filename in {'INCIDENT_WORK_BRIEF':'incident-work-brief',
                      'INCIDENT_SESSION_TIMELINE':'incident-session-timeline',
                      'INCIDENT_SUMMARY_LOOP':'incident-summary-loop'}.items():
    template=template.replace('{{'+key+'}}',bind_incident(ROOT,(ROOT/f'templates/{filename}.html.in').read_text()))
for lens in ['authority','provenance','lifecycle']:
    for key,value in lens_definition_and_example(ROOT,lens,'opening-'+lens).items():
        template=template.replace('{{'+key+'}}',value)
for key,value in {**FIGURES,**SOURCES}.items():template=template.replace('{{'+key+'}}',value)
figure_numbers=iter(range(1,len(DIAGRAMS)+1))
template=re.sub(r'(<span class="figure-number">)Figure \d+',lambda m:m.group(1)+f'Figure {next(figure_numbers):02}',template)

class ReadingWords(HTMLParser):
    def __init__(self):super().__init__();self.omit=0;self.words=0
    def handle_starttag(self,tag,attrs):
        if tag in ['svg','style','script','details']:self.omit+=1
    def handle_endtag(self,tag):
        if tag in ['svg','style','script','details']:self.omit-=1
    def handle_data(self,data):
        if self.omit==0:self.words+=len(re.findall(r'\b[\w’\'-]+\b',data))

counter=ReadingWords();counter.feed('<article id="lab-article"'+template.split('<article id="lab-article"',1)[1].split('</article>',1)[0]+'</article>')
template=template.replace('{{READING_TIME}}',str(math.ceil(counter.words/220)))
library=(ROOT/'reference-library.fragment.html').read_text()
def compose(include_library):
    result=template.replace('{{REFERENCE_LIBRARY}}',library if include_library else '')
    result=result.replace('{{REFERENCE_CSS}}','<link rel="stylesheet" href="assets/reference-library.css">' if include_library else '')
    result=result.replace('{{LIBRARY_SCRIPT}}','<script src="assets/reference-library.js" defer></script>' if include_library else '')
    result=result.replace('{{LOCAL_REFERENCE_ALIAS}}','' if include_library else '<span id="reference" class="anchor-point" aria-hidden="true"></span>')
    assert '{{' not in result,'Unresolved article construction placeholder'
    return result

reference_page=(ROOT/'templates/reference-library.html.in').read_text().replace('{{LIBRARY}}',library)

variants={'governance-lab-series.html':compose(False),REF:compose(False),CATREF:reference_page}
governance_pages,governance_redirect_metadata=governance_redirects(ROOT,variants[REF])
variants.update(governance_pages)
start_page,start_metadata=render_start_here(ROOT,CAT)
variants['start-here.html']=start_page
learning_pages,learning_metadata=render_learning_docs(ROOT,CAT)
variants.update(learning_pages)
variants.update(render_practical_docs(ROOT))
variants.update(render_research_pages(ROOT))
(ROOT/'research/learning-paths-model.json').write_text(json.dumps(learning_metadata,indent=2)+'\n')

class Inspect(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.ids=[];self.hrefs=[];self.images=[];self.resources=[];self.svgs=0;self.lens_icons=0;self.model_icons=0;self.text=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a':self.hrefs.append(a.get('href',''))
        if tag=='link':
            if a.get('rel')=='canonical':self.hrefs.append(a['href'])
            else:self.resources.append(a['href'])
        if tag=='script' and a.get('src'):self.resources.append(a['src'])
        if tag=='img':self.images.append(a['src']);assert a.get('alt') or (a.get('alt')=='' and a.get('aria-hidden')=='true'),'Image lacks an accessible description'
        if tag=='svg':self.svgs+=1;assert a.get('aria-hidden')=='true' or (a.get('role') in ('img','group') and a.get('aria-labelledby'))
        if tag=='svg' and 'data-lens-icon' in a:self.lens_icons+=1
        if tag=='svg' and 'data-model-icon' in a:self.model_icons+=1
    def handle_data(self,data):self.text.append(data)

inspections={}
for name,content in variants.items():
    inspection=Inspect();inspection.feed(content);inspections[name]=inspection
    assert len(inspection.ids)==len(set(inspection.ids)),('Duplicate article identifiers',name)
    if name in ('governance-lab-series.html',REF):
        assert inspection.lens_icons==6
        assert inspection.svgs==sum(f['display_renderer']=='inline-svg' for f in DIAGRAMS.values())+build_system_map.SVG_ELEMENT_COUNT+inspection.lens_icons+inspection.model_icons
for name,inspection in inspections.items():
    for href in inspection.hrefs:
        if href.startswith('#'):assert href[1:] in inspection.ids,(name,href)
        elif not urlsplit(href).scheme and not urlsplit(href).netloc:
            path,_,fragment=href.partition('#');assert path in variants or (ROOT/path).is_file(),path
            if path in inspections and fragment:assert fragment in inspections[path].ids,(name,href)
    for path in inspection.images+inspection.resources:assert (ROOT/path).is_file(),path
def write_document(path, content):
    # Keep the previous page intact until its full replacement is ready. Small
    # writes also avoid oversized write requests on the attachment filesystem.
    import os
    import tempfile
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.'+path.name+'.', suffix='.tmp', delete=False) as target:
            temporary = target.name
            data = content.encode('utf-8')
            for offset in range(0, len(data), 65536):
                target.write(data[offset:offset+65536])
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)

for name,content in variants.items():write_document(ROOT/name, content)
i=inspections['governance-lab-series.html']
output=ROOT/'governance-lab-series.html'
model={
 'schema_version':'visual-article-explanation/v1','status':'pass within document-construction scope','authority_effect':'none','mode':'mixed: artifact, architecture, process',
 'target_boundary':'Previously researched governance and integrated Lab model; exact 2026-10-08 source snapshot.',
 'opening_frame':{'starting_statement':'CyberAlchemy is a system for organizing knowledge and work.',
                  'progression':['familiar implicit meanings','explicit definitions and boundaries','distinct premises, axioms and invariants','owner-accepted authority over meaning','knowledge and work governed through three questions'],
                  'claim_scope':'Accepted definitions are described as a basic unit of authority over meaning within an exact owner scope. Other governing records retain their own roles and authority.',
                  'concrete_example':{'shared_template':'templates/export-completeness-definition.html.in',
                                      'term':'Complete customer-data export','version':'1.0.0',
                                      'formal_expression':'Complete(E, S, A, F) ⇔ RequiredIds(S, A, F) ⊆ ExportedIds(E)',
                                      'notation':{'E':'Saved export output','S':'Identified fixed source snapshot','A':'Declared customer account','F':'Declared row-selection filters',
                                                  'RequiredIds(S, A, F)':'Identifiers of rows in snapshot S belonging to account A and satisfying filters F',
                                                  'ExportedIds(E)':'Identifiers of rows present in saved output E'},
                                      'criterion':'Every required row identifier from the declared account, filters and fixed source snapshot is present in the saved output.',
                                      'scope':'Required identifier coverage only; duplicate/extra rows, value accuracy, actor permission and incident closure retain separate criteria.',
                                      'standing':'Illustrative reader-facing Definition structure and acceptance; no actual admission or registered example.'},
                  'source_definition_bindings':[{k:d[k] for k in ['term','ref','source','sha256']} for d in CAT['definitions'] if d['term'] in ['Definition','Authority','Premise','Axiom','Invariant']]},
 'user_intent':'A visual graph explanation of the integrated Lab, grounded in one agent investigating the illustrative Northstar export incident; authority, provenance and lifecycle connect through exact scope, record versions, evidence and separate state tracks.',
 'lanes':{'surface':'article header and export example','properties':'three lenses and seven independent facets',
          'components':'definitions, types, instances, product/project/work, agents and records',
          'internal_dependencies':'six conceptual graph views and seven source-mapped article diagrams','external_dependencies':'owner routes, tools, sources and primary literature in companion reference',
          'flow':'construction, evidence, admission and learning maps','lifecycle':'independent tracks, session termination and current-state panel',
          'risk_questions':'preserved current-state limits and deeper reference questions','visual_composition':'selectable local SVG concept neighborhoods, a guided example and the existing article figures'},
 'layer_interaction':['isolate one of six system views','trace a selected concept neighborhood','follow the incident investigation','compare governance lenses','illustrate session termination'],
 'incident_reading_structure':{
     'definition_layout':'Illustrated definition cards with visible native meaning and formulas; symbol explanations and full Lab fields remain available through one native disclosure per card. Field rows retain horizontal rules and open sides.',
     'definition_to_use':'Shared explicit transitions connect the definition with its incident application.',
     'templates':['templates/definition-application-bridge.html.in','templates/incident-work-map.html.in','templates/incident-work-brief.html.in','templates/incident-session-timeline.html.in','templates/incident-summary-loop.html.in'],
     'continuity':['intent and owner resolution','product outcome and exact realization association','repair project, goal and investigation work','record format and observation source graph','ephemeral assigned agent with current views and delegation','evidence, hypothesis, bounded lesson and future assessment','owner-authorized changes, saved project state and new session'],
     'source_definition_bindings':[{k:d[k] for k in ['term','ref','source','sha256']} for d in CAT['definitions'] if d['term'] in ['Intent','Intent Resolution','Product','Project','Goal','Work','Product Capability','Capability Realization Binding','Agent Assignment','Agent Session','Context View','Ontology View','Project State','Incident']],
     'standing':'Editorial representations of the existing fictional incident and selected definitions; no instances, relations, admission or runtime effects are created.'},
 'renderer':'L0: local semantic HTML/CSS/SVG; optional inline JavaScript for explanatory controls',
 'visual_library':'Installed x-ray library files are unavailable. Local node, boundary, arrow and feedback-loop compositions are declared explicitly here; no external renderer dependency.',
 'evidence_boundary':'All business values and instances are illustrative. Explicit relation signature examples are checked against the captured admitted catalog. Other arrows show conceptual or process order and create no new relation or authority.',
 'governance_lenses':LENS_VISUALS,
 'incident_example':{'input':'research/incident-extraction-case.json','sha256':hashlib.sha256((ROOT/'research/incident-extraction-case.json').read_bytes()).hexdigest(),
                     'standing':CASE['standing'],'case':CASE,'connection_rule_scope':'Only declared signature and qualifier illustrations; no Typed Relation instance is created.'},
 'definition_card_illustrations':{'manifest':'research/definition-card-images.json','assets':['assets/definition-completeness-v1.png','assets/definition-provenance-v1.png','assets/definition-lifecycle-v1.png'],'tool':'built-in image_gen.imagegen','scope':'Definition cards only; original scientific meanings, formulas and field values retained as native text.','interaction':'Core meaning and formulas remain visible; symbols and complete Lab fields share one native disclosure per card.','standing':'Editorial illustrations, not operational evidence or an admission.'},
 'governance_definition_presentations':{
     'provenance':{'template':'templates/provenance-definition.html.in','example_template':'templates/provenance-example.html.in',
                   'formal_expression':'Prov(x) = [(sourceᵢ, relationᵢ, operationᵢ, ownerᵢ, postureᵢ)]*',
                   'source_definition_bindings':[{k:d[k] for k in ['term','ref','source','sha256']} for d in CAT['definitions'] if d['term']=='Provenance'],
                   'standing':'Reader-facing presentation of the selected Provenance meaning; business records are illustrative.'},
     'lifecycle':{'template':'templates/lifecycle-definition.html.in','example_template':'templates/lifecycle-example.html.in',
                  'structure_expression':'Lifecycle(C) = (States(C), Initial(C), T(C), Gates(C), Effects(C))',
                  'formal_expression':'Permitted(x, C, s, t) ⇔ Applies(C, x) ∧ State_C(x) = s ∧ (s, t) ∈ T(C) ∧ GatesMet(C, x, s, t)',
                  'source_contract_binding':{'source':'research/sources/authority/foundation/v1/schema.json','selector':'/$defs/lifecycleProfile and /$defs/transition',
                                             'sha256':hashlib.sha256((ROOT/'research/sources/authority/foundation/v1/schema.json').read_bytes()).hexdigest()},
                  'source_definition_bindings':[{k:d[k] for k in ['term','ref','source','sha256']} for d in CAT['definitions'] if d['term'] in ['Definition','Governance-Axis Independence Invariant']],
                  'standing':'Explanatory definition based on lifecycle contracts, not a separately admitted Lifecycle definition. Sequence is illustrative.'},
     'reading_order':'Shared incident frame → definition in Lab format → exact incident example → continued explanation and cross-lens connection',
     'authority_effect':'none'},
 'governance_chapters':{'entry':REF+'#governance','chapters':[{ 'key':key,'destination':REF+'#'+route} for key,route in {'authority':'governance','provenance':'evidence','lifecycle':'change'}.items()],'legacy_redirects':governance_redirect_metadata,'progression':'Authority → provenance → lifecycle → the complete Lab model','navigation':'One canonical guide chapter per question; legacy articles redirect to the corresponding chapter or section.'},
 'system_map':{'model':'research/system-map-model.json','views':len(build_system_map.VIEWS),'graph_diagrams':len(build_system_map.VIEWS)+len(build_system_map.GOVERNANCE['focus_views'])-1,'governance_focus_views':len(build_system_map.GOVERNANCE['focus_views']),'governance_overview':{'concepts':6,'connections':5},'concept_groups':len(build_system_map.NODES),'source_posture':'captured definition bindings plus editorial role connections'},'diagrams':DIAGRAMS,'illustration':{'asset':'assets/project-workbench.png','delivery':'research/image-delivery.json','display_asset':'assets/project-workbench-1280.webp','prompt':'assets/illustration-prompt.txt','tool':'built-in image_gen.imagegen','role':'conceptual editorial illustration, no implementation or architecture evidence'},
 'design':{'source_record':'research/kep-design-source.json','layout_reference':'research/article-layout-reference.json','token_source':DESIGN['token_source'],'adapters':['assets/lab-editorial.css','assets/lab-landing.css','assets/lab-article.css','assets/system-map.css','assets/lab-ux.css','assets/governance-series.css','assets/lab-incident-model.css'],'brand_assets':[a['local_path'] for a in DESIGN['assets'] if a['local_path'].endswith(('.svg','.webp'))]},
 'scope_limits':PACK['limits']}
model['design'].update({
    'layout_reference': 'research/docs-design-reference.json',
    'adapters': model['design']['adapters'] + ['assets/lab-editorial-records.css', 'assets/lab-docs.css', 'assets/lab-library-docs.css', 'assets/lab-craft-docs.css', 'assets/site-search.css'],
    'navigation': {'script': 'assets/lab-docs.js', 'library_script': 'assets/lab-library-docs.js', 'craft_script': 'assets/lab-craft-docs.js', 'search_script': 'assets/site-search.js', 'search_index': 'research/site-search-index.json', 'mode': 'One visible topic with shared offline search, grouped navigation and a heading index across guide, reference catalogs, eight expanded essays and Craft; the full documents remain readable without scripts.'}
})
model['craft_documentation'] = {
    'entry': '../craft-documentation-proposal/craft-model.html',
    'review': 'research/craft-lab-consistency-review.json',
    'operation_resolution_record': 'research/operation-capacity-resolution.json',
    'calculation_verification_record': 'research/calculation-support-verification.json',
    'calculation_full_suite_record': 'research/calculation-full-suite-verification.json',
    'authority_effect': 'none',
    'guide_sections': ['craft-in-the-lab', 'craft-and-lab-records', 'craft-integration-scope'],
    'integration_posture': 'Explained use of Craft tools in governed Lab work; no runtime connector or automatic Project State write established.',
    'operation_resolution': 'Owner approved retaining Operation as state-changing, correcting the classifier as Calculation, and adding a typed Calculation successor contract. The original fixture remains historical evidence.'
}
(ROOT/'research/visual-article-model.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n')
(ROOT/'research/start-here-model.json').write_text(json.dumps(start_metadata,ensure_ascii=False,indent=2)+'\n')
receipt={'schema_version':'visual-article-render-inspection/v1','authority_effect':'none','svg_figures':len(DIAGRAMS),'inline_svg_figures':sum(f['display_renderer']=='inline-svg' for f in DIAGRAMS.values()),'responsive_html_figures':sum(f['display_renderer']=='responsive-html-flow' for f in DIAGRAMS.values()),'system_map_svg_views':len(build_system_map.VIEWS),'system_map_graph_diagrams':len(build_system_map.VIEWS)+len(build_system_map.GOVERNANCE['focus_views'])-1,'governance_focus_views':len(build_system_map.GOVERNANCE['focus_views']),'svg_total':i.svgs,'editorial_images':4,'definition_card_illustrations':3,'brand_images':len(i.images)-4,
         'responsive_html_lens_visuals':len(LENS_VISUALS),
         'governance_redirects':[{'path':p['legacy_page'],'destination':p['destination'],'mapped_sections':len(p['section_map'])} for p in governance_redirect_metadata],
         'reading_words':counter.words,'reading_minutes':math.ceil(counter.words/220),'article_outputs':[{ 'path':name,'bytes':(ROOT/name).stat().st_size,'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),'includes_library':name==CATREF} for name in variants],
         'local_links':'all paths and local fragment targets resolve','relation_examples':'declared ordered signatures match captured catalog',
         'scope':'Static document construction inspection; no browser interaction checks or implementation tests.',
         'html_bytes':output.stat().st_size,'html_sha256':hashlib.sha256(output.read_bytes()).hexdigest()}
(ROOT/'research/article-render-inspection.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'output':str(output),**receipt},ensure_ascii=False))

from build_site_search import build as build_site_search
import os
search_receipt=build_site_search() if os.environ.get('LAB_SITE_SKIP_SEARCH_INDEX')!='1' else None
if search_receipt:model['design']['navigation']['search_entries']=search_receipt['entries']
model['design']['navigation']['search_delivery']='Shared local script across the research entrance, product article, guide, library, learning paths and Craft, including the guide alias.'
(ROOT/'research/visual-article-model.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n')
