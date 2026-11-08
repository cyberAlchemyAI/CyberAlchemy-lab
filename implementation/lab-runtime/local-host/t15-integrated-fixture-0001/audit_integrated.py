"""Cold-replay actual integrated closure; emit no private archive content."""
from __future__ import annotations
import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'))
T03=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/local-lifecycle-actual-clock-0001'
OLD=T03/'native-durable-20261024/instances/legacy-local-4051bec8ca41c6e2'
SELECTED_INSTANCE='legacy-local-4636eca980a5d94d'
SELECTED_SOURCE='f07c87624a5cc133e00f36737674685e3aa5a5635a112a79319101b6d5f27ff2'
SELECTED_PACKAGE='da4d09f2f2953044859daad8a8830ecbb0fd198164ad10e5611d6c491056d0ee'
INPUT_PINS={
 'product/lab/release-candidates/v1/interface/api-integration-v30/source-manifest.json':'cfd9a932d87c565c22b915234bbf2a18bfed23f163607b95b96f24b2533e3a16',
 'authority/project-state-transitions/current.json':'12937950af2a00ef329deb1a922275250c61ad199b8f6216eab448e06bf49984',
 'authority/admissions/lab-specialist-owner-bootstrap-v1-0003/instances/project-state.json':'cccf18d2966cf0dd494f7d88b054243bb635a91bc84fdcbf5c70709b7b6f8793',
}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def parse(p):return json.loads(p.read_bytes())
def require(ok,message):
    if not ok:raise ValueError(message)
def fields(a,b,prefix=''):
    if isinstance(a,dict) and isinstance(b,dict):
        result=[]
        for key in sorted(set(a)|set(b)):
            if key not in a or key not in b:result.append({'field':prefix+'/'+key,'old':a.get(key),'new':b.get(key)})
            else:result+=fields(a[key],b[key],prefix+'/'+key)
        return result
    return [] if a==b else [{'field':prefix,'old':a,'new':b}]
def normalized(value,family):
    raw=json.dumps(value,sort_keys=True).replace(family.name,'FAMILY').replace(family.name.replace('-','_'),'FAMILY_MODULE')
    raw=raw.replace(family.parent.parent.relative_to(ROOT).as_posix(),'FIXTURE_ROOT')
    return json.loads(raw)
