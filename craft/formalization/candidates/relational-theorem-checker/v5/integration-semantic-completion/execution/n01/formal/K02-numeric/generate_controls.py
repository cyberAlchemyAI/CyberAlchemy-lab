"""Generate explicit synthetic grammar/value proof controls; this generator is not proved."""
from pathlib import Path
from decimal import Decimal
import json,re,hashlib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[9]

def binding(path):return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def digits(t):return '['+','.join(t)+']'
def parts(token):
    matched=re.fullmatch(r'(-?)(0|[1-9][0-9]*)(?:\.([0-9]+))?(?:([eE])([+-]?)([0-9]+))?',token)
    assert matched,token
    sign,integer,fraction,marker,exp_sign,exp_digits=matched.groups()
    fraction_text='none' if fraction is None else f'(some {digits(fraction)})'
    exp_text='none' if marker is None else '(some ⟨'+('true' if marker=='E' else 'false')+',.'+{'':'unsigned','+':'plus','-':'minus'}[exp_sign]+','+digits(exp_digits)+'⟩)'
    return '⟨'+('true' if sign else 'false')+','+digits(integer)+','+fraction_text+','+exp_text+'⟩'

def expected(token):
    value=Decimal(token)
    numerator,denominator=value.as_integer_ratio()
    return numerator//denominator if numerator>=0 and numerator%denominator==0 else None

def run():
    controls=[('ordinary_integer','42'),('integral_decimal','42.0'),('scaled_positive_exponent','4.2e1'),('scaled_negative_exponent','420e-1'),('zero_integer','0'),('negative_zero','-0'),('negative_decimal_zero','-0.0'),('signed_upper_exponent','42E+000'),('unsigned_upper_exponent','4.2E1'),('negative_exponent_zero','0E-00004'),('fraction_is_not_epoch','0.5'),('negative_nonzero','-42'),('negative_exponent_fraction','42e-1'),('fraction_and_exponent_cancel','0.42e2'),('negative_fraction','-0.5'),('negative_scaled_integer','-4.2e1'),('integral_trailing_zeroes','42.000'),('tiny_nonzero_fraction','42.0000000000000001'),('beyond_float_exact_integer','9007199254740993'),('large_exact_power','1e20'),('signed_positive_exponent','2E+3'),('minus_zero_exponent','42e-0'),('fraction_at_zero_epoch','0.000e-12'),('huge_positive_exponent_zero','0e1000000000000'),('huge_negative_exponent_zero','-0e-1000000000000')]
    malformed=[('empty_integer','', '⟨false,[],none,none⟩'),('leading_zero_integer','01','⟨false,[0,1],none,none⟩'),('empty_fraction','42.','⟨false,[4,2],some [],none⟩'),('empty_exponent','42e','⟨false,[4,2],none,some ⟨false,.unsigned,[]⟩⟩'),('empty_plus_exponent','42e+','⟨false,[4,2],none,some ⟨false,.plus,[]⟩⟩'),('empty_minus_exponent','42e-','⟨false,[4,2],none,some ⟨false,.minus,[]⟩⟩'),('out_of_range_digit','?','⟨false,[10],none,none⟩')]
    rows=['import DecimalGrammar','set_option autoImplicit false','namespace RelationalSuccessor.CandidateDecimal.Controls','open RelationalSuccessor.CandidateDecimal','']
    names=[];cases=[]
    def case(name,token,p,want,valid_syntax):
        value='none' if want is None else f'some {want}'
        rows.extend([f'def {name}Parts : Parts := {p}',f'theorem {name} : decodeWitness (.number {json.dumps(token)}) {name}Parts = {value} := by decide',''])
        names.append(name);cases.append({'name':name,'token':token,'expected_epoch':want,'expected_JSON_number_syntax':valid_syntax})
    for name,token in controls:case(name,token,parts(token),expected(token),True)
    for name,token,p in malformed:case(name,token,p,None,False)
    for name,token in [('unicode_digit','٤٢'),('leading_plus','+42'),('leading_space',' 42'),('trailing_space','42 '),('not_a_number','NaN'),('infinity','Infinity'),('different_number','43')]:
        case(name,token,'ordinary_integerParts',None,False if name!='different_number' else True)
        cases[-1]['scope']='Refuses this supplied witness by exact token mismatch; no universal raw-token parser claim.'
    extra=[('string_is_not_number','decodeWitness (.string "42") ordinary_integerParts = none','by decide'),('boolean_is_not_number','decodeWitness (.boolean true) ordinary_integerParts = none','by decide'),('null_is_not_number','decodeWitness .null ordinary_integerParts = none','by decide'),('equivalent_spellings_same_epoch','decodeWitness (.number "42") ordinary_integerParts = decodeWitness (.number "4.2e1") scaled_positive_exponentParts','by decide'),('ordinary_independent_value','EpochMeaning ordinary_integerParts 42','(decode_parts_exact ordinary_integerParts 42).mp (by decide)'),('scaled_independent_value','EpochMeaning scaled_positive_exponentParts 42','(decode_parts_exact scaled_positive_exponentParts 42).mp (by decide)'),('negative_zero_independent_value','EpochMeaning negative_zeroParts 0','(decode_parts_exact negative_zeroParts 0).mp (by decide)')]
    for name,expr,proof in extra: rows.extend([f'theorem {name} : {expr} := {proof}','']);names.append(name)
    rows.extend(f'#print axioms {name}' for name in names)
    rows.extend(['end RelationalSuccessor.CandidateDecimal.Controls',''])
    (HERE/'DecimalControls.lean').write_text('\n'.join(rows))
    corpus={'task':'N01','unit':'K02-numeric','cases':cases,'worked_proof_controls':len(names),'claim_scope':'Explicit synthetic AST witness/value controls; token substitution controls do not constitute a total lexical parser.','generator':binding(Path(__file__)),'byte_parser_proved':False,'raw_number_token_parser_proved':False,'inherited_discharges':0}
    (HERE/'numeric-corpus.json').write_text(json.dumps(corpus,indent=2,ensure_ascii=False)+'\n')
    capture={'task':'N01','unit':'K02-numeric','method':'Synthetic exact decimal witnesses and expected mathematical values; generated translation is not proved.','generator':binding(Path(__file__)),'controls':binding(HERE/'DecimalControls.lean'),'corpus':binding(HERE/'numeric-corpus.json'),'resolution_schema':binding(HERE.parent/'K02-pipeline/schemas/resolution-binding.schema.json'),'role_schema':binding(HERE.parent/'K02-pipeline/schemas/role-binding.schema.json'),'captured_context_is_synthetic':True,'raw_number_token_parser_proved':False,'byte_parser_proved':False,'schema_AST_correspondence_proved':False,'inherited_discharges':0}
    (HERE/'source-capture.json').write_text(json.dumps(capture,indent=2)+'\n')
    print('worked controls',len(names),'number witness cases',len(cases))

if __name__=='__main__':run()
