"""Generate explicit UTF-8 kernel controls and exact Python reference audit cases."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[9]
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def run():
    examples=[('empty',[]),('ASCII_boundaries',[0,127]),('two_min',[194,128]),('two_max',[223,191]),('three_min',[224,160,128]),('three_max',[239,191,191]),('before_surrogates',[237,159,191]),('after_surrogates',[238,128,128]),('four_min',[240,144,128,128]),('four_max',[244,143,191,191]),('g_clef',[240,157,132,158]),('precomposed',[195,169]),('decomposed',[101,204,129]),('BOM_is_scalar',[239,187,191]),('C0_overlong',[192,128]),('C1_overlong',[193,191]),('E0_overlong',[224,128,128]),('F0_overlong',[240,128,128,128]),('surrogate_first',[237,160,128]),('surrogate_last',[237,191,191]),('above_max',[244,144,128,128]),('four_above_max',[244,191,191,191]),('F5_leader',[245,128,128,128]),('FF_leader',[255]),('tail_alone_low',[128]),('tail_alone_high',[191]),('bad_second',[194,0]),('bad_third',[226,130,32]),('bad_fourth',[240,144,128,0]),('truncated_two',[194]),('truncated_three_first',[226]),('truncated_three_second',[226,130]),('truncated_four_first',[240]),('truncated_four_second',[240,144]),('truncated_four_third',[240,144,128]),('valid_then_invalid',[65,192,128]),('mixed_script',[65,226,137,162,206,145,46]),('korean',[237,149,156,234,181,173,236,150,180]),('large_exact_number_bytes',list(b'9007199254740993.0'))]
    rows=['import JsonDocumentMeaning','set_option autoImplicit false','namespace RelationalSuccessor.CandidateJsonBytes.Controls','open RelationalSuccessor.CandidateJsonBytes',''];names=[];cases=[]
    for name,content in examples:
        try: expected=[ord(c) for c in bytes(content).decode('utf-8',errors='strict')]
        except UnicodeDecodeError:expected=None
        term='none' if expected is None else 'some '+str(expected).replace(' ','')
        name='utf8_'+name
        rows.extend([f'theorem {name} : decodeUtf8 {str(content).replace(" ","")} = {term} := by decide','']);names.append(name)
        cases.append({'name':name,'bytes':content,'expected_scalars':expected,'reference':'Python strict UTF-8 decoding; illustration, not proof of RFC conformance.'})
    rows.append((HERE/'grammar-controls.inc').read_text())
    extra=[]
    import re
    extra=re.findall(r'^theorem (\w+)',(HERE/'grammar-controls.inc').read_text(),re.M);names+=extra
    rows.extend(f'#print axioms {name}' for name in names);rows.extend(['end RelationalSuccessor.CandidateJsonBytes.Controls',''])
    (HERE/'ByteControls.lean').write_text('\n'.join(rows))
    report={'task':'N01','unit':'K02-json-bytes','generator':binding(Path(__file__)),'grammar_controls':binding(HERE/'grammar-controls.inc'),'controls':binding(HERE/'ByteControls.lean'),'worked_control_declarations':len(names),'utf8_reference_cases':cases,'utf8_reference_case_count':len(cases),'grammar_control_names':extra,'complete_JSON_parser_implemented':False,'complete_JSON_parser_proved':False,'existing_scalar_AST_conversion_proved':False,'original_capture_to_AST_bridge_proved':False,'authenticated_capture_proved':False,'grammar_standard_translation_proved':False,'candidate_parser_profile_owner_accepted':False,'inherited_discharges':0,'authority_effect':'none'}
    (HERE/'source-capture.json').write_text(json.dumps(report,indent=2)+'\n');print('UTF-8 reference cases',len(cases),'worked controls',len(names))
if __name__=='__main__':run()
