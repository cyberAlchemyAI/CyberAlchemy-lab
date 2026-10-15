"""Check configuration shape only. It is not a byte/Nat decoder equivalence proof."""
from pathlib import Path
import copy,hashlib,json
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[9]
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def run():
    path=HERE/'resource-configuration.schema.json';schema=json.loads(path.read_text())
    Draft202012Validator.check_schema(schema);v=Draft202012Validator(schema)
    api=HERE/'candidate-api-contract.json'
    good={'captureLimits':{'perCaptureBytes':50000,'totalBytes':100000,'maxCaptures':100},'numericLimits':{'maxTokenCharacters':256,'maxMantissaDigits':128,'maxExponentDigits':4,'maxExponentMagnitude':1024}}
    cases=[('example-only',good,True),('zero-bounds',{'captureLimits':dict.fromkeys(good['captureLimits'],0),'numericLimits':dict.fromkeys(good['numericLimits'],0)},True)]
    for group in good:
        for field in good[group]:
            missing=copy.deepcopy(good);del missing[group][field];cases.append(('missing-'+field,missing,False))
            negative=copy.deepcopy(good);negative[group][field]=-1;cases.append(('negative-'+field,negative,False))
            string=copy.deepcopy(good);string[group][field]='1';cases.append(('string-'+field,string,False))
    extra=copy.deepcopy(good);extra['numericLimits']['extra']=1;cases.append(('extra-numeric-field',extra,False))
    top=copy.deepcopy(good);top['extra']=1;cases.append(('extra-top-field',top,False))
    checks=[]
    for name,value,expected in cases:
        actual=v.is_valid(value);assert actual==expected,name
        checks.append({'name':name,'input':value,'expected_valid':expected,'actual_valid':actual})
    report={'task':'N01','unit':'K02-evidence-resources','result':'candidate-schema-shape-audit-pass','driver':binding(Path(__file__)),'schema':binding(path),'api_contract':binding(api),'checks':checks,'byte_decoder_equivalence_proved':False,'JSON_schema_semantics_interpreter_proved':False,'measured_operational_policy':False,'inherited_discharges':0,'authority_effect':'none'}
    (HERE/'schema-shape-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Configuration shape checks:',len(checks))
if __name__=='__main__':run()
