"""Compare the explicit string corpus with a reference; do not claim independent proof checking."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[9]
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def lit(v):return str(v).replace(' ','')
def retained_units(s):
    raw=s.encode('utf-16-le',errors='surrogatepass')
    return [int.from_bytes(raw[i:i+2],'little') for i in range(0,len(raw),2)]
def run():
    capture=json.loads((HERE/'source-capture.json').read_text());verification=json.loads((HERE/'verification.json').read_text())
    assert verification['result']=='candidate-fragment-pass'
    source=(HERE/'StringControls.lean').read_text();cases=[]
    def statement(name,function,input,result):
        text=f'theorem {name} : {function} {lit(input)} = {result} := by decide'
        assert text in source,name
        qualified='RelationalSuccessor.CandidateJsonStrings.Controls.'+name
        assert qualified in verification['new_declarations'];return qualified
    for row in capture['string_reference_cases']:
        assert row['scalar_input']==[ord(c) for c in row['source']]
        try:
            decoded=json.loads(row['source']);assert isinstance(decoded,str);actual=retained_units(decoded)
        except json.JSONDecodeError:actual=None
        assert actual==row['expected_units'],row['name']
        result='none' if actual is None else 'some '+lit(actual)
        cases.append(dict(row,actual_reference_units=actual,compiled_declaration=statement(row['name'],'decodeString',row['scalar_input'],result)))
    controls=[]
    for row in capture['scalar_only_controls']:
        controls.append(statement(row['name'],'decodeString',row['scalar_input'],'none'))
    for row in capture['quoted_prefix_controls']:
        result='none' if row['expected_units'] is None else 'some ('+lit(row['expected_units'])+','+lit(row['expected_remaining'])+')'
        controls.append(statement(row['name'],'decodeQuoted',row['input'],result))
    for row in capture['byte_controls']:
        try:
            decoded=json.loads(bytes(row['bytes']).decode('utf-8',errors='strict'));assert isinstance(decoded,str);actual=retained_units(decoded)
        except (json.JSONDecodeError,UnicodeDecodeError):actual=None
        assert actual==row['expected_units'],row['name']
        result='none' if actual is None else 'some '+lit(actual)
        controls.append(statement(row['name'],'decodeStringBytes',row['bytes'],result))
    assert len(cases)==36 and len(controls)==19 and capture['worked_control_declarations']==55
    report={'task':'N01','unit':'K02-json-strings','result':'JSON-string-reference-corpus-audit-pass','driver':binding(Path(__file__)),'verification':binding(HERE/'verification.json'),'source_capture':binding(HERE/'source-capture.json'),'controls':binding(HERE/'StringControls.lean'),'case_count':len(cases),'cases':cases,'additional_control_names':controls,'worked_proof_controls':55,'claim_scope':'36 explicit kernel-compiled JSON string cases match strict Python JSON decoding followed by retained UTF-16-unit conversion; two scalar-invalid, eight suffix and nine UTF-8 controls are explicitly bound to compiled declarations. Finite corpus comparison and same-kernel replay are not independent proof checking or standard-to-theory translation.','complete_JSON_parser_proved':False,'existing_scalar_AST_conversion_proved':False,'grammar_standard_translation_proved':False,'original_capture_to_AST_bridge_proved':False,'candidate_parser_profile_owner_accepted':False,'byte_parser_proved':False,'authenticated_capture_proved':False,'N03_schema_freeze':False,'independent_checker_run':False,'inherited_discharges':0,'authority_effect':'none'}
    (HERE/'JSON-string-reference-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('36 string reference cases and 19 additional controls passed.')
if __name__=='__main__':run()
