"""Generate explicit kernel controls; reference agreement is separate from proof validity."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[9];N=HERE.parents[1]
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def units(s):
    raw=s.encode('utf-16-le',errors='surrogatepass')
    return [int.from_bytes(raw[i:i+2],'little') for i in range(0,len(raw),2)]
def lit(v):return str(v).replace(' ','')
def run():
    good=[('empty','""'),('plain','"abc"'),('quote','"\\\""'),('backslash','"\\\\"'),('solidus','"\\/"'),('backspace','"\\b"'),('formfeed','"\\f"'),('newline','"\\n"'),('return','"\\r"'),('tab','"\\t"'),('all_simple','"\\\"\\\\\\/\\b\\f\\n\\r\\t"'),('hex_zero','"\\u0000"'),('hex_lower','"\\u006b"'),('hex_upper','"\\u00AF"'),('hex_mixed','"\\uaBcD"'),('lone_high','"\\uD834"'),('lone_low','"\\uDEAD"'),('surrogate_pair','"\\uD834\\uDD1E"'),('raw_supplementary','"𝄞"'),('raw_maximum','"\U0010ffff"'),('raw_delete','"\x7f"'),('raw_space','" "')]
    bad=[('missing_start','abc"'),('unclosed','"abc'),('unknown_escape','"\\q"'),('short_hex','"\\u012"'),('bad_hex','"\\u0x12"'),('slash_unclosed','"\\'),('raw_tab','"\t"'),('raw_zero','"\x00"'),('raw_control31','"\x1f"'),('trailing_text','"a"x'),('second_string','"a""b"'),('raw_newline','"\n"'),('empty_input',''),('quote_only','"')]
    cases=[]
    for name,source in good+bad:
        try:decoded=json.loads(source);assert isinstance(decoded,str);expected=units(decoded)
        except json.JSONDecodeError:expected=None
        cases.append({'name':'string_'+name,'source':source,'scalar_input':[ord(c) for c in source],'expected_units':expected,'reference':'strict Python JSON string decoding, retained UTF-16 units'})
    scalar_controls=[{'name':'string_raw_surrogate_refused','scalar_input':[34,55296,34],'expected_units':None},{'name':'string_raw_above_max_refused','scalar_input':[34,1114112,34],'expected_units':None}]
    prefixes=[('prefix_comma',[34,97,34,44,99],[97],[44,99]),('prefix_empty',[34,34,58],[],[58]),('prefix_hex',[34,92,117,48,48,54,98,34,125],[107],[125]),('prefix_lone_surrogate',[34,92,117,68,69,65,68,34,44],[57005],[44]),('prefix_raw_supplementary',[34,119070,34,93],[55348,56606],[93]),('prefix_unclosed',[34,97],None,None),('prefix_invalid_escape',[34,92,113,34,44],None,None),('prefix_missing_start',[97,34],None,None)]
    byte_cases=[]
    for name,source in [good[0],good[10],good[16],good[17],good[18],bad[2],bad[9]]:
        raw=list(source.encode('utf-8'));matching=next(c for c in cases if c['source']==source)
        byte_cases.append({'name':'bytes_'+name,'bytes':raw,'expected_units':matching['expected_units']})
    byte_cases += [{'name':'bytes_invalid_utf8','bytes':[34,192,128,34],'expected_units':None},{'name':'bytes_direct_surrogate','bytes':[34,237,160,128,34],'expected_units':None}]
    declarations=[]
    for row in cases+scalar_controls:
        expected='none' if row['expected_units'] is None else 'some '+lit(row['expected_units'])
        declarations.append(f"theorem {row['name']} : decodeString {lit(row['scalar_input'])} = {expected} := by decide")
    for name,source,value,remaining in prefixes:
        expected='none' if value is None else 'some ('+lit(value)+','+lit(remaining)+')'
        declarations.append(f'theorem {name} : decodeQuoted {lit(source)} = {expected} := by decide')
    for row in byte_cases:
        expected='none' if row['expected_units'] is None else 'some '+lit(row['expected_units'])
        declarations.append(f"theorem {row['name']} : decodeStringBytes {lit(row['bytes'])} = {expected} := by decide")
    text='import QuotedStringDecoder\nset_option autoImplicit false\nset_option maxRecDepth 8192\nnamespace RelationalSuccessor.CandidateJsonStrings.Controls\nopen CandidateJsonStrings\n'+'\n\n'.join(declarations)+'\n\n'+'\n'.join('#print axioms '+d.split()[1] for d in declarations)+'\nend RelationalSuccessor.CandidateJsonStrings.Controls\n'
    (HERE/'StringControls.lean').write_text(text)
    save(HERE/'source-capture.json',{'task':'N01','unit':'K02-json-strings','generator':binding(Path(__file__)),'independent_grammar':binding(HERE.parent/'K02-json-bytes/JsonDocumentMeaning.lean'),'control_source':binding(HERE/'StringControls.lean'),'string_reference_cases':cases,'scalar_only_controls':scalar_controls,'quoted_prefix_controls':[{'name':name,'input':source,'expected_units':value,'expected_remaining':remaining} for name,source,value,remaining in prefixes],'byte_controls':byte_cases,'worked_control_declarations':len(declarations),'captured_context_is_synthetic':True,'byte_inputs_are_synthetic':True,'original_source_capture_authenticated':False,'candidate_parser_profile_owner_accepted':False,'inherited_discharges':0})
    save(HERE/'context-pack.json',{'task':'N01','unit':'K02-json-strings','scope':'Exact string-unit, quoted-prefix, whole-string and UTF-8 whole-string decoding against the pre-existing independent grammar. No full JSON document parser or scalar-AST conversion.','selected_sources':[binding(HERE.parent/'K02-json-bytes'/name) for name in ['JsonDocumentMeaning.lean','Utf8Meaning.lean','Utf8Stream.lean','verification.json','NEXT-IMPLEMENTATION.md']]+[binding(N/'assessments/K02.json'),binding(N/'K04-assessment-request.json')],'standard':{'url':'https://www.rfc-editor.org/rfc/rfc8259','sections':['7','8.2','8.3'],'use':'Escape meanings and retained UTF-16 units; no normalization or surrogate replacement.'},'decision':'Use the existing independent inductive meanings; retain unpaired escaped UTF-16 units. Scalar-AST conversion and public profile outcomes remain separate requirements.','write_scope':'New candidate package, exact review/progress evidence bindings.','gate_verdict':'Existing full-plan authorization for reversible native preparation; no semantic-owner or inherited admission inferred.','validation':'Fresh pinned compile/replay, dependency/axiom audits and explicit positive/negative reference corpus.','inherited_discharges':0,'authority_effect':'none'})
    print('Generated',len(declarations),'controls;',len(cases),'JSON string reference cases.')
if __name__=='__main__':run()
