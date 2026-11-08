from pathlib import Path
from html import escape
from html.parser import HTMLParser
import json
import math
import re
import hashlib
from source_labels import source_title, admission_title, display_text, display_value
from reference_reading import ReaderAids

ROOT = Path(__file__).resolve().parent
C = json.loads((ROOT/'research/catalog.json').read_text())
M = json.loads((ROOT/'research/context-pack.json').read_text())
E = json.loads((ROOT/'research/editorial-review.json').read_text())
LEARNING_MAP = json.loads((ROOT/'research/learning-map.json').read_text())
READER = json.loads((ROOT/'research/library-reader-copy.json').read_text())
assert READER['basis_catalog_sha256'] == hashlib.sha256((ROOT/'research/catalog.json').read_bytes()).hexdigest(), 'Reader explanations need review against the selected catalog'
assert set(READER['by_term']) == {d['term'] for d in C['definitions']}, 'Missing reviewed reader explanation'

def h(value):
    return escape(str(value), quote=True)

def slug(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')

def link(label, url):
    attrs = ' target="_blank" rel="noopener noreferrer"' if url.startswith('https://') else ''
    return f'<a href="{h(url)}"{attrs}>{h(display_text(label))}</a>'

pattern = re.compile(r'\[([^\]]+)\]\((https://[^\s)]+)\)')
def inline(text):
    out, start = [], 0
    for match in pattern.finditer(text):
        out.extend([h(text[start:match.start()]), link(match.group(1), match.group(2))])
        start = match.end()
    out.append(h(text[start:]))
    return ''.join(out)

def readable(value):
    return h(json.dumps(display_value(value), ensure_ascii=False, indent=2))

definitions_by_term = {}
definitions_by_ref = {}
for d in C['definitions']:
    definitions_by_term.setdefault(d['term'], []).append(d)
    definitions_by_ref[d['ref']] = d
types_by_ref = {t['artifact_type_ref']: t for t in C['artifact_types']}

def definition_title(d):
    scope = READER['scope_labels_by_identity'].get(d['identity'])
    return d['term'] + (' · ' + scope if scope else '')

def definition_link(d):
    return link(definition_title(d), '#def-' + slug(d['identity']))

def type_title(t):
    name = t['semantic_kind'].replace('-', ' ').capitalize()
    version = t['artifact_type_ref'].rsplit('/', 1)[-1]
    return name + ' · ' + version

def type_link(ref):
    return link(type_title(types_by_ref[ref]), '#type-' + slug(ref)) if ref in types_by_ref else h(ref)

READING = ReaderAids(C, type_link)

def acceptance_label(value):
    return {'admitted':'Accepted', 'admitted-current':'Accepted · selected current',
            'admitted-historical':'Accepted · earlier selection',
            'candidate-unadmitted':'Proposed · not accepted'}.get(value, value)

def status_text(value):
    return h(acceptance_label(value)) + ' <code>(' + h(value) + ')</code>'

TERMS = [
    ['Authority', 'Authority Surface', 'Authority Claim', 'Authority Boundary', 'Governance-Axis Independence Invariant', 'Policy', 'Constitution'],
    ['Provenance', 'Source', 'Observation', 'Operational Observation', 'Measurement Method', 'Measurement Result', 'Evidence', 'Evidence Set', 'Finding'],
    ['Semantic Epoch', 'Representation Revision', 'Derived Refresh', 'Decision', 'Decision Bundle', 'Admission Transaction', 'Project Semantic Event History', 'Project Governance Event History', 'Challenge Contract', 'Challenge Event'],
    ['Intent', 'Intent Resolution', 'Product', 'Product Thesis', 'Product Capability', 'Capability Realization Binding', 'Capability Instance', 'Project', 'Goal', 'Work', 'Craft Method', 'Implementation', 'Coordination Context', 'Bounded Context', 'Context Map', 'Context Request', 'Context View', 'Ledger'],
    ['Definition', 'Artifact Type', 'Schema', 'Artifact Type Resolution', 'Typed Relation', 'Relation Kind', 'Typed Coupling Invariant', 'Typed Connection Extension Rule', 'Root-Axis Independence Invariant', 'Ontology', 'Ontology Node', 'Ontology Edge', 'Ontology Cut', 'Ontology View', 'Model Instance Binding'],
    ['Actor', 'Principal', 'Role', 'Agent', 'Agent Profile', 'Agent Capability', 'Agent Instance', 'Agent Assignment', 'Delegation', 'Agent Session', 'Session Memory', 'Agent Action', 'Tool', 'Project State'],
    ['Research Inquiry', 'Research Run', 'Hypothesis', 'Experiment Design', 'Experiment Run', 'Operational Learning Cycle', 'Agent Reflection', 'Operational Lesson', 'Lesson Application', 'Lesson Outcome Assessment', 'Work Outcome Assessment', 'Failure Mode', 'Failure Occurrence', 'Failure Assessment', 'Incident', 'Failure Control Binding', 'Classification'],
    ['Stable Repository', 'Implementation', 'Conformance', 'Effect', 'Validation', 'Review', 'Residue', 'Drift Assessment'],
]
DESCRIPTIONS = [
    'How accepted meanings, record requirements and permissions guide what happens.',
    'How to trace a claim to its sources and decide what the evidence supports.',
    'How reviewed changes enter saved project records and their histories.',
    'How needs, products, projects, methods and implementation fit together.',
    'How meanings, record formats and permitted connections form a coherent model.',
    'How a temporary agent gets its assignment, permissions and project knowledge.',
    'How to learn from work and test whether a lesson helps in a later attempt.',
    'What the inspected sources establish, what is proposed and what remains unfinished.',
]
articles = []
for i, p in enumerate(sorted(ROOT.glob('0*.txt')), 1):
    paragraphs = p.read_text().strip().split('\n\n')
    articles.append({'id':f'essay-{i}', 'number':i, 'title':paragraphs[0], 'paragraphs':paragraphs[1:],
                     'description':DESCRIPTIONS[i-1], 'minutes':math.ceil(len(p.read_text().split())/230), 'file':p.name})

def cards(group):
    return ''.join(f'<a class="chapter-card" href="#{a["id"]}"><span class="chapter-number">{a["number"]:02}</span>'
                   f'<span class="chapter-card-title">{h(a["title"])}</span><span class="chapter-description">{h(a["description"])}</span>'
                   f'<span class="chapter-time">{a["minutes"]} minute read <span aria-hidden="true">↗</span></span></a>' for a in group)

lens_navigation=[]
lens_panels=[]
for index,lens in enumerate(LEARNING_MAP['lenses']):
    key=lens['id']
    selected='true' if index==0 else 'false'
    lens_navigation.append(f'<button class="map-lens" type="button" role="tab" id="lens-tab-{key}" aria-controls="lens-{key}" aria-selected="{selected}" tabindex="{0 if index==0 else -1}" data-lens="{key}"><span class="lens-index">{index+1:02}</span><span><strong>{h(lens["label"])}</strong><small>{h(lens["question"])}</small></span><span class="lens-arrow" aria-hidden="true">↗</span></button>')
    points=''.join('<li>'+h(p)+'</li>' for p in lens['points'])
    reading=''.join('<li>'+link(articles[n-1]['title'],'#essay-'+str(n))+'</li>' for n in lens['chapters'])
    terms=[d for term in lens['terms'] for d in definitions_by_term.get(term,[])]
    record_links=' · '.join(definition_link(d) for d in terms)
    lens_panels.append(f'<section class="map-panel" id="lens-{key}" role="tabpanel" aria-labelledby="lens-tab-{key}" tabindex="0" data-lens-panel="{key}"><div class="panel-label">{h(lens["label"])}</div><h3>{h(lens["title"])}</h3><p class="panel-summary">{h(lens["summary"])}</p><ul class="panel-points">{points}</ul><blockquote class="panel-example"><span>For example</span><p>{h(lens["example"])}</p></blockquote><a class="ds-button" href="governance-lab-series.html#{h(lens["guide"])}">Read the visual explanation <span aria-hidden="true">↗</span></a><div class="panel-reading"><span>Expanded articles</span><ul>{reading}</ul></div><div class="panel-records"><span>Inspect the definitions</span><p>{record_links}</p></div></section>')
landing=(ROOT/'landing-template.html').read_text().replace('{{LENS_NAV}}',''.join(lens_navigation)).replace('{{LENS_PANELS}}',''.join(lens_panels))

nav = ''
for a in articles:
    if a['number'] in [1,4]:
        nav += f'<p class="part-label">{"I · Governance" if a["number"]==1 else "II · The Lab model"}</p>'
    nav += f'<a href="#{a["id"]}" data-essay="{a["id"]}"><span class="nav-number">{a["number"]:02}</span><span>{h(a["title"])}</span></a>'

sections = []
READING_STEPS = {1:'scope', 2:'evidence', 3:'proposal', 4:'scope', 5:'evidence', 6:'handoff', 7:'handoff', 8:'proposal'}
COMPARISON_STEPS = {1:'meaning-and-record', 2:'observation-evidence-assessment', 3:'assignment-and-permission', 4:'purpose-and-effort', 5:'ontology-and-craft', 6:'state-and-views', 7:'observation-evidence-assessment', 8:'ontology-and-craft'}
for a in articles:
    i = a['number']-1
    body = '\n'.join('<p>'+inline(p)+'</p>' for p in a['paragraphs'])
    exact_terms = [d for t in TERMS[i] for d in definitions_by_term.get(t,[])]
    term_links = ' · '.join(definition_link(d) for d in exact_terms)
    source_links = ''.join('<li>'+link(source_title(s), s)+'</li>'
                           for p,s in zip(M['chapters'][i]['paths'],M['chapters'][i]['sources']))
    onward = (f'<a class="next-essay" href="#essay-{i+2}"><span>Continue to essay {i+2:02}</span><strong>{h(articles[i+1]["title"])} →</strong></a>'
              if i+1<len(articles) else '<a class="next-essay" href="#reference"><span>Inspect the model</span><strong>Open the reference catalog →</strong></a>')
    part = 'Part I · Governance' if i<3 else 'Part II · The Lab model'
    sections.append(f'<article id="{a["id"]}" data-source-name="{h(a["file"])}" aria-labelledby="{a["id"]}-title"><header class="article-heading">'
                    f'<div class="eyebrow">{part} <span aria-hidden="true">/</span> Essay {i+1:02} · {a["minutes"]} minute read</div>'
                    f'<h2 id="{a["id"]}-title">{h(a["title"])}</h2></header>'
                    f'<nav class="essay-reading-path" aria-label="Related learning paths"><a href="incident-walkthrough.html#{READING_STEPS[i+1]}">See this in the incident</a> · <a href="concept-comparisons.html#{COMPARISON_STEPS[i+1]}">Compare the relevant concepts</a></nav><div class="prose">{body}</div>'
                    f'<details class="essay-sources"><summary>Definitions and sources</summary>'
                    f'<p>{term_links}</p><ul>{source_links}</ul><p class="small">These links identify the definitions and sources used by this essay. A source’s older draft label does not override the acceptance recorded for its exact version.</p></details>{onward}</article>')

def item(item_id, title, badge, body, search):
    standing, separator, version = badge.partition(' · ')
    if separator and re.match(r'^\d+\.\d+', version):
        label=f'<span class="catalog-standing">Acceptance: {h(acceptance_label(standing))}</span><span class="catalog-version">Version: {h(version)}</span>'
    else:
        label=h(acceptance_label(badge))
    return f'<details class="catalog-item" id="{h(item_id)}" data-title="{h(title.lower())}" data-search="{h(search.lower())}"><summary><span class="catalog-title">{h(title)}</span><span class="badge">{label}</span></summary><div class="record-body">{body}</div></details>'

definition_rows = []
for d in sorted(C['definitions'],key=lambda x:(x['term'].lower(),x['identity'])):
    plain = d['plain_explanation']
    if not isinstance(plain,str): plain=json.dumps(plain,ensure_ascii=False)
    normative = ''.join('<p>'+h(display_text(p))+'</p>' for p in d['normative_statement'].split('\n\n'))
    boundaries = '<ul>'+''.join('<li>'+h(display_text(x))+'</li>' for x in d['boundary_conditions'])+'</ul>' if d['boundary_conditions'] else ''
    guide = READER['by_term'][d['term']]
    body = f'<p class="reader-intro">{h(guide)}</p>'
    body += READING.definition(d)
    if d['identity'] in READER['scope_labels_by_identity']:
        body += '<p class="small">This name is used in both Lab and Craft workflow scopes. This entry has its own identity and source; matching names do not merge the definitions.</p>'
    body += f'<details class="inner"><summary>Formal definition, source explanation and boundaries</summary><p class="small">The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.</p><h4>Source explanatory wording</h4><p>{h(display_text(plain))}</p><h4>Exact governing statement</h4><div class="normative">{normative}</div>'
    if d['formal_expression']: body+=f'<pre>{h(display_text(d["formal_expression"]))}</pre>'
    body += boundaries+'</details>'
    body += f'<dl><dt>Acceptance status</dt><dd>{status_text(d["effective_status"])}</dd><dt>Acceptance record</dt><dd>{h(admission_title(d["decision_ref"]))}</dd><dt>Original definition</dt><dd>{link("Read the original record",d["source"])}</dd></dl>'
    body += f'<details class="inner"><summary>Exact identity, version and content fingerprint</summary><dl><dt>Exact reference</dt><dd class="record-id">{h(d["ref"])}</dd><dt>Content fingerprint · SHA-256</dt><dd class="digest">{h(d["sha256"])}</dd></dl><p class="small">The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.</p></details>'
    if d['scope']: body+=f'<details class="inner"><summary>Where this definition applies—and its exclusions</summary><p class="small">Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.</p><pre>{readable(d["scope"])}</pre></details>'
    definition_rows.append(item('def-'+slug(d['identity']), definition_title(d), 'admitted · '+d['version'], body,
                                 guide+' '+definition_title(d)+' '+json.dumps(d,ensure_ascii=False)))

contract_rows = []
for t in C['artifact_types']:
    refs=' · '.join(definition_link(definitions_by_ref[r]) if r in definitions_by_ref else h(r) for r in t['semantic_definition_refs'])
    required=', '.join(t['schema_top_level_required']) or 'No required fields are declared directly at this level. Other schema sections or referenced rules may still require them.'
    body=f'<p>This contract specifies requirements for records of kind <code>{h(t["semantic_kind"])}</code>. Its linked definitions explain their meaning; its schema specifies structure and constraints.</p>'
    body+=f'<p><strong>Acceptance status:</strong> {status_text(t["lifecycle_state"])}.</p><p><strong>Definitions this format uses:</strong> {refs}</p>'
    body+=READING.record_type(t)
    body+=f'<details class="inner"><summary>Required fields and schema rules</summary><p><strong>Fields required at the selected level:</strong> {h(required)}</p><p class="small">Field names below are exact machine keys. Follow the full schema for nested fields, alternatives and referenced rules; this list is not a complete validation procedure.</p><p class="small">{h(display_text(t["schema_note"]))}</p></details>'
    body+=f'<details class="inner"><summary>Exact type reference and how a record identifies its type</summary><p class="record-id">{h(t["artifact_type_ref"])}</p><p class="small">A discriminator is a field and value identifying a record’s type. This is the declared rule; a filename is not type evidence.</p><pre>{readable(t["instance_discriminator"])}</pre></details>'
    body+=f'<dl><dt>Acceptance record</dt><dd>{h(admission_title(t["admission_decision_ref"]))}</dd>'
    body+=f'<dt>Contract</dt><dd>{link("Read the type contract", t["source"])}</dd><dt>Schema</dt><dd>{link("Read the schema", t["schema_source"])}'
    if t['schema_selector']:body+=' · selected section <code>'+h(t['schema_selector'])+'</code><span class="small"> (this contract uses that part of a shared schema)</span>'
    body+=f'</dd></dl><details class="inner"><summary>Schema content fingerprint and descriptor status</summary><dl><dt>Schema fingerprint · SHA-256</dt><dd class="digest">{h(t["schema_sha256"])}</dd></dl>'
    if t['descriptor_effective_states']:body+=f'<p class="small">Descriptor status codes: {h(", ".join(t["descriptor_effective_states"]))}. A descriptor is a registry record describing a type; its inventory is separate from contract bindings.</p>'
    body+='</details>'
    contract_rows.append(item('type-'+slug(t['artifact_type_ref']),type_title(t),t['lifecycle_state'],body,type_title(t)+' '+json.dumps(t,ensure_ascii=False)))

relation_rows=[]
for r in C['relations']:
    pairs=''.join(f'<tr><td>{h(p["source_kind"])}</td><td>{h(p["target_kind"])}</td></tr>' for p in r['allowed_endpoint_pairs'])
    body=f'<p class="small">The question this connection answers</p><p class="question">{h(r["unique_question"])}</p><p><strong>Acceptance status:</strong> {status_text(r["lifecycle_state"])}.</p><p><strong>Read in this direction:</strong> source → <strong>{h(r["predicate"])}</strong> → target. Each table row declares an allowed source-kind and target-kind combination; an actual connection must also meet the rule’s requirements.</p>'
    body+=f'<p><strong>Required extra details · qualifiers:</strong> {h(", ".join(r["required_qualifier_axes"]) or "None declared")}</p><p class="small">Qualifiers identify details such as version, scope, role, period or evidence. Use the exact allowed pair and its requirements; separate lists of sources and targets do not permit every combination.</p>'
    body+=f'<p><strong>Conclusions this link does not justify:</strong> {h(", ".join(r["forbidden_inferences"]))}</p>'
    body+=READING.relation(r)
    body+=f'<div class="table-scroll"><table><caption>{len(r["allowed_endpoint_pairs"])} allowed source–target kind pairs · direction matters</caption><thead><tr><th>Source kind</th><th>Target kind</th></tr></thead><tbody>{pairs}</tbody></table></div>'
    body+=f'<details class="inner"><summary>Exact meaning axis, effect and qualifier contract</summary><p class="record-id">{h(r["relation_kind_ref"])}</p><p><strong>Meaning axis:</strong> <code>{h(r["axis_id"])}</code> — the distinct semantic question this rule owns.</p><p>{h(r["operational_effect"])}</p><p class="small">The contract below declares the allowed qualifier fields and constraints. “Closed” means undeclared fields are not silently allowed.</p><pre>{readable(r["qualifier_contract"])}</pre></details>'
    body+=f'<dl><dt>Acceptance record</dt><dd>{h(admission_title(r["admission_decision_ref"]))}</dd><dt>Original contract</dt><dd>{link("Read the relation contract",r["source"])}</dd></dl><details class="inner"><summary>Contract content fingerprint</summary><p class="digest">{h(r["instance_sha256"])}</p><p class="small">SHA-256 identifies the captured contents, not truth or permission.</p></details>'
    relation_rows.append(item('rel-'+slug(r['relation_kind_id']),r['predicate'],f'{len(r["allowed_endpoint_pairs"])} allowed pairs',body,json.dumps(r,ensure_ascii=False)))

endpoint_rows=[]
for e in sorted(C['endpoints'],key=lambda x:x['endpoint_kind']):
    relation_links=lambda rs:' · '.join(link(r.removeprefix('relation.'),'#rel-'+slug(r)) for r in rs) or 'None declared'
    body=f'<p>An endpoint is the thing at either end of a connection. This entry identifies a permitted kind and the record-type contract that represents it.</p><p><strong>Record format · carrier:</strong> {type_link(e["carrier_ref"])}</p><p><strong>Connection rules where it may be the source:</strong> {relation_links(e["source_for"])}</p><p><strong>Connection rules where it may be the target:</strong> {relation_links(e["target_for"])}</p>'
    body+=f'<p class="small">These lists show where to look. Open the connection rule to find its allowed opposite endpoint and required versions and qualifiers. Being listed here does not allow every possible connection.</p><p><strong>Acceptance record:</strong> {h(admission_title(e["admission_ref"]))}</p>'
    body+=READING.endpoint(e)
    endpoint_rows.append(item('endpoint-'+slug(e['endpoint_kind']),e['endpoint_kind'].replace('-', ' ').capitalize(),e['lifecycle_state'],body,json.dumps(e,ensure_ascii=False)))

panels=''
for name,title,intro,rows in [
    ('definitions','Definitions','A definition states what a term means and where that meaning applies. Open an entry for a short introduction, then its exact governing statement.',definition_rows),
    ('types','Record formats · artifact-type contracts','An artifact is a recorded item, such as a work assignment or observation. Its type contract states the requirements for that kind of item; its schema supplies machine-readable structural rules.',contract_rows),
    ('relations','Connection rules · relation kinds','A relation kind defines one meaning of a connection and the permitted source–target kind pairs. A specific connection must also meet the rule’s version, scope and other requirements.',relation_rows),
    ('endpoints','Endpoint kinds','An endpoint is the thing at either end of a connection. These entries link each permitted kind to its record format and connection rules.',endpoint_rows)]:
    panels+=f'<section class="catalog-panel" id="catalog-{name}" data-panel="{name}" aria-labelledby="catalog-{name}-title"><h3 id="catalog-{name}-title">{title}</h3><p class="atlas-intro">{h(intro)}</p><p class="result-count" aria-live="polite">{len(rows)} records</p>'+''.join(rows)+'</section>'

historical_defs=''.join(f'<tr><td>{h(d["term"])}</td><td>{h(d["definition_id"]+"@"+d["version"])}</td><td>{h(admission_title(d["admission_decision_ref"]))}</td></tr>' for d in C['historical_definition_versions'])
historical_types=''.join(f'<tr><td>{h(d["artifact_type_ref"])}</td><td>{status_text(d["lifecycle_state"])}</td><td>{h(admission_title(d["admission_decision_ref"]))}</td></tr>' for d in C['historical_artifact_contracts'])
inventory=readable(C['artifact_registry_inventory'])
literature=''.join('<li>'+link(s['title'],s['url'])+'<p>'+h(READER['literature_notes_by_title'][s['title']])+'</p></li>' for s in M['literature'])
findings=''.join('<details class="finding"><summary>'+h(f['subject'])+' <span>'+h(f['status'])+'</span></summary><p>'+h(f['finding'])+'</p><p>'+h(f['treatment'])+'</p></details>' for f in E['remaining_model_questions'])

flow_titles=[('Need and chosen response','Record the purpose and select how to address it'),('Product, project and work','Identify the intended value, project scope and assigned work'),('Prepare the agent session','Select current project information and applicable permissions'),('Perform the work','Record actions, implementation and results within the assignment'),('Assess the evidence','Examine what happened and what the results support'),('Review and decide','Approve specific changes and their permitted consequences'),('Accept the changes together','Record the authorized consequences in one admission transaction'),('Save state and histories','Preserve project knowledge and separate change and approval histories'),('Prepare the next session','Build new task information from the accepted saved state')]
flow=''.join(f'<li><span>{i:02}</span><strong>{h(title)}</strong><p>{h(desc)}</p></li>' for i,(title,desc) in enumerate(flow_titles,1))
facet_rows=''.join(f'<tr><th>{h(a)}</th><td>{h(b)}</td></tr>' for a,b in [
    ('Kind','What kind of thing is this?'),('Status','What state does its declared lifecycle assign to it?'),('Evidence confidence','How strongly does the evidence support this claim within its stated limits?'),('Commitment confidence','How strongly does the responsible owner intend to proceed?'),('Provenance','Which sources and transformations produced it?'),('Owner','Who or which owner role is responsible, and within what scope?'),('Residue','What required matter remains unresolved or has not been preserved?')])

reader_guide='''<section class="overview" id="library-reading-guide" aria-labelledby="library-reading-guide-title">
<div class="eyebrow">Start here</div><h3 id="library-reading-guide-title">How to use this library</h3>
<p class="overview-intro">CyberAlchemy Lab organizes project work through explicit meanings, record requirements, evidence and decisions. The expanded essays explain the model. The catalog lets you inspect the definitions and contracts behind it.</p>
<p>New to the model? <a href="incident-walkthrough.html">Follow an incident</a> to see what the agent reads and records at each step. <a href="concept-comparisons.html">Compare the concepts</a> when similar terms are hard to distinguish.</p>
<p>For a first reading, start with <a href="#essay-1">Authority begins with meaning</a>, then <a href="#essay-4">What the Lab organizes</a> and <a href="#essay-6">An agent’s working session</a>. For the implementation status in this source snapshot, read <a href="#essay-8">What is operational today</a>.</p>
<div class="table-scroll"><table><caption>Choose the reference that answers your question</caption><thead><tr><th>Your question</th><th>Where to look</th></tr></thead><tbody>
<tr><td>What does this term mean?</td><td><a href="#catalog-definitions">Definitions</a>: introduction, exact governing statement and limits.</td></tr>
<tr><td>What must a record contain?</td><td><a href="#catalog-types">Record formats</a>: the type contract, its meaning definitions and schema.</td></tr>
<tr><td>Can these two kinds of records be connected?</td><td><a href="#catalog-relations">Connection rules</a>: the exact allowed source–target pair and required details. <a href="#catalog-endpoints">Endpoint kinds</a> help locate the relevant rules.</td></tr>
</tbody></table></div>
<details class="inner"><summary>Acceptance, versions and the date of this catalog</summary>
<p><strong>Accepted</strong> means a recorded decision has admitted that exact definition or contract for its stated scope. <strong>Selected current</strong> means the inspected registry uses it in its current selection. Neither status establishes deployment, activation or successful use.</p>
<p>An identity distinguishes one definition or contract from another. A version identifies a particular revision. Matching display names do not make two records identical. Three definition names appear in both Lab and Craft workflow scopes; their labels identify which entry you are reading.</p>
<p>An accepted record can retain an older version name containing “candidate.” Its recorded acceptance determines its standing. Earlier accepted versions remain in the historical lists even when the current selection uses another version.</p>
<p>A type contract can be accepted while an instance using it is still proposed. A <code>status</code> field in the schema describes the record form it validates; it is not the type registry’s acceptance decision. Each instance retains its own standing.</p>
<p>This library describes the sources captured on <strong>8 October 2026</strong>. Its counts cover the selected registries, not every repository object or every implemented feature. Short introductions and essays explain the records; they do not change their authority. The exact governing statements and original source links remain available in each entry.</p>
<p>Project State can preserve or reference proposals, evidence and unresolved matters with their own statuses. Acceptance of that state does not automatically accept every included record or promote its sources.</p>
</details>
<details class="inner"><summary>Terms you will meet in the records</summary><dl>
<dt>Scope</dt><dd>Where a meaning, rule or permission applies, and its limits.</dd>
<dt>Contract and schema</dt><dd>A contract states requirements. A schema expresses structural rules in a machine-readable form. Meeting a schema does not by itself prove truth or grant permission.</dd>
<dt>Reference and binding</dt><dd>A reference identifies another record; a binding explicitly associates particular records or versions. The binding’s own contract determines what that association means.</dd>
<dt>Canonical</dt><dd>In representation rules, the designated machine form with its declared approved origin. This is separate from semantic authority. A generated result can have a canonical type without becoming a second writable source of meaning; accepted definitions govern meaning through their own scope and decisions.</dd>
<dt>Projection or view</dt><dd>Information derived from selected source records for a particular question. An ontology view presents concepts and connections; a context view prepares information for work. Their source selections and omissions matter.</dd>
<dt>Qualifier</dt><dd>An extra detail required on a connection, such as version, scope, role, period or evidence.</dd>
<dt>Invariant</dt><dd>A condition the model requires to hold across the cases it covers. Stating an invariant does not prove that every implementation satisfies it.</dd>
<dt>Residue and claim ceiling</dt><dd>Residue is required matter that remains unresolved or unpreserved. A claim ceiling is the strongest conclusion the available record or evidence justifies.</dd>
<dt>Replay and cursor</dt><dd>Replay reconstructs a recorded state from its event history. A cursor identifies a position in that history.</dd>
<dt>Fingerprint or digest</dt><dd>A content identifier calculated from a record’s bytes, often using SHA-256. It supports checking which contents were captured; it does not establish their truth.</dd>
</dl></details>
<details class="inner"><summary>How to read the machine field names</summary>
<p>Names such as <code>source_ref</code> are exact field keys, retained so the explanation can be checked against the schema. A key ending in <code>_ref</code> refers to another record; <code>_version_ref</code> selects an exact version. Read the schema to learn which reference kinds are permitted.</p>
<p>In a JSON schema, <code>required</code> names mandatory fields, <code>properties</code> describes fields, <code>enum</code> restricts a value to a listed set, and <code>$ref</code> points to another schema section. A discriminator is the field-and-value rule that identifies a record’s type. These clues help you navigate; the full schema and type contract supply the complete requirements.</p>
</details></section>'''

css=(ROOT/'essay-base.css').read_text()+'''
.hero { padding-top:62px; }
.hero h1 { max-width:960px; }
.part-label { margin:28px 0 12px; font-size:12px; font-weight:650; color:var(--accent); letter-spacing:.035em; }
.chapter-grid { margin-top:14px; }
.chapter-card-title { font-size:23px; }
.chapter-number { margin-bottom:12px; }
.chapter-description { font-size:12px; }
.hero-status { display:flex; gap:10px; flex-wrap:wrap; font-size:12px; margin-top:24px; color:var(--muted); }
.hero-status strong { color:var(--ink); }
.hero-status span { border-right:1px solid var(--line); padding-right:12px; }
.hero-status span:last-child { border:0; }
.contents nav .part-label { margin:17px 0 5px; font-size:10px; }
.contents nav a { padding-top:7px; padding-bottom:7px; }
.contents-extra { margin-top:20px; }
.overview { margin:0 0 52px; border-top:1px solid var(--line); padding-top:34px; }
.overview h2 { font-family:var(--sans); font-size:27px; font-weight:550; }
.overview-intro,.atlas-intro { color:var(--muted); line-height:1.8; font-size:15px; max-width:850px; }
.flow { list-style:none; padding:0; margin:26px 0; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; }
.flow li { position:relative; border:1px solid var(--line); background:var(--surface); padding:18px 22px; }
.flow li span { display:block; color:var(--warm); font-size:11px; margin-bottom:10px; }
.flow strong { font-size:14px; font-weight:600; }
.flow p { color:var(--muted); font-size:12px; margin:8px 0 0; line-height:1.6; }
.flow-note { font-size:12px; color:var(--muted); line-height:1.8; }
.lens-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; padding:22px 0; border-top:1px solid var(--line); }
.lens-grid strong { font-family:var(--serif); font-weight:400; font-size:23px; }
.lens-grid p { font-size:13px; color:var(--muted); line-height:1.75; }
details>summary { cursor:pointer; }
.essay-sources { border-top:1px solid var(--line); margin-top:25px; padding:16px 0; font-size:12px; line-height:1.8; color:var(--muted); }
.essay-sources summary { color:var(--accent); font-weight:600; }
.essay-sources li { margin:8px 0; overflow-wrap:anywhere; }
.small { font-size:12px; color:var(--muted); line-height:1.8; }
.reference { border-top:1px solid var(--line); margin-top:45px; padding:48px 0; }
.reference h2 { margin-top:12px; }
.stats { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:25px 0; }
.stat { background:var(--surface); border:1px solid var(--line); padding:18px; }
.stat strong { display:block; font-family:var(--serif); font-size:34px; font-weight:400; }
.stat span { font-size:12px; line-height:1.6; color:var(--muted); }
.catalog-controls { position:sticky; top:63px; z-index:8; background:var(--paper); padding:18px 0; border-top:1px solid var(--line); border-bottom:1px solid var(--line); }
.catalog-controls label { display:block; font-size:12px; font-weight:600; margin-bottom:9px; }
.search-line { display:flex; gap:10px; }
.search-line input { width:100%; border:1px solid var(--line); border-radius:3px; padding:12px 14px; font:inherit; font-size:14px; color:var(--ink); background:var(--surface); }
button { font:inherit; color:var(--accent); cursor:pointer; border:1px solid var(--line); background:var(--surface); border-radius:3px; }
.search-line button { padding:0 18px; font-size:12px; }
.catalog-buttons { display:flex; flex-wrap:wrap; gap:8px; margin-top:13px; }
.catalog-buttons button { padding:9px 13px; font-size:12px; }
.catalog-buttons button[aria-pressed=true] { color:white; background:var(--accent); border-color:var(--accent); }
.catalog-panel { padding-top:20px; }
.catalog-panel h3 { font-size:20px; font-weight:500; }
.result-count { color:var(--muted); font-size:12px; }
.catalog-item { border:1px solid var(--line); background:var(--surface); margin:8px 0; border-radius:3px; scroll-margin-top:210px; }
.catalog-item>summary { display:flex; justify-content:space-between; align-items:center; gap:15px; padding:15px 18px; list-style:none; font-size:15px; }
.catalog-item>summary::-webkit-details-marker { display:none; }
.catalog-item>summary>span:first-child:before { content:'+'; color:var(--accent); margin-right:12px; font-family:var(--sans); }
.catalog-item[open]>summary>span:first-child:before { content:'−'; }
.catalog-item[open]>summary { border-bottom:1px solid var(--line); }
.badge { flex-shrink:0; color:var(--muted); font-size:10px; letter-spacing:.015em; background:var(--paper); padding:5px 8px; border-radius:3px; }
.record-body { padding:8px 22px 22px; font-size:14px; line-height:1.85; }
.record-body p { margin:15px 0; }
.record-id { font-size:12px; color:var(--accent); overflow-wrap:anywhere; }
.record-body dl { display:grid; grid-template-columns:155px minmax(0,1fr); gap:6px 14px; padding-top:12px; }
.record-body dt { font-size:12px; color:var(--muted); }
.record-body dd { margin:0; overflow-wrap:anywhere; font-size:12px; }
.inner { background:var(--paper); margin:14px 0; padding:12px 16px; }
.inner summary { font-size:12px; font-weight:600; color:var(--accent); }
.normative { font-family:var(--serif); font-size:16px; line-height:1.8; }
pre { white-space:pre-wrap; overflow-wrap:anywhere; font-size:12px; line-height:1.8; }
.table-scroll { overflow-x:auto; margin:18px 0; }
table { border-collapse:collapse; width:100%; font-size:12px; background:var(--surface); }
th,td { border-bottom:1px solid var(--line); text-align:left; padding:10px 13px; line-height:1.65; vertical-align:top; }
th { font-weight:600; }
caption { text-align:left; color:var(--muted); padding:8px 0; font-size:12px; }
.question { font-family:var(--serif); font-size:19px; }
.catalog-extras { margin-top:30px; }
.catalog-extras>details { border-top:1px solid var(--line); padding:18px 0; font-size:14px; }
.catalog-extras>details>summary { font-weight:600; color:var(--accent); }
.research { border-top:1px solid var(--line); padding:38px 0; }
.research h3 { font-size:20px; font-weight:550; margin-top:30px; }
.bibliography { list-style:none; padding:0; columns:2; column-gap:40px; }
.bibliography li { break-inside:avoid; margin-bottom:23px; font-size:14px; line-height:1.8; }
.bibliography p { font-size:12px; color:var(--muted); margin:6px 0 0; }
.finding { padding:14px 0; border-bottom:1px solid var(--line); font-size:13px; line-height:1.9; }
.finding summary { font-weight:600; }
.finding summary span { font-weight:400; color:var(--muted); font-size:11px; margin-left:10px; }
[hidden] { display:none!important; }
@media(max-width:760px) {
 .stats { grid-template-columns:repeat(2,1fr); }
 .flow { grid-template-columns:1fr; }
 .lens-grid { grid-template-columns:1fr; gap:5px; }
 .catalog-item>summary { align-items:flex-start; flex-direction:column; gap:8px; }
 .catalog-item .badge { margin-left:24px; }
 .record-body { padding:8px 16px 18px; }
 .record-body dl { grid-template-columns:1fr; gap:2px; }
 .record-body dd { margin-bottom:9px; }
 .bibliography { columns:1; }
 .catalog-controls { top:58px; }
 .chapter-grid { margin-top:12px; }
}
@media print {
 .overview,.reference,.research,.essay-sources { display:none; }
 .hero-status { font-size:9pt; }
}
'''

html='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Explore CyberAlchemy Lab through governance, the system model, agent work, operational learning and exact reference records.">
<meta name="color-scheme" content="light"><meta name="theme-color" content="#fdfaf3"><title>CyberAlchemy Lab — explore the system</title><link rel="stylesheet" href="assets/kep/design-system.css"><style>'''+css+'''</style><link rel="stylesheet" href="assets/lab-editorial.css"><link rel="stylesheet" href="assets/lab-landing.css"></head><body id="top" data-edition="reference">
<a class="skip-link" href="#learning-map">Skip to the learning map</a><div class="reading-progress" aria-hidden="true"></div>
<header class="topbar"><div class="topbar-inner"><a class="brand" href="#top"><img src="assets/kep/cyberalchemy-lab-logo-light-v2.svg" width="470" height="110" alt="CyberAlchemy Lab"><span class="brand-text" aria-hidden="true">CyberAlchemy Lab</span></a>
<nav aria-label="Primary navigation"><a href="#learning-map">Explore</a><a href="governance-lab-series.html">Visual guide ↗</a><a href="#reference">Reference</a></nav></div></header><main>'''+landing+reader_guide+'''
<details class="library-panel" id="articles-library"><summary><span class="library-number">01</span><span><strong>Expanded articles</strong><small>Eight readings on governance and the integrated Lab model</small></span><span class="library-toggle" aria-hidden="true">+</span></summary><div class="library-body">
<h2 class="part-label">Part I · Governance</h2><div class="chapter-grid">'''+cards(articles[:3])+'''</div>
<h2 class="part-label">Part II · The Lab model</h2><div class="chapter-grid">'''+cards(articles[3:])+'''</div>
<p class="series-note">The business examples illustrate the model. The essays distinguish accepted definitions and contracts from implemented software, recorded past executions and proposed work. This explanation does not itself approve changes or authorize actions.</p>
<section class="overview" aria-labelledby="overview-title"><div class="eyebrow">The model in one view</div><h2 id="overview-title">Work continues through project state</h2>
<p class="overview-intro">An agent begins with a purpose, selected project information and applicable rules and permissions. Reviewed, accepted changes enter saved project knowledge that a later session can inspect.</p>
<ol class="flow">'''+flow+'''</ol><p class="flow-note">This sequence explains the intended working loop. Each actual record connection still needs a declared connection rule; placement in this sequence does not create one. Essay 08 explains which parts have operational evidence. Experience can also lead to reflection, a proposed lesson, later use and an assessment of whether it helped.</p>
<div class="lens-grid"><div><strong>Authority</strong><p>Which accepted meanings and requirements apply, and who may authorize which consequences within what scope?</p></div><div><strong>Provenance</strong><p>Which sources, participants and transformations produced this record and its evidence?</p></div><div><strong>Lifecycle</strong><p>What states and transitions apply, and what has changed through time?</p></div></div></section>
<div class="reading-layout"><aside class="contents" aria-label="Series navigation"><p class="contents-label">Eight essays · Two parts</p><nav>'''+nav+'''</nav>
<div class="contents-extra"><a class="top-link" href="#reference">Reference catalog →</a><br><a class="top-link" href="#research">Sources and open questions →</a></div>
<p class="contents-note">Each machine agent exists for one session. Project State preserves saved project records and knowledge with their individual statuses. A later agent receives task information and concept maps derived from that state.</p></aside><div class="essays">'''+''.join(sections)+'''</div></div>
</div></details><details class="library-panel" id="catalog-library"><summary><span class="library-number">02</span><span><strong>Definitions, record formats and connections</strong><small>183 definitions · 121 format bindings · 41 connection rules · 109 endpoint kinds</small></span><span class="library-toggle" aria-hidden="true">+</span></summary><div class="library-body"><section class="reference" id="reference" aria-labelledby="reference-title"><div class="eyebrow">Reference catalog · 8 October 2026 snapshot</div><h2 id="reference-title">Inspect the meanings, formats and connections</h2>
<p class="atlas-intro">This catalog contains the complete current selections from the inspected registries—lists that record definitions, types and permitted connections. Open an entry to read its meaning, required format, acceptance or connection rules. Search by everyday explanation, term, exact identity or contract text.</p><p class="small">The summaries introduce each entry. Exact statements, technical references and original source links remain available inside it. See the <a href="#library-reading-guide">reading guide</a> for status and field explanations.</p>
<div class="stats"><div class="stat"><strong>183</strong><span>selected definition identities<br>189 accepted versions including history</span></div><div class="stat"><strong>121</strong><span>selected record-format bindings<br>143 accepted contracts including history</span></div><div class="stat"><strong>41</strong><span>connection-rule kinds<br>550 allowed source–target kind pairs</span></div><div class="stat"><strong>109</strong><span>named endpoint kinds<br>each identifies a permitted kind at one end of a link</span></div></div>
<p class="small">Acceptance comes from the recorded decisions and registry selection. An exact version can be accepted while its original name still contains “candidate.” Acceptance of a contract, the state of a particular subject and activation of software are separate facts.</p>
<div class="catalog-controls" data-theme="console"><label for="catalog-search">Search the reference catalog</label><div class="search-line"><input class="ds-input" id="catalog-search" type="search" placeholder="Term, identity or contract text" autocomplete="off"><button class="ds-button ds-button-secondary" type="button" id="clear-search">Clear</button></div><label class="search-scope" for="catalog-search-scope">Search in <select id="catalog-search-scope"><option value="all">Titles and complete records</option><option value="titles">Titles only</option></select></label><p class="search-help">Exact titles appear first, followed by title matches and references in other records.</p>
<div class="catalog-buttons" role="group" aria-label="Choose a catalog"><button type="button" data-select="definitions" aria-pressed="true">Definitions · 183</button><button type="button" data-select="types" aria-pressed="false">Record formats · 121</button><button type="button" data-select="relations" aria-pressed="false">Connection rules · 41</button><button type="button" data-select="endpoints" aria-pressed="false">Endpoint kinds · 109</button></div></div>'''+panels+'''
<div class="catalog-extras"><details><summary>Seven separate questions about a record</summary><p class="small">The three governance lenses are authority, provenance and lifecycle. These seven record facets describe separate matters within the wider model: status does not determine evidence confidence, and an owner’s commitment does not prove a claim.</p><div class="table-scroll"><table><thead><tr><th>Record facet</th><th>Question</th></tr></thead><tbody>'''+facet_rows+'''</tbody></table></div></details>
<details><summary>Earlier accepted definition versions · 6</summary><p class="small">These versions were accepted but are outside the inspected current selection. They remain in the captured registry, allowing earlier meanings and references to be examined.</p><div class="table-scroll"><table><thead><tr><th>Term</th><th>Exact reference</th><th>Acceptance record</th></tr></thead><tbody>'''+historical_defs+'''</tbody></table></div></details>
<details><summary>Earlier accepted record-type contracts · 22</summary><p class="small">These accepted contracts are outside the inspected current selection. Their historical listing is separate from the unaccepted proposals retained in the registry.</p><div class="table-scroll"><table><thead><tr><th>Contract</th><th>Recorded standing</th><th>Acceptance record</th></tr></thead><tbody>'''+historical_types+'''</tbody></table></div></details>
<details><summary>Why contract bindings and type descriptors have different counts</summary><p>A descriptor is a registry entry describing a type. A contract binding selects the requirements for a record kind or a section of a shared schema. The snapshot selects 114 accepted descriptors and seven additional bindings to shared schema sections, giving 121 current contract bindings.</p><p class="small">Separately, the registry retains seven earlier proposed descriptors that have not been accepted. Those seven proposals are a different set from the seven current shared-schema bindings. The captured inventory below retains its exact field names and counts.</p><pre>'''+inventory+'''</pre></details></div></section>
</div></details><details class="library-panel" id="research-library"><summary><span class="library-number">03</span><span><strong>Sources and open questions</strong><small>Research references, exact snapshots and the limits of the explanation</small></span><span class="library-toggle" aria-hidden="true">+</span></summary><div class="library-body"><section class="research" id="research" aria-labelledby="research-title"><div class="eyebrow">Research and editorial analysis</div><h2 id="research-title">Sources, interpretation and remaining work</h2>
<p class="atlas-intro">The essays combine registry entries with selected records about governance, integration, acceptance, implemented software, formal analysis and planned work. The research package preserves '''+str(len(M['sources']))+''' source files as captured on 8 October 2026, with content fingerprints to identify them. The catalog covers the inspected registry selections; the essays examine the sources relevant to their eight subjects. These records do not establish that the ontology covers the whole repository.</p>
<p class="small">The publications below help explain particular ideas. A comparison does not establish that the Lab implements the publication’s approach, complies with a standard or reproduces a study’s results. Reports of past validation describe the captured evidence; implementation checks were not rerun for this writing task.</p>
<h3>Primary literature</h3><ul class="bibliography">'''+literature+'''</ul>
<h3>Questions that remain open in this snapshot</h3>'''+findings+'''
<h3>How this explanation was written</h3><p class="atlas-intro">Each essay develops one argument and explains its technical vocabulary in context. The business examples make the concepts concrete; the catalog retains the full technical records. Short definition introductions are editorial aids beside the exact governing statements. Mensh and Kording’s paper informs the focus on a central contribution and what a reader needs to understand it. '''+link('Ten simple rules for structuring papers','https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005619')+'''.</p>
<p class="small">For detailed source tracking: '''+link('Source list and research scope','research/context-pack.json')+' · '+link('Catalog data · JSON','research/catalog.json')+' · '+link('Editorial review notes','research/editorial-review.json')+' · '+link('Series outline','series.txt')+'''</p>
<details class="essay-sources"><summary>Design and brand sources</summary><p>The editorial typography, reading surfaces, controls, Lab logo and red orb come from the KEP website’s shared design system. '''+link('Shared stylesheet','assets/kep/design-system.css')+' · '+link('Brand source record','research/kep-design-source.json')+'''.</p></details></section></div></details></section></main>
<footer><span>CyberAlchemy Lab · System explanation · Source snapshot: 8 October 2026</span><a href="#top">Back to top ↑</a></footer>
<script>
(() => {
 const essays=[...document.querySelectorAll('article')], links=[...document.querySelectorAll('[data-essay]')], progress=document.querySelector('.reading-progress');
 let pending=false;
 function update(){const height=document.documentElement.scrollHeight-innerHeight;progress.style.width=`${height>0?Math.min(100,Math.max(0,scrollY/height*100)):0}%`;let current=null;for(const e of essays){if(e.getClientRects().length&&e.getBoundingClientRect().top<=160)current=e.id;}links.forEach(l=>{if(l.dataset.essay===current)l.setAttribute('aria-current','location');else l.removeAttribute('aria-current');});pending=false;}
 function queue(){if(!pending){pending=true;requestAnimationFrame(update);}}
 addEventListener('scroll',queue,{passive:true});addEventListener('resize',queue);update();
 document.querySelectorAll('.library-panel').forEach(d=>d.addEventListener('toggle',queue));
 const lensTabs=[...document.querySelectorAll('[data-lens]')],lensPanels=[...document.querySelectorAll('[data-lens-panel]')];
 function chooseLens(name){lensTabs.forEach(t=>{const active=t.dataset.lens===name;t.setAttribute('aria-selected',String(active));t.tabIndex=active?0:-1;});lensPanels.forEach(p=>p.hidden=p.dataset.lensPanel!==name);queue();}
 lensTabs.forEach((tab,index)=>{tab.addEventListener('click',()=>chooseLens(tab.dataset.lens));tab.addEventListener('keydown',event=>{let next=index;if(['ArrowDown','ArrowRight'].includes(event.key))next=(index+1)%lensTabs.length;else if(['ArrowUp','ArrowLeft'].includes(event.key))next=(index+lensTabs.length-1)%lensTabs.length;else if(event.key==='Home')next=0;else if(event.key==='End')next=lensTabs.length-1;else return;event.preventDefault();chooseLens(lensTabs[next].dataset.lens);lensTabs[next].focus();});});
 chooseLens('governance');
 const panels=[...document.querySelectorAll('[data-panel]')], buttons=[...document.querySelectorAll('[data-select]')], search=document.getElementById('catalog-search');
 function select(name){panels.forEach(p=>p.hidden=p.dataset.panel!==name);buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.select===name)));}
 function filter(){const q=search.value.trim().toLocaleLowerCase();panels.forEach(p=>{let n=0;const rows=[...p.querySelectorAll('.catalog-item')];rows.forEach(r=>{r.hidden=!r.dataset.search.includes(q);if(!r.hidden)n++;});p.querySelector('.result-count').textContent=`${n} of ${rows.length} records${q?' match this search':''}`;});}
 buttons.forEach(b=>b.addEventListener('click',()=>select(b.dataset.select)));search.addEventListener('input',filter);document.getElementById('clear-search').addEventListener('click',()=>{search.value='';filter();search.focus();});
 function revealHash(){let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}const target=document.getElementById(id);if(!target)return;const lens=target.closest('[data-lens-panel]');if(lens)chooseLens(lens.dataset.lensPanel);const panel=target.closest('.catalog-panel');if(panel){search.value='';filter();select(panel.dataset.panel);}let d=target;while(d){if(d.tagName==='DETAILS')d.open=true;d=d.parentElement;}requestAnimationFrame(()=>{target.scrollIntoView({block:'start'});queue();});}
 select('definitions');filter();addEventListener('hashchange',revealHash);document.addEventListener('click',event=>{const a=event.target.closest('a[href^="#"]');if(a&&a.hash===location.hash)revealHash();});revealHash();
})();
</script></body></html>'''

class DocumentInspection(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=[]; self.hrefs=[]; self.resources=[]; self.articles=0; self.paragraphs=[]; self.prose=False; self.p=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a':self.hrefs.append(a.get('href',''))
        if tag=='link':self.resources.append(a['href'])
        if tag=='img':self.resources.append(a['src']);assert a.get('alt') or (a.get('alt')=='' and a.get('aria-hidden')=='true'),'Missing image description'
        if tag=='article':self.articles+=1
        if tag=='div' and a.get('class')=='prose':self.prose=True
        if tag=='p' and self.prose:self.p=''
    def handle_data(self,data):
        if self.p is not None:self.p+=data
    def handle_endtag(self,tag):
        if tag=='p' and self.p is not None:self.paragraphs.append(self.p);self.p=None
        if tag=='div' and self.prose:self.prose=False

# The complete source library gets a separate page in render_article.py.
# Keep its exact texts and IDs in one fragment so existing deep links survive.
library_start=html.index('<section class="resource-shelf"')
library_end=html.index('</section></main>')+len('</section>')
library_html=html[library_start:library_end]
check=DocumentInspection();check.feed(library_html)
expected=[pattern.sub(lambda m:m.group(1),p) for a in articles for p in a['paragraphs']]
assert check.paragraphs==expected,'Essay text lost in rendering'
assert check.articles==8
assert len(check.ids)==len(set(check.ids)),'Duplicate document identifiers'
foreign_ids={}
for href in check.hrefs:
    if href.startswith('#'):assert href[1:] in check.ids,('Missing navigation target',href)
    elif not href.startswith('https://'):
        path,_,fragment=href.partition('#');assert (ROOT/path).is_file(),('Missing local source link',href)
        if fragment:
            if path not in foreign_ids:
                foreign=DocumentInspection();foreign.feed((ROOT/path).read_text());foreign_ids[path]=set(foreign.ids)
            assert fragment in foreign_ids[path],('Missing guide section',href)
assert not M['issues'],'Registry/source binding mismatch'
for path in check.resources:assert (ROOT/path).is_file(),('Missing design asset',path)
for source in M['sources']:
    assert hashlib.sha256((ROOT/source['snapshot_path']).read_bytes()).hexdigest()==source['sha256'],'Snapshot digest mismatch'
output=ROOT/'reference-library.fragment.html';output.write_text(library_html,encoding='utf-8')
(ROOT/'assets/reference-library.css').write_text('@scope (.resource-shelf) {\n'+css+'\n}\n',encoding='utf-8')
receipt={'schema_version':'essay-render-inspection/v1','authority_effect':'none','essays':check.articles,'learning_lenses':len(LEARNING_MAP['lenses']),'entry_structure':'Three expandable library sections on a separate reference page.',
         'preserved_paragraphs':len(check.paragraphs),'catalog_counts':C['counts'],'captured_sources':len(M['sources']),
         'local_links':'all resolve','snapshot_integrity':'all captured digests match','registry_binding_discrepancies':M['issues'],
         'scope':'Document construction and static content inspection only; no implementation tests or browser interaction checks.',
         'html_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'bytes':output.stat().st_size}
(ROOT/'research/render-inspection.json').write_text(json.dumps(receipt,indent=2)+'\n')
(ROOT/'research/reference-reading-aids.json').write_text(json.dumps(READING.receipt(),indent=2)+'\n')
print(json.dumps({'output':str(output),**receipt},ensure_ascii=False))
