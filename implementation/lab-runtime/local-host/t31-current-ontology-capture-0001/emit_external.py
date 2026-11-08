"""Generate a separately selected external host ontology capture component.

The selected API Source stays untouched. Only snapshot-capability origin
selection differs; all native hydration/body/stage/UTC checks remain original.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
BASE=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v75-current-fixtures-0001/workflow_ontology_outputs.py'
PIN='3c4daa9660888bb478d12ab9e1a931148eee327bb57a3b3cc880a9548561e416'
def transform(raw):
    if hashlib.sha256(raw).hexdigest()!=PIN:raise ValueError('exact selected ontology capture predecessor required')
    text=raw.decode()
    old='def __init__(self,host,capability,*,module,control_binding,route_rows,read_public,source_rows,carriers,guard):'
    new='def __init__(self,host,capability,*,module,control_binding,route_rows,read_public,source_rows,carriers,guard,external_selection):'
    if text.count(old)!=1:raise ValueError('exact capture constructor seam required')
    text=text.replace(old,new,1)
    old='        self.host=host;self.capability=capability;'
    new="        need(type(external_selection) is ExternalCapabilitySelection and external_selection.host is host, 'exact private external capability selection required')\n        self.external_selection=external_selection\n"+old
    if text.count(old)!=1:raise ValueError('exact private selection seam required')
    text=text.replace(old,new,1)
    old="selected_resolver(self.capability,{'resolver_binding':p['capability_binding'],'resolver_entrypoint':p['capability_entrypoint']},self.read_public,self.source_rows)"
    new="self.external_selection.guard(self.capability,{'resolver_binding':p['capability_binding'],'resolver_entrypoint':p['capability_entrypoint']})"
    if text.count(old)!=2:raise ValueError('both original capability effect boundaries required')
    text=text.replace(old,new)
    helper=(HERE/'external_capability.py').read_text()
    text=helper+'\n\n'+text
    compile(text,'external_ontology_capture.py','exec')
    return text.encode()
def emit(destination):
    destination=Path(destination);destination.mkdir(mode=0o700,parents=True,exist_ok=False)
    raw=transform(BASE.read_bytes());(destination/'external_ontology_capture.py').write_bytes(raw)
    receipt={'schema_version':'lab-external-ontology-capture-code/v1','predecessor':{'path':BASE.relative_to(ROOT).as_posix(),'sha256':PIN},
      'helper':{'path':str(HERE/'external_capability.py'),'sha256':hashlib.sha256((HERE/'external_capability.py').read_bytes()).hexdigest()},
      'external_capture_sha256':hashlib.sha256(raw).hexdigest(),'API_Source_or_wire_protocol_changed':False,
      'private_capability_origin_checks_changed':2,'rich_method_template_native_body_stage_and_UTC_checks_preserved':True,
      'actual_native_qualification':False,'authority_effect':'none'}
    (destination/'PINS.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');return receipt
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('destination');print(json.dumps(emit(parser.parse_args().destination),sort_keys=True))
