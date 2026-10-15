"""Generate full-document controls retaining original numeric lexemes and ordered object pairs."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[9];N=HERE.parents[1]
class RawNumber(str):pass
class RawObject(list):pass
def reject_constant(value):raise ValueError(value)
def parse_reference(source):return json.loads(source,parse_int=RawNumber,parse_float=RawNumber,parse_constant=reject_constant,object_pairs_hook=RawObject)
def units(source):
    raw=source.encode('utf-16-le',errors='surrogatepass')
    return [int.from_bytes(raw[i:i+2],'little') for i in range(0,len(raw),2)]
def view(value):
    if value is None:return {'tag':'null'}
    if isinstance(value,bool):return {'tag':'boolean','value':value}
    if isinstance(value,RawNumber):return {'tag':'number','token':str(value)}
    if isinstance(value,str):return {'tag':'string','units':units(value)}
    if isinstance(value,RawObject):return {'tag':'object','entries':[{'key_units':units(key),'value':view(item)} for key,item in value]}
    assert isinstance(value,list);return {'tag':'array','values':[view(item) for item in value]}
def lit(value):return str(value).replace(' ','')
def term(value):
    tag=value['tag']
    if tag=='null':return '.null'
    if tag=='boolean':return '.boolean '+str(value['value']).lower()
    if tag=='number':return '.number '+json.dumps(value['token'])
    if tag=='string':return '.string '+lit(value['units'])
    if tag=='array':return '.array ['+','.join(term(item) for item in value['values'])+']'
    return '.object ['+','.join('('+lit(item['key_units'])+','+term(item['value'])+')' for item in value['entries'])+']'
def b(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(name,d):(HERE/name).write_text(json.dumps(d,indent=2)+'\n')
def run():
    good=['null','false','true','0','-0','42.0','4.2e1','9007199254740993','""','"k"','"\\u006b"','"\\uDEAD"','"𝄞"','"\\uD834\\uDD1E"','[]','[ ]','{}','{ \t\r\n }','[null,true,false]','[42,42.0,4.2e1]','[[[]]]','{"k":null}','{"k":null,"\\u006b":true}','{"\\uDEAD":"\\uD800"}','[{},[],{"a":[1,{"b":false}]}]',' \t\n { "x" : [ 1 , 2 ] , "y" : { "z" : "\\n" } } \r\n','["\\\"", "\\\\", "\\/"]','{"b":1,"a":2,"b":3}']
    bad=['',' ','[','{','[1,]','{"a":1,}','[,]','{,}','[1 2]','{"a" 1}','{a:1}','{"a":}','{"a":1 "b":2}','[truex]','[1abc]','{"a":1e}','[01]','[1.]','truex','null null','1,2','[]x','{}[]','NaN','Infinity','[\v]','\u00a0null','"\\q"','"unclosed','"\n"','{"a":true:1}','{"a":1]','[1}','[1,,2]']
    rows=[];declarations=[]
    for i,source in enumerate(good+bad):
        try:expected=view(parse_reference(source))
        except (json.JSONDecodeError,ValueError):expected=None
        assert (expected is not None)==(source in good)
        row={'name':f'document_{i:02}','source':source,'input':[ord(c) for c in source],'expected':expected};rows.append(row)
        result='none' if expected is None else 'some ('+term(expected)+')'
        declarations.append(f"theorem {row['name']} : parseDocument {lit(row['input'])} = {result} := by rfl")
    byte_rows=[]
    for index in [0,5,11,12,14,22,25,28,32,45]:
        row=rows[index];name='byte_'+row['name'];raw=list(row['source'].encode('utf-8'))
        byte_rows.append({'name':name,'bytes':raw,'expected':row['expected']})
        result='none' if row['expected'] is None else 'some ('+term(row['expected'])+')'
        declarations.append(f'theorem {name} : parseDocumentBytes {lit(raw)} = {result} := by rfl')
    scalar_controls=[('raw_surrogate',[34,55296,34]),('above_unicode',[34,1114112,34])]
    for name,input in scalar_controls:declarations.append(f'theorem {name} : parseDocument {lit(input)} = none := by rfl')
    invalid_bytes=[('byte_overlong',[34,192,128,34]),('byte_surrogate',[34,237,160,128,34]),('byte_truncated',[34,240,159,34]),('byte_bom',[239,187,191,110,117,108,108])]
    for name,input in invalid_bytes:declarations.append(f'theorem {name} : parseDocumentBytes {lit(input)} = none := by rfl')
    primitive_controls=[('primitive_true_unknown',[116,114,117,101,120],None),('primitive_number_unknown',[49,97],None),('primitive_string_unknown',[34,97,34,97],None),('primitive_colon_refused',[34,97,34,58],None),('primitive_array_refused',[91,93],None)]
    for name,input,_ in primitive_controls:declarations.append(f'theorem {name} : decodePrimitive {lit(input)} = none := by rfl')
    text='import RecursiveJsonParser\nset_option autoImplicit false\nset_option maxRecDepth 131072\nset_option maxHeartbeats 4000000\nnamespace RelationalSuccessor.CandidateJsonParser.Controls\nopen CandidateJsonParser CandidateJsonBytes\n'+'\n\n'.join(declarations)+'\n\n'+'\n'.join('#print axioms '+d.split()[1] for d in declarations)+'\nend RelationalSuccessor.CandidateJsonParser.Controls\n';(HERE/'ParserControls.lean').write_text(text)
    save('source-capture.json',{'task':'N01','unit':'K02-json-parser','generator':b(Path(__file__)),'controls':b(HERE/'ParserControls.lean'),'independent_grammar':b(HERE.parent/'K02-json-bytes/JsonDocumentMeaning.lean'),'document_reference_cases':rows,'byte_controls':byte_rows,'scalar_controls':[{'name':name,'input':input} for name,input in scalar_controls],'invalid_byte_controls':[{'name':name,'bytes':input} for name,input in invalid_bytes],'primitive_boundary_controls':[{'name':name,'input':input} for name,input,_ in primitive_controls],'worked_control_declarations':len(declarations),'captured_context_is_synthetic':True,'original_source_capture_authenticated':False,'candidate_parser_profile_owner_accepted':False,'BOM_policy':'This candidate performs no BOM cleanup; supporting optional BOM tolerance would require explicit profile review.','inherited_discharges':0})
    save('context-pack.json',{'task':'N01','unit':'K02-json-parser','scope':'Independent primitive/container-body/boundary meanings; exact primitive dispatcher; complete recursive raw JSON parser implementation with structural termination and finite worked controls. Full recursive soundness/completeness and sufficient-budget proofs remain required.','selected_sources':[b(HERE.parent/'K02-json-bytes/JsonDocumentMeaning.lean'),b(HERE.parent/'K02-json-strings/QuotedStringDecoder.lean'),b(HERE.parent/'K02-json-strings/verification.json'),b(HERE.parent/'K02-json-tokens/NumberPrefixDecoder.lean'),b(HERE.parent/'K02-json-tokens/verification.json'),b(HERE.parent/'K02-json-tokens/NEXT-IMPLEMENTATION.md'),b(N/'K04-assessment-request.json')],'standard':{'url':'https://www.rfc-editor.org/rfc/rfc8259','sections':['2','3','4','5','6','7','8'],'use':'Existing independent complete grammar, ordered raw object members and retained UTF-16 units. Standard-to-meaning translation remains separate.'},'decision':'Specify grammar meanings before recursive implementation; preserve duplicate decoded keys and unpaired escaped UTF-16 units. Do not infer quantified grammar adequacy from termination or finite corpus success.','write_scope':'New N01 candidate package and exact evidence/progress bindings only.','gate_verdict':'Reversible native preparation under existing complete-plan authorization; no global/owner/profile acceptance or inherited admission inferred.','validation':'Pinned fresh compile/replay, axiom/import audits; quantified primitive exactness and finite full-document byte/scalar controls with ordered pairs/original lexemes.','inherited_discharges':0,'authority_effect':'none'})
    print('Generated',len(declarations),'controls,',len(rows),'document reference cases.')
if __name__=='__main__':run()
