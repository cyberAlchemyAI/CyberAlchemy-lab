#!/usr/bin/env python3
"""Read-only structural/currentness checks; create a fresh evidence output only.

No runtime tests, admission writes, source reinterpretation or owner decisions.
"""
from pathlib import Path
import hashlib
import json
import re
import sys
import jsonschema

STEP=Path(__file__).resolve().parent
ROOT=STEP.parents[5]
def load(p): return json.loads(Path(p).read_bytes())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p): return {'path':str(p.relative_to(ROOT)), 'sha256':sha(p)}
def pointer(v,s):
    assert s.startswith('/') and s!='/', 'unsupported or ambiguous selector'
    for k in s[1:].split('/'):
        k=k.replace('~1','/').replace('~0','~')
        v=v[int(k)] if isinstance(v,list) else v[k]
    assert v is not None
    return v

def main():
    results=[]
    def check(name, ok):
        assert ok,name
        results.append({'check':name,'result':'PASS'})
    schema=load(STEP/'postimages.schema.json')
    for name,selector in [('registry-postimage.json','registry'),('drift-audit-postimage.json','drift'),('artifact-type-registry-postimage.json','types')]:
        selected={**schema, '$ref':'#/$defs/'+selector}
        jsonschema.Draft202012Validator(selected).validate(load(STEP/name))
        check('local candidate closed schema: '+name, True)
    freeze=load(STEP/'review-inputs.json')
    for f in freeze['files']: check('frozen input: '+f['path'],sha(ROOT/f['path'])==f['sha256'])
    baseline=load(ROOT/'authority/definitions/registry.json')
    proposed=load(STEP/'registry-postimage.json')
    entries={e['definition_id']+'@'+e['version']:e for e in baseline['entries']}
    check('all inherited registry rows unchanged',all(e in proposed['entries'] for e in baseline['entries']))
    check('exact version and lookup counts',len(proposed['entries'])==194 and len(proposed['proposed_current_lookup'])==187)
    check('index covers each exact version once',all((STEP/'DEFINITIONS-INDEX.md').read_text().count('`'+e['definition_id']+'@'+e['version']+'`')==1 for e in proposed['entries']))
    for e in proposed['entries']: check('registry target digest: '+e['definition_id']+'@'+e['version'],sha(ROOT/e['path'])==e['sha256'])
    check('drift registry binding',load(STEP/'drift-audit-postimage.json')['registry_sha256']==sha(STEP/'registry-postimage.json'))
    types=load(ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json')
    proposed_types=load(STEP/'artifact-type-registry-postimage.json')
    check('143 inherited type contracts exact',len(types['admitted_contracts'])==143 and types['admitted_contracts']==proposed_types['inherited_admitted_contracts'])
    check('type current selections inherited exact',types['current_by_identity']==proposed_types['inherited_current_by_identity'])
    selection=load(STEP/'selection.json')['targets']
    delta=load(STEP/'registration-delta.json')
    for i,row in enumerate(delta['proposed_new_registrations']):
        check('latest semantic binding: '+row['artifact_type_ref'],row['semantic_definition_refs']==[selection[i+3]['definition_ref']])
    for p in delta['proposed_descriptor_revisions']:
        check('exact latest descriptor: '+p['path'],sha(ROOT/p['path'])==p['sha256'])
    old=load(ROOT/entries[baseline['current_lookup']['cal.definition.definition']]['path'])
    new=load(ROOT/selection[2]['path'])
    for key in ['normative_statement','formal_expression']:
        check('foundational field preserved: '+key,old['voices']['scientific_formal'][key]==new['voices']['scientific_formal'][key])
    check('foundational authority scope preserved',old['scope']==new['scope'])
    d13p=ROOT/'docs/decisions/0013-foundation-01-admission/decision.json'
    d13=load(d13p); records={r['record_id']:r for r in d13['admitted_records']}
    decision_paths={}
    for p in (ROOT/'docs/decisions').glob('*/decision.json'):
        value=load(p)
        if 'decision_id' in value: decision_paths[value['decision_id']]=p
        for member in value.get('decision_refs',[]): decision_paths[member]=p
    closed=[]; source_files={d13p}
    for target in selection:
        definition=load(ROOT/target['path'])
        for s in definition['source_refs']:
            if s['source_ref'] in records:
                e=records[s['source_ref']]; decision=d13['decision_id']
            else:
                e=entries[s['source_ref']]; decision=e['admission_decision_ref']
            p=ROOT/e['path']; dp=decision_paths[decision]
            check('admitted source posture and decision: '+s['source_ref'],s['admission_posture']=='admitted' and s['source_admission_ref']==decision and load(dp)['status']=='owner-admitted')
            check('whole-source digest: '+s['source_ref'],sha(p)==s['content_sha256']==e['sha256'])
            pointer(load(p),s['selector'])
            closed.append({'subject':target['definition_ref'],'source_ref':s['source_ref'],'selector':s['selector'],
                'source':ref(p),'standing_decision':ref(dp),'result':'PASS'})
            source_files.update([p,dp])
    check('41 admitted source bindings across all five subjects',len(closed)==41)
    broken=[]
    for p in STEP.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' in target or target.startswith('#'):continue
            if not (p.parent/target.split('#')[0]).exists():broken.append([p.name,target])
    check('all local Markdown links resolve',not broken)
    pending=load(STEP/'remaining-decisions.json')['decisions']
    check('16 independent review items remain pending',len(pending)==16 and all(d['status']=='pending' and d['selected_outcome'] is None for d in pending))
    if (STEP/'package-manifest.json').exists():
        for f in load(STEP/'package-manifest.json')['files']:check('frozen package: '+f['path'],sha(ROOT/f['path'])==f['sha256'])
    result={'schema_version':'cal.define-exact-postimage-integrity/v1','authority_effect':'none',
        'checks':results,'closed_sources':closed,'additional_frozen_source_files':[ref(p) for p in sorted(source_files)],
        'technical_source_gaps':0,'owner_fidelity':'pending','admission_ready':False,'runtime_tests_executed':False,
        'checker':ref(Path(__file__).resolve()),'claim_ceiling':'Integrity, recorded source standing, selector resolution and structural projection only. No source-interpretation acceptance, owner authentication, global consistency, adoption or applied effect.'}
    if len(sys.argv)>1:
        out=Path(sys.argv[1]).resolve()
        assert out.parent==STEP, 'evidence output must remain in this candidate step'
        with out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'checks_passed':len(results),'source_bindings':len(closed),'technical_source_gaps':0,'owner_acceptance':False,'admissions':0}))

if __name__=='__main__':main()
