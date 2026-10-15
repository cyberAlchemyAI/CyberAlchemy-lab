import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
CAPTURE=RUN/'T07/api17-task-local-capture-0005'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bind=lambda p:{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
packet_path=RUN/'T00/final-capture5-input-packet-0001.json'
assert sha(packet_path)=='34fb89f5ad60406814546b55fb25a14fb6eda520e0466c85afd92b59a36e0829'
packet=json.loads(packet_path.read_bytes())
peer_path=RUN/'T07/final-capture5-inputs-independent-review-0001/independent-review-0001.json'
assert sha(peer_path)=='89abc1361d5650888976d67c4a202a860c8278f7fe168e44c346d89487be6958'
peer=json.loads(peer_path.read_bytes())
assert peer['result']=='PASS' and peer['findings']==[] and peer['authority_effect']=='none'
assert peer['reviewed_root_packet_binding']==bind(packet_path)
wrapper={'schema_version':'lab-T00-capture5-inputs-peer/v1-candidate','result':'PASS','authority_effect':'none','reviewed_root_packet_binding':bind(packet_path),'review_binding':bind(peer_path),'limitations':peer['limitations']}
Draft202012Validator(json.loads((CAPTURE/'root-peer-wrapper.schema.json').read_bytes())).validate(wrapper)
wrapper_path=RUN/'T00/final-capture5-peer-wrapper-0001.json'
with wrapper_path.open('x') as f:f.write(json.dumps(wrapper,sort_keys=True,indent=2)+'\n')
selection=json.loads((CAPTURE/'component-selection-draft.json').read_bytes())
assert selection['inputs'] is None and selection['final_root_packet_binding'] is None and selection['final_peer_review_binding'] is None
selection.update(status='closed-for-Root-capture',inputs=packet['inputs'],final_root_packet_binding=bind(packet_path),final_peer_review_binding=bind(wrapper_path))
Draft202012Validator(json.loads((CAPTURE/'selection.schema.json').read_bytes())).validate(selection)
target=CAPTURE/'final-component-selection-0001.json'
with target.open('x') as f:f.write(json.dumps(selection,sort_keys=True,indent=2)+'\n')
assert not (CAPTURE/'capture-result.json').exists()
print(json.dumps({'wrapper_binding':bind(wrapper_path),'selection_binding':bind(target),'writer_imported_or_executed':False}))
