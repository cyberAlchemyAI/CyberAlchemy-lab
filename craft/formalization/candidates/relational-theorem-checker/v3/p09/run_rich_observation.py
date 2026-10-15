"""Measure the retained richer source in combined layout under its unchanged policy."""
from pathlib import Path
import json
import sys
import uuid
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p03.context import C,binding,require
from v3.p09.api import Client

request=C.decode((BASE/'p01/request-fixture.json').read_bytes());request['layout']='combined'
data=(json.dumps(request,ensure_ascii=False,allow_nan=False)+'\n').encode();input_path=HERE/'rich-combined-request.json';input_path.write_bytes(data)
client=Client(request['resource_policy'],BASE/'p07/consumer-runs'/('P09-rich-combined-'+uuid.uuid4().hex))
answer=client.qualify(data);status=answer['status']
require(status in ['qualified-candidate','unknown-resource'],'Unexpected rich result: '+str(answer['diagnostic']))
if status=='qualified-candidate':
    require(client.live_event(answer),'successful rich invocation lost its event')
    require(answer['qualification']['qualified_result']['manifest']['obligations']==[o['id'] for o in C.required_inventory('rule-only')],'rich catalog shrink')
else:require(not client.live_event(answer) and not answer['qualification']['claims'],'rich exhaustion acquired claims')
output=HERE/'rich-combined-result.json';output.write_text(json.dumps(answer,indent=2)+'\n')
report={'result':'pass','input':binding(input_path),'output':binding(output),'source_fixture':binding(BASE/'p01/request-fixture.json'),
    'expected':'Fresh complete twenty-obligation qualification or explicit safe resource refusal under the unchanged policy',
    'observed':status,'actual_fresh_horn_qualifications':int(status=='qualified-candidate'),
    'scope':'One actual richer target/scope cyclic workload in combined layout. If exhausted, no proof completion or application capability is claimed; accepted P08 rich staged evidence remains separate.',
    'authority_effect':'none'}
(HERE/'rich-layout-observation.json').write_text(json.dumps(report,indent=2)+'\n');print('Rich combined observation:',status,flush=True)
