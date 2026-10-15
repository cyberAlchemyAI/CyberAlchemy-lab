#!/usr/bin/env python3
"""Read-only admission preparation verifier. No semantic/owner/admission effects."""
import argparse, hashlib, importlib.util, json, sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[7]
OUT=Path(__file__).resolve().parent
CHECKS=[]

def read(p):return json.loads((ROOT/p).read_text())
def check(label,truth):
    CHECKS.append({'check':label,'result':'PASS' if truth else 'FAIL'})
    if not truth:raise ValueError(label)
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def exact(item):
    p=ROOT/item['path']
    return p.is_file() and sha(item['path'])==item['sha256'] and ('bytes' not in item or p.stat().st_size==item['bytes'])
def validator(path,selector=None):
    schema=read(path)
    if selector:schema={'$schema':schema.get('$schema'),'$defs':schema['$defs'],'$ref':selector}
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)
def load_module(p,name):
    spec=importlib.util.spec_from_file_location(name,ROOT/p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def descriptor_errors(d,original):
    schema=OUT/'carriers/local-descriptor-review.schema.json'
    errors=[str(x) for x in Draft202012Validator(json.loads(schema.read_text())).iter_errors(d)]
    if d.get('classification',{}).get('artifact_type_ref')!='cal.artifact-type.artifact-type/v3':errors.append('root must be current v3')
    if d.get('classification',{}).get('semantic_kind')!='artifact-type':errors.append('descriptor is an artifact type; represented instance kind is separate')
    if d.get('authority_effect')!='none' or d.get('status')!='candidate-unadmitted':errors.append('candidate has no effect')
    if d.get('artifact_type_root_binding')!=original['artifact_type_root_binding']:errors.append('root exact binding differs')
    if d.get('semantic_definition_bindings')!=original['semantic_definition_bindings']:errors.append('meaning binding or standing differs')
    if d.get('semantic_definition_refs')!=original['semantic_definition_refs']:errors.append('semantic identity differs')
    if d.get('schema_digest')!=original['schema_digest']:errors.append('instance schema differs')
    return errors

def registry_errors(doc):
    errors=list(validator(OUT.relative_to(ROOT)/'registry/mixed-review.schema.json').iter_errors(doc))
    refs=[r['definition_id']+'@'+r['version'] for r in doc['entries']]
    if len(refs)!=len(set(refs)):errors.append('duplicate exact identity')
    if any(v not in refs or not v.startswith(k+'@') for k,v in doc['proposed_current_lookup'].items()):errors.append('lookup must select exact identity@version')
    for row in doc['entries']:
        ref=row['definition_id']+'@'+row['version']
        if sha(row['path'])!=row['sha256']:errors.append('source digest mismatch')
        if doc['carrier_bindings'][ref]!=read(row['path'])['classification']['artifact_type_ref']:errors.append('source carrier mismatch')
    return errors

def main():
    rel=OUT.relative_to(ROOT)
    inputs=read(rel/'input-bindings.json')['bindings']
    for item in inputs:check('exact input '+item['path'],exact(item))
    subj=read(rel/'subjects.json');baseline=read(rel/'baseline.json')
    for key in ['definition_registry','definition_index','historical_drift','artifact_type_registry','current_project_state_pointer','current_runtime_bundle']:
        check('live baseline unchanged '+key,exact(baseline[key]))
    subjects=subj['selected_meanings']
    for s in subjects:
        check('exact meaning '+s['definition_ref'],exact(s))
        val=validator(s['schema']['path'])
        check('closed meaning schema '+s['definition_ref'],not list(val.iter_errors(read(s['path']))))
        # Use the existing exact projection generator; no producer invocation.
        gen=load_module(s['generator']['path'],'definition_gen_'+s['model_role'])
        render=getattr(gen,'render',None) or getattr(gen,'render_definition',None)
        check('definition projection callable '+s['model_role'],render is not None)
        got=render(read(s['path'])).rstrip()+'\n'
        check('exact human projection '+s['model_role'],got==(ROOT/s['human_projection']['path']).read_text())
    live=read(baseline['definition_registry']['path']);mixed=read(rel/'registry/mixed-review.json');strict=read(rel/'registry/v1-bootstrap-authored.json')
    check('mixed local closed schema',not list(validator(rel/'registry/mixed-review.schema.json').iter_errors(mixed)))
    check('inherited rows exact equality',mixed['entries'][:189]==live['entries'])
    check('six new versions and five new identities',len(mixed['entries'])==195 and len(mixed['proposed_current_lookup'])==188)
    by_ref={r['definition_id']+'@'+r['version']:r for r in mixed['entries']}
    check('unique exact registry identities',len(by_ref)==195)
    for k,v in mixed['proposed_current_lookup'].items():check('exact lookup '+k,v in by_ref and v.startswith(k+'@'))
    for e in mixed['entries']:
        ref=e['definition_id']+'@'+e['version']; doc=read(e['path'])
        check('entry exact source '+ref,sha(e['path'])==e['sha256'])
        check('entry exact carrier '+ref,mixed['carrier_bindings'][ref]==doc['classification']['artifact_type_ref'])
    check('old lookup preserved except explicit foundation successor',all(mixed['proposed_current_lookup'][k]==v for k,v in live['current_lookup'].items() if k!='cal.definition.definition'))
    check('all new rows retain candidate state and no Decision',all(r['lifecycle_state']=='candidate-authored' and r['admission_decision_ref'] is None for r in mixed['entries'][189:]))
    check('strict v1 original authoring schema',not list(validator('authority/foundation/v1/schema.json','#/$defs/definitionRegistry').iter_errors(strict)))
    check('strict v1 exact 191 bootstrap rows',len(strict['entries'])==191)
    check('all strict bootstrap sources really v1',all(read(r['path'])['classification']['artifact_type_ref']=='cal.artifact-type.definition/v1' for r in strict['entries']))
    gen=load_module(Path('authority/foundation/v1/render.py'),'foundation_projection')
    check('v1 index deterministic',gen.registry(strict).rstrip()+'\n'==(OUT/'registry/V1-BOOTSTRAP-INDEX.md').read_text())
    drift=read(rel/'registry/drift-audit.json')
    check('original drift carrier schema',not list(validator('authority/foundation/v1/schema.json','#/$defs/driftAudit').iter_errors(drift)))
    check('drift exact registry binding',sha(drift['registry_ref'])==drift['registry_sha256'])
    check('drift deterministic projection',gen.drift(drift).rstrip()+'\n'==(OUT/'registry/DRIFT-AUDIT.md').read_text())
    old_drift=read(baseline['historical_drift']['path']);pres=read(rel/'registry/historical-drift-preservation.json')
    check('all inherited drift findings retained',old_drift['findings']==pres['findings'] and len(pres['findings'])==baseline['historical_drift_findings'])
    carriers=read(rel/'carriers/subjects.json')['descriptors']; tgen=load_module(Path('tooling/generators/artifact_type_successor.py'),'type_projection')
    required=read('authority/artifact-types/artifact-type/v3/artifact.json')['instance_contract']['required_semantic_fields']
    for c in carriers:
        d=read(c['subject']['path']);check('descriptor local checks '+c['slug'],not descriptor_errors(d,d))
        check('descriptor complete field correspondence '+c['slug'],set(required)<=set(d))
        check('descriptor projection '+c['slug'],tgen.render_artifact(d)==(ROOT/Path(c['subject']['path']).with_name('ARTIFACT.md')).read_text())
        check('descriptor pending semantic premises '+c['slug'],all(x['admission_posture']=='candidate-unadmitted' for x in d['semantic_definition_bindings']))
        for binding in d['semantic_definition_bindings']:check('descriptor exact premise '+c['slug'],exact(binding))
        check('descriptor instance schema binding '+c['slug'],sha(c['schema_path'])==d['schema_digest'])
        pred=d['predecessor_contract'];check('preserved predecessor '+c['slug'],exact(pred))
        if c['slug']=='definition-binding':
            old=read('authority/artifact-types/definition/v2/artifact.json')
            for k in ['schema_ref','schema_digest','instance_contract','allowed_relation_kinds','relation_roles']:check('Definition/v2 preserved '+k,d[k]==old[k])
    pg=load_module(Path('define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles/generator.py'),'profile_projection')
    for kind,selector in [('evaluation','evaluationProfile'),('lifecycle','lifecycleProfile')]:
        p=rel/'profiles'/f'{kind}.json';data=read(p)
        check('profile unchanged bytes '+kind,sha(p)==sha(Path('define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles')/f'{kind}.json'))
        check('profile closed schema '+kind,not list(validator('define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles/profile-carriers.schema.json','#/$defs/'+selector).iter_errors(data)))
        check('profile deterministic projection '+kind,pg.render(data)==(OUT/'profiles'/(kind.upper()+'.md')).read_text())
        check('profile exact schema digest '+kind,sha('define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles/profile-carriers.schema.json')==data['schema_digest'])
        check('profile exact check contract '+kind,sha(data['binding_contract_ref'])==data['binding_contract_sha256'])
    for f in read(rel/'fixtures.json')['negative_cases']:
        bad=read(f['path'])
        if f['kind']=='descriptor':errors=descriptor_errors(bad,read(f['positive']))
        elif f['kind']=='registry':errors=registry_errors(bad)
        elif f['kind']=='v1-registry':errors=list(validator('authority/foundation/v1/schema.json','#/$defs/definitionRegistry').iter_errors(bad))
        else:errors=list(validator('define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles/profile-carriers.schema.json',f['schema_selector']).iter_errors(bad))
        check('hostile rejection '+f['path'],bool(errors))
    typ=read(rel/'registry/artifact-type-registration.json');old_types=read(baseline['artifact_type_registry']['path'])
    check('143 contracts preserved',typ['preserved_admitted_contracts']==old_types['admitted_contracts'] and len(typ['preserved_admitted_contracts'])==143)
    check('all historical type descriptors preserved',typ['preserved_descriptors']==old_types['descriptors'])
    check('only two type current selections change',len(typ['current_selection_changes'])==2 and all(x['identity'] in ['cal.artifact-type.evaluation-profile','cal.artifact-type.lifecycle-profile'] for x in typ['current_selection_changes']))
    check('Definition and metamodel TypeRefs remain stable',typ['proposed_current_by_identity']['cal.artifact-type.definition']=='cal.artifact-type.definition/v2' and typ['proposed_current_by_identity']['cal.artifact-type.artifact-type']=='cal.artifact-type.artifact-type/v3')
    refs=[x['artifact_type_ref'] for x in typ['preserved_admitted_contracts']+typ['proposed_contracts']]
    check('145 distinct contract refs if later applied',len(refs)==len(set(refs))==145)
    check('two candidate contracts no invented Decision',all(x['admission_decision_ref'] is None and x['lifecycle_state']=='candidate-unadmitted' for x in typ['proposed_contracts']))
    overlay=read(rel/'registry/definition-binding-overlay.json')
    check('binding is one revision no new contract',overlay['stable_artifact_type_ref']=='cal.artifact-type.definition/v2' and overlay['new_type_ref'] is False and overlay['effective_decision_ref'] is None)
    reqs=read(rel/'owner-requests.json')['requests'];seen=set()
    for r in reqs:
        check('acyclic ordered dependencies '+r['request_id'],set(r['depends_on'])<=seen);seen.add(r['request_id'])
        check('unselected request '+r['request_id'],r['selected'] is False and r['actual_decision_ref'] is None and r['actual_effect_ref'] is None)
        for material in r['review_material']:check('exact request material '+r['request_id']+' '+material['path'],exact(material))
    check('visibility excluded from semantic selection',next(x for x in reqs if x['request_id']=='COHERENT-VISIBILITY')['included_for_selection'] is False)
    standing=read(rel/'standing.json')
    check('no invented effective v2 standing',standing['actual_admission_ready'] is False and standing['v2_profiles']['actual_check_11']=='NOT_EVALUABLE')
    acceptance=read(rel/'fresh-fidelity-acceptance.json')
    check('fresh acceptance binds exact old manifest',exact(acceptance['frozen_review_package']) and acceptance['frozen_review_package']['sha256']=='19bbecca1fffd7e8508b34903475ebbe985922e038781e8745388de42201ab6f')
    consumers=read(rel/'consumers/compatibility.json')
    for c in consumers['preserved_canonical_sources']:check('preserved canonical consumer '+c['path'],exact(c))
    for c in consumers['selected_operational_consumers']:check('preserved operational consumer '+c['subject']['path'],exact(c['subject']))
    provider=(ROOT/'implementation/lab-runtime/v2/lab_runtime/sources.py').read_text()
    check('current provider digest-pin finding directly supported','cap.read("authority/definitions/registry.json", cap.materials[BASE + "/registries/definition-registry.json"])' in provider)
    for k in ['definition_registry','definition_index','historical_drift','artifact_type_registry','current_project_state_pointer','current_runtime_bundle']:check('final live baseline preserved '+k,exact(baseline[k]))
    return {'schema_version':'cal.define-admission-preparation-verification/v1','authority_effect':'none','result':'PASS','scope':'Exact preparation, schemas, generated views, declared dependency order, rejection fixtures and preservation only; not an adopted-profile Evaluation, owner qualification, runtime conformance or admission readiness.','checks_passed':len(CHECKS),'checks':CHECKS,'negative_cases_rejected':len(read(rel/'fixtures.json')['negative_cases']),'actual_admission_ready':False,'actual_admissions':0}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path);args=parser.parse_args()
    try:report=main()
    except Exception as e:
        print(json.dumps({'result':'FAIL','error':str(e),'checks_completed':len(CHECKS)}));sys.exit(1)
    if args.report:
        with args.report.open('x') as f:f.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='checks'}))
