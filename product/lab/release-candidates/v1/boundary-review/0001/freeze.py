"""Freeze R06 partial inspection sources and all retained upstream evidence."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent;ROOT = HERE.parents[5]
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'


def bind(path):
    return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')


def main():
    out=HERE/'source-manifest.json';assert not out.exists()
    rows={}
    def add(row):
        row={'path':row['path'],'sha256':row['sha256']}
        assert rows.get(row['path'],row)==row and bind(ROOT/row['path'])==row,row['path']
        rows[row['path']]=row
    parents=[RUN/'R01-design-evidence.json',
       ROOT/'product/lab/release-candidates/v1/packaging/R02/close/receipts/0001.json',
       ROOT/'implementation/lab-ontology/candidates/v1/currentness/successors/0001/receipts/O04-0002.json']
    for path in parents:
        value=json.loads(path.read_bytes());assert value['result']=='PASS'
        for row in value['files']:add(row)
        add(bind(path))
    for path in [RUN/'authorization.json',ROOT/'docs/plans/0009-lab-integrated-roadmap/work-pack/tasks/R06.md',
       ROOT/'product/lab/release-candidates/v1/interface/current-participation-v3/packages/0001/branch.snapshot',
       ROOT/'product/lab/release-candidates/v1/interface/current-participation-v3/packages/0001/manifest.json',
       ROOT/'implementation/lab-ontology/candidates/v1/migration/source-selection.json',ROOT/'.gitignore']:
        add(bind(path))
    context=RUN/'context-R06-boundary-0001.json';c=json.loads(context.read_bytes())
    assert c['strict_coverage']=='PASS' and c['blockers']==[]
    for row in c['source_bindings']:add(row)
    add(bind(context))
    for path in HERE.glob('*.py'):ast.parse(path.read_bytes());add(bind(path))
    put(out,{'schema_version':'lab-R06-boundary-source/v1-candidate','files':[rows[k] for k in sorted(rows)],
       'upstream_receipt_bindings':[bind(p) for p in parents],
       'context_binding':bind(context),
       'scope':'Original R06 partial: exact current R02 code/control/dependencies, protected Source3 provenance and all140private migration items; complete integrated final selection remains required.',
       'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,
       'frozen_before_boundary_checks_or_inventory_outputs':True})
    print(json.dumps({'result':'FROZEN','files':len(rows),'source_binding':bind(out)}),flush=True)


if __name__ == '__main__':main()
