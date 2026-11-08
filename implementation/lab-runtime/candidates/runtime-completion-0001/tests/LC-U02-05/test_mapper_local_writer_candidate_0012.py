"""Static/pure tests only; execute and PackageWriter constructor are never called."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
import time
import types
import unittest
from unittest import mock
C=W=INPUTS=PLAN=None

class Tests(unittest.TestCase):
    def test_actual_selected_plan_exact_55_leaves(self):
        selected,raw,leaves,frames=C.validate_plan(PLAN)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),PLAN['manifest_sha256']);self.assertEqual(len(leaves),55)
        self.assertEqual(set(leaves),set(W.SCHEDULE));manifest=json.loads(leaves['manifest.json']);self.assertEqual(len(manifest['files']),54)
        for row in manifest['files']:
            name=row['path'].removeprefix(C.model.PACKAGE+'/');self.assertEqual(row['sha256'],hashlib.sha256(leaves[name]).hexdigest())
        self.assertEqual(selected['begin_pins']['mapper'],manifest['source_manifest_binding']['sha256'])
        self.assertEqual(C.preflight(PLAN)['effect_executed'],False)

    def test_plan_copy_leaf_and_digest_mutation_refuse(self):
        for kind in ('copy','leaf','digest','scratch','evidence'):
            p=copy.deepcopy(PLAN)
            if kind=='copy':p['copies'][0]['raw_hex']='00'
            elif kind=='leaf':p['leaves']['manifest.json']='00'
            elif kind=='digest':p['manifest_sha256']='f'*64
            else:p[kind]+='-wrong'
            with self.assertRaises(Exception):C.validate_plan(p)

    def test_repeated_effect_preflight_refuses(self):
        with mock.patch.object(C.os.path,'lexists',return_value=True):
            with self.assertRaises(RuntimeError):C.preflight(PLAN)

    def test_real_writer_single_thread_guard_precedes_umask_or_mkdir(self):
        obj=object.__new__(W.PackageWriter)
        with mock.patch.object(W.threading,'active_count',return_value=2),mock.patch.object(W.os,'umask') as mask,mock.patch.object(W.os,'mkdir') as mkdir:
            with self.assertRaises(W.Refusal):obj._mkdir(-1,'never')
            mask.assert_not_called();mkdir.assert_not_called()

    def test_fixture_single_thread_refuses_before_tree_claim(self):
        with mock.patch.object(C.threading,'active_count',return_value=2),mock.patch.object(C,'HeldCanonicalDirectory') as held:
            with self.assertRaises(RuntimeError):C.OwnedTree(C.SCRATCH)
            held.assert_not_called()

    def test_real_writer_attachment_failure_precedes_leaf_open(self):
        obj=object.__new__(W.PackageWriter);obj.closed=False;obj.unknown=False;obj.finished=False;obj.index=0;obj.total=0
        obj._scan=mock.Mock(side_effect=W.Refusal('selected-fixture-detached'))
        with mock.patch.object(W.os,'open') as opened:
            with self.assertRaises(W.Refusal):obj.emit(W.SCHEDULE[0],b'fixture')
            opened.assert_not_called();self.assertTrue(obj.unknown)

    def test_deadline_check_refuses_expired_synchronous_return(self):
        with mock.patch.object(C,'time',types.SimpleNamespace(monotonic=lambda:10)):
            C.deadline(11)
            for end in (10,9):
                with self.assertRaises(RuntimeError):C.deadline(end)
        tree=ast.parse(Path(INPUTS['candidate']['path']).read_bytes())
        exchange=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='exchange')
        calls=sorted((n.lineno,n.col_offset,ast.unparse(n.func)) for n in ast.walk(exchange) if isinstance(n,ast.Call));names=[x[2] for x in calls]
        begin=names.index('server.prepare_one');send=names.index('server.send_pending')
        self.assertIn('deadline',names[begin+1:send])

    def test_owned_teardown_attempts_each_once_and_retains_uncertainty(self):
        obj=object.__new__(C.OwnedTree);obj.closed=False;obj.uncertain=False;obj.fds={'':111,'child':222};obj.parent=mock.Mock();obj.parent.close.side_effect=RuntimeError('synthetic')
        calls=[]
        def close(fd):
            calls.append(fd)
            if fd==222:raise OSError('synthetic')
        with mock.patch.object(C.os,'close',side_effect=close):obj.close();obj.close()
        self.assertEqual(calls,[222,111]);obj.parent.close.assert_called_once();self.assertTrue(obj.uncertain)

    def test_parent_detachment_refuses_before_path_scan(self):
        obj=object.__new__(C.OwnedTree);obj.parent=types.SimpleNamespace(attached=lambda:False);obj.fds={'':111}
        with mock.patch.object(C.os,'lstat') as stat:
            with self.assertRaises(RuntimeError):obj.attached()
            stat.assert_not_called()

    def test_effect_body_has_no_spawn_thread_namespace_or_native(self):
        tree=ast.parse(Path(INPUTS['candidate']['path']).read_bytes())
        for n in ast.walk(tree):
            if isinstance(n,ast.Call):self.assertNotIn(ast.unparse(n.func).split('.')[-1],('Popen','fork','execve','Thread','start','system','run_native','spawn_standin'))
        text=ast.unparse(tree);self.assertIn('server.prepare_one()',text);self.assertIn('server.send_pending()',text)
        self.assertIn('server.writer._scan()',text);self.assertIn('runner.read_exact',text)


def main(inputs,candidate):
    global C,W,INPUTS,PLAN
    C=candidate;W=C.writer;INPUTS=inputs
    b=Path(inputs['plan']['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==inputs['plan']['sha256'];PLAN=json.loads(b)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    print(json.dumps({'result':'PASS' if result.wasSuccessful() else 'FAIL','checks':result.testsRun,'static_only':True,'effect_runs':0,'package_writes':0,'namespace_runs':0,'host_qualified':False},sort_keys=True))
    return 0 if result.wasSuccessful() else 1
