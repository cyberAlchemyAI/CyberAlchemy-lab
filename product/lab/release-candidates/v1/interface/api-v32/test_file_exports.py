"""Actual nonce-authenticated public export, retry, uncertainty and stdio checks."""
import copy
import fcntl
from datetime import timedelta
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
import uuid
from .protocol import *
from .auth import ReaderChannel, now
from .service import Service
from . import export_fixture as F
from . import metadata_fixture as MF
from . import artifact_model as M
from . import export_kernel as K
from .handlers import cut
PROFILE = None
SOURCE = None

class FileExports(unittest.TestCase):
    events = []
    public = []
    @classmethod
    def setUpClass(cls):
        cls.schemas = Schemas(PROFILE)
        cls.cm = source.replay_source('custody-participation')
        cls.view = cls.cm.__enter__()
        cls.selected = F.selection(cls.view)
        cls.period_path = source.custody_delivery().reader.HERE / 'packages/0001/period.json'
        cls.original_period = cls.period_path.read_bytes()
    @classmethod
    def tearDownClass(cls):
        assert cls.period_path.read_bytes() == cls.original_period
        cls.cm.__exit__(None, None, None)
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory(prefix='cal-R03-public-file-export-')))
        self.root.chmod(0o700)
        self.key, self.policy, self.pin = F.provision(self.root, self.selected)
        self.start()
    def start(self):
        self.channel = ReaderChannel(self.policy, self.pin, self.schemas)
        proof = MF.proof(self.key, self.channel.challenge)
        auth = self.channel.authenticate(proof)
        self.service = Service(self.view, self.channel, self.schemas)
        self.addCleanup(self.service.close)
        self.public.append({'owned_root': str(self.root), 'public_policy': source.parse(self.policy.read_bytes()), 'signed_nonce_proof': source.parse(proof), 'authentication_reply': auth, 'authority_effect': 'none'})
    def policy_change(self, change):
        self.service.close()
        value = source.parse(self.policy.read_bytes())
        change(value)
        raw = compact(value)
        self.policy.write_bytes(raw)
        self.pin = source.sha(raw)
        self.start()
    def call(self, **options):
        return F.call(self.service, self.selected, **options)
    def invoke(self, call):
        raw = compact(call)
        reply = self.service.call(raw)
        self.events.append({'call': copy.deepcopy(call), 'reply': copy.deepcopy(reply)})
        return reply
    def success(self, call):
        reply = self.invoke(call)
        self.assertEqual(reply['kind'], 'result', reply)
        return reply['message']
    def output(self):
        return Path(self.channel.policy['export_control']['output_root'])
    def generation(self, call):
        return self.output() / K.sha(compact(call['message']))
    def assert_no_claim(self):
        self.assertEqual(list((self.root / 'workspace/journal').glob('*')), [])
        self.assertEqual({p.name for p in self.output().iterdir()}, {'.scope.json'})
    def refused(self, change):
        call = self.call()
        change(call)
        reply = self.invoke(call)
        self.assertNotEqual(reply.get('kind'), 'result', reply)
        self.assert_no_claim()
        return reply
    def test_00_actual_public_byte_export(self):
        call = self.call()
        result = self.success(call)
        self.assertEqual(result['posture'], 'published')
        self.assertEqual(result['request_binding']['sha256'], source.sha(message_bytes(compact(call))))
        with M.model_read_batch(self.view):
            for path, header in zip(self.selected['managed_relative_paths'], self.selected['artifact_refs'], strict=True):
                raw = M.record_bytes(self.view, self.view.subjects[header['version_ref']])[0]
                self.assertEqual((self.generation(call) / 'files' / path).read_bytes(), raw)
        self.assertFalse(result['canonical_replay_source'])
        self.assertIsNone(self.service.sessions)
    def test_01_actual_public_rendered_export(self):
        call = self.call(mode='rendered')
        result = self.success(call)
        self.assertEqual(result['posture'], 'published')
        with M.model_read_batch(self.view):
            for path, header in zip(self.selected['managed_relative_paths'], self.selected['artifact_refs'], strict=True):
                raw = M.record_bytes(self.view, self.view.subjects[header['version_ref']])[0]
                output = (self.generation(call) / 'files' / path).read_bytes()
                self.assertEqual(json.loads(output), json.loads(raw))
                self.assertTrue(output.endswith(b'\n'))
    def test_02_exact_retry_never_rewrites(self):
        call = self.call()
        first = self.success(call)
        before = {p.relative_to(self.output()).as_posix(): (p.stat().st_ino,p.read_bytes()) for p in self.output().rglob('*') if p.is_file()}
        call['call_id'] = 'call:retry:' + uuid.uuid4().hex
        self.assertEqual(self.success(call), first)
        self.assertEqual(before, {p.relative_to(self.output()).as_posix(): (p.stat().st_ino,p.read_bytes()) for p in self.output().rglob('*') if p.is_file()})
    def test_03_same_key_different_fingerprint_conflicts(self):
        call = self.call()
        self.success(call)
        call['call_id'] = 'call:conflict:' + uuid.uuid4().hex
        call['message']['mode'] = 'rendered'
        call['message']['renderer_binding'] = self.channel.policy['export_control']['renderer_binding']
        reply = self.invoke(call)
        self.assertEqual(reply['message']['code'], 'idempotency-conflict')
        self.assertFalse(self.generation(call).exists())
    def test_04_actual_durable_operation_inspection(self):
        result = self.success(self.call())
        query = MF.call(self.channel.context, 'operation.inspect', cut(self.view), lookup={'operation':'files.materialize','idempotency_key':'fixture:public-export'})
        inspected = self.success(query)
        self.assertEqual(inspected['posture'], 'completed')
        self.assertFalse(inspected['retry_allowed'])
        self.assertFalse(inspected['reconciliation_required'])
        self.assertEqual(source.parse(self.service.vault.object_read(inspected['result_binding'])), result)
    def test_05_metadata_eight_operation_grant_cannot_export(self):
        call = self.call()
        self.service.close()
        # A metadata grant receives its own fresh workspace. Export generations
        # and directory scope remain protected by the original export grant.
        separate = Path(self.enterContext(tempfile.TemporaryDirectory(prefix='cal-R03-export-denied-metadata-')))
        separate.chmod(0o700)
        self.key,self.policy,self.pin = MF.provision(separate,{}, {}, scoped=False)
        self.start()
        call['caller_context_ref'] = self.channel.context['context_ref']
        reply = self.invoke(call)
        self.assertEqual(reply['code'], 'unsupported-operation')
        self.assertEqual(list((self.root / 'workspace/journal').glob('*')), [])
        self.assertEqual(list((separate / 'workspace/journal').glob('*')), [])
    def test_06_complete_selection_required(self):
        self.refused(lambda c: c['message']['artifact_refs'].pop())
    def test_07_privacy_binding_change_refused(self):
        self.refused(lambda c: c['message']['privacy_review_binding'].update(sha256='0'*64))
    def test_08_output_scope_change_refused(self):
        self.refused(lambda c: c['message'].update(output_root_scope_ref='/tmp/unselected'))
    def test_09_parent_path_refused(self):
        self.refused(lambda c: c['message']['managed_relative_paths'].__setitem__(0,'../escape.json'))
    def test_10_session_memory_refused(self):
        self.refused(lambda c: c['message'].update(include_session_memory=True))
    def test_11_actor_impersonation_refused(self):
        self.refused(lambda c: c['message']['actor'].update(principal_ref='person:owner'))
    def test_12_small_output_budget_before_claim(self):
        self.policy_change(lambda v: v['export_control'].update(max_output_bytes=1))
        reply = self.refused(lambda c: None)
        self.assertEqual(reply['message']['code'], 'budget-exceeded')
    def test_13_generation_quota_and_recorded_retry(self):
        self.policy_change(lambda v: v['export_control'].update(max_generations=1))
        call = self.call()
        first = self.success(call)
        other = self.call(key='fixture:second-export', mode='rendered')
        reply = self.invoke(other)
        self.assertEqual(reply['message']['code'], 'budget-exceeded')
        call['call_id'] = 'call:quota-retry:' + uuid.uuid4().hex
        self.assertEqual(self.success(call), first)
    def test_14_deleted_generation_not_recreated_on_retry(self):
        call = self.call()
        self.success(call)
        shutil.rmtree(self.generation(call))
        call['call_id'] = 'call:missing-retry:' + uuid.uuid4().hex
        reply = self.invoke(call)
        self.assertEqual(reply['message']['code'], 'recovery-required')
        self.assertFalse(self.generation(call).exists())
    def test_15_changed_output_not_rewritten_on_retry(self):
        call = self.call()
        self.success(call)
        path = self.generation(call) / 'files' / self.selected['managed_relative_paths'][0]
        path.write_bytes(b'changed fixture output')
        call['call_id'] = 'call:tamper-retry:' + uuid.uuid4().hex
        reply = self.invoke(call)
        self.assertEqual(reply['message']['code'], 'recovery-required')
        self.assertEqual(path.read_bytes(), b'changed fixture output')
    def test_16_revoked_policy_blocks_recorded_retry(self):
        call = self.call()
        self.success(call)
        value = source.parse(self.policy.read_bytes())
        value['revoked'] = True
        self.policy.write_bytes(compact(value))
        call['call_id'] = 'call:revoked-retry:' + uuid.uuid4().hex
        reply = self.invoke(call)
        self.assertEqual(reply['code'], 'unauthenticated-channel')
    def test_17_pending_generation_no_redispatch(self):
        call = self.call()
        generation = self.generation(call)
        generation.mkdir(mode=0o700)
        (generation / 'fixture-pending.json').write_bytes(b'preserve pending generation')
        reply = self.invoke(call)
        self.assertEqual(reply['kind'], 'error')
        self.assertEqual(reply['message']['code'], 'indeterminate')
        self.assertEqual({p.name for p in generation.iterdir()}, {'fixture-pending.json'})
        query = MF.call(self.channel.context, 'operation.inspect', cut(self.view), lookup={'operation':'files.materialize','idempotency_key':'fixture:public-export'})
        result = self.success(query)
        self.assertEqual(result['posture'], 'indeterminate')
        self.assertTrue(result['reconciliation_required'])
    def test_18_opened_root_inode_is_bound(self):
        call = self.call()
        root = self.output()
        moved = root.with_name('exports-original')
        root.rename(moved)
        root.mkdir(mode=0o700)
        (root / '.scope.json').write_bytes((moved / '.scope.json').read_bytes())
        reply = self.invoke(call)
        self.assertEqual(reply['code'], 'unauthenticated-channel')
        self.assertEqual({p.name for p in root.iterdir()}, {'.scope.json'})
    def test_19_export_grant_cannot_invoke_Sessions(self):
        for operation in ('context.get','session.open','session.close','session.inspect'):
            call = self.call()
            call['operation'] = operation
            reply = self.invoke(call)
            self.assertEqual(reply['code'], 'unsupported-operation')
        self.assert_no_claim()
    def test_20_stdio_actual_nonce_and_export(self):
        self.service.close()
        process = subprocess.Popen([sys.executable,str(HERE/'serve.py'),'--policy',str(self.policy),'--policy-sha256',self.pin,'--source-sha256',SOURCE,'--protocol-profile-sha256',PROFILE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            challenge = source.parse(process.stdout.readline())
            process.stdin.write(MF.proof(self.key, challenge) + b'\n')
            process.stdin.flush()
            auth = source.parse(process.stdout.readline())
            client = SimpleNamespace(channel=SimpleNamespace(context=auth['context'],policy=source.parse(self.policy.read_bytes())),schemas=self.schemas)
            call = F.call(client,self.selected,key='fixture:stdio-export')
            process.stdin.write(compact(call) + b'\n')
            process.stdin.flush()
            reply = source.parse(process.stdout.readline())
            self.assertEqual(reply['kind'], 'result', reply)
            self.assertEqual(reply['message']['posture'], 'published')
            self.events.append({'call': call,'reply':reply,'actual_stdio':True})
            self.public.append({'owned_root':str(self.root),'actual_stdio_challenge':challenge,'authentication_reply':auth,'authority_effect':'none'})
            process.stdin.close()
            code = process.wait(timeout=120)
            self.assertEqual(code,0,process.stderr.read().decode())
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            for stream in (process.stdout,process.stderr):
                stream.close()
    def test_21_deadline_refused_before_claim(self):
        reply = self.refused(lambda c: c.update(deadline=(now()-timedelta(seconds=1)).isoformat()))
        self.assertEqual(reply['message']['code'], 'deadline-exceeded')
    def test_22_kernel_refuses_root_swap_after_plan(self):
        call = self.call()
        request = call['message']
        materials = []
        with M.model_read_batch(self.view):
            for header in request['artifact_refs']:
                raw,locator,encoding,_ = M.record_bytes(self.view,self.view.subjects[header['version_ref']])
                materials.append(K.Material(compact(header),raw,locator,encoding))
        control = self.channel.policy['export_control']
        selected = K.Selection(request['selection_ref'],compact(request['source_cut']),tuple(materials),self.service.vault.material(control['privacy_review_binding']))
        root = self.output()
        calls = [0]
        def fixture_permission():
            calls[0] += 1
            if calls[0] == 2:
                root.rename(root.with_name('exports-original'))
                root.mkdir(mode=0o700)
            return True
        host = K.ExportHost(root,request['output_root_scope_ref'],request['actor'],selected,self.schemas,self.view.custody_signed_sources.guard,fixture_permission,1048576,control['output_root_identity'])
        with self.assertRaises(ValueError):
            host.materialize(request)
        self.assertEqual(list(root.iterdir()),[])
        self.assertTrue((root.with_name('exports-original')/'.scope.json').is_file())
    def test_23_busy_quota_lock_retains_pending_key(self):
        descriptor = os.open(self.output()/'.generation.lock',os.O_RDWR|os.O_CREAT|os.O_EXCL,0o600)
        try:
            fcntl.flock(descriptor,fcntl.LOCK_EX|fcntl.LOCK_NB)
            call = self.call()
            reply = self.invoke(call)
            self.assertEqual(reply['message']['code'],'recovery-required')
        finally:
            os.close(descriptor)
        query = MF.call(self.channel.context,'operation.inspect',cut(self.view),lookup={'operation':'files.materialize','idempotency_key':'fixture:public-export'})
        result = self.success(query)
        self.assertTrue(result['reconciliation_required'])
        self.assertEqual(result['posture'],'indeterminate')
        call['call_id'] = 'call:lock-retry:'+uuid.uuid4().hex
        reply = self.invoke(call)
        self.assertEqual(reply['message']['code'],'recovery-required')
        self.assertEqual({p.name for p in self.output().iterdir()},{'.scope.json','.generation.lock'})
