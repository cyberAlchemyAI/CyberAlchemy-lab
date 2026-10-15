"""Check the explicit raw-number corpus against an exact Decimal reference."""
from pathlib import Path
from decimal import Decimal
import hashlib,json,re
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[9]
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def reject(value):raise ValueError(value)
def reference(token):
    if token!=token.strip():return False,None
    try:value=json.loads(token,parse_float=Decimal,parse_int=int,parse_constant=reject)
    except (ValueError,ArithmeticError):return False,None
    if isinstance(value,bool) or not isinstance(value,(int,Decimal)):return False,None
    n,d=Decimal(value).as_integer_ratio()
    return True,n//d if n>=0 and n%d==0 else None

def run():
    corpus=json.loads((HERE/'number-parser-corpus.json').read_text())
    cases=[]
    for case in corpus['cases']:
        syntax,epoch=reference(case['token'])
        assert epoch==case['expected_epoch'],case
        cases.append(dict(case,exact_reference_number_syntax=syntax,exact_reference_epoch=epoch))
    controls=(HERE/'NumberParserControls.lean').read_text()
    assert len(re.findall(r'^theorem ',controls,re.M))==corpus['worked_proof_controls']==53
    assert len(cases)==corpus['case_count']==46
    schemas=[]
    for kind in ['resolution','role']:
        source=HERE.parent/'K02-pipeline/schemas'/f'{kind}-binding.schema.json'
        d=json.loads(source.read_text());assert d['$defs']['frame']['properties']['epoch']=={'type':'integer','minimum':0}
        schemas.append(binding(source))
    result={'task':'N01','unit':'K02-number-parser','result':'exact-raw-number-corpus-audit-pass','driver':binding(Path(__file__)),'corpus':binding(HERE/'number-parser-corpus.json'),'schemas':schemas,'case_count':len(cases),'worked_proof_controls':53,'cases':cases,'claim_scope':'Exact Decimal observations for the explicit raw-token corpus and epoch subschema source shape. The reference/generator and a full JSON Schema interpreter/byte bridge are not proved.','byte_parser_proved':False,'schema_AST_correspondence_proved':False,'JSON_schema_semantics_interpreter_proved':False,'authenticated_capture_proved':False,'supported_resource_envelope_measured':False,'N03_schema_freeze':False,'inherited_discharges':0}
    (HERE/'raw-number-reference-audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'result':result['result'],'cases':len(cases),'worked_proof_controls':53}))
if __name__=='__main__':run()
