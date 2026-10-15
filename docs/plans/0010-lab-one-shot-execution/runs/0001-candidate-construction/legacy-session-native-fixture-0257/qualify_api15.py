"""Actual common API15 legacy fixture qualification; first refusal retained."""
import fcntl,hashlib,importlib.util,json,os,sys,tempfile,time
from pathlib import Path
OUT=Path(__file__).resolve().parent;RUN=OUT.parent;ROOT=RUN.parents[4];API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v15'
SOURCE='87a1b1971166c0dfd9517d060bd6bf9d3b643544da809d2e87e3bc432cc449ac';PROFILE='88f4c0bc7cdf5a2e455739a83975e4ddfc8e0381f19709d52fe710efeacffc9a'
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def boot(n,p):
 s=importlib.util.spec_from_file_location(n,p/'__init__.py',submodule_search_locations=[str(p)]);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m)
def main():
 assert not (OUT/'api15-proof.json').exists()
 fd=os.open(RUN/'final-api-regression-0173-0190.execution.lock',os.O_RDONLY|os.O_NOFOLLOW);fcntl.flock(fd,fcntl.LOCK_SH)
 start=time.monotonic();checks=[];entry=False;exit_ok=False;clean=False;status='FAIL';stage='full-source-entry';root=None;channel=None;service=None;calls=[]
 try:
  boot('_cal_actual_legacy_api15_0257',API);G=__import__('_cal_actual_legacy_api15_0257.guard',fromlist=['verify']);G.verify(SOURCE);entry=True
  P=__import__('_cal_actual_legacy_api15_0257.protocol',fromlist=['Schemas']);F=__import__('_cal_actual_legacy_api15_0257.example_fixture',fromlist=['provision']);A=__import__('_cal_actual_legacy_api15_0257.auth',fromlist=['ReaderChannel']);S=__import__('_cal_actual_legacy_api15_0257.service',fromlist=['Service']);C=__import__('_cal_actual_legacy_api15_0257.legacy_context_sessions',fromlist=['D']);schemas=P.Schemas(PROFILE)
  stage='actual-native-source'
  with P.source.replay_source('legacy-session-fixture') as view:
   assert P.source.legacy_session_view(view) and view.custody_signed_sources is view.legacy_signed_sources
   assert type(view) is C.D.reader.Inspection and type(view.legacy_signed_sources) is C.D.reader.adapter.SignedSources
   checks.append({'case':stage,'result':'PASS','actual_signed_store_ref':view.legacy_signed_sources.source_cut['store_ref'],'actual_public_selector':'legacy-session-fixture','retained_internal_ABI':'custody-participation'})
   materials,metadata,target=F.materials_for(view)
   with tempfile.TemporaryDirectory(prefix='cal-legacy-session-fixture-0257-public-') as tmp:
    root=Path(tmp);root.chmod(0o700);stage='fresh-private-grant'
    refresh=__import__('_cal_actual_legacy_api15_0257.projection_refresh',fromlist=['control'])
    key,path,pin=F.provision(root,'legacy-session-fixture',materials,metadata,principal=C.R.PRINCIPAL,projection_control=refresh.control(view))
    policy=P.frame_parse(path.read_bytes());valid=schemas.valid('reader-authentication',policy)
    checks.append({'case':'actual-authentication-policy-schema','result':'PASS' if valid else 'FAIL','actual_valid':valid,'policy_bytes_recorded':False,'selected_schema_binding':bind(API/'authentication.schema.json')})
    stage='actual-ReaderChannel-construction'
    try:
     channel=A.ReaderChannel(path,pin,schemas);channel.authenticate(F.proof(key,channel.challenge));service=S.Service(view,channel,schemas)
     stage='public-lab-status';request=F.call(channel.context,'lab.status',__import__('_cal_actual_legacy_api15_0257.handlers',fromlist=['cut']).cut(view));raw=P.compact(request)
     record={'original_request':request,'request_sha256':P.source.sha(raw),'reply':None};calls.append(record)
     with (OUT/'api15-events.jsonl').open('a') as log:log.write(json.dumps({'phase':'attempt',**record})+'\n');log.flush()
     record['reply']=service.call(raw)
     with (OUT/'api15-events.jsonl').open('a') as log:log.write(json.dumps({'phase':'returned',**record})+'\n');log.flush()
     assert record['reply']['kind']=='result';status='PASS'
    finally:
     if service is not None:service.close()
     if channel is not None:channel.close()
     key=None
   clean=not root.exists()
 except BaseException as error:
  static=str(error) if str(error) in ('reader policy schema differs','actual independent legacy SignedSources/Inspection required') else None
  checks.append({'case':stage,'result':'FAIL','error_class':type(error).__name__,'static_require_message':static});status='FAIL'
 finally:
  if root is not None:clean=not root.exists()
  try:
   if 'G' in locals():G.verify(SOURCE);exit_ok=True
  finally:
   result={'schema_version':'lab-independent-legacy-common-API-proof/v1-candidate','result':status,'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),'caller_binding':bind(Path(__file__).resolve()),'checks':checks,'actual_public_call_count':len(calls),'full15entry':entry,'full15exit':exit_ok,'owned_root':str(root) if root else None,'owned_private_root_absent':clean,'duration_seconds':time.monotonic()-start,'fixture_only':True,'whole_Context_Session_Machine_lifecycle_qualified':False,'authority_effect':'none','actual_owner_outcome':None}
   with (OUT/'api15-proof.json').open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
   fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
 print(json.dumps({'result':status,'proof_binding':bind(OUT/'api15-proof.json')}),flush=True)
 return 0 if status=='PASS' and exit_ok and clean else 1
if __name__=='__main__':raise SystemExit(main())
