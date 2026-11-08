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


def good_mounts():
    return b''.join(f'{i} 0 0:{i} / {target} ro,relatime - ext4 /dev/root rw\n'.encode()
                    for i,target in enumerate(C.MOUNT_TARGETS,1))

class ReleaseTests(unittest.TestCase):
    def test_disposable_projection_exact_six_ro_mounts(self):
        value = R.projection('b'*32,NOW)
        argv = value['create_argv']
        self.assertFalse(value['effect_enabled'])
        self.assertEqual(value['role'],'probe/public-only')
        self.assertEqual(argv.count('--mount'),6)
        self.assertEqual([argv[i+1] for i,v in enumerate(argv) if v == '--mount'],
                         [f"type=bind,src={m['source']},dst={m['target']},readonly"
                          for m in value['mounts']])
        self.assertEqual([m['target'] for m in value['mounts']],
                         ['/workspace','/control','/runner','/cache-disabled',
                          '/attempt/input/lab-context-native-reader','/context-policy'])
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
        with self.assertRaisesRegex(R.Refused,'INSPECT_SIX_EXACT_RO_BINDS'):
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
        with self.assertRaisesRegex(RuntimeError,'SIX_VFS_READ_ONLY_MOUNTS'):
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
                 'six_read_only_mounts':True,'policy_sha256':R.sha(R.POLICY_PUBLIC),
                 'policy_erofs_errno':30,'mountinfo_raw_retained':True,
                 'nested_writable_or_private_mount':False,
                 'post_ack_visibility':True,'cid_absent':True,'name_absent':True,
                 'mountinfo_sha256':R.sha(good_mounts())}
        raw = R.wire(value)
        summary = R.wire({'status':'PROVISIONAL_EXTERNAL_OS_REVIEW_REQUIRED',
                          'terminal_sha256':R.sha(raw),'attempt':str(R.ATTEMPT),
                          'name':R.NAME,'retry_allowed':False})
        gone = Result(1,b'[]\n',
                      f'Error response from daemon: No such container: {value["cid"]}\n'.encode())
        absent = Result()
        self.assertEqual(O.join(0,summary,b'',raw,R.REQUEST,gone,absent,good_mounts(),R.POLICY_PUBLIC)['overall'],
                         'PASS_BOUNDED_PUBLIC_NAMESPACE_PROBE_ONLY')
        for label,args in [
            ('nonzero',(1,summary,b'',raw,R.REQUEST,gone,absent)),
            ('stderr',(0,summary,b'bad',raw,R.REQUEST,gone,absent)),
            ('output',(0,summary,b'',raw,b'wrong',gone,absent)),
            ('cid',(0,summary,b'',raw,R.REQUEST,Result(0,b'cid\n'),absent)),
            ('name',(0,summary,b'',raw,R.REQUEST,gone,Result(out=b'cid\n'))),
        ]:
            with self.subTest(label=label),self.assertRaises(O.Refused):
                O.join(*args,good_mounts(),R.POLICY_PUBLIC)
        for mounts, policy in ((good_mounts()+b'9 0 0:9 / /context-policy/hidden rw - ext4 /dev/root rw\n',R.POLICY_PUBLIC),
                               (good_mounts(),b'wrong-public-policy')):
            with self.assertRaises((O.Refused,R.Refused)):
                O.join(0,summary,b'',raw,R.REQUEST,gone,absent,mounts,policy)
        bad = dict(value,post_ack_visibility=False)
        with self.assertRaises(O.Refused):
            O.join(0,summary,b'',R.wire(bad),R.REQUEST,gone,absent,good_mounts(),R.POLICY_PUBLIC)




if __name__ == '__main__': unittest.main()

