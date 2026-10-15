"""Register this verified candidate component without accepting N01 or discharging IDs."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
N=HERE.parents[1]
H=HERE.parents[3]
ROOT=HERE.parents[9]
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')

def run():
    v=read(HERE/'verification.json');a=read(HERE/'import-resolution-audit.json')
    assert v['new_declaration_count']==84 and v['result']=='candidate-fragment-pass'
    assert len(v['records'])==22 and sum(r['inspected_declarations'] for r in v['records'])==254
    assert a['result']=='import-resolution-audit-pass' and a['resolved_source_phase_pairs']==22 and a['verification']==bind(HERE/'verification.json')
    index=read(N/'formal-preparation-index.json');assert index['total_distinct_new_candidate_theorems']==757 and not index.get('number_parser_packages')
    p=HERE/'MODEL-REVIEW.md';text=p.read_text();total=round(sum(r['seconds'] for r in v['records']),3);maximum=max(r['seconds'] for r in v['records'])
    text+=f'''
Fresh verification passed all 84 new declarations, including 53 worked controls,
through 22 pinned compile/replay invocations and 254 dependency-inclusive axiom
inspections. All 22 matching-phase import audits passed. Only the allowed standard
axioms occur; no placeholder or native proof shortcut is used. Compile/elaboration
took {total} seconds total, with a {maximum}-second maximum module. These are not
runtime limit measurements. The 46-case exact Decimal audit passed separately.
Same pinned-kernel replay is not mandatory independent proof checking.
''';p.write_text(text)
    old=read(N/'formal/K02-numeric/refinement-matrix.json')
    matrix={'task':'N01','unit':'K02-number-parser','status':'candidate-exact-number-parser-and-epoch-AST-verified','definition':old['definition'],'context_pack':bind(HERE/'context-pack.json'),'source_capture':bind(HERE/'source-capture.json'),'rows':[],'number_token_parser_proved':True,'raw_number_token_parser_proved':True,'token_representation_completeness_proved':True,'token_representation_uniqueness_proved':True,'numeric_AST_decoder_proved':True,'complete_frame_AST_proved':False,'complete_binding_record_AST_proved':False,'schema_AST_correspondence_proved':False,'byte_parser_proved':False,'authenticated_capture_proved':False,'complete_K02_source_refinement':False,'inherited_discharges':0,'authority_effect':'none','verification':bind(HERE/'verification.json'),'import_resolution_audit':bind(HERE/'import-resolution-audit.json'),'raw_number_reference_audit':bind(HERE/'raw-number-reference-audit.json')}
    for row in old['rows']:
        matrix['rows'].append({'id':row['id'],'candidate_components':['Exact complete ASCII JSON-number grammar parsing and unique retained representation','Exact natural epoch AST decoder without caller witness or float normalization'] if ':meaning:' in row['id'] else [],'still_required':['All Frame/body/record fields and full schema/byte/capture/digest correspondence','Authentic providers and all nineteen source semantic policies','Full source/Selection integration and public outcome/resource contracts','Whole source/effect/theory proofs and mandatory independent closure checking','All remaining actual owner/global/use assessments'],'inherited_status':'pending','inherited_discharge':False})
    save(HERE/'refinement-matrix.json',matrix)
    api={'task':'N01','unit':'K02-number-parser','status':'non-admitted-candidate-pure-function','function':'RelationalSuccessor.CandidateNumberParser.decodeEpochAst','inputs':['retained JSON number AST with the exact original number lexeme; other AST types refuse'],'output':'Option Nat','qualified_output_meaning':'Exact JSON-number lexical grammar and independent nonnegative integral decimal-value equation. Representation is constructed internally.','caller_representation_witness_required':False,'raw_number_token_parser_implemented':True,'token_representation_completeness_proved':True,'token_representation_uniqueness_proved':True,'None_meaning':'The AST is not a number token with a natural epoch value; final public syntax/value/resource classification is pending.','byte_parser_proved':False,'whole_JSON_document_parser_proved':False,'full_binding_record_parser_proved':False,'schema_AST_correspondence_proved':False,'authenticated_capture_proved':False,'supported_resource_envelope_measured':False,'public_outcome_classification_implemented':False,'N03_API_freeze':False,'inherited_discharges':0,'authority_effect':'none'}
    save(HERE/'candidate-api-contract.json',api)
    package={'unit':'K02-number-parser','kind':'relation.addresses-intent','verification':bind(HERE/'verification.json'),'theorems':84,'number_token_parser_proved':True,'raw_number_token_parser_proved':True,'token_representation_completeness_proved':True,'token_representation_uniqueness_proved':True,'numeric_AST_decoder_proved':True,'complete_frame_AST_proved':False,'complete_binding_record_AST_proved':False,'schema_AST_correspondence_proved':False,'complete_source_refinement':False,'inherited_discharges':0,'import_resolution_audit':bind(HERE/'import-resolution-audit.json'),'raw_number_reference_audit':bind(HERE/'raw-number-reference-audit.json'),'candidate_api_contract':bind(HERE/'candidate-api-contract.json'),'model_review':bind(HERE/'MODEL-REVIEW.md'),'refinement_matrix':bind(HERE/'refinement-matrix.json'),'next_implementation_plan':bind(HERE/'NEXT-IMPLEMENTATION.md')}
    index['number_parser_packages']=[package];index['number_parser_candidate_theorems']=84;index['total_distinct_new_candidate_theorems']=841;save(N/'formal-preparation-index.json',index)
    p=N/'sequential-review.json';d=read(p);assert d['candidate_fragment_theorems']==757 and d['current_unit']=='K04';d['candidate_fragment_theorems']=841;d['candidate_number_parser_packages']=1;save(p,d)
    p=H/'execution/plan.json';d=read(p);progress=next(t for t in d['tasks'] if t['id']=='N01')['progress'];assert progress['candidate_fragment_theorems']==757
    progress['candidate_fragment_theorems']=841;progress['number_parser_candidate_theorems']=84;progress['candidate_number_parser_packages']=1
    for key,file in [('verification','verification.json'),('import_audit','import-resolution-audit.json'),('review','MODEL-REVIEW.md'),('refinement_matrix','refinement-matrix.json'),('raw_number_reference_audit','raw-number-reference-audit.json'),('candidate_api_contract','candidate-api-contract.json'),('next_implementation_plan','NEXT-IMPLEMENTATION.md')]:progress['K02_number_parser_'+key]=bind(HERE/file)
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in {str((N/'formal-preparation-index.json').relative_to(ROOT)),str((N/'sequential-review.json').relative_to(ROOT))}:value.update(bind(ROOT/value['path']))
    save(p,d)
    p=N/'check_current_review.py';text=p.read_text();text=text.replace("index.get('numeric_packages', [])):","index.get('numeric_packages', []) +\n                    index.get('number_parser_packages', [])):")
    marker='    assert len(declarations) == len(set(declarations))'
    block='''        if package.get('number_token_parser_proved'):
            assert proof['number_token_parser_proved'] is True
            assert proof['complete_JSON_number_grammar_proved'] is True
            assert proof['raw_number_token_parser_proved'] is True
            assert proof['token_representation_completeness_proved'] is True
            assert proof['token_representation_uniqueness_proved'] is True
            assert proof['numeric_AST_decoder_proved'] is True
            assert proof['complete_frame_AST_proved'] is False
            assert proof['complete_binding_record_AST_proved'] is False
            assert proof['binding_schema_AST_correspondence_proved'] is False
            assert proof['supported_resource_envelope_measured'] is False
            assert proof['byte_parser_proved'] is False
            assert proof['authenticated_capture_proved'] is False
            assert proof['whole_K02_source_refinement_proved'] is False
            read(ROOT / proof['context_pack']['path'])
            read(ROOT / proof['source_capture']['path'])
            audit = read(ROOT / package['raw_number_reference_audit']['path'])
            assert audit['result'] == 'exact-raw-number-corpus-audit-pass'
            assert audit['case_count'] == len(audit['cases']) == 46
            assert audit['worked_proof_controls'] == 53
            assert all(row['expected_epoch'] == row['exact_reference_epoch'] for row in audit['cases'])
            assert audit['byte_parser_proved'] is False
            assert audit['schema_AST_correspondence_proved'] is False
            assert audit['N03_schema_freeze'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['N03_API_freeze'] is False
            assert api['raw_number_token_parser_implemented'] is True
            assert api['caller_representation_witness_required'] is False
            assert api['whole_JSON_document_parser_proved'] is False
            assert api['public_outcome_classification_implemented'] is False
'''
    assert text.count(marker)==1;text=text.replace(marker,block+marker);p.write_text(text)
    p=H/'execution/PROGRESS.md';text=p.read_text();text=text.replace('making 757 distinct verified candidate declarations in total.','and exact number-token parsing adds 84, making 841 distinct verified candidate declarations in total.')
    text+='''
K02-number-parser closes the raw number-token gap: exact complete JSON-number
character grammar parsing, complete reconstruction, representation completeness/
uniqueness and exact natural epoch AST decoding now have quantified independent
meaning equivalences. The epoch adapter constructs its own representation and
preserves decimal/exponent/negative-zero spellings without float conversion.
Fifty-three controls include 46 raw numeric cases, ignored-suffix and precision
refusals, valid fractional syntax and adapter composition. All 84 new declarations
pass 22 fresh compile/replay invocations, 254 dependency-inclusive axiom inspections
and 22 matching-phase import audits. The exact Decimal corpus audit passes separately.
The total is 841 scoped candidate declarations. All Frame/body/record fields,
full schema and byte/token/AST/digest/capture bridges, authentic providers/nineteen
policies, public outcomes/resources and whole-source/effect/theory/independent
closure remain open. No inherited discharge or owner/profile acceptance is inferred:
263 IDs remain pending, 90 original discharges retain scope, K04/global reviews
remain pending and only N00 is accepted. The full 20-task, 41-kind/550-pair/seven-
extension formalization-first plan remains active.
''';p.write_text(text)
    print('Registered 84 exact number parser declarations; total 841; all 263 IDs pending; full original scope preserved.')

if __name__=='__main__':run()
