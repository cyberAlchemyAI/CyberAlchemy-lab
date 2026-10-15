"""Audit explicit compiled cases against strict UTF-8 reference behavior, not proof checking."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[9]
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def run():
    capture=json.loads((HERE/'source-capture.json').read_text());v=json.loads((HERE/'verification.json').read_text());assert v['result']=='candidate-fragment-pass'
    text=(HERE/'ByteControls.lean').read_text();cases=[]
    for row in capture['utf8_reference_cases']:
        try:actual=[ord(c) for c in bytes(row['bytes']).decode('utf-8',errors='strict')]
        except UnicodeDecodeError:actual=None
        assert actual==row['expected_scalars'],row['name']
        expected='none' if actual is None else 'some '+str(actual).replace(' ','')
        statement=f'theorem {row["name"]} : decodeUtf8 {str(row["bytes"]).replace(" ","")} = {expected} := by decide'
        assert statement in text,row['name']
        qualified='RelationalSuccessor.CandidateJsonBytes.Controls.'+row['name'];assert qualified in v['new_declarations']
        cases.append(dict(row,actual_reference_scalars=actual,compiled_declaration=qualified))
    for name in capture['grammar_control_names']:
        assert 'RelationalSuccessor.CandidateJsonBytes.Controls.'+name in v['new_declarations']
    assert len(cases)==39 and capture['worked_control_declarations']==47
    report={'task':'N01','unit':'K02-json-bytes','result':'UTF8-reference-corpus-audit-pass','driver':binding(Path(__file__)),'verification':binding(HERE/'verification.json'),'source_capture':binding(HERE/'source-capture.json'),'controls':binding(HERE/'ByteControls.lean'),'case_count':len(cases),'cases':cases,'worked_proof_controls':47,'grammar_controls':capture['grammar_control_names'],'claim_scope':'Thirty-nine explicit kernel-compiled byte cases match strict Python UTF-8 reference behavior. Eight additional kernel controls concern independent JSON grammar meanings. Neither this corpus nor the local meanings prove translation of RFC prose, a full JSON parser, scalar-AST conversion or independent proof checking.','complete_JSON_parser_proved':False,'existing_scalar_AST_conversion_proved':False,'grammar_standard_translation_proved':False,'original_capture_to_AST_bridge_proved':False,'candidate_parser_profile_owner_accepted':False,'byte_parser_proved':False,'authenticated_capture_proved':False,'N03_schema_freeze':False,'independent_checker_run':False,'inherited_discharges':0,'authority_effect':'none'}
    (HERE/'UTF8-reference-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'result':report['result'],'UTF8_cases':len(cases),'grammar_controls':len(capture['grammar_control_names'])}))
if __name__=='__main__':run()
