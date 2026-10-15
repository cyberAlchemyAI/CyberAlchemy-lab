"""Actual projection refresh, exact original wire schemas and fail-closed guards."""
import argparse
import base64
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack
from datetime import timedelta
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
API = HERE.parent / 'api-v16'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def emit(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as out:
        out.write((json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--shard', choices=['A','B','C','D','E'])
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--profile-sha256', required=True)
    parser.add_argument('--producer-sha256', required=True)
    args = parser.parse_args()
    assert sha(HERE / 'source-manifest.json') == args.producer_sha256
    for row in json.loads((HERE / 'source-manifest.json').read_bytes())['files']:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    assert sha(API / 'source-manifest.json') == args.source_sha256
    for row in json.loads((API / 'source-manifest.json').read_bytes())['files']:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    groups={'A':range(0,5),'B':range(5,10),'C':range(10,15),'D':range(15,18),'E':range(18,21)}
    if args.shard is None:
        output=HERE/'receipts/0001';output.mkdir(parents=True,exist_ok=False);children=[]
        for group in groups:
            directory=output/group;directory.mkdir();stdout=(directory/'producer.stdout').open('xb');stderr=(directory/'producer.stderr').open('xb')
            command=[sys.executable,str(Path(__file__).resolve()),'--source-sha256',args.source_sha256,'--profile-sha256',args.profile_sha256,'--producer-sha256',args.producer_sha256,'--shard',group]
            child=subprocess.Popen(command,cwd=ROOT,stdout=stdout,stderr=stderr);children.append((group,child,stdout,stderr))
        emit(output/'started.json',{'children':[{'group':g,'pid':c.pid} for g,c,_,_ in children],'authority_effect':'none'})
        observed=[]
        for group,child,stdout,stderr in children:
            code=child.wait();stdout.close();stderr.close();observed.append({'group':group,'pid':child.pid,'exit_code':code,'terminal_observed':True})
        reports=[json.loads((output/g/'tests.json').read_bytes()) for g in groups];events=[]
        for group in groups:events+=json.loads((output/group/'wire-observations.json').read_bytes())
        methods=[n for r in reports for n in r['methods']]
        passed=all(r['result']=='PASS' and r['all_owned_roots_removed'] for r in reports) and all(r['exit_code']==0 for r in observed) and len(methods)==len(set(methods))==21
        report={'result':'PASS' if passed else 'FAIL','tests_run':sum(r['tests_run'] for r in reports),'errors':sum(r['errors'] for r in reports),'failures':sum(r['failures'] for r in reports),'methods':methods,'children':observed,'all_owned_roots_removed':all(r['all_owned_roots_removed'] for r in reports),'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'fixture_correction':'Original transport error schema resource is transport-error; all 21 original methods retained and executed exactly once in isolated groups.'}
        emit(output/'tests.json',report);emit(output/'wire-observations.json',events);print(json.dumps({'result':report['result'],'tests':report['tests_run'],'processes':len(observed)}),flush=True);return 0 if passed else 1
    name = '_cal_api_v16'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module; spec.loader.exec_module(module)
    S = __import__(name + '.service', fromlist=['Service'])
    F = __import__(name + '.fixtures', fromlist=['provision'])
    P = __import__(name + '.projection_refresh', fromlist=['ProjectionRefresh'])
    W = __import__(name + '.workspace', fromlist=['privacy'])
    output = HERE / 'receipts/0001' / args.shard
    events, roots, observations = [], [], []

    class ProjectionTests(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.stack = ExitStack(); cls.addClassCleanup(cls.stack.close)
            cls.view = cls.stack.enter_context(S.source.replay_source('reference-corrected'))
            cls.schemas = S.Schemas(args.profile_sha256)
            cls.grant = P.control(cls.view)

        def setUp(self):
            self.stack = ExitStack(); self.addCleanup(self.stack.close)
            self.root = Path(self.stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-R03-projection-tests-')))
            roots.append(str(self.root)); self.root.chmod(0o700)
            self.key, self.policy, self.pin = F.provision(self.root, 'reference-corrected', projection_control=self.grant)
            self.channel = F.ReaderChannel(self.policy, self.pin, self.schemas)
            self.channel.authenticate(F.proof(self.key, self.channel.challenge))
            self.service = S.Service(self.view, self.channel, self.schemas); self.addCleanup(self.service.close)

        def request(self):
            c = F.call(self.channel.context, 'lab.status', S.cut(self.view)); budget = c['message']['budget']; budget['max_actions'] = 1
            selected = self.service.handlers.generations.get(S.source.sha(S.compact(S.cut(self.view))))
            c.update(operation='projection.refresh', idempotency_key='refresh:' + F.uuid.uuid4().hex, message={
                'schema_version': 'lab-projection-refresh-request/v1-candidate', 'request_ref': 'request:refresh:' + F.uuid.uuid4().hex,
                'source_cut': copy.deepcopy(S.cut(self.view)), 'projector_binding': self.grant['projector_binding'],
                'contract_catalog_binding': self.grant['contract_catalog_binding'],
                'expected_generation_binding': None if selected is None else selected.binding,
                'budget': budget, 'authority_effect': 'none'})
            return c

        def invoke(self, c, raw=None):
            raw = S.compact(c) if raw is None else raw
            r = self.service.call(raw)
            events.append({'original_call_base64': base64.b64encode(raw).decode(), 'reply': copy.deepcopy(r)})
            self.assertTrue(self.schemas.valid('api-reply', r) or self.schemas.valid('transport-error', r), r)
            W.privacy(r)
            return r

        def success(self, c, raw=None):
            r = self.invoke(c, raw); self.assertEqual(r.get('kind'), 'result', r); return r['message']

        def error(self, c, code):
            r = self.invoke(c); self.assertEqual(r.get('kind'), 'error', r); self.assertEqual(r['message']['code'], code)

        def selected(self):
            return self.service.handlers.generations[S.source.sha(S.compact(S.cut(self.view)))]

        def test_00_real_ready_generation_and_all_original_watermarks(self):
            before = copy.deepcopy(self.view.data); c = self.request(); r = self.success(c); g = self.selected()
            self.assertEqual(r['posture'], 'ready'); self.assertFalse(r['canonical_replay_source']); g.verify()
            self.assertEqual(r['generation_binding'], g.binding); self.assertEqual(self.view.data, before)
            v = S.source.parse(self.service.vault.object_read(r['source_verification_binding']))
            self.assertEqual(v['stream_watermarks'], S.cut(self.view)['streams']); self.assertEqual(v['foreign_key_violations'], [])
            self.assertEqual(v['table_counts']['artifact_revision'], len(g.items)); self.assertEqual(v['table_counts']['projection_gap'], len(g.gaps))
            self.assertEqual(v['original_message_byte_sha256'], S.source.sha(S.message_bytes(S.compact(c))))
            self.assertEqual(g.path.stat().st_mode & 0o777, 0o600)

        def test_01_exact_retry_does_not_rebuild(self):
            c = self.request(); first = self.success(c); c['call_id'] = 'call:retry'
            with patch.object(P, 'Generation', side_effect=AssertionError('must not recreate')):
                self.assertEqual(first, self.success(c))

        def test_02_different_input_same_key_conflicts(self):
            c = self.request(); self.success(c); c['call_id'] = 'call:changed'; c['message']['request_ref'] += ':changed'
            self.error(c, 'idempotency-conflict')

        def test_03_pending_claim_never_redispatches(self):
            c = self.request(); self.service.vault.claim(c, S.compact(c), self.channel.context)
            with patch.object(P, 'Generation', side_effect=AssertionError('must not dispatch')):
                self.error(c, 'recovery-required')
            i = F.call(self.channel.context, 'operation.inspect', None, lookup={'operation': 'projection.refresh', 'idempotency_key': c['idempotency_key']})
            self.assertEqual(self.success(i)['posture'], 'indeterminate')

        def test_04_host_permission_required(self):
            p = S.source.parse(self.policy.read_bytes()); p['projection_control'] = None; self.policy.write_bytes(S.compact(p))
            self.channel.expected_sha = S.source.sha(self.policy.read_bytes()); self.channel.policy = self.channel.policy_guard()
            self.error(self.request(), 'unauthorized'); self.assertFalse(list((self.root / 'workspace/journal').iterdir()))

        def test_05_exact_projector_required(self):
            c = self.request(); c['message']['projector_binding'] = {'ref': 'unselected', 'sha256': '0' * 64}
            self.error(c, 'invalid-contract')

        def test_06_exact_catalog_required(self):
            c = self.request(); c['message']['contract_catalog_binding'] = {'ref': 'unselected', 'sha256': '0' * 64}
            self.error(c, 'invalid-contract')

        def test_07_exact_current_generation_required(self):
            c = self.request(); c['message']['expected_generation_binding'] = {'ref': 'generation:unselected', 'sha256': '0' * 64}
            self.error(c, 'conflict')

        def test_08_generation_replacement_disposes_old_cache(self):
            first = self.success(self.request()); old = self.selected(); path = old.path
            second = self.success(self.request()); self.assertNotEqual(first['generation_binding'], second['generation_binding'])
            self.assertFalse(path.exists()); self.selected().verify()

        def test_09_zero_action_budget_refused(self):
            c = self.request(); c['message']['budget']['max_actions'] = 0
            self.error(c, 'unauthorized'); self.assertEqual(self.service.projections.created, 0)

        def test_10_expired_deadline_refused_before_creation(self):
            c = self.request(); c['deadline'] = (F.now() - timedelta(seconds=1)).isoformat()
            self.error(c, 'deadline-exceeded'); self.assertEqual(self.service.projections.created, 0)

        def test_11_actual_foreign_keys_and_row_corruption_refused(self):
            self.success(self.request()); g = self.selected(); c = self.request()
            g.db.execute('PRAGMA query_only=OFF'); g.db.execute("UPDATE artifact_revision SET byte_sha256=?", ('0' * 64,)); g.db.commit()
            self.error(c, 'integrity-failed'); self.assertIs(g, self.selected())

        def test_12_constructor_failure_keeps_old_visible_generation(self):
            self.success(self.request()); g = self.selected()
            with patch.object(P, 'Generation', side_effect=ValueError('simulated owned builder failure')):
                self.error(self.request(), 'indeterminate')
            self.assertIs(self.selected(), g); g.verify()

        def test_13_postbuild_guard_failure_removes_staging(self):
            self.success(self.request()); g = self.selected(); created = []
            Original = P.Generation
            def build(*a, **kw):
                new = Original(*a, **kw); created.append(new.path); return new
            with patch.object(P, 'Generation', side_effect=build), patch.object(self.service.handlers, 'current', side_effect=[True, True, False]):
                self.error(self.request(), 'indeterminate')
            self.assertEqual(len(created), 1); self.assertFalse(created[0].exists()); self.assertIs(self.selected(), g); g.verify()

        def test_14_current_policy_change_revokes_channel(self):
            c = self.request(); self.policy.write_bytes(self.policy.read_bytes() + b' ')
            r = self.invoke(c); self.assertEqual(r['code'], 'unauthenticated-channel'); self.assertEqual(self.service.projections.created, 0)

        def test_15_outer_inner_cut_mismatch_refused(self):
            c = self.request(); c['expected_source_cut']['commit_sha256'] = '0' * 64
            self.error(c, 'invalid-contract')

        def test_16_original_received_message_bytes_retained(self):
            c = self.request(); raw = json.dumps(c, indent=3).encode(); result = self.success(c, raw)
            v = S.source.parse(self.service.vault.object_read(result['source_verification_binding']))
            self.assertEqual(v['original_message_byte_sha256'], S.source.sha(S.message_bytes(raw)))
            self.assertNotEqual(v['original_message_byte_sha256'], S.source.sha(S.compact(c['message'])))

        def test_17_sql_query_matches_original_canonical_query(self):
            self.success(self.request())
            c = F.call(self.channel.context, 'artifact.query', S.cut(self.view)); canonical = self.success(c)
            c['call_id'] = 'call:sql'; c['message']['query_basis'] = 'projection'; projected = self.success(c)
            self.assertEqual(canonical['results'], projected['results']); self.assertEqual(canonical['connections'], projected['connections'])
            self.assertEqual(projected['projection_generation'], self.selected().binding)

        def test_18_protected_historical_session_memory_never_cached(self):
            self.success(self.request()); g = self.selected()
            protected = [s for s in self.view.subjects.values() if s['kind'] == 'agent-session' and s['record'].get('payload', {}).get('session_memory')]
            self.assertTrue(protected)
            from importlib import import_module
            M = import_module(name + '.artifact_model')
            for subject in protected:
                self.assertEqual(g.db.execute('SELECT count(*) FROM content_cache WHERE byte_sha256=?', (M.artifact_ref(self.view, subject)['byte_sha256'],)).fetchone()[0], 0)
            for raw, in g.db.execute('SELECT content FROM content_cache'):
                W.privacy(S.source.parse(raw))

        def test_19_whitespace_retry_uses_same_control_fingerprint(self):
            c = self.request(); first = self.success(c); c['call_id'] = 'call:spaces'
            self.assertEqual(first, self.success(c, json.dumps(c, indent=2).encode()))

        def test_20_generation_budget_last_allowed_build_succeeds(self):
            p = S.source.parse(self.policy.read_bytes()); p['projection_control']['max_generations'] = 1
            self.policy.write_bytes(S.compact(p)); self.channel.expected_sha = S.source.sha(self.policy.read_bytes()); self.channel.policy = self.channel.policy_guard()
            self.assertEqual(self.success(self.request())['posture'], 'ready'); self.error(self.request(), 'budget-exceeded')

    with (output / 'tests.stdout').open('x') as stdout, (output / 'tests.stderr').open('x') as stderr:
        names=unittest.defaultTestLoader.getTestCaseNames(ProjectionTests);assert len(names)==21
        selected=[n for n in names if int(n.split('_')[1]) in groups[args.shard]]
        result = unittest.TextTestRunner(stream=stderr, verbosity=2).run(unittest.TestSuite(ProjectionTests(n) for n in selected))
    report = {'result': 'PASS' if result.wasSuccessful() else 'FAIL', 'tests_run': result.testsRun, 'errors': len(result.errors), 'failures': len(result.failures),
              'all_owned_roots_removed': all(not Path(p).exists() for p in roots), 'methods': selected,
              'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False}
    emit(output / 'tests.json', report); emit(output / 'wire-observations.json', events)
    print(json.dumps(report), flush=True)
    return 0 if report['result'] == 'PASS' and report['all_owned_roots_removed'] else 1


if __name__ == '__main__': raise SystemExit(main())
