"""Read-only supplemental final Root-packet review; capture writer unexecuted."""
import ast,copy,hashlib,json,os,sys
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
PROP=RUN/'T07/final-capture5-inputs-proposal-0001'
CAP5=RUN/'T07/api17-task-local-capture-0005'
CAP4=RUN/'T07/api17-task-local-capture-0004'
INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
assert Path(sys.executable)==INSTALL/'bin/python'
sys.path.insert(0,str(INSTALL/'deps'))
import jsonschema
sha=lambda x:hashlib.sha256(x).hexdigest()
held={}
def read(p,pin):
    raw=p.read_bytes();assert sha(raw)==pin,str(p);held[str(p)]=pin;return raw
def load(p,pin):return json.loads(read(p,pin))
def bload(r):return load(ROOT/r['path'],r['sha256'])
fd0=len(os.listdir('/proc/self/fd'))
hh=load(PROP/'HANDOFF.json','dce6d5be23dbc4b32e844468ec53c5f16c6427800f9eed607e4cdde1fa7f6007')
mf=load(PROP/'source-manifest.json','e0628f63fae23904ef622260496a41f7dbdc9a2f6b94afeb09158fb665704508')
assert len(mf['files'])==3898
for r in mf['files']:assert len(read(ROOT/r['path'],r['sha256']))==r['size_bytes']
inp=bload(hh['inputs_binding']);template=bload(hh['Root_packet_template'])
packetbinding=dict(path='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T00/final-capture5-input-packet-0001.json',sha256='34fb89f5ad60406814546b55fb25a14fb6eda520e0466c85afd92b59a36e0829')
packet=bload(packetbinding)
expected=copy.deepcopy(template);expected['status']='Root-reviewed-merged-native-family5-ready-for-capture'
assert packet==expected and packet['inputs']==inp
rootreview=load(RUN/'T00/final-capture5-input-root-review-0001.json','785f753b39ed0228d440861bd654c77e9f72e8e9cf82c82b2a198d66b5939250')
assert rootreview['authority_effect']=='none'
schema=json.loads((CAP5/'root-input-packet.schema.json').read_bytes())
jsonschema.Draft202012Validator.check_schema(schema);validator=jsonschema.Draft202012Validator(schema);validator.validate(packet)
draft=bload(hh['selection_draft']);jsonschema.Draft202012Validator(json.loads((CAP5/'selection.schema.json').read_bytes())).validate(draft)
assert draft['inputs'] is None and draft['final_root_packet_binding'] is None and draft['final_peer_review_binding'] is None
assert list(validator.iter_errors(template))
assert list(jsonschema.Draft202012Validator(json.loads((CAP5/'root-peer-wrapper.schema.json').read_bytes())).iter_errors(bload(hh['peer_template'])))
writer=read(CAP5/'capture_v5.py','488db1f09b24e987035a5c249104972bb18ef7a618d6e593f17305695cb6e7ef')
t=ast.parse(writer,filename=str(CAP5/'capture_v5.py'))
literals={n.targets[0].id:ast.literal_eval(n.value) for n in t.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ['REQUIRED_PREPARATION_BINDINGS','ROLE_TARGETS']}
direct={r['path']:r['sha256'] for r in inp['direct_inputs']}
components={r['path']:r['sha256'] for r in inp['component_manifests']}
for r in literals['REQUIRED_PREPARATION_BINDINGS'].values():assert direct[r['path']]==r['sha256']
for k in ['recipe5_manifest','parent_capture4_manifest','input_preparer4_manifest','instrumentation_manifest']:
    r=literals['REQUIRED_PREPARATION_BINDINGS'][k];assert components[r['path']]==r['sha256']
assert set(inp['active_family']['family_bindings'])==set(literals['ROLE_TARGETS'])
lineage=bload(draft['lineage_binding'])
original=json.loads((CAP4/'lineage-preimages'/lineage['capture3_selection_binding']['path']).read_bytes())
known={r['path']:r for r in original['api_expected_files']}
overlay=bload(draft['known_overlay_receipt_binding'])
known.update({r['path']:r for r in overlay['actual_target_bindings']})
assert len(known)==165 and known=={r['path']:r for r in draft['known_api_expected_files']}
selector=load(RUN/'T02/selector-merge-0005/application-receipt.json','71877e214513ea86b1d963d5e48c2fb49577172ec37a1ececef19688948308f0')
assert selector['changed_files']==4 and selector['unchanged_files']==1
known.update({r['actual']['path']:r['actual'] for r in selector['rows']})
assert known=={r['path']:r for r in inp['api_expected_files']}
assert len(packet['merged_receipt_bindings'])==10
for r in packet['merged_receipt_bindings']:bload(r)
public=bload(hh['T35_public_requirements_binding'])
def flatten(v):
    if isinstance(v,dict):
        if set(v)=={'path','sha256'}:yield v
        else:
            for x in v.values():yield from flatten(x)
    elif isinstance(v,list):
        for x in v:yield from flatten(x)
requirements={r['path']:r for r in flatten(public)};assert len(requirements)==34
for p,r in requirements.items():assert direct[p]==r['sha256']
for p,pin in held.items():assert sha(Path(p).read_bytes())==pin
assert len(os.listdir('/proc/self/fd'))==fd0
report=dict(result='PASS-independent-exact-actual-Root-packet',reviewed_root_packet_binding=packetbinding,reviewed_Root_own_review_sha256='785f753b39ed0228d440861bd654c77e9f72e8e9cf82c82b2a198d66b5939250',proposal_handoff_sha256='dce6d5be23dbc4b32e844468ec53c5f16c6427800f9eed607e4cdde1fa7f6007',proposal_manifest_sha256='e0628f63fae23904ef622260496a41f7dbdc9a2f6b94afeb09158fb665704508',proposal_audit_rows=3898,inputs_sha256=hh['inputs_binding']['sha256'],Root_packet_only_semantic_delta='status Root-reviewed-merged-native-family5-ready-for-capture',schema_valid_actual_packet=True,draft_valid_and_inactive=True,Root_and_peer_unresolved_templates_refuse=True,known165_exact_declared160_margin8_selector4_derivation=True,all_required_preparations_and_T35_public34_selected=True,actualmerged_receipts=10,FD_delta=0,writer_imported_or_executed=False,shared_mutation=False,authority_effect='none',task_complete=False)
with (Path(__file__).parent/'actual-root-packet-controls-0001.json').open('x') as f:f.write(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps(report,sort_keys=True))
