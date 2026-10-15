"""Audit explicit token corpus agreement; this is not independent proof checking."""
from pathlib import Path
import hashlib,json
from decimal import Decimal
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[9]
def b(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def lit(v):return str(v).replace(' ','')
def run():
    capture=json.loads((HERE/'source-capture.json').read_text());verification=json.loads((HERE/'verification.json').read_text())
    assert verification['result']=='candidate-fragment-pass'
    source=(HERE/'TokenControls.lean').read_text();cases=[];additional=[]
    def check(name,function,input,result,method='decide'):
        statement=f'theorem {name} : {function} {lit(input)} = {result} := by {method}'
        assert statement in source,name
        qualified='RelationalSuccessor.CandidateJsonTokens.Controls.'+name
        assert qualified in verification['new_declarations'];return qualified
    for row in capture['whole_number_reference_cases']:
        assert row['input']==[ord(c) for c in row['source']]
        try:
            parsed=json.loads(row['source'],parse_float=Decimal,parse_int=Decimal)
            valid=isinstance(parsed,Decimal) and row['source']==row['source'].strip(' \t\r\n')
        except (json.JSONDecodeError,ValueError):valid=False
        actual=row['source'] if valid else None
        assert actual==row['expected_token'],row['name']
        result='none' if actual is None else 'some '+json.dumps(actual)
        cases.append(dict(row,actual_reference_token=actual,compiled_declaration=check(row['name'],'decodeWholeNumber',row['input'],result)))
    for row in capture['number_prefix_controls']:
        result='none' if row['expected_token'] is None else 'some ('+json.dumps(row['expected_token'])+','+lit(row['expected_remaining'])+')'
        additional.append(check(row['name'],'decodeNumber',row['input'],result))
    for row in capture['literal_prefix_controls']:
        result='none' if row['expected_value'] is None else 'some ('+row['expected_value']+','+lit(row['expected_remaining'])+')'
        additional.append(check(row['name'],'decodeLiteral',row['input'],result,'rfl'))
    for row in capture['whitespace_controls']:
        additional.append(check(row['name'],'scanWhitespace',row['input'],'('+lit(row['word'])+','+lit(row['remaining'])+')'))
    assert len(cases)==38 and len(additional)==25 and capture['worked_control_declarations']==63
    report={'task':'N01','unit':'K02-json-tokens','result':'JSON-token-reference-corpus-audit-pass','driver':b(Path(__file__)),'verification':b(HERE/'verification.json'),'source_capture':b(HERE/'source-capture.json'),'controls':b(HERE/'TokenControls.lean'),'case_count':len(cases),'cases':cases,'additional_control_names':additional,'worked_proof_controls':63,'claim_scope':'38 explicit kernel-compiled whole-number cases agree with strict Python JSON numeric recognition using Decimal while forbidding surrounding token whitespace and preserving exact spelling. 25 additional number-prefix/literal/whitespace controls are bound to exact compiled declarations. Finite corpus agreement and same-kernel replay do not prove RFC translation or independent proof checking.','complete_JSON_parser_proved':False,'existing_scalar_AST_conversion_proved':False,'grammar_standard_translation_proved':False,'original_capture_to_AST_bridge_proved':False,'candidate_parser_profile_owner_accepted':False,'byte_parser_proved':False,'authenticated_capture_proved':False,'N03_schema_freeze':False,'independent_checker_run':False,'inherited_discharges':0,'authority_effect':'none'}
    (HERE/'JSON-token-reference-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('38 number reference cases and 25 additional controls passed.')
if __name__=='__main__':run()
