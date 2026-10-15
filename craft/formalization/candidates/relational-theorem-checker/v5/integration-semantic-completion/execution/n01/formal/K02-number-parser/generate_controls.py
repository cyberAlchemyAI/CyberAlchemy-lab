"""Generate explicit raw-token controls; the Python translator/reference is not proved."""
from pathlib import Path
from decimal import Decimal
import hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[9]
SOURCE=HERE.parent/'K02-numeric/numeric-corpus.json'

def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def reject(value):raise ValueError(value)
def expected(token):
    if token!=token.strip():return None
    try:value=json.loads(token,parse_float=Decimal,parse_int=int,parse_constant=reject)
    except (ValueError,ArithmeticError):return None
    if isinstance(value,bool) or not isinstance(value,(int,Decimal)):return None
    n,d=Decimal(value).as_integer_ratio()
    return n//d if n>=0 and n%d==0 else None

def run():
    source=json.loads(SOURCE.read_text())
    rows=['import NumberEpochAst','set_option autoImplicit false','namespace RelationalSuccessor.CandidateNumberParser.Controls','open RelationalSuccessor.CandidateNumberParser','open RelationalSuccessor.CandidateDecimal','']
    names=[];cases=[]
    inputs=[(c['name'],c['token']) for c in source['cases']]+[('ignored_suffix','42garbage'),('second_exponent','42e1e1'),('second_fraction','42.0.0'),('leading_line_break','\n42'),('negative_leading_zero','-01'),('fraction_without_integer','.42'),('large_exact_decimal','9007199254740993.0')]
    for name,token in inputs:
        want=expected(token)
        output='none' if want is None else f'some {want}'
        rows.extend([f'theorem {name} : decodeEpochAst (.number {json.dumps(token,ensure_ascii=False)}) = {output} := by decide',''])
        names.append(name);cases.append({'name':name,'token':token,'expected_epoch':want})
    extras=[('string_is_not_number','decodeEpochAst (.string "42") = none','by decide'),('boolean_is_not_number','decodeEpochAst (.boolean true) = none','by decide'),('null_is_not_number','decodeEpochAst .null = none','by decide'),('equivalent_spellings_same_epoch','decodeEpochAst (.number "42") = decodeEpochAst (.number "4.2e1")','by decide'),('fraction_has_valid_syntax','∃ parts, parseToken "0.5" = some parts','⟨⟨false,[0],some [5],none⟩,by decide⟩'),('raw_independent_epoch_meaning','TokenEpochMeaning "4.2e1" 42','(token_epoch_exact "4.2e1" 42).mp scaled_positive_exponent'),('adapter_uses_total_number_parser','epochAdapter.decode (.number "42.0") = some 42','by decide')]
    for name,expr,proof in extras:
        rows.extend([f'theorem {name} : {expr} := {proof}','']);names.append(name)
    rows.extend(f'#print axioms {name}' for name in names)
    rows.extend(['end RelationalSuccessor.CandidateNumberParser.Controls',''])
    (HERE/'NumberParserControls.lean').write_text('\n'.join(rows))
    corpus={'task':'N01','unit':'K02-number-parser','cases':cases,'case_count':len(cases),'worked_proof_controls':len(names),'source_corpus':binding(SOURCE),'generator':binding(Path(__file__)),'claim_scope':'Synthetic explicit raw-number AST controls and exact Decimal expected values. This generator/reference is not a proved byte/parser bridge.','byte_parser_proved':False,'inherited_discharges':0}
    (HERE/'number-parser-corpus.json').write_text(json.dumps(corpus,indent=2,ensure_ascii=False)+'\n')
    capture={'task':'N01','unit':'K02-number-parser','method':'Synthetic retained number AST lexemes with independently exact Decimal expected values; generator translation not proved.','generator':binding(Path(__file__)),'controls':binding(HERE/'NumberParserControls.lean'),'corpus':binding(HERE/'number-parser-corpus.json'),'original_numeric_corpus':binding(SOURCE),'numeric_reference_audit':binding(HERE.parent/'K02-numeric/numeric-reference-audit.json'),'captured_context_is_synthetic':True,'byte_parser_proved':False,'schema_AST_correspondence_proved':False,'authenticated_capture_proved':False,'inherited_discharges':0}
    (HERE/'source-capture.json').write_text(json.dumps(capture,indent=2)+'\n')
    print('raw number cases',len(cases),'worked controls',len(names))

if __name__=='__main__':run()
