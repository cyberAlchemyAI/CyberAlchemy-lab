"""Causal static tests for the disabled public-only namespace probe release."""
import datetime as dt
import errno
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import release as R
import observer as O
import probe_child as C

NOW = dt.datetime(2026,10,20,17,0,tzinfo=dt.timezone.utc)


class Result:
    def __init__(self,code=0,out=b'',err=b''):
        self.returncode,self.stdout,self.stderr = code,out,err


class ReleaseTests(unittest.TestCase):
    def test_disposable_projection_exact_five_ro_mounts(self):
        value = R.projection('b'*32,NOW)
        argv = value['create_argv']
        self.assertFalse(value['effect_enabled'])
        self.assertEqual(value['role'],'probe/public-only')
        self.assertEqual(argv.count('--mount'),5)
        self.assertEqual([argv[i+1] for i,v in enumerate(argv) if v == '--mount'],
                         [f"type=bind,src={m['source']},dst={m['target']},readonly"
                          for m in value['mounts']])
        self.assertEqual([m['target'] for m in value['mounts']],
                         ['/workspace','/control','/runner','/cache-disabled',
                          '/attempt/input/lab-context-native-reader'])
        self.assertTrue(all(m['source'].startswith(str(R.ATTEMPT)+'/')
                            for m in value['mounts']))
        self.assertEqual(argv[argv.index('--name')+1],R.NAME)
        self.assertEqual(argv[-2],R.PINS[R.CHILD])
        self.assertEqual(json.loads(argv[-1])['token'],'b'*32)
        self.assertFalse(any('dst=/workspace/' in arg for arg in argv))

    def test_original_stage_and_private_cannot_enter_projection(self):
        good = R.projection('b'*32,NOW)
        self.assertNotEqual(good['mounts'][0]['source'],
                            str(R.PARENT/'context-successor-20261020-0001/context-attempt/root'))
        self.assertNotIn('private',str(good['mounts']))
        with mock.patch.object(R,'ATTEMPT',R.PARENT/'context-successor-20261020-0001/context-attempt/root'):
            with self.assertRaises(R.Refused): R.projection('b'*32,NOW)
        with mock.patch.object(R,'ROLE','product/lab/release-candidates/v1/interface/docker-context-20261020-0002'):
            with self.assertRaises(R.Refused): R.projection('b'*32,NOW)

    def test_pins_and_expiry_refuse(self):
        with self.assertRaises(R.Refused): R.projection('bad',NOW)
        with self.assertRaises(ValueError):
            R.projection('a'*32,dt.datetime(2026,10,21,15,0,tzinfo=dt.timezone.utc))
        bad = dict(R.PINS)
        bad[R.CONTROLLER_REVIEW] = '0'*64
        with mock.patch.object(R,'PINS',bad),self.assertRaises(R.Refused):
            R.projection('a'*32,NOW)

    def test_entrypoints_refuse_without_any_effect(self):
        with mock.patch.object(R,'run_once',side_effect=AssertionError('effect')):
            with self.assertRaisesRegex(R.Refused,'EFFECT_DISABLED'):
                R.execute()
        with mock.patch.object(O,'run_observer',side_effect=AssertionError('effect')):
            with self.assertRaisesRegex(O.Refused,'EFFECT_DISABLED'):
                O.execute()

    def test_no_retry_claim_and_exact_public_leaf(self):
        with tempfile.TemporaryDirectory(prefix='public-probe-fixture-',dir=R.HERE) as base:
            path = Path(base)/'once'
            first = R.Attempt(path)
            first.claim()
            try:
                first.mkdir('stage',0o755)
                first.mkdir('stage/probe',0o755)
                first.write('stage/probe/request.json',R.REQUEST,0o444)
                self.assertEqual((path/'stage/probe/request.json').read_bytes(),R.REQUEST)
                self.assertEqual(json.loads((path/'consumed.json').read_bytes())['retry_allowed'],False)
            finally:
                first.close()
            second = R.Attempt(path)
            try:
                with self.assertRaises(FileExistsError): second.claim()
            finally:
                second.close()

    def test_umask_0077_reproduces_predecessor_and_repairs_new_attempt(self):
        source = R.LOCAL/'context-public-namespace-probe-release-0002/release.py'
        spec = importlib.util.spec_from_file_location('old_public_probe_fixture',source)
        old = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(old)
        with tempfile.TemporaryDirectory(prefix='public-umask-fixture-',dir=R.HERE) as base:
            old_path = Path(base)/'old-once'
            new_path = Path(base)/'new-once'
            previous_umask = os.umask(0o077)
            try:
                predecessor = old.Attempt(old_path)
                predecessor.claim()
                try:
                    with self.assertRaisesRegex(old.Refused,'DIR_MODE_OR_OWNER'):
                        predecessor.mkdir('stage',0o755)
                    self.assertEqual((old_path/'stage').stat().st_mode & 0o777,0o700)
                    self.assertFalse(json.loads((old_path/'consumed.json').read_bytes())['retry_allowed'])
                finally:
                    predecessor.close()
                successor = R.Attempt(new_path)
                successor.claim()
                try:
                    successor.mkdir('stage/probe/public-only',0o755)
                    successor.mkdir('control',0o700)
                    successor.write('stage/probe/public-only/request.json',R.REQUEST,0o444)
                    for name in ('stage','stage/probe','stage/probe/public-only'):
                        self.assertEqual((new_path/name).stat().st_mode & 0o777,0o755)
                    self.assertEqual((new_path/'control').stat().st_mode & 0o777,0o700)
                    self.assertEqual((new_path/'stage/probe/public-only/request.json').read_bytes(),R.REQUEST)
                    self.assertFalse(json.loads((new_path/'consumed.json').read_bytes())['retry_allowed'])
                finally:
                    successor.close()
            finally:
                os.umask(previous_umask)

    def test_existing_wrong_mode_is_refused_without_chmod(self):
        with tempfile.TemporaryDirectory(prefix='public-existing-fixture-',dir=R.HERE) as base:
            path = Path(base)/'once'
            attempt = R.Attempt(path)
            attempt.claim()
            try:
                os.mkdir(path/'stage',0o700)
                with mock.patch.object(R.os,'fchmod',side_effect=AssertionError('existing chmod')):
                    with self.assertRaisesRegex(R.Refused,'DIR_MODE_OR_OWNER'):
                        attempt.mkdir('stage',0o755)
                self.assertEqual((path/'stage').stat().st_mode & 0o777,0o700)
                self.assertFalse(json.loads((path/'consumed.json').read_bytes())['retry_allowed'])
            finally:
                attempt.close()

    def test_failure_after_open_closes_child_descriptor(self):
        with tempfile.TemporaryDirectory(prefix='public-open-fixture-',dir=R.HERE) as base:
            path = Path(base)/'once'
            attempt = R.Attempt(path)
            attempt.claim()
            real_open = os.open
            acquired = []
            def tracked_open(name,*args,**kwargs):
                fd = real_open(name,*args,**kwargs)
                if name == 'stage': acquired.append(fd)
                return fd
            try:
                previous_umask = os.umask(0o077)
                try:
                    with mock.patch.object(R.os,'open',side_effect=tracked_open),\
                         mock.patch.object(R.os,'fchmod',side_effect=OSError('fixture chmod')):
                        with self.assertRaisesRegex(OSError,'fixture chmod'):
                            attempt.mkdir('stage',0o755)
                finally:
                    os.umask(previous_umask)
                self.assertEqual(len(acquired),1)
                with self.assertRaises(OSError): os.fstat(acquired[0])
                self.assertTrue((path/'stage').is_dir())
                self.assertEqual((path/'stage').stat().st_mode & 0o777,0o700)
            finally:
                attempt.close()

    def test_inspect_exact_mounts_and_negatives(self):
        selected = R.projection('b'*32,NOW)
        cid = 'c'*64
        row = {'Id':cid,'Name':'/'+R.NAME,'Image':R.IMAGE,
               'HostConfig':{'ReadonlyRootfs':True,'NetworkMode':'none'},
               'State':{'Pid':123},'Mounts':[
                   {'Source':m['source'],'Destination':m['target'],
                    'Type':'bind','RW':False} for m in selected['mounts']]}
        self.assertEqual(R.verify_inspect(json.dumps([row]).encode(),cid,selected,True),123)
        row['Mounts'][0]['RW'] = True
        with self.assertRaisesRegex(R.Refused,'INSPECT_FIVE_EXACT_RO_BINDS'):
            R.verify_inspect(json.dumps([row]).encode(),cid,selected,True)
        row['Mounts'][0]['RW'] = False
        row['Mounts'].append({'Source':'/private','Destination':'/workspace/private',
                              'Type':'bind','RW':False})
        with self.assertRaises(R.Refused):
            R.verify_inspect(json.dumps([row]).encode(),cid,selected,True)

    def test_child_mount_and_erofs_causal(self):
        good = b''.join(f'{i} 0 0:{i} / {target} ro,relatime - ext4 /dev/root rw\n'.encode()
                        for i,target in enumerate(C.MOUNT_TARGETS,1))
        self.assertEqual(len(C.mountinfo_ro(good)),64)
        with self.assertRaisesRegex(RuntimeError,'FIVE_VFS_READ_ONLY_MOUNTS'):
            C.mountinfo_ro(good.replace(b'ro,relatime',b'rw,relatime'))
        with self.assertRaisesRegex(RuntimeError,'WORKSPACE_RO_NO_NESTED_MOUNT'):
            C.mountinfo_ro(good+b'6 1 0:6 / /workspace/nested rw - ext4 /dev/root rw\n')
        def fail(*_): raise OSError(errno.EROFS,'read-only')
        self.assertEqual(C.require_erofs(fail,lambda _:False),30)
        with self.assertRaisesRegex(RuntimeError,'EROFS_SENTINEL'):
            C.require_erofs(fail,lambda _:True)

    def test_external_join_exact_os_and_postack(self):
        value = {'schema':'context-public-only-probe-terminal/v1',
                 'status':'PROVISIONAL_EXTERNAL_OS_REVIEW_REQUIRED',
                 'name':R.NAME,'attempt':str(R.ATTEMPT),'retry_allowed':False,
                 'cid':'c'*64,'child_pid':123,
                 'parent_peer':[123,os.getuid(),os.getgid()],
                 'erofs_errno':30,'request_sha256':R.sha(R.REQUEST),
                 'child_os_exit':0,'child_stdout_sha256':R.sha(b''),
                 'child_stderr_sha256':R.sha(b''),
                 'five_read_only_mounts':True,
                 'nested_writable_or_private_mount':False,
                 'post_ack_visibility':True,'cid_absent':True,'name_absent':True,
                 'mountinfo_sha256':'d'*64}
        raw = R.wire(value)
        summary = R.wire({'status':'PROVISIONAL_EXTERNAL_OS_REVIEW_REQUIRED',
                          'terminal_sha256':R.sha(raw),'attempt':str(R.ATTEMPT),
                          'name':R.NAME,'retry_allowed':False})
        gone = Result(1,b'[]\n',
                      f'Error response from daemon: No such container: {value["cid"]}\n'.encode())
        absent = Result()
        self.assertEqual(O.join(0,summary,b'',raw,R.REQUEST,gone,absent)['overall'],
                         'PASS_BOUNDED_PUBLIC_NAMESPACE_PROBE_ONLY')
        for label,args in [
            ('nonzero',(1,summary,b'',raw,R.REQUEST,gone,absent)),
            ('stderr',(0,summary,b'bad',raw,R.REQUEST,gone,absent)),
            ('output',(0,summary,b'',raw,b'wrong',gone,absent)),
            ('cid',(0,summary,b'',raw,R.REQUEST,Result(0,b'cid\n'),absent)),
            ('name',(0,summary,b'',raw,R.REQUEST,gone,Result(out=b'cid\n'))),
        ]:
            with self.subTest(label=label),self.assertRaises(O.Refused):
                O.join(*args)
        bad = dict(value,post_ack_visibility=False)
        with self.assertRaises(O.Refused):
            O.join(0,summary,b'',R.wire(bad),R.REQUEST,gone,absent)

    def test_real_popen_observer_lifecycle_success_late_timeout_and_exit(self):
        terminal_value = {
            'schema':'context-public-only-probe-terminal/v1',
            'status':'PROVISIONAL_EXTERNAL_OS_REVIEW_REQUIRED',
            'name':O.R.NAME,'attempt':str(O.R.ATTEMPT),'retry_allowed':False,
            'cid':'c'*64,'child_pid':123,
            'parent_peer':[123,os.getuid(),os.getgid()],
            'erofs_errno':30,'request_sha256':O.R.sha(O.R.REQUEST),
            'child_os_exit':0,'child_stdout_sha256':O.R.sha(b''),
            'child_stderr_sha256':O.R.sha(b''),
            'five_read_only_mounts':True,
            'nested_writable_or_private_mount':False,
            'post_ack_visibility':True,'cid_absent':True,'name_absent':True,
            'mountinfo_sha256':'d'*64}
        terminal = O.R.wire(terminal_value)
        summary = O.R.wire({
            'status':'PROVISIONAL_EXTERNAL_OS_REVIEW_REQUIRED',
            'terminal_sha256':O.R.sha(terminal),
            'attempt':str(O.R.ATTEMPT),'name':O.R.NAME,'retry_allowed':False})
        def read_file(path,digest):
            path = Path(path)
            if path == O.R.ATTEMPT/'terminal.json':
                self.assertEqual(digest,O.R.sha(terminal))
                return terminal
            if path == O.R.OUTPUT:
                self.assertEqual(digest,O.R.sha(O.R.REQUEST))
                return O.R.REQUEST
            return O.R.check_file(path,digest)
        def docker(argv):
            if argv[1] == 'inspect':
                return Result(1,b'[]\n',
                    f'Error response from daemon: No such container: {terminal_value["cid"]}\n'.encode())
            self.assertEqual(argv[1],'ps')
            return Result()
        with tempfile.TemporaryDirectory(prefix='observer-popen-fixture-',
                                         dir=R.HERE) as base:
            for label,tail,exit_code,timeout,expected in (
                ('success','',0,2,'PASS'),
                ('late',"time.sleep(0.05);sys.stdout.buffer.write(b'LATE\\n');sys.stdout.flush()",0,2,'UNKNOWN'),
                ('timeout','time.sleep(1)',0,0.05,'UNKNOWN'),
                ('overflow',"sys.stdout.buffer.write(b'X'*9000);sys.stdout.flush()",0,2,'UNKNOWN'),
                ('exit','',7,2,'UNKNOWN')):
                script = ';'.join(x for x in (
                    'import sys,time',
                    "sys.stdout.buffer.write(bytes.fromhex('"+summary.hex()+"'))",
                    'sys.stdout.flush()',tail,f'sys.exit({exit_code})') if x)
                def real_spawn(_argv,**kwargs):
                    return subprocess.Popen([sys.executable,'-I','-B','-S','-c',script],
                                            **kwargs)
                observation = Path(base)/label
                with self.subTest(label=label),mock.patch.object(O,'EFFECT_ENABLED',True),\
                     mock.patch.object(O.R,'EFFECT_ENABLED',True):
                    if expected == 'PASS':
                        try:
                            result = O.run_observer(spawn=real_spawn,
                                preflight=lambda **_:None,read_file=read_file,
                                docker_call=docker,observation_path=observation,
                                timeout=timeout)
                        except O.Refused:
                            self.fail((observation/'observation.json').read_text())
                        self.assertEqual(result['overall'],
                                         'PASS_BOUNDED_PUBLIC_NAMESPACE_PROBE_ONLY')
                        self.assertEqual(json.loads((observation/'observation.json').read_bytes())['status'],
                                         'PROVISIONAL_MATCH')
                    else:
                        with self.assertRaisesRegex(O.Refused,'EXTERNAL_OBSERVER_UNKNOWN_NO_RETRY'):
                            O.run_observer(spawn=real_spawn,
                                preflight=lambda **_:None,read_file=read_file,
                                docker_call=docker,observation_path=observation,
                                timeout=timeout)
                        record = json.loads((observation/'observation.json').read_bytes())
                        self.assertEqual(record['status'],'UNKNOWN_PRESERVE_NO_RETRY')
                        self.assertEqual(record['error_class'],
                            {'late':'JSONDecodeError','timeout':'TimeoutExpired',
                             'overflow':'CaptureUnknown','exit':'Refused'}[label])
                        if label == 'timeout':
                            self.assertEqual((observation/'stdout').read_bytes(),summary)
                        if label == 'overflow':
                            self.assertEqual(len((observation/'stdout').read_bytes()),O.CAPTURE)
                    self.assertFalse(json.loads((observation/'consumed.json').read_bytes())['retry_allowed'])

    def test_failed_release_empty_stdout_retains_direct_exit_reason(self):
        with tempfile.TemporaryDirectory(prefix='failed-release-fixture-',dir=R.HERE) as base:
            observation = Path(base)/'observer'
            def failed_spawn(_argv,**kwargs):
                return subprocess.Popen([sys.executable,'-I','-B','-S','-c',
                    "import sys;sys.stderr.buffer.write(b'public fixture failure\\n');sys.exit(1)"],
                    **kwargs)
            with mock.patch.object(O,'EFFECT_ENABLED',True),\
                 mock.patch.object(O.R,'EFFECT_ENABLED',True):
                with self.assertRaisesRegex(O.Refused,'EXTERNAL_OBSERVER_UNKNOWN_NO_RETRY'):
                    O.run_observer(spawn=failed_spawn,preflight=lambda **_:None,
                                   read_file=lambda *_: (_ for _ in ()).throw(
                                       AssertionError('must not parse terminal')),
                                   docker_call=lambda *_: (_ for _ in ()).throw(
                                       AssertionError('must not call Docker')),
                                   observation_path=observation,timeout=2)
            record = json.loads((observation/'observation.json').read_bytes())
            self.assertEqual(record['status'],'UNKNOWN_PRESERVE_NO_RETRY')
            self.assertEqual(record['error_class'],'Refused')
            self.assertEqual(record['error_detail'],'EXTERNAL_RELEASE_EXIT_OR_STREAMS')
            self.assertEqual((observation/'stdout').read_bytes(),b'')
            self.assertEqual((observation/'stderr').read_bytes(),b'public fixture failure\n')


if __name__ == '__main__': unittest.main()
