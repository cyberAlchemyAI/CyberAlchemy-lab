"""Compare finite full-document controls against strict UTF-8/JSON reference behavior; not independent proof checking."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[9]
class Number(str):pass
class Object(list):pass
def constant(value):raise ValueError(value)
def units(s):
    raw=s.encode('utf-16-le',errors='surrogatepass')
    return [int.from_bytes(raw[i:i+2],'little') for i in range(0,len(raw),2)]
def reference(source):
    value=json.loads(source,parse_int=Number,parse_float=Number,parse_constant=constant,object_pairs_hook=Object)
    def decode(value):
        if value is None:return {'tag':'null'}
        if isinstance(value,bool):return {'tag':'boolean','value':value}
        if isinstance(value,Number):return {'tag':'number','token':str(value)}
        if isinstance(value,str):return {'tag':'string','units':units(value)}
        if isinstance(value,Object):return {'tag':'object','entries':[{'key_units':units(key),'value':decode(item)} for key,item in value]}
        assert isinstance(value,list);return {'tag':'array','values':[decode(item) for item in value]}
    return decode(value)
def lit(value):return str(value).replace(' ','')
def term(value):
    if value['tag']=='null':return '.null'
    if value['tag']=='boolean':return '.boolean '+str(value['value']).lower()
    if value['tag']=='number':return '.number '+json.dumps(value['token'])
    if value['tag']=='string':return '.string '+lit(value['units'])
    if value['tag']=='array':return '.array ['+','.join(term(item) for item in value['values'])+']'
    return '.object ['+','.join('('+lit(item['key_units'])+','+term(item['value'])+')' for item in value['entries'])+']'
def b(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def run():
    capture=json.loads((HERE/'source-capture.json').read_text());v=json.loads((HERE/'verification.json').read_text());assert v['result']=='candidate-fragment-pass'
    source=(HERE/'ParserControls.lean').read_text();cases=[];additional=[]
    def check(name,function,input,expected):
        result='none' if expected is None else 'some ('+term(expected)+')'
        statement=f'theorem {name} : {function} {lit(input)} = {result} := by rfl'
        assert statement in source,name
        qualified='RelationalSuccessor.CandidateJsonParser.Controls.'+name
        assert qualified in v['new_declarations'];return qualified
    for row in capture['document_reference_cases']:
        assert row['input']==[ord(c) for c in row['source']]
        try:actual=reference(row['source'])
        except (json.JSONDecodeError,ValueError):actual=None
        assert actual==row['expected'],row['name']
        cases.append(dict(row,actual_reference=actual,compiled_declaration=check(row['name'],'parseDocument',row['input'],actual)))
    for row in capture['byte_controls']:
        try:actual=reference(bytes(row['bytes']).decode('utf-8',errors='strict'))
        except (json.JSONDecodeError,ValueError,UnicodeDecodeError):actual=None
        assert actual==row['expected'],row['name']
        additional.append(check(row['name'],'parseDocumentBytes',row['bytes'],actual))
    for row in capture['scalar_controls']:additional.append(check(row['name'],'parseDocument',row['input'],None))
    for row in capture['invalid_byte_controls']:
        try:actual=reference(bytes(row['bytes']).decode('utf-8',errors='strict'))
        except (json.JSONDecodeError,ValueError,UnicodeDecodeError):actual=None
        assert actual is None,row['name']
        additional.append(check(row['name'],'parseDocumentBytes',row['bytes'],None))
    for row in capture['primitive_boundary_controls']:additional.append(check(row['name'],'decodePrimitive',row['input'],None))
    assert len(cases)==62 and len(additional)==21 and capture['worked_control_declarations']==83
    report={'task':'N01','unit':'K02-json-parser','result':'JSON-document-reference-corpus-audit-pass','driver':b(Path(__file__)),'verification':b(HERE/'verification.json'),'source_capture':b(HERE/'source-capture.json'),'controls':b(HERE/'ParserControls.lean'),'case_count':len(cases),'cases':cases,'additional_control_names':additional,'worked_proof_controls':83,'claim_scope':'62 explicit kernel-compiled full-document cases agree with Python JSON recognition retaining original numeric lexemes, UTF-16 units and ordered duplicate object pairs; 21 additional compiled controls exercise UTF-8, scalar and primitive-boundary behavior. This finite evidence does not prove complete recursive grammar soundness/completeness, budget sufficiency, standard translation or independent proof checking.','complete_JSON_parser_implemented':True,'complete_JSON_parser_proved':False,'recursion_budget_sufficiency_proved':False,'existing_scalar_AST_conversion_proved':False,'grammar_standard_translation_proved':False,'original_capture_to_AST_bridge_proved':False,'candidate_parser_profile_owner_accepted':False,'byte_parser_proved':False,'authenticated_capture_proved':False,'N03_schema_freeze':False,'independent_checker_run':False,'inherited_discharges':0,'authority_effect':'none'}
    (HERE/'JSON-document-reference-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('62 document reference cases and 21 additional controls passed.')
if __name__=='__main__':run()
