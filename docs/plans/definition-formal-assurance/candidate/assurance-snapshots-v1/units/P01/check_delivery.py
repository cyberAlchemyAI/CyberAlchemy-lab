"""Read-only verification of this stage's bytes, input bindings and boundary."""
import json
import hashlib
from pathlib import Path
import select_profile as s

ROOT=s.ROOT
BASE=ROOT/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1'
UNIT=Path(__file__).resolve().parent


def verify_file(row):
    actual=hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()
    if actual!=row['sha256']:raise ValueError('stale-bound-file: '+row['path'])


def main():
    manifests=[BASE/'units/A04/delivery-manifest.json',BASE/'units/C01/delivery-manifest.json',UNIT/'delivery-manifest.json']
    counts={}
    for path in manifests:
        manifest=json.loads(path.read_text());files=manifest['files']
        if len({row['path'] for row in files})!=len(files):raise ValueError('duplicate-delivery-path')
        for row in files:verify_file(row)
        counts[str(path.relative_to(ROOT))]=len(files)
    for unit in ['C02','C03','P01']:
        receipt=json.loads((BASE/f'units/{unit}/receipt.json').read_text())
        for row in receipt['inputs']+receipt['outputs']:verify_file(row)
        if receipt['authority_effect']!='none' or receipt['goal_status']!='active':raise ValueError('incorrect-candidate-receipt-boundary')
    snapshot=json.loads((BASE/'current-snapshot.json').read_text());source=s.r.verify(snapshot,ROOT)
    inventory=json.loads((BASE/'tooling-assessment.json').read_text());s.validate_policy(s.load_policy());s.verify_inventory(inventory)
    import dependencies as d
    actual=json.loads((BASE/'units/C03/current-graph-boundary.json').read_text())
    roots=[d.source_ref(row) for row in snapshot['current_entries']]
    packets=[json.loads((BASE/'units/A04/hypothesis-review-packet.json').read_text())]
    d.verify_graph(actual,snapshot,roots,packets)
    if len(actual['nodes'])!=183 or actual['edges'] or len(actual['missing_or_quarantined_interpretations'])!=182 or actual['semantic_ready']:raise ValueError('incorrect-current-graph-boundary')
    print(json.dumps({'result':'PASS','delivery_manifests':counts,'source_capture':source,'new_tests':51,'current_graph_nodes':183,'missing_graph_packets':182,'authority_effect':'none','full_project_completion':'not-established'},indent=2,sort_keys=True))


if __name__=='__main__':main()
