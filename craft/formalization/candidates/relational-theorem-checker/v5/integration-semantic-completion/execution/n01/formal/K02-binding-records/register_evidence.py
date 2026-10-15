"""Register verified AST candidates only; retain all pending obligations and assessments."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
N=HERE.parents[1];H=HERE.parents[3];ROOT=HERE.parents[9]
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def run():
    v=read(HERE/'verification.json');a=read(HERE/'import-resolution-audit.json');sa=read(HERE/'full-schema-source-audit.json')
    assert v['new_declaration_count']==94 and v['result']=='candidate-fragment-pass'
    assert len(v['records'])==44 and sum(x['inspected_declarations'] for x in v['records'])==536
    assert a['result']=='import-resolution-audit-pass' and a['resolved_source_phase_pairs']==44 and a['verification']==bind(HERE/'verification.json')
    assert sa['result']=='candidate-full-binding-schema-source-shape-audit-pass' and len(sa['exact_shape_assertions'])==12 and sa['case_count']==68
    index=read(N/'formal-preparation-index.json');seq=read(N/'sequential-review.json');plan=read(H/'execution/plan.json');progress=next(t for t in plan['tasks'] if t['id']=='N01')['progress']
    assert not index.get('binding_record_packages') and index['total_distinct_new_candidate_theorems']==841
    assert seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==841 and seq['current_unit']=='K04'
    assert seq['new_inherited_discharges']==progress['inherited_discharges']==index['inherited_discharges']==0
    p=HERE/'MODEL-REVIEW.md';text=p.read_text();text+=f"\nFresh verification passed all 94 declarations (10 general/field theorems and 84\nworked controls), through 44 compile/replay invocations, 536 dependency-inclusive\naxiom inspections and 44 matching-phase import audits. Only the allowed standard\naxioms occur. Fresh compilation/elaboration took {sum(x['seconds'] for x in v['records']):.3f}\nseconds total; the largest module took {max(x['seconds'] for x in v['records']):.3f} seconds. These timings\nare not runtime resource measurements. The full-schema source audit passed all\n12 comparisons and 68 syntax cases. No independent checker was run here.\n";p.write_text(text)
    old=read(N/'formal/K02-number-parser/refinement-matrix.json')
    matrix={'task':'N01','unit':'K02-binding-records','status':'candidate-full-binding-record-AST-verified','definition':old['definition'],'context_pack':bind(HERE/'context-pack.json'),'source_capture':bind(HERE/'source-capture.json'),'rows':[],'complete_frame_AST_proved':True,'complete_binding_record_AST_proved':True,'field_preserving_binding_record_AST_proved':True,'binding_schema_AST_correspondence_proved':False,'byte_parser_proved':False,'authenticated_capture_proved':False,'complete_K02_source_refinement':False,'inherited_discharges':0,'authority_effect':'none','verification':bind(HERE/'verification.json'),'import_resolution_audit':bind(HERE/'import-resolution-audit.json'),'full_schema_source_audit':bind(HERE/'full-schema-source-audit.json')}
    for row in old['rows']:
        matrix['rows'].append({'id':row['id'],'candidate_components':['Complete exact Frame/Body/fixed-version-and-kind Record AST decoding','Independent field-preservation meanings and exact natural epoch adapter'] if ':meaning:' in row['id'] else [],'still_required':['Byte/AST/full Schema semantics/capture/digest correspondence','Authenticated parsed-record-to-catalog bridge and all nineteen source semantic policies','Full source/Selection integration, public outcomes and runtime resources','Whole source/effect/theory proofs and mandatory independent checking','Actual remaining relation/global/use assessments under their own scope'],'inherited_status':'pending','inherited_discharge':False})
    save(HERE/'refinement-matrix.json',matrix)
    api={'task':'N01','unit':'K02-binding-records','status':'non-admitted-candidate-pure-functions','functions':[{'function':'RelationalSuccessor.CandidateBindingRecords.resolutionRecord.decode','output':'Option (Record Resolution)','fixed_kind':'intent-resolution-qualifier-binding','fixed_schema_version':'cyberalchemy-lab-intent-resolution-qualifier-binding/candidate-v1'},{'function':'RelationalSuccessor.CandidateBindingRecords.roleRecord.decode','output':'Option (Record Role)','fixed_kind':'intent-addressing-role-binding','fixed_schema_version':'cyberalchemy-lab-intent-addressing-role-binding/candidate-v1'}],'inputs':['Retained complete record AST with duplicate fields and original number lexemes preserved'],'qualified_output_meaning':'Independent complete closed-record AST meaning with all five record, three body and eight frame fields preserved; typed target schema is fixed per public function.','body_type_reused':'RelationalSuccessor.CandidateOwnedBindings.Body','None_meaning':'The retained AST does not have an output satisfying this fixed local record meaning; public error classification remains pending.','binding_record_AST_decoder_proved':True,'complete_frame_AST_proved':True,'field_preserving_binding_record_AST_proved':True,'byte_parser_proved':False,'whole_JSON_document_parser_proved':False,'binding_schema_AST_correspondence_proved':False,'authenticated_capture_proved':False,'supported_resource_envelope_measured':False,'public_outcome_classification_implemented':False,'N03_API_freeze':False,'inherited_discharges':0,'authority_effect':'none'}
    save(HERE/'candidate-api-contract.json',api)
    package={'unit':'K02-binding-records','kind':'relation.addresses-intent','verification':bind(HERE/'verification.json'),'theorems':94,'binding_record_AST_decoder_proved':True,'complete_frame_AST_proved':True,'complete_binding_record_AST_proved':True,'field_preserving_binding_record_AST_proved':True,'binding_schema_AST_correspondence_proved':False,'complete_source_refinement':False,'inherited_discharges':0}
    files={'import_resolution_audit':'import-resolution-audit.json','full_schema_source_audit':'full-schema-source-audit.json','candidate_api_contract':'candidate-api-contract.json','model_review':'MODEL-REVIEW.md','refinement_matrix':'refinement-matrix.json','next_implementation_plan':'NEXT-IMPLEMENTATION.md'}
    for k,file in files.items():package[k]=bind(HERE/file)
    index['binding_record_packages']=[package];index['binding_record_candidate_theorems']=94;index['total_distinct_new_candidate_theorems']=935;save(N/'formal-preparation-index.json',index)
    seq['candidate_fragment_theorems']=935;seq['candidate_binding_record_packages']=1;save(N/'sequential-review.json',seq)
    progress['candidate_fragment_theorems']=935;progress['binding_record_candidate_theorems']=94;progress['candidate_binding_record_packages']=1
    for k,file in dict(files,verification='verification.json').items():progress['K02_binding_records_'+k]=bind(HERE/file)
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in {str((N/'formal-preparation-index.json').relative_to(ROOT)),str((N/'sequential-review.json').relative_to(ROOT))}:value.update(bind(ROOT/value['path']))
    save(H/'execution/plan.json',plan)
    p=N/'check_current_review.py';text=p.read_text();old="index.get('number_parser_packages', [])):";assert text.count(old)==1
    text=text.replace(old,"index.get('number_parser_packages', []) +\n                    index.get('binding_record_packages', [])):")
    marker='    assert len(declarations) == len(set(declarations))';assert text.count(marker)==1
    block='''        if package.get('binding_record_AST_decoder_proved'):
            assert proof['binding_record_AST_decoder_proved'] is True
            assert proof['complete_frame_AST_proved'] is True
            assert proof['complete_binding_record_AST_proved'] is True
            assert proof['field_preserving_binding_record_AST_proved'] is True
            assert proof['binding_schema_AST_correspondence_proved'] is False
            assert proof['JSON_schema_semantics_interpreter_proved'] is False
            assert proof['raw_binding_record_parser_proved'] is False
            assert proof['byte_parser_proved'] is False
            assert proof['authenticated_capture_proved'] is False
            assert proof['whole_K02_source_refinement_proved'] is False
            assert proof['supported_resource_envelope_measured'] is False
            read(ROOT / proof['context_pack']['path'])
            capture = read(ROOT / proof['source_capture']['path'])
            assert capture['worked_control_declarations'] == 84
            assert capture['binding_record_bytes_are_synthetic'] is True
            audit = read(ROOT / package['full_schema_source_audit']['path'])
            assert audit['result'] == 'candidate-full-binding-schema-source-shape-audit-pass'
            assert len(audit['exact_shape_assertions']) == 12
            assert audit['case_count'] == len(audit['cases']) == 68
            assert all(row['actual'] == row['expected'] for row in audit['cases'])
            assert audit['binding_schema_AST_correspondence_proved'] is False
            assert audit['byte_parser_proved'] is False
            assert audit['N03_schema_freeze'] is False
            api = read(ROOT / package['candidate_api_contract']['path'])
            assert api['N03_API_freeze'] is False
            assert api['binding_record_AST_decoder_proved'] is True
            assert api['whole_JSON_document_parser_proved'] is False
            assert api['public_outcome_classification_implemented'] is False
'''
    p.write_text(text.replace(marker,block+marker))
    p=H/'execution/PROGRESS.md';text=p.read_text();text=text.replace('making 841 distinct verified candidate declarations in total.','and full binding-record AST formalization adds 94, making 935 distinct verified candidate declarations in total.')
    text+='''
K02-binding-records completes the eight-field Frame, typed Body and enclosing
fixed-version/fixed-kind resolution and role Record AST decoders. Ten quantified
exactness/field theorems and 84 worked controls pass 44 fresh compile/replay
invocations, 536 dependency-inclusive axiom inspections and 44 matching-phase
import audits. The full-schema source audit passes 12 structural comparisons and
68 syntax cases. This proves local independent AST meanings and field preservation;
it does not prove a general Schema interpreter, original-byte parsing, authenticated
capture/catalog construction, all nineteen source policies or whole-source closure.
The registered total is 935 distinct scoped candidate declarations. All 263 inherited
IDs remain pending, all 90 original discharges retain scope, four actual meaning
assessments remain recorded, K04 and D01-D08 remain pending, N01 remains in progress
and only N00 is accepted (1/20). N02/N03 closure/freezing, the seven-extension
integration and final new bounded-use assessment remain in the original active plan.
''';p.write_text(text)
    print('Registered 94 binding-record AST declarations; total 935. All 263 inherited IDs remain pending; K04 remains the current actual owner review.')
if __name__=='__main__':run()
