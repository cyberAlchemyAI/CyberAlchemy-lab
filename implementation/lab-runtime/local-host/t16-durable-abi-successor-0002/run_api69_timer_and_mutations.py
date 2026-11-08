"""Run inherited all-eleven and wrong-delivery methods on sealed API64 ABI."""
import hashlib, importlib, importlib.metadata, importlib.util, json, platform, sys, time, unittest
from pathlib import Path
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[4]
INSTALL = Path('/home/vlad_/.local/share/cyberalchemy-lab/native-install/t22-0001')
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v69-t16-call-source-scope-0001'
SOURCE = '28f0bdcc125076f8568c374326fee20eb7822a75e2cf7df49091224a4ad30f9f'
PROFILE = '74be9b75498a98bf728a2e4ce3a2ec889ddc98d40e5136cbc8eff110b826c0d5'
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
if sha(API / 'source-manifest.json') != SOURCE or sha(API / 'contract-profile.json') != PROFILE:
    raise ValueError('API64 source/profile differs')
sys.path.insert(0, str(INSTALL / 'deps'))
if (platform.python_version(), importlib.metadata.version('jsonschema'), importlib.metadata.version('cryptography')) != ('3.14.4', '4.23.0', '46.0.5'):
    raise ValueError('selected ABI differs')
NAME = '_cal_t16_api69_timer_focus'
spec = importlib.util.spec_from_file_location(NAME, API / '__init__.py', submodule_search_locations=[str(API)])
package = importlib.util.module_from_spec(spec)
sys.modules[NAME] = package
spec.loader.exec_module(package)
importlib.import_module(NAME + '.guard').verify(SOURCE)
mod = importlib.import_module(NAME + '.run_session_checks')
mod.SOURCE = SOURCE
mod.PROFILE = PROFILE
original_invoke = mod.Sessions.invoke
def timed_invoke(self, call, *, raw=None):
    start = time.monotonic()
    try:
        reply = original_invoke(self, call, raw=raw)
        print(json.dumps({'operation': call['operation'], 'kind': reply.get('kind'),
                          'code': reply.get('message', {}).get('code'),
                          'elapsed_seconds': round(time.monotonic() - start, 3),
                          'authority_effect': 'none'}, sort_keys=True), flush=True)
        return reply
    except BaseException as error:
        print(json.dumps({'operation': call.get('operation'), 'exception_type': type(error).__name__,
                          'elapsed_seconds': round(time.monotonic() - start, 3),
                          'authority_effect': 'none'}, sort_keys=True), flush=True)
        raise
mod.Sessions.invoke = timed_invoke
def actual_freshness_mutations(self):
    import uuid
    helper=importlib.import_module(NAME+'.session_source_freshness')
    selected=self.view.fresh_signed_sources
    bridge=self.service.sessions.bridge
    with self.channel.verified_source_call(bridge) as verified:
        self.assertTrue(verified)
        self.channel.guard()
        direct=selected.view.integrated_reader.HERE/'packages/0001/artifacts/00.json'
        raw=direct.read_bytes();original_sha=hashlib.sha256(raw).hexdigest()
        try:
            direct.write_bytes(raw+b' ')
            with self.assertRaises(ValueError):self.channel.guard()
        finally:direct.write_bytes(raw)
        self.assertEqual(hashlib.sha256(direct.read_bytes()).hexdigest(),original_sha)
        self.channel.guard()
        private_raw=self.policy.read_bytes()
        try:
            self.policy.write_bytes(private_raw+b' ')
            with self.assertRaises(ValueError):self.channel.guard()
        finally:self.policy.write_bytes(private_raw)
        self.channel.guard()
        # This per-process data mutation and new task-owned file retarget an
        # otherwise physically valid baseline. No shared baseline file is edited.
        probe=Path(__file__).resolve().parent/('_owned-baseline-probe-'+uuid.uuid4().hex+'.json')
        rel=probe.relative_to(ROOT).as_posix()
        materials=selected.view.data['baseline']['materials']
        self.assertNotIn(rel,materials)
        try:
            probe.write_bytes(b'{"fixture":"retarget-probe"}\n');probe.chmod(0o600)
            materials[rel]=hashlib.sha256(probe.read_bytes()).hexdigest()
            self.assertEqual(helper.fresh_selected_source(selected,bridge._live_family),bridge._live_family)
            with self.assertRaises(ValueError):self.channel.guard()
        finally:
            materials.pop(rel,None)
            probe.unlink(missing_ok=True)
        self.channel.guard()
        saved_context=copy.deepcopy(self.channel.context)
        try:
            self.channel.context['context_ref']='opaque:substitution-probe'
            with self.assertRaises(ValueError):self.channel.guard()
        finally:self.channel.context.clear();self.channel.context.update(saved_context)
        self.channel.guard()
    self.assertIsNone(getattr(self.channel._source_call_local,'value',None))
    self.channel.guard();selected.guard()
    print(json.dumps({'actual_mutations':'PASS','direct_family_bytes_restored':True,
        'private_policy_bytes_restored':True,'per_process_baseline_retarget_refused':True,'opaque_context_substitution_refused':True,'call_scope_erased':True,
        'owned_probe_removed':True,'shared_baseline_files_changed':False,
        'authority_effect':'none'},sort_keys=True),flush=True)
mod.Sessions.test_external_actual_freshness_mutations=actual_freshness_mutations
ids = ['test_external_actual_freshness_mutations','test_27_actual_expiry_timer_disposes']
suite = unittest.TestSuite(mod.Sessions(identity) for identity in ids)
result = unittest.TextTestRunner(verbosity=2).run(suite)
print(json.dumps({'api_source_sha256': SOURCE, 'api_profile_sha256': PROFILE,
                  'method_ids': ids, 'run': result.testsRun, 'failures': len(result.failures),
                  'errors': len(result.errors), 'success': result.wasSuccessful(),
                  'authority_effect': 'none'}, sort_keys=True))
if not result.wasSuccessful():
    raise SystemExit(1)
