#!/usr/bin/env python3
"""Review the sealed candidate and publish corrected explanatory projections."""
import copy
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path

import jsonschema

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
ROOT=Path(__file__).resolve().parents[8]
observations=[]


def ref(p):
    p=p if isinstance(p,Path) and p.is_absolute() else ROOT/p
    b=p.read_bytes()
    return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}


def load(p):
    p=p if isinstance(p,Path) and p.is_absolute() else ROOT/p
    return json.loads(p.read_text())


def digest(v):
    return hashlib.sha256((json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()


def check(name,condition):
    observations.append({'check_id':name,'outcome':'PASS' if condition else 'FAIL'})
    if not condition:raise ValueError(name)


def write(name,value):
    with (OUT/name).open('x') as f:
        f.write(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n')


manifest=load(BASE/'package-manifest.json')
for item in manifest['files']:check('sealed:'+item['path'],ref(item['path'])==item)
model=load(BASE/'model.json')
pack=load(BASE/'incident-pack.json')
schema=load(BASE/'pack-embedding.schema.json')
prior_review=load(BASE/'review-report.json')
for item in prior_review['protected_live_material']:check('live:'+item['path'],ref(item['path'])==item)
for subject in model['selected_meanings']:
    check('subject:'+subject['definition_ref'],ref(subject['path'])['sha256']==subject['sha256'])
    jsonschema.Draft202012Validator(load(subject['schema']['path'])).validate(load(subject['path']))
    check('subject-schema:'+subject['definition_ref'],True)
    spec=importlib.util.spec_from_file_location('selected_renderer',ROOT/subject['generator']['path'])
    r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
    check('subject-projection:'+subject['definition_ref'],r.render(load(subject['path']))==(ROOT/subject['human_projection']['path']).read_text())


def resolve_pointer(document,selector):
    current=document
    if not selector.startswith('/'):raise ValueError('local selector required')
    for component in selector[1:].split('/'):
        component=component.replace('~1','/').replace('~0','~')
        current=current[int(component)] if isinstance(current,list) else current[component]
    return current


def review_pack(p):
    errors=[]
    try:jsonschema.Draft202012Validator(schema).validate(p)
    except jsonschema.ValidationError:errors.append('shape');return errors
    apps={a['application_id']:a for a in p['applications']}
    if len(apps)!=len(p['applications']):errors.append('duplicate application')
    concepts=[c['concept_id'] for c in p['concepts']]
    if len(set(concepts))!=len(concepts) or set(concepts)!=set(p['required_concepts']):errors.append('concept coverage')
    sources={e['evidence_id']:e for e in p['evidence']}
    if len(sources)!=len(p['evidence']):errors.append('duplicate evidence')
    for a in p['applications']:
        mref=a['meaning_ref']
        if mref['kind']!='task-local-proposal':
            errors.append('external application not qualified by this preview');continue
        try:m=resolve_pointer(p,mref['selector'])
        except (KeyError,IndexError,ValueError,TypeError):errors.append('unresolved meaning selector');continue
        if mref['meaning_id']!=m.get('meaning_id') or mref['revision']!=m.get('revision') or digest(m)!=mref['sha256']:errors.append('meaning identity/revision/hash')
        if m.get('scope_ref')!=p['scope']['task_ref'] or a['task_ref']!=p['scope']['task_ref']:errors.append('task scope')
        params=m['parameters'];bindings=a['bindings']
        if set(bindings)-set(params):errors.append('undeclared parameter')
        if {k for k,v in params.items() if v['required']}-set(bindings)!=set(a['binding_gaps']):errors.append('required parameter gap')
        for k,v in bindings.items():
            if k in params and not isinstance(v,{'string':str,'object':dict}[params[k]['type']]):errors.append('parameter type')
        covered=set()
        for source in a['value_provenance']:
            covered.update(source['parameters'])
            if source['evidence_id'] not in sources:errors.append('value provenance missing')
        if set(bindings)-covered:errors.append('value provenance incomplete')
    for y in p['assessments']:
        a=apps.get(y['application_id'])
        if a is None:errors.append('assessment application missing');continue
        if a['revision']!=y['application_revision'] or digest(a)!=y['application_sha256']:errors.append('assessment application stale')
        if y['meaning_sha256']!=a['meaning_ref']['sha256']:errors.append('assessment meaning stale')
        selected=set()
        for e in y['evidence_bindings']:
            selected.add(e['evidence_id'])
            if e['evidence_id'] not in sources or digest(sources[e['evidence_id']])!=e['sha256']:errors.append('assessment evidence stale')
        if set(a['bindings'].get(k) for k in ['S','E'])-selected:errors.append('assessment required evidence omitted')
        if y['method']['implementation']!=ref(BASE/'prepare.py'):errors.append('fixture method implementation mismatch')
    return errors


check('incident-selector-type-provenance-integrity',not review_pack(pack))
additional=[]
for name,change,expected in [
    ('missing-local-selector',lambda p:p['applications'][0]['meaning_ref'].update(selector='/working_meanings/9'),'unresolved meaning selector'),
    ('wrong-meaning-identity',lambda p:p['applications'][0]['meaning_ref'].update(meaning_id='another-meaning'),'meaning identity/revision/hash'),
    ('wrong-meaning-revision',lambda p:p['applications'][0]['meaning_ref'].update(revision=2),'meaning identity/revision/hash'),
    ('parameter-type-mismatch',lambda p:p['applications'][0]['bindings'].update(A=2),'shape'),
    ('duplicate-application-id',lambda p:p['applications'].append(copy.deepcopy(p['applications'][0])),'duplicate application'),
    ('application-outside-task',lambda p:p['applications'][0].update(task_ref='task:other'),'task scope'),
    ('required-evidence-omitted',lambda p:p['assessments'][0].update(evidence_bindings=[]),'assessment required evidence omitted'),
    ('binding-without-value-provenance',lambda p:p['applications'][0].update(value_provenance=[]),'value provenance incomplete'),
]:
    p=copy.deepcopy(pack);change(p);errors=review_pack(p)
    check('additional-control:'+name,expected in errors)
    additional.append({'case':name,'expected':expected,'observed':errors})
p=copy.deepcopy(pack);p['assessments']=[]
check('optional-assessment-absent',not review_pack(p))
p['applications'][0]['bindings'].pop('F');p['applications'][0]['binding_gaps']=['F']
check('explicit-partial-binding-valid-as-record',not review_pack(p))

# Correct the main diagram and historic labels. These are explanatory changes,
# not amendments to the already sealed candidate definition bytes.
main=(BASE/'MODEL.md').read_text()
start=main.index('```mermaid');end=main.index('```',start+10)+3
main=main[:start]+'''```mermaid
flowchart TD
  A[Intent, Goal and selected context] --> B[Define]
  B --> C[Definition Pack]
  C --> D[Exact meanings and embedded working proposals]
  D --> E[Definition applications with task values]
  E --> F[Separately produced assessments inside the Pack]
  C --> G[Explicit selection for governed Definition preparation]
  G --> H[Complete candidate and evaluation evidence]
  H --> I[Owner decision and confirmed application]
  I --> J[Governed Project State and derived views]
```
'''+main[end:]
main=main.replace('## 2. The five meanings','## 2. The six meanings')
main=main.replace('Definition, Pack and Define use the existing Definition/v2 carrier.','Definition, Pack, Define and Definition application use the existing Definition/v2 carrier.')
main=main.replace('### The proposed Definition','### The task-local proposed meaning')
main=main.replace('The full original normative statements','The full selected candidate normative statements')
main=main.replace('complete exported Definition records, exact evidence and an owner review package with visible blockers.','a complete embedded task Pack, exact evidence and complete Definition records when their admission preparation is selected, with visible blockers.')
main=main.replace('4. Evaluation evidence with exact subject/profile/input bindings, check outcomes, causal blockers and claim limits.','4. Scoped preparation evidence and separately supplied task assessments. A governed Evaluation, when required and actually executed, retains exact subject/profile/input bindings, all declared check outcomes, causal blockers and claim limits.')
main=main.replace('The index and drift material are generated from their exact selected inputs. The 12 inherited drift findings are preserved,','The revised candidate registry/index preview is prepared. Exact revised drift and qualified full-cohort compatibility remain open; the prior frozen drift material is preserved. The 12 inherited drift findings are preserved,')
main=main.replace('| G01 — Define and Definition Pack meanings | Two reviewed three-voice meanings','| G01 — Define, Definition Pack and Definition application meanings | Three candidate three-voice meanings')
main=main.replace('| G05 — Complete candidate exporter | A candidate prepare command produces complete Definition/v2 records or explicit blockers, with exact field lineage and safe output. |','| G05 — Task Pack and selected Definition exporter | A candidate prepare command emits the embedded task Pack and complete Definition/v2 records when selected, with exact field lineage and safe output. |')
main=main.replace('| COHERENT-VISIBILITY | PACK-AND-DEFINE, PROFILE-MEANINGS, PROFILE-MECHANICS, PROFILE-TYPES, PROFILE-ADOPTION, FOUNDATIONAL-SUCCESSOR, DEFINITION-BINDING |','| COHERENT-VISIBILITY | PACK-AND-DEFINE, PROFILE-MEANINGS, PROFILE-MECHANICS, PROFILE-TYPES, PROFILE-ADOPTION, FOUNDATIONAL-SUCCESSOR, DEFINITION-BINDING, DEFINITION-APPLICATION |')

# Preserve each relative link's original target after moving this corrected
# presentation one directory deeper.
main=re.sub(r'\]\(([^)]+)\)',lambda m:']('+('../'+m.group(1) if not m.group(1).startswith(('http:','https:','#')) else m.group(1))+')',main)
main=main.replace('[Review report](../REVIEW.md)','[Review report](REVIEW.md)')
write('MODEL.md',main)
model['incident']['working_meaning_selector']=model['incident'].pop('working_meananing_selector')
model['presentation_review_supplement']={'model':ref(OUT/'MODEL.md'),'status':'corrected flow, optional outputs and scope labels; candidate meaning bytes unchanged'}
write('model.json',model)
check('corrected-six-meaning-heading','## 2. The six meanings' in main and '## 2. The five meanings' not in main)
check('diagram-does-not-force-materialization','Explicit selection for governed Definition preparation' in main and 'D --> E[Complete proposed Definitions]' not in main)
check('profile-subject-check-count-unchanged',len(load(ROOT/'define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles/check-contracts.json')['checks'])==14)
for target in re.findall(r'\]\(([^)]+)\)',main):
    if target.startswith(('http:','https:','#')) or target=='REVIEW.md':continue
    check('corrected-link:'+target,(OUT/target.split('#')[0]).exists())
for item in prior_review['protected_live_material']:check('final-live-preserved:'+item['path'],ref(item['path'])==item)
review={'authority_effect':'none','reviewer':'authoring assistant supplemental self-review','predecessor_manifest':ref(BASE/'package-manifest.json'),'executed_checks':observations,'passed_checks':len(observations),'failed_checks':0,'additional_controls':additional,'initial_controls':17,'total_named_controls':25,'application_without_assessment_checked':True,'partial_binding_with_explicit_gap_checked':True,'corrections':['Workflow diagram now has embedded application/assessment path and explicit optional materialization.','Six-meaning heading, Definition/v2 carrier list and task-local criterion label corrected.','Optional executed Evaluation and pending revised drift are explicit.','Selectors, meaning identity/revision, value types, provenance and assessment evidence completeness reviewed.'],'limitations':['Self-review and finite synthetic controls only; no global semantic proof or independent owner acceptance.','New meaning and changed candidate.4 records still require fresh exact fidelity/formal correspondence, impact and applicable standing.','Preview schema is not the complete generic production adapter or admitted Evaluation/Measurement Result carrier.','No runtime suite, admission, type registration or application executed.'],'admission_ready':False,'actual_admissions':0,'application':False}
write('review-report.json',review)
write('REVIEW.md',f'''# Final review before presentation

The initial revision passed 109 scoped checks and 17 named synthetic controls. This supplemental review passed **{len(observations)} additional scoped checks**, including eight additional negative controls, for **25 named synthetic controls in total**. Application-without-assessment and explicit partial-binding checks also passed.

The review corrected the workflow diagram so embedded task applications/assessments are visible and standalone Definition preparation requires explicit selection. It corrected the six-meaning heading, carrier list, task-local criterion label, optional Evaluation output and pending revised drift statement. Candidate meaning bytes and the sealed predecessor remain unchanged.

Selector, meaning identity/revision, value-type, provenance, duplicate application, task-scope and required assessment-evidence controls were checked. A partial application can be recorded with explicit gaps; that is not FullyBound or evaluable without the missing inputs.

## Incident result

- Initial saved output: 12,000 required IDs, 11,800 required IDs present, 200 missing; inclusion **FAIL**.
- Saved retry: same proposed meaning, new application/evidence epoch, 12,000 required IDs present; inclusion **PASS**.
- Extras do not violate inclusion; exclusivity remains open. Unknown population is **NOT_EVALUABLE**, while established empty population satisfies inclusion.
- Undeclared tolerance changes the criterion contract; it is not accepted as parameter substitution. Stale application/evidence bindings remain invalid.

This is authoring-assistant self-review and executed local synthetic evidence. No production Define run, complete governed Evaluation/Measurement Result, independent owner fidelity acceptance, global semantic proof, shared admission, permission or incident closure is claimed. Revised drift/impact/standing and exact admission requirements remain open.

Read [the corrected complete model](MODEL.md), [Definition application](../definitions/definition-application/DEFINITION.md), [the single incident Pack](../incident-pack.json), [full candidate contracts](../CONTRACTS.md), [initial review observations](../review-report.json) and [supplemental observations](review-report.json).
''')
for target in re.findall(r'\]\(([^)]+)\)',(OUT/'REVIEW.md').read_text()):
    assert (OUT/target).exists(),target
files=[ref(OUT/x) for x in ['review.py','MODEL.md','model.json','review-report.json','REVIEW.md']]
write('package-manifest.json',{'schema_version':'cal.define-application-reviewed-presentation-manifest/v1','authority_effect':'none','predecessor_seal':ref(BASE/'package-manifest.json'),'files':files,'status':'frozen corrected full model and supplemental self-review; no owner effect selected','exclusions':['manifest itself','later verification/routing records','mutable navigation/progress'],'admission_ready':False,'actual_decision_ref':None,'application':False})
print(json.dumps({'manifest':ref(OUT/'package-manifest.json'),'additional_checks':len(observations),'total_named_controls':25,'model':str(OUT/'MODEL.md')},indent=2))
