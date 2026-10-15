"""Original protocol and source closure audit; no API call or Agent created."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
sys.path.insert(0,str(HERE))
from fixtures import Fixture
sys.path.insert(0,str(HERE.parent/'api-v12'))
from protocol import Schemas


def main():
    checks=[]
    def check(value,name):
        if not value:raise ValueError(name)
        checks.append({'test':name,'result':'PASS'})
    for manifest in ['source-manifest.json','corrected-test-source-manifest.json','contract-audit-source-manifest.json']:
        for row in json.loads((HERE/manifest).read_bytes())['files']:
            p=ROOT/row['path'];check(p.is_file() and not p.is_symlink() and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],'exact selected source '+row['path'])
    schemas=Schemas('e1ea018567f49955ce14f756f83f156d4522599682742475c2a0ec5812c26e44');schemas.guard()
    check(importlib.metadata.version('jsonschema')=='4.23.0','selected R02 schema validator')
    with TemporaryDirectory(prefix='cal-R03-protocol-preflight-audit-') as tmp:
        root=Path(tmp);fixture=Fixture(root)
        for row in fixture.records:
            fixture.sources.get(row.artifact)
            check(schemas.protocol_valid('urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/artifact_ref',row.artifact),'actual original protocol artifact reference '+row.artifact['carrier_ref'])
        check(schemas.protocol_valid('urn:cyberalchemy-lab:protocol:context-query:v1-candidate',fixture.context()),'fixture context message satisfies original exact request contract')
        check(schemas.protocol_valid('urn:cyberalchemy-lab:protocol:agent-session-open:v1-candidate',fixture.open()),'fixture Session message satisfies original exact request contract')
        a=fixture.context_plan();b=fixture.open_plan()
        check(not a['Agent_created'] and not b['Session_created'] and not b['permission_result_is_dispatch_token'],'preflight is not active creation or permission token')
        check(a['authority_effect']==b['authority_effect']=='none','construction has no authority effect')
        check(all(p.stat().st_mode & 0o777==0o600 for p in root.iterdir()),'all selected original fixture files private mode')
    check(not root.exists(),'owned source fixture root removed')
    for manifest in ['source-manifest.json','corrected-test-source-manifest.json']:
        for row in json.loads((HERE/manifest).read_bytes())['files']:
            check(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source unchanged after conformance checks '+row['path'])
    value={'schema_version':'lab-session-preflight-contract-audit/v1-candidate','result':'PASS','checks':checks,'checks_count':len(checks),
        'authority_effect':'none','actual_owner_outcome':None,'public_API_calls_executed':0,'active_Agents_created':0,'human_pilot_outcome':None,
        'claim_ceiling':'Actual original carrier/control schema conformance and isolated source/participation preflight only. No actual fresh context delivery, Machine Agent creation or public API implementation is proved.'}
    dest=HERE/'receipts/contract-audit.json'
    if dest.exists():raise ValueError('audit receipt already exists')
    dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps({'result':'PASS','checks':len(checks)}),flush=True)

if __name__=='__main__':main()
