import argparse, json, os, sys, traceback, types, unittest
from pathlib import Path
from test_support import B, P, Fixture


class StartupTests(unittest.TestCase):
    def fixture(self, **kw):
        value = Fixture(TEMP, **kw); self.addCleanup(value.close); return value
    def test_complete_source8_chain_and_exact_cleanup(self):
        f=self.fixture(); result=f.startup().run()
        self.assertIsNone(result.primary_code, result.public()); self.assertEqual(result.cleanup_codes, ())
        self.assertEqual(result.effect_state,'owned-inert'); self.assertFalse(result.actual_startup_qualified)
        self.assertEqual(f.event_list(), ['protected-reader','protected-verify','schemas','source-enter','mapper',
            'channel','authenticate','service','context-generate',
            'sessions-close','handlers-close','channel-close','source-exit'])
    def test_complete_legacy_is_distinct(self):
        f=self.fixture(family='legacy-source8-20261018-b'); r=f.startup().run()
        self.assertIsNone(r.primary_code,r.public()); self.assertEqual(r.cleanup_codes,())
    def test_selection_external_anchor(self):
        f=self.fixture()
        with self.assertRaises(P.Refusal): B.Startup(f.custody,f.raw,'0'*64)
        self.assertEqual(f.event_list(),[])
    def test_fixture_cannot_promote_actual(self):
        f=self.fixture(); f.selection['posture']='actual'; f.reseal()
        with self.assertRaises(P.Refusal): f.startup()
        self.assertEqual(f.event_list(),[])
    def test_family_unknown_no_fallback(self):
        f=self.fixture(); f.selection['family']='source8'; f.reseal()
        with self.assertRaises(P.Refusal): f.startup()
    def test_family_changed_consistently_still_original_producer_refusal(self):
        f=self.fixture(); f.selection['family']='legacy-source8-20261018-b'; f.reseal()
        r=f.startup().run(); self.assertIsNotNone(r.primary_code); self.assertNotIn('channel',f.event_list())
    def test_metadata_policy_cannot_satisfy_sessions(self):
        f=self.fixture(config={'metadata':True}); r=f.startup().run()
        self.assertIsNotNone(r.primary_code); self.assertNotIn('service',f.event_list())
        self.assertEqual(f.event_list(),[])
    def test_sessions_none_refuses_and_cleans_returned_host(self):
        f=self.fixture(config={'sessions_none':True}); r=f.startup().run()
        self.assertIsNotNone(r.primary_code); self.assertIn('handlers-close',f.event_list())
        self.assertNotIn('context-generate',f.event_list())
    def test_plan_v1_does_not_satisfy_bridge(self):
        f=self.fixture(family='legacy-source8-20261018-b',role='installation-metadata',config={'plan_v1':True}); r=f.startup().run()
        self.assertIsNotNone(r.primary_code); self.assertNotIn('verify-environment',f.event_list())
    def test_preloaded_lookalike_origin_refuses_before_effect(self):
        f=self.fixture(); row=f.selection['modules']['modules'][0]
        forged=types.ModuleType(row['name']); forged.__file__=f.inputs.path(row['file_id'])
        forged.__spec__=__import__('importlib.util',fromlist=['spec_from_file_location']).spec_from_file_location(row['name'],forged.__file__)
        sys.modules[row['name']]=forged
        with self.assertRaises(P.Refusal): f.startup()
        self.assertIs(sys.modules[row['name']],forged); self.assertEqual(f.event_list(),[])
    def test_missing_required_role(self):
        f=self.fixture(); f.selection['modules']['modules']=[r for r in f.selection['modules']['modules'] if r['role']!='release']; f.reseal()
        with self.assertRaises(P.Refusal): f.startup()
    def test_source_substitution_after_selection_before_import(self):
        f=self.fixture(); startup=f.startup(); (f.root/'code/common.py').write_bytes(b'raise RuntimeError("PRIVATE")')
        result=startup.run(); self.assertEqual(result.effect_state,'none'); self.assertEqual(f.event_list(),[])
    def test_cold_runtime_omission(self):
        f=self.fixture(); f.selection['cold']['runtime_origins']=[]; f.reseal()
        r=f.startup().run(); self.assertEqual(r.effect_state,'none'); self.assertEqual(f.event_list(),[])
    def test_cold_origin_omission(self):
        f=self.fixture(); f.selection['cold']['origins']=[]; f.reseal()
        r=f.startup().run(); self.assertEqual(r.effect_state,'none'); self.assertEqual(f.event_list(),[])
    def test_full_repeated_rows_preserved(self):
        f=self.fixture(); startup=f.startup(); r=startup.run()
        self.assertIsNone(r.primary_code,r.public()); self.assertEqual(startup.cold_observation['metadata_tables'],[('current-source',2)])
    def test_omitted_closure_member(self):
        f=self.fixture(); f.selection['modules']['closure_file_ids'].remove('runtime'); f.reseal()
        with self.assertRaises(P.Refusal):f.startup()
        self.assertEqual(f.event_list(),[])
    def test_partial_constructor_is_unknown_sanitized(self):
        f=self.fixture(config={'fail':'service'}); r=f.startup().run()
        self.assertEqual(r.primary_code,'CONTEXT_SESSIONS_FAILED'); self.assertEqual(r.effect_state,'unknown')
        self.assertIn('channel-close',f.event_list()); self.assertIn('source-exit',f.event_list())
        self.assertNotIn('INERT_PRIVATE_MARKER',json.dumps(r.public())); self.assertNotIn('/private/',json.dumps(r.public()))
    def test_failed_constructor_and_postguard_retains_both(self):
        f=self.fixture(config={'fail':'service'}); check=f.custody.check
        def boundary(stage):
            if 'service' in f.event_list() and stage=='context-sessions': raise RuntimeError('PRIVATE_POST')
            return check(stage)
        f.custody.check=boundary
        r=f.startup().run(); self.assertEqual(r.primary_code,'CONTEXT_SESSIONS_FAILED')
        self.assertIn('CONTEXT_SESSIONS_POSTGUARD_FAILED',r.secondary_codes)
    def test_postguard_failure_disposes_returned_channel(self):
        f=self.fixture(); check=f.custody.check
        def boundary(stage):
            if stage=='reader-channel' and 'channel' in f.event_list(): raise RuntimeError('PRIVATE_POST')
            return check(stage)
        f.custody.check=boundary; r=f.startup().run()
        self.assertEqual(r.primary_code,'READER_CHANNEL_FAILED'); self.assertIn('channel-close',f.event_list())
        self.assertIn('source-exit',f.event_list())
    def test_cleanup_failure_does_not_skip_other_resources(self):
        f=self.fixture(config={'fail':'sessions-close'}); r=f.startup().run()
        self.assertIsNone(r.primary_code,r.public()); self.assertIn('SESSIONS_CLOSE_FAILED',r.cleanup_codes)
        self.assertIn('handlers-close',f.event_list()); self.assertIn('channel-close',f.event_list()); self.assertIn('source-exit',f.event_list())
    def test_denied_guarded_cleanup_still_local_release(self):
        f=self.fixture(); check=f.custody.check
        def boundary(stage):
            if stage=='cleanup': raise P.Refusal('DENIED')
            return check(stage)
        f.custody.check=boundary; r=f.startup().run()
        self.assertEqual(r.effect_state,'unknown'); self.assertIn('channel-close',f.event_list())
        self.assertNotIn('sessions-close',f.event_list()); self.assertNotIn('source-exit',f.event_list())
        self.assertIn('SOURCE_EXIT_FAILED',r.cleanup_codes)
    def test_cleanup_interrupt_delayed_until_all_remaining_owners(self):
        f=self.fixture(config={'interrupt':'sessions-close'});startup=f.startup()
        with self.assertRaises(KeyboardInterrupt):startup.run()
        self.assertEqual(f.event_list()[-4:],['sessions-close','handlers-close','channel-close','source-exit'])
        self.assertTrue(startup.modules._closed)
        self.assertFalse(any(n==f.package or n.startswith(f.package+'.')for n in sys.modules))
    def test_cleanup_interrupt_keeps_prior_constructor_failure(self):
        f=self.fixture(config={'fail':'context-generate','interrupt':'sessions-close'});startup=f.startup();result=startup.run()
        self.assertEqual(result.primary_code,'CONTEXT_QUERY_FAILED');self.assertEqual(result.effect_state,'unknown')
        self.assertIn('SESSIONS_CLOSE_FAILED',result.cleanup_codes);self.assertIn('CLEANUP_INTERRUPTED',result.secondary_codes)
        self.assertEqual(f.event_list()[-4:],['sessions-close','handlers-close','channel-close','source-exit'])
        self.assertTrue(startup.modules._closed)
        self.assertFalse(any(n==f.package or n.startswith(f.package+'.')for n in sys.modules))

    def test_one_attempt_no_producer_retry(self):
        f=self.fixture(); startup=f.startup(); startup.run(); events=f.event_list()
        with self.assertRaises(P.Refusal): startup.run()
        self.assertEqual(events,f.event_list())
    def test_unselected_dynamic_exec_refused(self):
        f=self.fixture(); source=(f.root/'code/common.py').read_bytes()+b'\nexec("UNSELECTED = 1")\n'
        f.put('common','code/common.py',source,'execution')
        # Update public declared row coherently: the independently selected code
        # still cannot execute an unselected generated program.
        row={'path':'code/common.py','sha256':P.digest(source)}
        f.put('document','document.json',P.canonical({'files':[row,row]}),'evidence')
        policy=P.parse((f.root/'cold-policy.json').read_bytes()); policy['documents'][0]['binding']=f.file_binding('document')
        f.put('cold_policy','cold-policy.json',P.canonical(policy),'evidence')
        f.selection['cold']['policy_sha256']=P.digest(P.canonical(policy)); f.reseal()
        r=f.startup().run(); self.assertEqual(r.primary_code,'MODULE_IMPORT_FAILED')
        self.assertEqual(f.event_list(),[])
    def test_foreign_module_replacement_preserved_on_close(self):
        f=self.fixture(); modules=B.SelectedModules(f.custody,f.selection['modules']); modules.enter()
        module=modules.module('protocol'); name=module.__name__; foreign=types.ModuleType(name)
        sys.modules[name]=foreign
        with self.assertRaises(P.Refusal): modules.guard()
        self.assertIn('MODULE_REPLACEMENT_PRESERVED',modules.close()); self.assertIs(sys.modules[name],foreign)
    def test_loaded_class_code_substitution_refuses(self):
        f=self.fixture(); modules=B.SelectedModules(f.custody,f.selection['modules']); modules.enter()
        try:
            module=modules.module('protocol')
            def malicious(self,**kwargs): return None
            module.Schemas.__init__.__code__=malicious.__code__
            with self.assertRaises(P.Refusal): modules.guard()
        finally: modules.close()
    def test_source_exit_failure_retained(self):
        f=self.fixture(config={'fail':'source-exit'}); r=f.startup().run()
        self.assertIn('SOURCE_EXIT_FAILED',r.cleanup_codes); self.assertEqual(r.effect_state,'unknown')


def main():
    global TEMP
    parser=argparse.ArgumentParser(); parser.add_argument('--temp-root',required=True,type=Path); args=parser.parse_args()
    TEMP=args.temp_root
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(StartupTests))
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS' if result.wasSuccessful() else 'FAIL',
                      'checks':result.testsRun,'effect_state':'owned-inert','cleanup':'clean'}))
    raise SystemExit(0 if result.wasSuccessful() else 1)
if __name__=='__main__': main()
