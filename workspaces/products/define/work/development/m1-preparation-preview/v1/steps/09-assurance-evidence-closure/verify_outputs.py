#!/usr/bin/env python3
"""Independently recheck stored witness truth, exact package and hostile shapes.

Does not import construction/refresh functions from the assurance producer.
Optional output is create-only. No runtime or authority effect is performed.
"""
from pathlib import Path
import copy
import hashlib
import json
import re
import sys
import jsonschema

STEP=Path(__file__).resolve().parent
ROOT=STEP.parents[5]
sys.path.insert(0,str(ROOT/'craft/formalization/candidates/definition-assurance-v1'))
import verifier
import ir

def load(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    checks=[]
    def check(name,ok,detail=None):
        assert ok,name
        checks.append({'check':name,'result':'PASS','detail':detail})
    core=load(STEP/'formal-core.json');w=load(STEP/'witnesses.json')
    declarations=core['declarations'];sorts={d['symbol_id']:d['symbol_id'] for d in declarations if d['kind']=='sort'}
    symbols={d['symbol_id']:d for d in declarations if d['kind']!='sort'}
    for f in core['axioms']:ir.formula(f,sorts,symbols)
    denotations={}
    for witness in w['finite_models']:
        den=verifier.Denotation(declarations,witness['model'])
        check('stored witness satisfies every typed axiom: '+witness['name'],all(den.truth(f) for f in core['axioms']))
        denotations[witness['name']]=den
    base=denotations['joint interpreted scope']
    for row in w['pairs']:
        ir.formula(row['query'],sorts,symbols)
        check('stored directional distinction '+row['left']+'/'+row['right'],base.truth(row['query']))
        check('supplied distinguishing entity exists',row['witness'] in w['finite_models'][0]['model']['domains']['Entity'])
    for row in w['boundaries']:
        ir.formula(row['query'],sorts,symbols)
        name='declared contracts and conforming saved result without runtime execution' if row['model']=='no-execution world' else 'joint interpreted scope'
        check('stored non-entailment '+row['premise'],not denotations[name].truth(row['query']))
    check('all 42 unordered pairs have two directed witnesses',len(w['pairs'])==84 and len({tuple(sorted([p['left'],p['right']])) for p in w['pairs']})==42)
    check('17 executed controls passed',len(load(STEP/'controls.json')['controls'])==17 and all(r['result']=='PASS' for r in load(STEP/'controls.json')['controls']))
    # Positive targets and hostile field changes go through the selected exact
    # schema, rather than a nominal label or a fabricated manual PASS.
    schema_controls=[]
    for t in load(STEP/'targets.json')['targets']:
        d=load(ROOT/t['path']);validator=jsonschema.Draft202012Validator(load(ROOT/t['schema']['path']))
        validator.validate(d)
        variants={}
        v=copy.deepcopy(d);v['implicit_admission']=True;variants['undeclared authority field']=v
        v=copy.deepcopy(d);v.pop('scope');variants['missing declared scope']=v
        v=copy.deepcopy(d);v['voices']['plain_language']['normative']=True;variants['normative plain voice']=v
        for name,variant in variants.items():
            rejected=bool(list(validator.iter_errors(variant)));check('hostile Definition schema '+t['model_role']+' '+name,rejected)
            schema_controls.append({'subject':t['definition_ref'],'mutation':name,'rejected':rejected})
    p=ROOT/'define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles'
    schema=load(p/'profile-carriers.schema.json')
    for name,key in [('evaluation.json','evaluationProfile'),('lifecycle.json','lifecycleProfile')]:
        d=load(p/name);validator=jsonschema.Draft202012Validator({**schema,'$ref':'#/$defs/'+key});validator.validate(d)
        v=copy.deepcopy(d);v['subject_artifact_type_ref']='cal.artifact-type.definition/v1';check('v2 profile rejects v1 subject '+name,bool(list(validator.iter_errors(v))))
        v=copy.deepcopy(d);v['auto_admit']=True;check('v2 profile rejects implicit effect '+name,bool(list(validator.iter_errors(v))))
        v=copy.deepcopy(d);v.pop('binding_contract_sha256');check('profile requires exact contract digest '+name,bool(list(validator.iter_errors(v))))
    impact=load(STEP/'consumer-impact-evidence.json')
    check('corrected impacted-record classification',impact['reference_classification_counts']=={'direct source':34,'evidence only':2,'foundational subject self-reference':1} and impact['actual_definition_consumers']==36)
    check('source closure exactly 41 bindings',len(load(STEP/'source-closure.json')['bindings'])==41)
    selection=load(STEP/'accepted-review-selections.json');check('16 scoped conversational selections',selection['selected_count']==16 and len(selection['selections'])==16)
    # Candidate standing must not disappear merely because rules/models passed.
    preview=load(STEP/'evaluation-preview.json');check('no invented full pre-decision PASS',all(e['pre_decision_aggregate']=='NOT_EVALUABLE' and not e['eligible_for_admission'] for e in preview['evaluations']))
    if (STEP/'package-manifest.json').exists():
        manifest=load(STEP/'package-manifest.json')
        for f in manifest['files']:check('exact final manifest '+f['path'],sha(ROOT/f['path'])==f['sha256'])
        for f in manifest['external_inputs']:check('exact external review input '+f['path'],sha(ROOT/f['path'])==f['sha256'])
    if (STEP/'registry-postimage.json').exists():
        r=load(STEP/'registry-postimage.json');baseline=load(ROOT/'authority/definitions/registry.json')
        check('all historical registry rows retained',all(e in r['entries'] for e in baseline['entries']))
        check('194 unique exact versions',len(r['entries'])==194 and len({e['definition_id']+'@'+e['version'] for e in r['entries']})==194)
        check('187 proposed identities',len(r['proposed_current_lookup'])==187)
        check('live 189 versions and 183 identities unchanged',len(baseline['entries'])==189 and len(baseline['current_lookup'])==183 and sha(ROOT/r['predecessor']['path'])==r['predecessor']['sha256'])
        text=(STEP/'DEFINITIONS-INDEX.md').read_text();check('every registry version indexed once',all(text.count('`'+e['definition_id']+'@'+e['version']+'`')==1 for e in r['entries']))
        check('no fake decision on five pending versions',sum(e['lifecycle_state']=='candidate-unadmitted' for e in r['entries'])==5 and all('admission_decision_ref' not in e for e in r['entries'] if e['lifecycle_state']=='candidate-unadmitted'))
        check('drift binds exact refreshed registry',load(STEP/'drift-audit-postimage.json')['registry_sha256']==sha(STEP/'registry-postimage.json'))
    broken=[]
    for p in STEP.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' in target or target.startswith('#'):continue
            if not (p.parent/target.split('#')[0]).exists():broken.append([p.name,target])
    check('local review links resolve',not broken)
    result={'schema_version':'cal.define-closure-independent-verification/v1','authority_effect':'none','checks':checks,'schema_controls':schema_controls,
        'checker':{'path':str(Path(__file__).resolve().relative_to(ROOT)),'sha256':sha(Path(__file__).resolve())},'admissions':0,'admission_ready':False,
        'ceiling':'Independent model structure/typed formula satisfaction and exact output/source checks. Owner fidelity, full source equivalence and actual adoption/effect authority are not supplied.'}
    if len(sys.argv)>1:
        path=Path(sys.argv[1]).resolve();assert path.parent==STEP
        with path.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'independent_checks':len(checks),'witnesses':len(w['pairs']),'schema_rejection_cases':len(schema_controls)+6,'admissions':0}))

if __name__=='__main__':main()
