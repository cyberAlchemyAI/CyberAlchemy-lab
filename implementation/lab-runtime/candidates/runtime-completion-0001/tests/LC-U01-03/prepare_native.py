"""Materialize the native policy core for actual independent interpretation review."""
import argparse
import json
from pathlib import Path
import sys
S=Path(__file__).absolute().parents[2];R=S.parents[3]
DEPS=R/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/deps'
sys.path[:0]=[str(S/'contracts'),str(S/'selectors'),str(S/'evidence_index'),str(DEPS)]
from lab_contracts.codec import canonical,sha
from lab_selectors.anchors import RootAnchor,AnchoredReader,identity
from lab_evidence.inventory import build
from lab_evidence.history import historical
from lab_evidence.native_policy import proposal

def bound(path):
    raw=path.read_bytes()
    return {'kind':'execution','root_id':'repo','relative_path':str(path.relative_to(R)),
            'sha256':sha(raw),'size_bytes':len(raw)}

parser=argparse.ArgumentParser();parser.add_argument('--temp-root',required=True)
args=parser.parse_args();U=Path(args.temp_root)
expected=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U01-03'
if U!=expected:raise ValueError('OWNED_UNIT_ROOT')
selection=bound(S/'evidence_index/original-inventory-selection.json')
history=bound(S/'evidence_index/historical-selection.json')
documents=json.loads((R/selection['relative_path']).read_bytes())['documents']
historical_documents=json.loads((R/history['relative_path']).read_bytes())['documents']
A=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/acceleration-audit-20261018'
mapping=[bound(A/'implementation-plan-0001/manifest.json'),
         bound(A/'design-audit-0001/CONTRACTS.md'),
         bound(A/'design-audit-0001/RESOLVED-CONTRACTS.md'),
         bound(A/'design-audit-0001/workflow-proof-stages.json'),
         bound(R/'docs/plans/0011-lab-runtime-completion/analysis/qualification-release.md')]
bindings=[selection,history,*mapping]+[d['binding'] for d in documents+historical_documents]
bindings=list({canonical(b):b for b in bindings}.values())
reader=AnchoredReader([RootAnchor('repo',str(R),identity(R.stat()))],bindings)
inventory=build(reader,selection)
cross=json.loads((A/'implementation-plan-0001/original-crosswalk.json').read_bytes())
manifest=json.loads(reader.read(mapping[0]))
core,source_map,accounting=proposal(inventory,mapping,cross['task_to_units'],
    {u['id']:u['external_gates'] for u in manifest['units']})
history_result=historical(reader,history)
artifacts={'native-policy-core-0005.json':core,'native-policy-source-map-0005.json':source_map,
           'native-policy-accounting-0005.json':accounting,'native-inventory-0005.json':inventory.view(),
           'native-historical-0005.json':history_result.projection}
print(json.dumps({'artifact_sizes':{name:len(canonical(value)) for name,value in artifacts.items()},
                  'accounting':accounting}),file=sys.stderr)
for name,value in artifacts.items():
    raw=canonical(value)
    with (U/name).open('xb') as f:f.write(raw)
summary={name:{'sha256':sha(canonical(value)),'size_bytes':len(canonical(value))} for name,value in artifacts.items()}
with (U/'native-core-postimage-0005.json').open('x') as f:json.dump(summary,f,indent=2);f.write('\n')
print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS','checks':5,
                  'effect_state':'owned-inert','cleanup':'retained-owned'}))
