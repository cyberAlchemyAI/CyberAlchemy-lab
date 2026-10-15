"""Produce the new closed contract from the sealed A01 structural vocabulary."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[7]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1'
raw=(IMPL/'schemas/input-envelope.json').read_bytes();upstream=json.loads(raw)
def obj(properties):return {'type':'object','additionalProperties':False,'properties':properties,'required':list(properties)}
def arr(items,minimum=0):return {'type':'array','items':items,'minItems':minimum,'uniqueItems':True}
def ref(key):return {'$ref':'#/$defs/'+key}
text={'type':'string','minLength':1};identity=copy.deepcopy(upstream['$defs']['source-ref']['properties']['definition_id']);sha=copy.deepcopy(upstream['$defs']['binding']['properties']['sha256']);nullable_binding={'anyOf':[ref('binding'),{'type':'null'}]}
defs=copy.deepcopy(upstream['$defs'])
defs['source-unit']=obj({'unit_id':identity,'selector':{'type':'string','pattern':'^/'},'text_sha256':sha,'length_characters':{'type':'integer','minimum':1},'source_facet':{'enum':['normative','boundary','explanatory','scope','claim-ceiling','unresolved']}})
defs['correspondence']=obj({'unit_id':identity,'clause_id':identity,'end_character':{'type':'integer','minimum':1},'excerpt':text})
defs['review-case']=obj({'case_id':identity,'scenario':text,'expected_interpretation':text,'rationale':text,'related_clause_ids':arr(identity)})
defs['dependency-link']=obj({'clause_id':identity,'dependency_ref':ref('source-ref'),'kind':{'enum':['semantic-use','imported-traceability','unresolved']},'rationale':text})
defs['assumption-link']=obj({'clause_id':identity,'assumption_id':identity})
defs['source-conflict']=obj({'finding_id':identity,'selectors':arr({'type':'string','pattern':'^/'},1),'description':text,'status':{'enum':['unresolved','candidate-route-recorded']},'owner_route':text})
schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:cyberalchemy-lab:definition-assurance:interpretation:v1-candidate',**obj({'schema_version':{'const':'definition-assurance-correspondence/v1-candidate'},'authority_effect':{'const':'none'},'upstream_schema_sha256':{'const':hashlib.sha256(raw).hexdigest()},'source_selection':{'const':'current'},'inventory_policy':{'const':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1'},'interpretation':ref('interpretation'),'source_units':arr(ref('source-unit'),1),'correspondence':arr(ref('correspondence'),1),'dependency_links':arr(ref('dependency-link')),'dependency_closure':obj({'status':{'enum':['unresolved','candidate-explicit-closure']},'review_ref':nullable_binding,'unresolved_notes':arr(text)}),'assumption_links':arr(ref('assumption-link')),'source_precedence':obj({'normative_voice':{'const':'/voices/scientific_formal'},'conflicts':arr(ref('source-conflict')),'review_ref':nullable_binding}),'review_packet':obj({'instances':arr(ref('review-case'),1),'counterexamples':arr(ref('review-case'),1),'known_losses':arr(text),'review_status':{'enum':['pending','candidate-agent-reviewed']},'review_ref':nullable_binding})}),'$defs':defs,'description':'Closed source-correspondence contract. Structural conformance, total textual accounting, dependency selection, logical typing, source-owner fidelity and proof remain separate. No owner acceptance or readiness can be self-declared here.'}
with (IMPL/'schemas/interpretation.json').open('x') as f:json.dump(schema,f,indent=2,sort_keys=True);f.write('\n')
print('Produced interpretation contract with',len(defs),'local definitions')
