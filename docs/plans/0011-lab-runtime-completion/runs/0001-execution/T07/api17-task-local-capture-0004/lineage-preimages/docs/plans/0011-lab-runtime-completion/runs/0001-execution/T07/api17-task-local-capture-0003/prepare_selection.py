"""Author complete independent expectations; no API/runtime mutation."""
import copy,hashlib,json
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
HERE=RUN/'T07/api17-task-local-capture-0003'
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(path,pin=None):
    path=Path(path);path=path if path.is_absolute() else ROOT/path
    assert path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents)
    raw=path.read_bytes();assert pin is None or sha(raw)==pin,str(path)
    return {'path':str(path.relative_to(ROOT)),'sha256':sha(raw)}
def load(path,pin):
    row=bind(path,pin);return json.loads((ROOT/row['path']).read_bytes())
draft=load(HERE/'component-selection-DRAFT.json','7c2bcdb45babf7ef7abf89f68693f276c9e5cc7dd76a2aeba4f12ab2a530280a')
pre=load(HERE/'preimage/source-manifest.json','a909f378b8a1c5f6f02fe6bcbafa56da7f2fe873a3865ab7853b443d57b249f2')
prior={row['path']:row for row in pre['files']}
patch=load(RUN/'T02/current-selector-staging-0002/patch-ledger.json','c63786e305d4e3edacb49bbd72882bec861b278428a43a2379dd3508db2a68cb')
assert len(patch['rows'])==4 and patch['actual_API_modified'] is False
changes={row['target']:row for row in patch['rows']};assert len(changes)==4
selection=copy.deepcopy(draft)
selection['schema_version']='lab-root-current-component-selection/v3-candidate'
selection.pop('draft_only');selection.pop('pending_family_selection')
selection['claim_ceiling']='Exact owned current-family diagnostic execution input selection only. Source/profile digests follow independent capture. Failed first family and older SDK/startup evidence are provenance; no whole API, historical physical closure, margin, owner, publication or final qualification.'
selection['selected_at']='2026-10-14; actual final owned selection after completed native family'
selection['api_expected_files']=[]
for path in sorted(API.rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts or 'receipts' in path.parts:continue
    if path.name in ('source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json','INPUT-ACCOUNTING.json'):continue
    name=str(path.relative_to(ROOT));assert name in prior,'unselected prior API origin '+name
    bind(path,prior[name]['sha256'])
    if name in changes:
        row=changes[name];assert bind(ROOT/row['preimage']['path'],prior[name]['sha256'])==row['preimage']
        bind(ROOT/row['postimage']['path'],row['postimage']['sha256'])
        selection['api_expected_files'].append({'path':name,'sha256':row['postimage']['sha256']})
    else:selection['api_expected_files'].append(prior[name])
selection['helper_expected_files']=[]
for folder in ['machine-context-scope-v2-completion-0001','lesson-host-composition-v46-completion-0001','lesson-application-v4-completion-0001']:
    for path in sorted((API.parent/folder).rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts:
            name=str(path.relative_to(ROOT));assert name in prior;selection['helper_expected_files'].append(bind(path,prior[name]['sha256']))
assert len(selection['helper_expected_files'])==7
family=RUN/'T02/optimized-family-preparation-0002'
selection['current_family_selections'].append(bind(family/'instances/optimized-0002/runtime/runtime-selection.json','6004ecf7533954ee180f87186f46339b4e66a9c816252c40edf6ed2f98ea13bd'))
selection['component_manifests'].append({'base':'.',**bind(family/'recipe-selection.json','54134cd404171931986b92651f534099f1652c7680b899804393b96605538eff')})
old_stager=str((RUN/'T02/prepare-current-selectors-0002.py').relative_to(ROOT))
for row in selection['direct_inputs']:
    if row['path']==old_stager:
        row.update(bind(RUN/'T02/prepare-current-selectors-0002-preimage-0001.py','2bba815db6232a71c4f431b3ebcc4fd41f7104a38cb5327752dd2ee39397a853'))
direct={row['path']:row for row in selection['direct_inputs']}
def add(path,pin=None):
    row=bind(path,pin);assert direct.get(row['path'],row)==row;direct[row['path']]=row
add(RUN/'T02/prepare-current-selectors-0002.py','05556b7b82b8480eb248de9b81772b2ede44733a814f1db8af9bcb506e92c5c8')
add(RUN/'T35/prepare-full-learning-inputs-0001.py','2934c6de5b0db15899142eb7a82a89ae30428b4c7841e397e11bcbcbd1d8564a')
add(RUN/'T35/full-learning-inputs-0001/selection.json','d1a1569c7e290d51f6c47cfecb611fa01b58d49599926558de887657b00f53aa')
add(RUN/'T35/input-preparation-independent-review-0001/independent-review.json','c000a0fb67be3cd00469f5947bc778babf2284ff6d68bbc8074b676873acd001')
add(family/'reports/observer-0001/actual_attempt.py','9f747d34ae85af09c5094dfc98f5a4774bd7c4d13683caca776665daed968082')
add(family/'reports/observer-0001/authentication_verify.py')
add(family/'root-family-acceptance-0001.json')
add(family/'reports/observer-0001/actual-terminal.json','b73fb10b9371cbf648cdb28be6fa54356ea476b8e1dac41a7aea1d183aa02c05')
add(family/'reports/observer-0001/final-verification.json','d0aea7b30a387ef629ded04ee02eeecdc528cef43c4586468d61ddc89f00c865')
add(RUN/'T03/optimized-capture-selection-0002.json','295ff7139c855749a20083394ea013f3b6e7e6efd7812563e1e4daeddcf18fe9')
add(RUN/'T03/context-parser-correction-0002/HANDOFF.json','0d3c6a01d8fbb3e1f5884d866b2b89e34dc7c437c6502781adede9fc053ab92d')
for row in patch['rows']:
    add(ROOT/row['preimage']['path'],row['preimage']['sha256']);add(ROOT/row['postimage']['path'],row['postimage']['sha256'])
add(RUN/'T02/current-selector-staging-0002/patch-ledger.json','c63786e305d4e3edacb49bbd72882bec861b278428a43a2379dd3508db2a68cb')
add(RUN/'T02/current-selector-staging-0002/independent-review-0001/independent-review.json','9a252c838e740b61c75fbf93947971c4470e1e99e7104f65a21d81ef12a3ec9f')
add(RUN/'T07/capture3-independent-preparation-review-0001/independent-review-0002.json','75d7eee74375b905888c6a639e054472e1595dc2cf1d0428757336f89fa6aebf')
add(HERE/'prepare_selection.py')
selection['direct_inputs']=[direct[path] for path in sorted(direct)]
for row in selection['direct_inputs']:bind(ROOT/row['path'],row['sha256'])
for component in selection['component_manifests']:bind(ROOT/component['path'],component['sha256'])
for row in selection['current_family_selections']:bind(ROOT/row['path'],row['sha256'])
selection['superseded_template_metadata_basis']={'descriptor_binding':selection['current_family_selections'][-1],'patch_ledger_binding':bind(RUN/'T02/current-selector-staging-0002/patch-ledger.json'),'scope':'New descriptor original_templates are immutable authoring provenance. Exact old API template bytes retained at their explicit preimage files; they confer no old code execution eligibility or qualification.'}
with (HERE/'component-selection.json').open('x') as f:json.dump(selection,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'selection_binding':bind(HERE/'component-selection.json'),'API_expected_files':len(selection['api_expected_files']),'helper_expected_files':len(selection['helper_expected_files']),'complete_family_selections':len(selection['current_family_selections']),'components':len(selection['component_manifests']),'direct_inputs':len(selection['direct_inputs']),'actual_API_modified':False,'runtime_started':False,'authority_effect':'none'}))
