"""Closed real nested Vault contract, no API construction."""
import copy,json,os
from pathlib import Path
from jsonschema import Draft202012Validator
import composite as C
import checks
from control import ROOT,compact,sha
HERE=Path(__file__).resolve().parent
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/revision-0002'
def main():
    root,config,_,_=checks.fixture();config['source']['bootstrap_bindings']=[config['provisioning_binding']]
    validator=Draft202012Validator(json.loads((HERE/'composite.config.schema.json').read_bytes()));validator.check_schema(validator.schema)
    validator.validate(config);C.config_shape(config);cases=[{'case':'v2 exact outer policy custody and original nested Vault is schema and semantic qualified','result':'PASS-contract-only'}]
    for label,mutate in [('v1 version',lambda v:v.update(schema_version='lab-composite-operator-config/v1-candidate')),('outer bootstrap manifest alias',lambda v:v['branches']['base'].update(files={'workspace.json':v['branches']['base']['files']['workspace/workspace.json']})),('missing exact Vault selector',lambda v:v['branches']['base'].pop('vault')),('unselected inner Vault root',lambda v:v['branches']['base']['vault'].update(root=str(root/'actions'))),('unknown issuer control',lambda v:v['handoff']['issuers']['grant'].update(actual_governing_authority=True))]:
        bad=copy.deepcopy(config);mutate(bad)
        try:C.config_shape(bad)
        except ValueError:pass
        else:raise AssertionError(label+' semantically accepted')
        # The root relation is a semantic constraint; JSON Schema rejects the
        # remaining closed shape/version mistakes independently.
        if label!='unselected inner Vault root':assert not validator.is_valid(bad)
        cases.append({'case':label+' refused by semantic contract','result':'PASS-refused'})
    out=RUN/'schema-evidence-0001.json';value={'schema_version':'lab-T06-schema-controls/v2-candidate','result':'PASS','cases':cases,'owned_root':str(root),'actual_full34_construction':False,'authority_effect':'none','task_complete':False}
    fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as s:s.write(json.dumps(value,indent=2,sort_keys=True).encode()+b'\n')
    print(json.dumps({'result':'PASS','cases':len(cases),'report':str(out)}))
if __name__=='__main__':main()
