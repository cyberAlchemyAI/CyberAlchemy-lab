"""Construction-only fresh native cold×2 and Context; never imports API74.

The installer mints a private construct-context selection. This process exits
before final metadata pins/receipt become ready. No callbacks are patched.
"""
import argparse,hashlib,importlib.util,json,os,sys,time,uuid
from datetime import datetime,timezone,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
# The selected native interpreter's dependency location is fixed by the private
# installer layout; its full1010 verification is the trusted launcher's job.
NATIVE=ROOT.parent/'.cal-runtime/native';sys.path.insert(0,str(NATIVE/'deps'));sys.path.insert(0,str(HERE))
import metadata as M
import cold_original_batch_0001 as ORIGINAL_BATCH

def package(name,path):
 spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)]);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod
 try:spec.loader.exec_module(mod)
 except BaseException:
  if sys.modules.get(name) is mod:del sys.modules[name]
  raise
 return mod

def selected_provider(receipt_pin):
 """Use only the selection the independently verified launcher activated."""
 P=sys.modules.get('cal_installed_runtime_selection_v1')
 M.need(P is not None,'trusted construction bootstrap has not activated a provider')
 selected=P.current()
 M.need(selected.receipt_pin==receipt_pin and selected.phase=='construct-context' and selected.purpose=='construct-context','construction bootstrap receipt or purpose differs')
 M.need(P.root()==ROOT,'construction bootstrap selects another repository')
 P.guard()
 return P

def main(receipt_pin):
 need=M.need
 P=selected_provider(receipt_pin)
 P.guard();family_source=P.binding('family.source');family=ROOT/Path(family_source['path']).parent.parent
 name='_cal_portable_native_construction_'+uuid.uuid4().hex;package(name,family/'source')
 C=__import__(name+'.cold',fromlist=['*']);B=__import__(name+'.base',fromlist=['*']);R=__import__(name+'.records',fromlist=['*'])
 pin=family_source['sha256'];pkg=P.binding('family.source_package')['sha256'];cuts=[];roots=[];started=time.monotonic()
 for unused in range(2):
  with C.open_source(pin,pkg) as view:
   roots.append(view.root);now=datetime.now(timezone.utc);need(datetime.fromisoformat(view.period['not_before'])<=now<datetime.fromisoformat(view.period['expires_at']),'actual Source period expired during installed cold proof')
   need(datetime.fromisoformat(view.period['expires_at'])-datetime.fromisoformat(view.period['not_before'])==timedelta(hours=24),'retained fixed Source period changed')
   for identity in (R.PRINCIPAL,R.PROFILE,R.ASSIGNMENT,R.IMPLEMENTATION,R.WORK,R.CONTEXT):need(view.data['projection']['subjects'][identity+'@'+R.VERSION]['effective_state']=='local-admitted-current','installed original record currentness differs')
   ORIGINAL_BATCH.verify(view,B,family)
   cuts.append((view.data['head']['transaction_digest'],view.handle.common.digest(view.data['projection'])))
 need(cuts[0]==cuts[1] and all(not r.exists() for r in roots),'installed independent cold parity or cleanup differs');B.verify_source(pin)
 binding=lambda path:{'path':str(path.relative_to(ROOT)),'sha256':M.sha(M.capture(path))}
 observation={'result':'PASS-native-cold','independent_cold_replays':2,'original_byte_parity':True,'original_byte_parity_method':'original custody.content_rows per independent verified cut','owned_cold_roots_removed':True,'source_binding':binding(family/'source/source-manifest.json'),'package_binding':binding(family/'source/packages/0001/manifest.json'),'period_binding':binding(family/'source/packages/0001/period.json'),'private_signer_removed':B.load(family/'source/packages/0001/build-result.json')['owned_store_and_key_removed'],'fixture_only':True,'actual_human_review':False,'authority_effect':'none','actual_owner_outcome':None,'public_API_qualified':False}
 # The cold target is null in construction selection until this real outcome.
 selected=P.current();cold_path=ROOT/selected.package['binding_paths']['family.cold'];need(cold_path.relative_to(ROOT).as_posix() in selected.package['generated_metadata_paths'],'cold proof output outside declared metadata')
 cold_path.parent.mkdir(parents=True,exist_ok=True);cold_path.write_bytes(M.encoded({'observation':observation,'actual_native_seconds':time.monotonic()-started,'authority_effect':'none'}));cold_path.chmod(0o644)
 # Delete only the declared derived Context outputs in this owned private
 # stage. OriginalSource26, Mapper events and signed history are untouched.
 context_output=family/'context/packages/0001';allowed=set(selected.package['generated_metadata_paths'])
 for path in sorted(context_output.rglob('*'),key=lambda p:len(p.parts),reverse=True):
  if path.is_dir():path.rmdir()
  else:need(path.relative_to(ROOT).as_posix() in allowed and not path.is_symlink(),'undeclared Context stage output');path.unlink()
 context_output.rmdir()
 dname='_cal_portable_context_construction_'+uuid.uuid4().hex;package(dname,family/'context');D=__import__(dname+'.build',fromlist=['*'])
 result=D.build(P.binding('family.context_source')['sha256'],P.binding('family.mapper_package')['sha256'])
 P.guard()
 return {'result':'PASS-construction-native-cold-and-fresh-Context','cold_observation':observation,'Context_observation':result,'final_ready_receipt_emitted':False,'original_Source_Artifact_bodies_changed':False,'authority_effect':'none'}
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--receipt-pin',required=True);args=parser.parse_args();print(json.dumps(main(args.receipt_pin),sort_keys=True),flush=True)
