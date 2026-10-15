"""Inspect every original carrier selector; never construct synthetic Artifacts."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[6]
COMPONENT=ROOT/'product/lab/release-candidates/v1/interface/release-proof-inputs-v2-completion-0001'
sys.path.insert(0,str(COMPONENT))
import test_inputs as T

def main():
    rows=[]
    with tempfile.TemporaryDirectory(prefix='owned-graph-inventory-',dir=RUN) as scratch:
        f=T.VariedFixture(Path(scratch))
        for c in f.registry['admitted_contracts']:f.document(c['schema_path'])
        reader=f.reader(seconds=600)
        with reader.boundary():
            schemas=T.G.Schemas(reader,f.schema_rows)
            for i,c in enumerate(f.registry['admitted_contracts']):
                captured=next(r for r in f.catalog['rows']if r['represented_contract_ref']==c['artifact_type_ref'])
                row={'carrier_ref':c['artifact_type_ref'],'registry_pointer':'/admitted_contracts/'+str(i),
                    'lifecycle_state':c['lifecycle_state'],'descriptor_path':c['artifact_path'],
                    'descriptor_sha256':c['artifact_sha256'],'descriptor_pointer':captured['selector'],
                    'schema_path':c['schema_path'],'schema_sha256':c['schema_sha256'],
                    'instance_schema_selector':c['schema_selector'],'representation_kind':captured['representation_kind']}
                try:
                    slots=schemas.slots(c['schema_path'],c['schema_selector'])
                    row.update(status='EXACT-SCHEMA-SLOTS',slots={k:[list(loc)for loc in v]for k,v in slots.items()})
                except T.P.Refusal as exc:row.update(status='UNSUPPORTED-SCHEMA-SELECTOR',reason=str(exc))
                rows.append(row)
    report={'schema_version':'lab-original-carrier-selector-inventory/v1',
        'registry_sha256':hashlib.sha256((ROOT/T.REGISTRY).read_bytes()).hexdigest(),
        'catalog_sha256':hashlib.sha256((ROOT/T.CATALOG).read_bytes()).hexdigest(),
        'component_sha256':hashlib.sha256((COMPONENT/'semantic_graph.py').read_bytes()).hexdigest(),
        'rows':rows,'total':len(rows),'supported_schema_selectors':sum(r['status']=='EXACT-SCHEMA-SLOTS'for r in rows),
        'actual_instance_graph_qualification':False,'authority_effect':'none','owned_scratch_cleaned':not Path(scratch).exists()}
    target=RUN/'carrier-profile-inventory.json'
    if target.exists():raise RuntimeError('inventory evidence already exists')
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k!='rows'}))
    return 0 if all(r['status']=='EXACT-SCHEMA-SLOTS'for r in rows)else 1

if __name__=='__main__':sys.exit(main())