def old_archive():
    handle=parse(OLD/'source/packages/0001/archive-handle.json')
    raw=Path(handle['path']).read_bytes();require(sha(raw)==handle['sha256'],'old archive changed')
    return json.loads(raw)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--instance',required=True);args=ap.parse_args();family=HERE/'instances'/args.instance
    require(args.instance==SELECTED_INSTANCE and family.is_dir() and family.parent==HERE/'instances','family scope differs')
    spec=importlib.util.spec_from_file_location('_integrated_audit_constructor',HERE/'construct_integrated.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    name='_integrated_independent_audit_'+family.name.replace('-','_');m.package(name,family/'source')
    C=__import__(name+'.cold',fromlist=['*']);R=__import__(name+'.records',fromlist=['*'])
    source_pin=sha((family/'source/source-manifest.json').read_bytes());package_pin=sha((family/'source/packages/0001/manifest.json').read_bytes())
    require((source_pin,package_pin)==(SELECTED_SOURCE,SELECTED_PACKAGE),'independent actual Source phase pins differ')
    oldrows=parse(OLD/'source/packages/0001/record-index.json');newrows=parse(family/'source/packages/0001/record-index.json')
    oldby={row['kind']:parse(ROOT/row['original_binding']['path']) for row in oldrows if row['kind']!='typed-relation'}
    newby={row['kind']:parse(ROOT/row['original_binding']['path']) for row in newrows if row['kind']!='typed-relation'}
    with C.open_source(source_pin,package_pin) as view:
        subjects=view.data['projection']['subjects']
        require(len(subjects)==619,'actual signed subject inventory differs')
        require(len(view.data['baseline']['materials'])==859,'actual signed baseline material inventory differs')
        require(len(newrows)==26 and len({r['version_ref'] for r in newrows})==26,'fresh record identity collision')
        require(sum(r['carrier_ref']=='cal.artifact-type.typed-relation/v3' for r in newrows)==12,'declared typed relations differ')
        require(len(view.data['transactions'])==3,'actual bootstrap + two signed transactions differ')
        actual_targets=[len(tx['proposal']['targets']) for tx in view.data['transactions'][1:]]
        require(actual_targets==[2,26],'actual signed target count differs')
        prior=json.loads(base64.b64decode(old_archive()['files']['baseline.json']['base64_original_bytes']))
        retained=['challenge-contract:cyberalchemy-lab-operational-foundation','principal:repository-owner','agent-session:first-governed-agent-episode:2026-10-06']
        retained_rows=[]
        for identity in retained:
            before=[r for r in prior['subjects'].values() if r['identity']==identity]
            after=[r for r in view.data['baseline']['subjects'].values() if r['identity']==identity]
            require(bool(before) and before==after,'original operator/historical witness changed '+identity)
            retained_rows.append({'identity':identity,'versions':len(before),'byte_identical_signed_baseline_rows':True})
        api30='product/lab/release-candidates/v1/interface/api-integration-v30/source-manifest.json'
        materials=view.data['baseline']['materials'];require(api30 in materials,'API30 manifest not signed baseline material')
        for path,digest in INPUT_PINS.items():
            require(materials.get(path)==digest and sha((ROOT/path).read_bytes())==digest,'three-input signed baseline provenance differs '+path)
        work=newby['work'];require('API30' in work['payload']['work_statement'],'actual Work objective differs')
        contract=newby['challenge-contract'];require(contract['payload']['eligible_challenger_kinds']==['agent-instance'],'Agent fixture Contract broadened')
        one=[s for s in subjects.values() if s['carrier_ref']=='cal.artifact-type.operational-lesson/v1' and s['effective_state'] in ('admitted-current','local-admitted-current')]
        require(len(one)==1,'actual one current Lesson differs')
        counts={'signed_subjects':len(subjects),'baseline_materials':len(materials),'source_records':len(newrows),'signed_transaction_targets':actual_targets,'original_targets':sum(actual_targets),'current_Lessons':len(one)}
    mapping=parse(family/'mapped/packages/0001/mapping.json')
    require(mapping['source_closure']['accounted_subjects']==619
            and len(mapping['projection_dispositions'])==619
            and {r['version_ref'] for r in mapping['projection_dispositions']}==set(subjects),
            'actual complete signed Source disposition inventory differs')
    # The selected mapper manifest gives its exact mapping locator; do not infer
    # node totals from the stage's expected-count declarations.
    mapping_rows=mapping['rows'];nodes=[r for r in mapping_rows if r['subject_identity']['subject_kind']=='node'];edges=[r for r in mapping_rows if r['subject_identity']['subject_kind']=='relation']
    require(len(nodes)==18 and len(edges)==12 and mapping['semantic_cursor']==mapping['governance_cursor']==30,'actual mapped closure differs')
    context=parse(family/'context/packages/0001/build-result.json')
    require(context['actual_generated_artifact_carriers']==35 and context['ontology_nodes']==18 and context['ontology_edges']==12,'actual Context closure differs')
    context_index=parse(family/'context/packages/0001/artifact-index.json')
    require(len(context_index)==35 and len({r['artifact']['version_ref'] for r in context_index})==35,'actual Context artifact inventory differs')
    generated=[]
    for row in context_index:
        raw=(ROOT/row['original_binding']['path']).read_bytes()
        require(sha(raw)==row['original_binding']['sha256']==row['artifact']['byte_sha256'],'actual Context original byte join differs')
        generated.append(json.loads(raw))
    require(sum(b['kind']=='ontology-node' for b in generated)==18 and sum(b['kind']=='ontology-edge' for b in generated)==12,'actual Context node/edge bodies differ')
    delivery=parse(family/'context/packages/0001/delivery.json')
    require(delivery['posture']=='ready' and delivery['source_cut']==mapping['source_cut'],'actual Context ready/source lineage differs')
    for role in ('mapped','context'):
        receipt=parse(HERE/'reports'/(family.name+'-'+role+'-attempt0002.json'))
        observed=receipt['observation'];manifest=family/role/'source-manifest.json';package=family/role/'packages/0001/manifest.json'
        require(receipt['result']=='PASS' and observed['package_binding']==m.binding(package),'actual role phase package binding differs')
        source_key='mapper_binding' if role=='mapped' else 'context_binding'
        require(observed[source_key]==m.binding(manifest),'actual role phase source binding differs')
        for row in parse(package)['files']:
            require(sha((ROOT/row['path']).read_bytes())==row['sha256'],'actual role package physical byte differs')
    diffs={kind:fields(normalized(oldby[kind],OLD),normalized(newby[kind],family)) for kind in ('intent','goal','work','context')}
    result={'schema_version':'lab-integrated-independent-cold-audit/v1-candidate','result':'PASS','family':family.relative_to(ROOT).as_posix(),'counts':counts,'mapper_nodes':len(nodes),'mapper_edges':len(edges),'semantic_governance_cursor':30,'Context_carriers':35,'retained_witnesses':retained_rows,'signed_baseline_input_bindings':[{'path':p,'sha256':d} for p,d in INPUT_PINS.items()],'semantic_substitutions':diffs,'new_distinct_Agent_Contract':contract['node_id'],'source_binding':m.binding(family/'source/source-manifest.json'),'fixture_only':True,'actual_owner_outcome':None,'authority_effect':'none','shared_API_qualified':False}
    destination=HERE/'reports'/(family.name+'-independent-closure-audit-0004.json');m.write(destination,result);print(json.dumps({'result':'PASS','counts':counts,'receipt':m.binding(destination)},sort_keys=True),flush=True)
if __name__=='__main__':main()
