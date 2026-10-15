"""Generate finite Unicode boundary controls from an independent strict UTF-16 reference."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
CASES=[[],[0],[8,9,10,13],[34,92],[65],[55295],[57344],[65535],
 [55296,56320],[56319,57343],[55357,56832],[65,55357,56832,66],
 [55296],[56319],[56320],[57343],[55296,65],[55296,55296],
 [56320,55296],[65536],[1114112],[4294967296],[65,55296],
 [55296,56320,55296],[55296,56320,56320],[55296,56320,55296,56320],
 [55295,57344],[56319,56320],[55296,57343],[0,55296,56320,0],
 [55357,56832,55357,56832],[55296,56320,65536],[55296,65536],[57344,55296,56320]]
def codes(xs):return '['+','.join(map(str,xs))+']'
def chars(xs):return 'String.ofList ['+','.join('Char.ofNat '+str(x) for x in xs)+']'
lines=['import ScalarDocumentComposition','set_option autoImplicit false','namespace RelationalSuccessor.CandidateScalarConversion'];rows=[];names=[]
for i,units in enumerate(CASES):
 try:
  text=b''.join(x.to_bytes(2,'little') for x in units).decode('utf-16-le',errors='strict')
  scalar=[ord(c) for c in text];rhs='some ('+chars(scalar)+')';status='supported'
 except (OverflowError,UnicodeDecodeError):scalar=None;rhs='none';status='unsupported'
 name=f'string_control_{i:02}';names.append(name);lines.append(f'theorem {name} : decodeString {codes(units)} = {rhs} := by rfl')
 rows.append({'units':units,'reference_outcome':status,'reference_scalars':scalar,'theorem':name})
controls=[
 ('nested_array_unsupported','convertValue (.array [.null,.string [55296]]) = none'),
 ('nested_object_key_unsupported','convertValue (.object [([55296],.null)]) = none'),
 ('nested_object_value_unsupported','convertValue (.object [([97],.string [56320])]) = none'),
 ('duplicate_entries_retained','convertValue (.object [([97],.null),([97],.boolean true)]) = some (.object [("a",.null),("a",.boolean true)])'),
 ('nested_valid_pair','convertValue (.array [.string [55357,56832],.number "-0.00e+000"]) = some (.array [.string "😀",.number "-0.00e+000"])'),
]
for name,goal in controls:
 names.append(name); helper='convertValues' if 'array' in name or name=='nested_valid_pair' else 'convertEntries'
 lines.extend([f'theorem {name} : {goal} := by',f'  simp only [convertValue,{helper},Option.bind_some] <;> rfl'])
name='escaped_unpaired_is_unsupported';names.append(name);lines.extend([
 f'theorem {name} : classifyBytes [34,92,117,100,56,48,48,34] = .unsupportedScalar (.string [55296]) := by',
 '  unfold classifyBytes',
 '  change (match convertValue (.string [55296]) with | none => ConversionOutcome.unsupportedScalar (.string [55296]) | some value => .converted value) = .unsupportedScalar (.string [55296])',
 '  simp only [convertValue]','  rfl'])
name='malformed_utf8_is_invalid';names.append(name);lines.append(f'theorem {name} : classifyBytes [34,255,34] = .invalidSyntax := by rfl')
name='different_key_spellings_retained';names.append(name)
bytecodes=list(b'{"a":null,"\\u0061":true}')
lines.extend([f'theorem {name} : parseScalarDocumentBytes {codes(bytecodes)} = some (.object [("a",.null),("a",.boolean true)]) := by',
 '  unfold parseScalarDocumentBytes',
 '  change convertValue (.object [([97],.null),([97],.boolean true)]) = some (.object [("a",.null),("a",.boolean true)])',
 '  exact duplicate_entries_retained'])
name='decoded_duplicate_binding_key_refused';names.append(name);lines.extend([
 f'theorem {name} : CandidateJsonSource.decodeObject ["a"] (.object [("a",.null),("a",.boolean true)]) = none := by rfl'])
lines += ['#print axioms '+name for name in names]+['end RelationalSuccessor.CandidateScalarConversion']
(HERE/'ScalarConversionControls.lean').write_text('\n\n'.join(lines)+'\n')
(HERE/'reference-controls.json').write_text(json.dumps({'reference':'Python strict utf-16-le decoding; units outside the 16-bit range refuse before decoding','reference_string_cases':len(rows),'rows':rows,'structural_and_byte_controls':names[len(rows):],'control_declarations':len(names),'coverage':'Finite Unicode/representation boundaries complement quantified proofs; not a resource or external-standard conformance qualification.','inherited_discharges':0},indent=2)+'\n')
print('Generated',len(names),'controls;',len(rows),'strict UTF-16 reference cases.')
