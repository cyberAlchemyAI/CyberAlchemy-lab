"""Independent exact-decimal corpus observations, not a proved translator or parser."""
from pathlib import Path
from decimal import Decimal
from jsonschema import Draft202012Validator
import json,hashlib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[9]

def binding(path):return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def reject_constant(value):raise ValueError(value)
def inspect(token):
    # This input is a number token, not an entire JSON document. Surrounding
    # document whitespace must not be counted as part of a valid token.
    if token != token.strip():return False,None
    try:value=json.loads(token,parse_float=Decimal,parse_int=int,parse_constant=reject_constant)
    except (ValueError,ArithmeticError):return False,None
    if not isinstance(value,(int,Decimal)) or isinstance(value,bool):return False,None
    numerator,denominator=Decimal(value).as_integer_ratio()
    epoch=numerator//denominator if numerator>=0 and numerator%denominator==0 else None
    return True,epoch

def run():
    corpus=json.loads((HERE/'numeric-corpus.json').read_text())
    rows=[]
    for case in corpus['cases']:
        syntax,epoch=inspect(case['token'])
        assert syntax==case['expected_JSON_number_syntax'],case
        if 'scope' not in case:assert epoch==case['expected_epoch'],case
        rows.append({'name':case['name'],'token':case['token'],'exact_reference_number_syntax':syntax,'exact_reference_epoch':epoch,'candidate_witness_expected_epoch':case['expected_epoch'],'witness_substitution_case':'scope' in case})
    schemas=[]
    for kind in ['resolution','role']:
        source=HERE.parent/'K02-pipeline/schemas'/f'{kind}-binding.schema.json'
        schema=json.loads(source.read_text())
        assert schema['$defs']['frame']['properties']['epoch']=={'type':'integer','minimum':0}
        schemas.append(binding(source))
    # A direct, observed translation hazard: default Python JSON decoding loses
    # a fractional residue before an integer schema validator sees the value.
    token='42.0000000000000001'
    ordinary=json.loads(token)
    validator=Draft202012Validator({'type':'integer','minimum':0})
    rounded_valid=validator.is_valid(ordinary)
    syntax,exact=inspect(token)
    assert syntax and exact is None and rounded_valid
    hazard={'token':token,'default_python_json_value':ordinary,'integer_schema_accepts_rounded_value':rounded_valid,'exact_reference_epoch':exact,'meaning':'The original token is fractional. A float conversion can hide this fact before schema validation. This is a concrete Python observation, not a theorem about every JSON library.'}
    report={'task':'N01','unit':'K02-numeric','result':'exact-decimal-corpus-reference-audit-pass','driver':binding(Path(__file__)),'corpus':binding(HERE/'numeric-corpus.json'),'sources':schemas,'cases':rows,'case_count':len(rows),'binary_float_translation_counterexample':hazard,'claim_scope':'Exact Decimal JSON observations for the explicit corpus and exact epoch schema shape. The Python reference/generator and schema interpreter are not formally proved. Wrong supplied witnesses are not a raw-token parser refusal.','raw_number_token_parser_proved':False,'byte_parser_proved':False,'schema_AST_correspondence_proved':False,'authenticated_capture_proved':False,'supported_resource_envelope_measured':False,'N03_schema_freeze':False,'inherited_discharges':0}
    (HERE/'numeric-reference-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'result':report['result'],'cases':len(rows),'float_translation_hazard_reproduced':True}))

if __name__=='__main__':run()
