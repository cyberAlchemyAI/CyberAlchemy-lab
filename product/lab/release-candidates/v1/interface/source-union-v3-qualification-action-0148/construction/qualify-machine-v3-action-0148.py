"""Focused original Machine refusals and fresh source2 byte-stamp comparison.
Actual classes/functions/tests remain original. No callbacks/clocks are patched.
"""
import hashlib,importlib.util,json,sys,time,unittest,cProfile,pstats
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');I=ROOT/'product/lab/release-candidates/v1/interface';API=I/'api-session-source-v3-action-0148';OUT=Path('/tmp/cal-session-diagnostic-action-0148/machine-v3-qualification-0001');OUT.mkdir(mode=0o700)
start=time.monotonic();pin='d3a4b7f7116583700c11e059be4c931d84373433175f458f92ab0d1f779d69c9';profile='3b9d8a30c1700ce8bed1e1407d7320ab19a9cf569452fc7d52cdfb3967033cac'
def emit(v):
 with (OUT/'events.jsonl').open('a') as f:f.write(json.dumps({'elapsed_seconds':time.monotonic()-start,**v},sort_keys=True)+'\n');f.flush()
n='_cal_actual_machine_source3_action_0148';s=importlib.util.spec_from_file_location(n,API/'__init__.py',submodule_search_locations=[str(API)]);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m)
g=__import__(n+'.guard',fromlist=['verify']);emit({'phase':'entry-history-guard'});g.verify(pin)
b=__import__(n+'.test_custody_sessions',fromlist=['Sessions']);b.PROFILE=profile;b.SOURCE=pin
mt=__import__(n+'.test_machine_transport',fromlist=['MachineTransport']);cls=mt.MachineTransport
names=['test_03_signed_proof_replay_refused','test_06_public_Actor_spoof_does_not_change_trusted_identity','test_07_real_effect_request_refused_before_journal_claim','test_10_real_policy_revocation_invalidates_credential']
# Original class setup once. Direct original TestCase.run does original per-case
# setUp/tearDown/cleanup. Original class cleanup runs in finally, including its
# unchanged signed source exit callbacks. No fixture helper is overridden.
emit({'phase':'original-class-setup','methods':names});cls.setUpClass()
try:
 selected=cls.view.custody_signed_sources;old=selected.original_entrypoint_source
 stamps={'records_byte_stamp_equal':selected.record_stamp(selected.records)==old.record_stamp(old.records),'schemas_byte_stamp_equal':selected.schema_stamp(selected.schemas)==old.schema_stamp(old.schemas),'signed_transaction_original_bindings_equal':selected.original_bindings==old.original_bindings,'source_cut_equal':selected.source_cut==old.source_cut,'actual_original_entrypoint_module':type(selected.original_entrypoint_reader).__module__,'records_stamp_sha256':hashlib.sha256(selected.record_stamp(selected.records)).hexdigest(),'schemas_stamp_sha256':hashlib.sha256(selected.schema_stamp(selected.schemas)).hexdigest()}
 assert all(stamps[k] is True for k in ['records_byte_stamp_equal','schemas_byte_stamp_equal','signed_transaction_original_bindings_equal','source_cut_equal'])
 prof=cProfile.Profile();p0=time.monotonic();prof.enable();selected.guard();prof.disable();stamps['fresh_guard_seconds']=time.monotonic()-p0;prof.dump_stats(OUT/'current-source2-guard.profile')
 with (OUT/'current-source2-guard-profile.txt').open('x') as f:pstats.Stats(prof,stream=f).sort_stats('cumulative').print_stats(35)
 (OUT/'source-preservation.json').write_text(json.dumps(stamps,indent=2,sort_keys=True)+'\n');emit({'phase':'fresh-source2-preservation-and-measurement',**stamps})
 with (OUT/'tests.log').open('x') as stream:
  result=unittest.TextTestRunner(stream=stream,verbosity=2)._makeResult()
  for name in names:
   emit({'phase':'actual-original-method','method':name});cls(name).run(result)
finally:cls.doClassCleanups()
assert not cls._class_cleanups and not cls.tearDown_exceptions
emit({'phase':'exit-history-guard'});g.verify(pin)
wire=cls.events;machine=cls.machine_events
(OUT/'wire.json').write_text(json.dumps({'parent_calls':wire,'machine_calls':machine},indent=2,sort_keys=True)+'\n')
report={'result':'PASS' if result.wasSuccessful() and result.testsRun==len(names) else 'FAIL','actual_methods':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'original_test_bodies_assertions_callbacks_clocks_changed':False,'actual_parent_public_calls':len(wire),'actual_machine_public_calls':len(machine),'source_sha256':pin,'profile_sha256':profile,'full_history_source_entry_exit_passed':True,'actual_original_class_cleanup_completed':True,'source_preservation_binding':{'path':str(OUT/'source-preservation.json'),'sha256':hashlib.sha256((OUT/'source-preservation.json').read_bytes()).hexdigest()},'elapsed_seconds':time.monotonic()-start,'authority_effect':'none','actual_owner_outcome':None,'claim_ceiling':'Four focused original Machine refusals and actual current-source2 facts equality/guard measure; common34 port requires fresh qualification.'}
(OUT/'qualification.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report),flush=True)
