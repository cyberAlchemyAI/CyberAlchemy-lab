"""Bind exact authored rules, original schemas and qualified classification inputs."""
import ast
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]


def binding(path):
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    assert not (HERE/'source-manifest.json').exists()
    selected={}
    def add(path):
        row=binding(path);previous=selected.get(row['path'])
        assert previous in (None,row)
        selected[row['path']]=row
    for path in HERE.iterdir():
        if path.is_file():add(path)
        if path.suffix=='.py':ast.parse(path.read_bytes())
    schemas=[];kind_schemas={}
    for path in sorted((ROOT/'authority/artifact-types').glob('*/v*/schema.json')):
        value=json.loads(path.read_bytes());add(path)
        kind=value.get('properties',{}).get('kind',{}).get('const')
        if kind is None:
            # Legacy envelopes have other identities and are validated by the
            # host. They cannot be reinterpreted as node-based failure records.
            continue
        schemas.append(binding(path))
        carrier='cal.artifact-type.'+kind+'/'+path.parent.name
        assert carrier not in kind_schemas;kind_schemas[carrier]=value['$id']
    paths=[ROOT/'docs/proposals/0007-lab-integrated-schema-package/schemas/common.schema.json',
           ROOT/'docs/proposals/0007-lab-integrated-schema-package/schemas/failure-assessment-request.schema.json']
    paths+=list(HERE.glob('*.schema.json'))
    for path in paths:add(path);schemas.append(binding(path))
    add(ROOT/'docs/proposals/0008-lab-api-contracts/operations/failure.assess.json')
    add(ROOT/'docs/proposals/0007-lab-integrated-schema-package/examples/failure-assessment-request.json')
    for kind in ['implementation','failure-occurrence','failure-mode','classification-scheme',
                 'classification-value','classification-assignment','hypothesis','failure-assessment','evidence-set']:
        add(ROOT/'authority/artifact-types'/kind/'v1/fixtures/valid/record.json')
    classifier=HERE.parent/'classification-rules-v2'
    for row in json.loads((classifier/'source-manifest.json').read_bytes())['files']:
        assert binding(ROOT/row['path'])==row;add(ROOT/row['path'])
    add(classifier/'source-manifest.json');add(classifier/'receipts/proof-0001.json')
    value={'schema_version':'lab-failure-assessment-rule-source/v1-candidate','expected_tests':46,
        'files':sorted(selected.values(),key=lambda r:r['path']),'schemas':schemas,'kind_schemas':kind_schemas,
        'authority_effect':'none','actual_owner_outcome':None,'whole_API_qualified':False,'task_complete':False}
    with (HERE/'source-manifest.json').open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps({'source_binding':binding(HERE/'source-manifest.json'),'selected_files':len(selected),
                     'original_carrier_schemas':len(kind_schemas),'expected_tests':46,'authority_effect':'none'}),flush=True)


if __name__=='__main__':main()
