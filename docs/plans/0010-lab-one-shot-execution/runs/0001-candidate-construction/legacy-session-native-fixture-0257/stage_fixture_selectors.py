"""Authored fixture selector successors, with every test AST delta declared."""
import ast,hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parent.parents[4];BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD=BASE/'api-integration-v14';NEW=OUT/'fixture-postimages'
def methods(raw):return {n.name:n for n in ast.walk(ast.parse(raw)) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def ast_sha(n):return hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()
def period(s):
 return s.replace("'2026-10-12T01:28:58.791379+00:00'","EXPECTED_NOT_BEFORE").replace("'2026-10-13T01:28:58.791379+00:00'","EXPECTED_EXPIRES_AT").replace("'2026-10-10T02:45:14.443492+00:00'","EXPECTED_PREVIOUS_EXPIRES_AT")+'        self.assertEqual(old,EXPECTED_ORIGINAL5_PERIOD)\n        self.assertTrue(verify_retained_original_period_chain(source))\n'
def origins(s):
 s=s.replace("HERE.parent/'current-source-adapter-v4/", "HERE.parent/EXPECTED_READER_ROOT/'")
 return s.replace("'product/lab/release-candidates/v1/interface/current-source-adapter-v4/reader.py#SelectedReader.open_signed'","EXPECTED_ENTRYPOINT")
names=['test_custody_sessions.py','test_custody_api.py','test_current_controls.py','test_termination_boundaries.py']
allowed={names[0]:{'test_29_source_and_period_unchanged','test_30_current_handler_profile_retains_all_original_contracts','test_31_frozen_producer_modules_retain_original_origins'},names[1]:{'test_01_same_original_reader_objects','test_04_actual_product_revision_witness','test_05_all10declared_source_connections_current','test_11_fixed_original_period_and_owned_host_scope'},names[2]:{'test_02_new_source_keeps_original_expired_period_exact','test_03_exact_current_profile_and_protocol_controls','test_04_actual_selected_reader_implementation','test_05_actual_guarded_byte_model_origin_and_body','test_06_actual_current_Service_selects_distinct_adapter_and_producer','test_07_exact_new_episode_Work_Product_and_ten_relations'},names[3]:set()}
ledger=[]
for name in names:
 raw=(OLD/name).read_text();original=methods(raw);lines=raw.splitlines(keepends=True)
 for method in sorted(original.values(),key=lambda n:n.lineno,reverse=True):
  s=''.join(lines[method.lineno-1:method.end_lineno]);m=method.name
  if name==names[0]:
   if m.startswith('test_29_'):s=period(s)
   elif m.startswith('test_30_'):s=s.replace('len(SUPPORTED),24','len(SUPPORTED),34')
   elif m.startswith('test_31_'):s=origins(s)+'        self.assertEqual(impl["code_binding"]["sha256"],EXPECTED_READER_SHA)\n'
  if name==names[1]:
   if m.startswith('test_01_'):s=s.replace('source.custody_delivery()','source.legacy_delivery()')
   elif m.startswith('test_04_'):s=s.replace("'product:cyberalchemy-lab@current-episode-0003.candidate.1'",'EXPECTED_PRODUCT_VERSION')
   elif m.startswith('test_05_'):s=s.replace("'typed-relation:R03-current-episode-0004:'",'EXPECTED_RELATION_PREFIX').replace("r['version_ref'].startswith(EXPECTED_RELATION_PREFIX)","r['version_ref'] in EXPECTED_RELATION_VERSIONS")
   elif m.startswith('test_11_'):s=period(s)
  if name==names[2]:
   if m.startswith('test_02_'):
    s=period(s).replace("'principal:R03-current-episode-0004'",'EXPECTED_PRINCIPAL')
   elif m.startswith('test_03_'):s=s.replace('len(SUPPORTED),24','len(SUPPORTED),34')
   elif m.startswith('test_04_'):s=origins(s)+'        self.assertEqual(evidence["code_binding"]["sha256"],EXPECTED_READER_SHA)\n'
   elif m.startswith('test_05_'):s=origins(s).replace("'custody-participation'",'PUBLIC_SOURCE_NAME')
   elif m.startswith('test_06_'):s=s.replace("'custody-participation'",'PUBLIC_SOURCE_NAME')
   elif m.startswith('test_07_'):s=s.replace("'typed-relation:R03-current-episode-0004:'",'EXPECTED_RELATION_PREFIX').replace("h['identity_ref'].startswith(EXPECTED_RELATION_PREFIX)","h['version_ref'] in EXPECTED_RELATION_VERSIONS")
  lines[method.lineno-1:method.end_lineno]=[s]
 new=''.join(lines)
 # These are authored fixture module/setup selectors. Method bodies above are
 # changed only by the independently declared exact selector edits.
 if name in names[:2]:
  new=new.replace('from .custody_context_sessions import stable_policy,R,D,EL','from .legacy_context_sessions import stable_policy,R,D,EL').replace('from .custody_context_sessions import D,R','from .legacy_context_sessions import D,R')
  new=new.replace("'custody-participation'",'PUBLIC_SOURCE_NAME')
 if name==names[2]:new=new.replace('from .custody_context_sessions import D,R','from .legacy_context_sessions import D,R')
 if name==names[3]:
  new=new.replace('from .custody_context_sessions import R','from .legacy_context_sessions import R').replace("'custody-participation'",'PUBLIC_SOURCE_NAME')
 new=new.replace('from .contextlib import ExitStack','from .contextlib import ExitStack')
 # CurrentControls scoped_service is a fixture helper outside the test methods.
 if name==names[2]:
  node=next(n for n in ast.walk(ast.parse(new)) if isinstance(n,ast.FunctionDef) and n.name=='scoped_service')
  ls=new.splitlines(keepends=True);part=''.join(ls[node.lineno-1:node.end_lineno]).replace("'custody-participation'",'PUBLIC_SOURCE_NAME');ls[node.lineno-1:node.end_lineno]=[part];new=''.join(ls)
 new='from .legacy_fixture_selection import *\n'+new
 actual=methods(new);changed={k for k in original if ast_sha(original[k])!=ast_sha(actual[k])};assert changed==allowed[name],(name,changed,allowed[name])
 p=NEW/name;p.write_text(new)
 ledger.append({'file':name,'old_file_sha256':hashlib.sha256(raw.encode()).hexdigest(),'new_file_sha256':hashlib.sha256(new.encode()).hexdigest(),'total_methods':len(original),'unchanged_method_ASTs':sorted(set(original)-changed),'selector_deltas':[{'method':k,'before_AST_sha256':ast_sha(original[k]),'after_AST_sha256':ast_sha(actual[k]),'reason':'Distinct independently signed legacy-v3 fixture identity/origin/period or original actual34 operation cardinality; clock/lease/refusal assertions retained.'} for k in sorted(changed)]})
with (OUT/'fixture-selector-ledger.json').open('x') as f:json.dump({'schema_version':'lab-authored-fixture-selector-deltas/v1-candidate','all_original_methods_passed':False,'qualification':False,'original5_renewed':False,'files':ledger},f,indent=2,sort_keys=True);f.write('\n')