class PolicyMountTests(unittest.TestCase):
    def test_policy_mount_is_distinct_public_only_and_exact(self):
        selected=R.projection('a'*32,NOW)
        self.assertEqual(selected['mounts'][-1],{'source':str(R.ATTEMPT/'policy-public'),'target':'/context-policy','read_only':True})
        self.assertFalse(selected['policy_mount_is_authority'])
        self.assertFalse(R.EFFECT_ENABLED);self.assertFalse(O.EFFECT_ENABLED)
        self.assertNotIn('context-jit-private',str(selected))
    def test_raw_mountinfo_retained_encoding_and_parser_parity(self):
        import base64,ast
        raw=good_mounts();ready={'mountinfo_b64':base64.b64encode(raw).decode(),'mountinfo_sha256':R.sha(raw)}
        self.assertEqual(R.decode_mountinfo(ready),raw)
        nodes=[]
        for mod in (R,C):
            tree=ast.parse(Path(mod.__file__).read_bytes())
            nodes.append(ast.dump(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='mountinfo_ro'),include_attributes=False))
        self.assertEqual(nodes[0],nodes[1])
        for change in ({'mountinfo_sha256':'0'*64},{'mountinfo_b64':'!!!!'},{'mountinfo_b64':'a'*87385}):
            with self.assertRaises(R.Refused):R.decode_mountinfo(dict(ready,**change))
    def test_missing_writable_duplicate_nested_policy_mounts_refuse(self):
        raw=good_mounts()
        rows=raw.splitlines(keepends=True)
        for bad in (b''.join(rows[:-1]),raw.replace(b'/context-policy ro',b'/context-policy rw'),
                    raw+rows[-1],raw+b'8 0 0:8 / /context-policy/key rw - ext4 /dev/root rw\n'):
            for mod in (R,C):
                with self.assertRaises((R.Refused,RuntimeError)):mod.mountinfo_ro(bad)
    def test_policy_erofs_is_discriminating(self):
        for error in (errno.EACCES,errno.ENOENT):
            with self.assertRaisesRegex(RuntimeError,'POLICY_EROFS_REQUIRED'):
                C.require_policy_erofs(lambda *_:(_ for _ in ()).throw(OSError(error,'inert')))
        self.assertEqual(C.require_policy_erofs(lambda *_:(_ for _ in ()).throw(OSError(errno.EROFS,'inert'))),30)
        closed=[]
        with self.assertRaisesRegex(RuntimeError,'POLICY_MOUNT_WRITABLE'):
            C.require_policy_erofs(lambda *_:73,closed.append)
        self.assertEqual(closed,[73])
    def test_public_policy_readback_mode_bytes_and_nofollow(self):
        with tempfile.TemporaryDirectory(prefix='public-policy-fixture-',dir=R.HERE) as d:
            path=Path(d)/'permission.json';path.write_bytes(R.POLICY_PUBLIC);path.chmod(0o600)
            with mock.patch.object(C,'POLICY_PATH',path):
                self.assertEqual(C.read_policy(),R.sha(R.POLICY_PUBLIC))
                path.write_bytes(b'wrong')
                with self.assertRaisesRegex(RuntimeError,'PUBLIC_POLICY_READBACK'):C.read_policy()
                path.write_bytes(R.POLICY_PUBLIC);path.chmod(0o644)
                with self.assertRaisesRegex(RuntimeError,'PUBLIC_POLICY_READBACK'):C.read_policy()
            link=Path(d)/'link';link.symlink_to(path)
            with mock.patch.object(C,'POLICY_PATH',link):
                with self.assertRaises(OSError):C.read_policy()
    def test_public_policy_parent_write_only_after_ready_in_source(self):
        import ast
        text=Path(R.__file__).read_text();node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='run_once')
        body=ast.get_source_segment(text,node)
        self.assertLess(body.index('ready = recv'),body.index("attempt.write('child-mountinfo.txt'"))
        self.assertLess(body.index("attempt.write('child-mountinfo.txt'"),body.index("'context-public-probe-go/v1'"))
        self.assertLess(body.index("'context-public-probe-go/v1'"),body.index("attempt.write('policy-public/permission.json'"))
        self.assertLess(body.index("attempt.write('policy-public/permission.json'"),body.index("'context-public-probe-ack/v1'"))
    def test_synthetic_child_handshake_includes_policy_and_raw_original(self):
        import io,base64
        token='e'*32;packets=[]
        with tempfile.TemporaryDirectory(prefix='public-child-fixture-',dir=R.HERE) as d:
            here=Path(d);out=here/'packages/0001'
            class Socket:
                def settimeout(self,*a):pass
                def connect(self,p):self.path=p
                def getsockopt(self,*a):
                    import struct
                    return struct.pack('3i',0,os.getuid(),os.getgid())
                def send(self,raw):packets.append(json.loads(raw));return len(raw)
                def recv(self,*a):
                    if len(packets)==1 and not out.exists():
                        out.mkdir(parents=True);(out/'request.json').write_bytes(R.REQUEST)
                        return R.wire({'schema':'context-public-probe-go/v1','token':token})
                    return R.wire({'schema':'context-public-probe-ack/v1','token':token,'leaf':'request.json','sha256':R.sha(R.REQUEST),'policy_sha256':R.sha(R.POLICY_PUBLIC)})
                def close(self):self.closed=True
            sock=Socket()
            with mock.patch.object(C,'HERE',here),mock.patch.object(C,'OUT',out),\
                 mock.patch('builtins.open',return_value=io.BytesIO(good_mounts())),\
                 mock.patch.object(C.socket,'socket',return_value=sock),\
                 mock.patch.object(C,'require_erofs',return_value=30),\
                 mock.patch.object(C,'read_policy',return_value=R.sha(R.POLICY_PUBLIC)),\
                 mock.patch.object(C,'require_policy_erofs',return_value=30):
                C.main({'token':token,'uid':os.getuid(),'gid':os.getgid()})
            self.assertTrue(sock.closed);self.assertEqual(len(packets),2)
            self.assertEqual(base64.b64decode(packets[0]['mountinfo_b64']),good_mounts())
            self.assertEqual(packets[1]['policy_sha256'],R.sha(R.POLICY_PUBLIC))
            self.assertEqual(packets[1]['policy_erofs_errno'],30)
