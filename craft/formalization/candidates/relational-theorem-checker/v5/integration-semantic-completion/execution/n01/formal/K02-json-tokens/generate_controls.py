"""Generate exact lexeme/suffix controls, preserving token spellings rather than floating-point values."""
from pathlib import Path
import hashlib,json
from decimal import Decimal
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[9];N=HERE.parents[1]
def b(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def lit(v):return str(v).replace(' ','')
def save(name,d):(HERE/name).write_text(json.dumps(d,indent=2)+'\n')
def run():
    good=['0','-0','1','10','-10','42.0','4.2e1','4.2E+1','-12.34e-56','1e0','1E-0','0e+123456789','1.0e-0002','9007199254740993','1e999999999']
    bad=['','-','+1','00','01','-00','-01','.1','1.','1e','1E+','1e-','1ee2','1.2.3','--1','1+2','NaN','Infinity','1a',' 1','1 ','١','0x10']
    declarations=[];number_cases=[]
    for i,source in enumerate(good+bad):
        try:parsed=json.loads(source,parse_float=Decimal,parse_int=Decimal);valid=isinstance(parsed,Decimal) and source==source.strip(' \t\r\n')
        except (json.JSONDecodeError,ValueError):valid=False
        assert valid==(source in good)
        row={'name':f'whole_number_{i:02}','source':source,'input':[ord(c) for c in source],'expected_token':source if valid else None};number_cases.append(row)
        result='some '+json.dumps(source) if valid else 'none'
        declarations.append(f"theorem {row['name']} : decodeWholeNumber {lit(row['input'])} = {result} := by decide")
    prefixes=[('number_comma','42,0','42',',0'),('number_close_array','4.2e1]','4.2e1',']'),('number_close_object','-0}','-0','}'),('number_space','1 \t','1',' \t'),('number_unknown_suffix','1abc','1','abc'),('number_incomplete_exponent','1e]',None,None),('number_leading_zero','01,',None,None),('number_adjacent_sign','1-2,',None,None),('number_partial_fraction','1.,',None,None),('number_upper_exp','1E+02\r','1E+02','\r')]
    prefix_cases=[]
    for name,source,token,rest in prefixes:
        row={'name':name,'input':[ord(c) for c in source],'expected_token':token,'expected_remaining':None if rest is None else [ord(c) for c in rest]};prefix_cases.append(row)
        result='none' if token is None else 'some ('+json.dumps(token)+','+lit(row['expected_remaining'])+')'
        declarations.append(f"theorem {name} : decodeNumber {lit(row['input'])} = {result} := by decide")
    literal_cases=[]
    for name,source,value,rest in [('null_prefix','null,1','.null',',1'),('false_prefix','false]','.boolean false',']'),('true_prefix','true}', '.boolean true','}'),('true_unknown_suffix','truex','.boolean true','x'),('null_unclosed','nul',None,None),('false_upper','False',None,None),('true_upper','TRUE',None,None),('literal_missing','',None,None),('literal_space',' null',None,None)]:
        row={'name':name,'input':[ord(c) for c in source],'expected_value':value,'expected_remaining':None if rest is None else [ord(c) for c in rest]};literal_cases.append(row)
        result='none' if value is None else 'some ('+value+','+lit(row['expected_remaining'])+')'
        declarations.append(f"theorem {name} : decodeLiteral {lit(row['input'])} = {result} := by rfl")
    whitespace_cases=[]
    for name,input,word,rest in [('ws_all',[32,9,10,13,110],[32,9,10,13],[110]),('ws_empty',[],[],[]),('ws_no_trim',[49,32],[],[49,32]),('ws_nonbreaking',[160,32],[],[160,32]),('ws_vertical_tab',[11,32],[],[11,32]),('ws_only',[9,9,32],[9,9,32],[])]:
        whitespace_cases.append({'name':name,'input':input,'word':word,'remaining':rest})
        declarations.append(f'theorem {name} : scanWhitespace {lit(input)} = ({lit(word)},{lit(rest)}) := by decide')
    text='import NumberPrefixDecoder\nset_option autoImplicit false\nset_option maxRecDepth 8192\nnamespace RelationalSuccessor.CandidateJsonTokens.Controls\nopen CandidateJsonTokens CandidateJsonBytes\n'+'\n\n'.join(declarations)+'\n\n'+'\n'.join('#print axioms '+d.split()[1] for d in declarations)+'\nend RelationalSuccessor.CandidateJsonTokens.Controls\n'
    (HERE/'TokenControls.lean').write_text(text)
    save('source-capture.json',{'task':'N01','unit':'K02-json-tokens','generator':b(Path(__file__)),'control_source':b(HERE/'TokenControls.lean'),'independent_grammar':b(HERE.parent/'K02-json-bytes/JsonDocumentMeaning.lean'),'decimal_grammar':b(HERE.parent/'K02-numeric/DecimalGrammar.lean'),'whole_number_reference_cases':number_cases,'number_prefix_controls':prefix_cases,'literal_prefix_controls':literal_cases,'whitespace_controls':whitespace_cases,'worked_control_declarations':len(declarations),'captured_context_is_synthetic':True,'original_source_capture_authenticated':False,'candidate_parser_profile_owner_accepted':False,'inherited_discharges':0})
    save('context-pack.json',{'task':'N01','unit':'K02-json-tokens','scope':'Independent maximal numeric/whitespace runs, exact literals and number prefixes retaining original spellings and exact suffixes; container boundary interface formalized before implementation.','selected_sources':[b(HERE.parent/'K02-json-bytes/JsonDocumentMeaning.lean'),b(HERE.parent/'K02-json-strings/NEXT-IMPLEMENTATION.md'),b(HERE.parent/'K02-json-strings/verification.json'),b(HERE.parent/'K02-number-parser/NumberTokenParser.lean'),b(HERE.parent/'K02-number-parser/NumberGrammarComplete.lean'),b(N/'K04-assessment-request.json')],'standard':{'url':'https://www.rfc-editor.org/rfc/rfc8259','sections':['2','3','6'],'use':'JSON whitespace, literal and numeric token grammar. Existing independent grammar is reused; RFC prose translation remains unproved.'},'decision':'Formalize prefix meanings first. Scan the maximal numeric-character run and qualify the entire token against the existing grammar; retain exact spelling. Document/container boundary checks remain a separate layer.','write_scope':'New N01 candidate package and exact evidence/progress bindings only.','gate_verdict':'Reversible preparation under existing full-plan authorization; no new owner/global acceptance or inherited admission inferred.','validation':'Fresh pinned compile/replay and axiom/import audits; original spellings, incomplete exponents/fractions, leading zeros, suffix and whitespace controls.','inherited_discharges':0,'authority_effect':'none'})
    print('Generated',len(declarations),'controls,',len(number_cases),'whole-number reference cases.')
if __name__=='__main__':run()
