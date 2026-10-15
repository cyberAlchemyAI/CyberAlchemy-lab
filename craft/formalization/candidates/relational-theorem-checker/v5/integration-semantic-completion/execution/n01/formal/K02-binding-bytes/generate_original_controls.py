"""Use exact original byte fixtures and separate typed-record expectations; no authentication claim."""
from pathlib import Path
import hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[9];SRC=HERE.parent/'K02-binding-records/generate_controls.py'
spec=importlib.util.spec_from_file_location('original_record_literals',SRC);literal=importlib.util.module_from_spec(spec);spec.loader.exec_module(literal)
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def raw_ast(x):
 if x is None:return '.null'
 if isinstance(x,bool):return '.boolean '+('true' if x else 'false')
 if isinstance(x,int):return '(.number '+json.dumps(str(x))+')'
 if isinstance(x,str):return '(.string ['+','.join(str(ord(c)) for c in x)+'])'
 if isinstance(x,list):return '(.array ['+','.join(raw_ast(v) for v in x)+'])'
 if isinstance(x,dict):return '(.object ['+','.join('(['+','.join(str(ord(c)) for c in k)+'],'+raw_ast(v)+')' for k,v in x.items())+'])'
 raise ValueError(x)
def run():
 lines=['import CaptureBytesCatalog','set_option autoImplicit false','set_option maxRecDepth 65536','set_option maxHeartbeats 10000000','namespace RelationalSuccessor.CandidateBindingBytes.Controls'];names=[];fixtures=[]
 for kind,typ in [('resolution','CandidateIntentAddressing.Resolution'),('role','CandidateIntentAddressing.Role')]:
  file=HERE.parent/f'K02-pipeline/schemas/{kind}-binding.fixture.json';original=file.read_bytes();expected=json.loads(original)
  lines.extend([f'def {kind}Bytes : CandidateJsonBytes.Bytes := ['+','.join(map(str,original))+']',f'def {kind}Expected : CandidateBindingRecords.Record {typ} := '+literal.record(kind,expected)])
  function='decodeResolutionBytes' if kind=='resolution' else 'decodeRoleBytes'
  lines.extend([f'def {kind}Raw : CandidateJsonBytes.RawValue := '+raw_ast(expected),f'def {kind}Ast : J := '+literal.ast(expected)])
  name=f'original_{kind}_raw_bytes_accept';names.append(name)
  lines.append(f'theorem {name} : CandidateJsonParser.parseDocumentBytes {kind}Bytes = some {kind}Raw := by rfl')
  name=f'original_{kind}_scalar_conversion_accept';names.append(name)
  helper=',CandidateScalarConversion.convertValues' if kind=='resolution' else ''
  lines.extend([f'theorem {name} : CandidateScalarConversion.convertValue {kind}Raw = some {kind}Ast := by',f'  simp only [{kind}Raw,CandidateScalarConversion.convertValue,CandidateScalarConversion.convertEntries{helper},Option.bind_some] <;> rfl'])
  name=f'original_{kind}_bytes_accept';names.append(name)
  lines.extend([f'theorem {name} : {function} {kind}Bytes = some {kind}Expected := by',f'  simp only [{function},decodeRecordBytes,CandidateScalarConversion.parseScalarDocumentBytes,original_{kind}_raw_bytes_accept,Option.bind_some,original_{kind}_scalar_conversion_accept]', '  decide'])
  fixtures.append({'kind':kind,'original_bytes':binding(file),'byte_length':len(original),'typed_expected_record_from_fixture':True,'synthetic_reference_and_review_roots':True})
 lines+=['#print axioms '+name for name in names]+['end RelationalSuccessor.CandidateBindingBytes.Controls']
 (HERE/'OriginalByteControls.lean').write_text('\n\n'.join(lines)+'\n')
 (HERE/'original-byte-controls.json').write_text(json.dumps({'task':'N01','unit':'K02-binding-bytes','generator':binding(Path(__file__)),'typed_literal_generator':binding(SRC),'fixtures':fixtures,'controls':binding(HERE/'OriginalByteControls.lean'),'worked_control_declarations':len(names),'original_fixture_bytes_used':True,'bytes_not_replaced_by_AST_literals':True,'typed_expectation_translation_proved':False,'authenticated_capture_proved':False,'inherited_discharges':0},indent=2)+'\n')
 print('Generated',len(names),'kernel controls using exact original byte fixtures.')
if __name__=='__main__':run()
