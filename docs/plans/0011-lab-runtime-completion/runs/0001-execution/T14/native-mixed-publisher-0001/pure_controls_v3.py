"""Final mixed-scope typed-original metadata and hard origin refusal controls."""
import json,types
from .pure_controls_v2 import main as prior
from . import contracts as C
from .origins import require_original
from .ontology_static_controls import main as ontology_static

def main():
    result=prior();roles=['decision','decision-bundle','decision-checkpoint','admission-transaction','project-state','project-semantic-event-history','project-governance-event-history']
    files={'validation/context.json':b'{}','targets/fixture.json':C.compact({'kind':'work','node_id':'fixture:work','scope_ref':'fixture:original-body-scope'})}
    for role in roles:files['instances/'+role+'.json']=C.compact({'kind':role,'node_id':'fixture:'+role,'scope_ref':'fixture:container'})
    review={'bundle_id':'fixture-owned','authority':{'scope_ref':'fixture:container'},'targets':[{'record_path':'targets/fixture.json','identity':'fixture:work','version_ref':'fixture:work@1','carrier_ref':'fixture:work-carrier','kind':'work'}]}
    original=types.SimpleNamespace(loads=json.loads,_carrier=lambda context,kind:'fixture:carrier:'+kind)
    records=C.typed_records(files,{},review,original);target=next(r for r in records if r['original_path']=='targets/fixture.json')
    assert target['artifact']['scope_ref']=='fixture:container'and target['artifact']['byte_sha256']==C.sha(files['targets/fixture.json'])
    assert json.loads(files['targets/fixture.json'])['scope_ref']=='fixture:original-body-scope'
    result['checks'].append('interchange container scope preserves distinct original target-body scope and exact bytes')
    try:require_original(types.SimpleNamespace(expected=[]),types.SimpleNamespace(__file__='/unselected/owned-fixture.py'),'repository-publisher')
    except C.Refusal:pass
    else:raise AssertionError('foreign original producer origin accepted')
    result['checks'].append('authoritative producer role cannot be assigned to arbitrary selected fixture origin')
    static=ontology_static();result['checks'].extend(static['checks']);result['count']=len(result['checks']);return result
