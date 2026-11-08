"""Disposable owned scratch and same-process seqpacket tests only."""
import base64
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import socket
import stat
import tempfile
import unittest
import uuid
from unittest import mock
from array import array

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from t35_external_v1.phase_scoped_v2 import context_ipc_model_0001 as model
from t35_external_v1.phase_scoped_v2 import context_package_writer_0001 as writer
from t35_external_v1.phase_scoped_v2 import context_package_transport_0001 as transport


class ContextScratchTests(unittest.TestCase):
    def setUp(self):
        self.scratch = Path('/tmp')/('lc-u02-05-context-writer-'+uuid.uuid4().hex)
        self.scratch.mkdir(mode=0o700)
        self.scratch_identity=(self.scratch.stat().st_dev,self.scratch.stat().st_ino)
        self.context = self.scratch/'output/legacy-fixture-source/context'
        self.context.mkdir(parents=True,mode=0o700)
        for p in (self.scratch,self.scratch/'output',self.context.parent,self.context): p.chmod(0o700)
        self.private = Path(str(self.scratch).replace('context-writer-','context-private-',1))
        self.addCleanup(self.cleanup)
        self.source = {'path':str(self.context/'source-manifest.json'),'sha256':'a'*64}
        self.now = dt.datetime(2026,10,19,12,tzinfo=dt.timezone.utc)
        self.peer = (os.getpid(),transport.wire.process_start(os.getpid()),os.getuid(),os.getgid())
        self.period = {'not_before':'2026-10-19T11:00:00Z','expires_at':'2026-10-19T13:00:00Z','binding':{'path':'/tmp/synthetic-source/period.json','sha256':'b'*64}}
        protocol = model.ProtocolModel(attempt_id='scratch-context-0001',selection_sha256='c'*64,predecessor={n:model.sha(n.encode()) for n in ('source','source_package','mapped','mapped_package')},package_path=str(self.context/'packages/0001'),private_root_path=str(self.private),uid=os.getuid(),source_period=self.period,source_scope_ref='scope:synthetic',principal_ref='principal:synthetic',mapped_output_sha256=model.sha(b'mapped-output'),peer=self.peer,now=self.now)
        self.session = transport.ScratchSession(self.context,self.source,protocol)
        self.parent,self.client = transport.wire.socket_pair()
        self.server=transport.Server(self.parent,self.peer,self.session)
        self.addCleanup(self.server.close)
        self.addCleanup(self.client.close)
        self.key=Ed25519PrivateKey.from_private_bytes(b'\x02'*32)
        self.policy={'schema_version':'lab-context-host-policy/v1-candidate','host_uid':os.getuid(),'principal_ref':'principal:synthetic','scope_ref':'scope:synthetic','reader_public_key':base64.b64encode(self.key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)).decode(),'not_before':'2026-10-19T11:59:59Z','expires_at':'2026-10-19T12:20:00Z','max_input_bytes':model.REQUEST_MAX,'max_output_bytes':model.ARTIFACT_TOTAL_MAX,'max_session_seconds':900,'period_binding':self.period['binding'],'allowed_operations':['context.get','session.open'],'authority_effect':'none','actual_owner_outcome':None}

    def cleanup(self):
        # Only roots exclusively created by this test, after assertions. Never
        # enumerate/delete an unrelated /tmp prefix or author evidence tree.
        for p in (self.private,self.scratch):
            if p.exists():
                self.assertEqual(p.lstat().st_uid,os.getuid())
                self.assertTrue(p.is_dir() and not p.is_symlink())
                if p == self.scratch:self.assertEqual((p.stat().st_dev,p.stat().st_ino),self.scratch_identity)
                shutil.rmtree(p)
        self.assertFalse(self.private.exists())
        self.assertFalse(self.scratch.exists())
        print(json.dumps({'scratch_cleanup':'observed_absent','scratch':str(self.scratch),'scratch_identity':self.scratch_identity,'private':str(self.private)}))

    def exchange(self,verb,payload):
        raw=transport.frame(self.session,verb,payload)
        transport.wire.send_frame(self.client,raw)
        self.server.receive_one()
        ack=model.codec.decode(transport.wire.recv_frame(self.client,self.peer))
        self.assertEqual(ack['request_sha256'],model.sha(raw))
        self.assertFalse(ack['effect_ready'])
        return ack

    def action(self,verb,payload=None):
        return self.exchange('ACTION',{'verb':verb,'payload':{} if payload is None else payload})

    def initial(self):
        self.action('PREPARE')
        self.assertEqual(list((self.context/'packages/0001').iterdir()),[])
        self.action('PRIVATE_ROOT')
        self.action('PROVISION',{'path':str(self.private/'permission.json'),'policy':self.policy,'policy_sha256':model.sha(model.encoded(self.policy))})
        self.assertEqual((self.private/'permission.json').read_bytes(),model.encoded(self.policy))

    def proof(self):
        challenge={'schema_version':'lab-context-host-challenge/v1-candidate','host_instance_ref':'host:synthetic','connection_ref':'connection:synthetic','nonce':'d'*64,'policy_sha256':model.sha(model.encoded(self.policy)),'expires_at':self.policy['expires_at'],'authority_effect':'none'}
        return model.compact({'challenge':challenge,'signature':base64.b64encode(self.key.sign(model.compact(challenge))).decode()})

    def blob(self,name,raw):
        self.exchange('BLOB_BEGIN',{'leaf':name,'sha256':model.sha(raw),'size_bytes':len(raw)})
        for offset in range(0,len(raw),transport.CHUNK_MAX):
            self.exchange('BLOB_CHUNK',{'offset':offset,'bytes_base64':base64.b64encode(raw[offset:offset+transport.CHUNK_MAX]).decode()})

    def emit(self,name,raw):
        self.blob(name,raw)
        return self.action('EMIT',{'leaf':name})

    def prefix38(self):
        self.initial()
        for name,raw in [('request.json',b'x'*70000),('authentication-proof.json',self.proof()),('trusted-context.json',b'{"synthetic":true}'),('host-permission-public.json',model.encoded(self.policy))]:
            self.emit(name,raw)
        ack=self.action('NATIVE_READ',{'mapped_package_sha256':model.sha(b'mapped_package'),'output_sha256':model.sha(b'mapped-output'),'size_bytes':13})
        self.assertEqual(ack['observation'],'MODEL_ONLY')
        for name in writer.LEAVES[4:38]: self.emit(name,model.encoded({'synthetic_leaf':name,'authority_effect':'none'}))

    def manifest(self):
        owned=self.session.writer
        return model.encoded({'schema_version':'lab-context-scratch-package/v1-inert','files':owned.manifest_rows(),'source_manifest_binding':self.source,'authority_effect':'none','actual_owner_outcome':None,'delivery_binding':{'path':str(self.context/'packages/0001/delivery.json'),'sha256':owned.hashes['delivery.json']},'provenance_binding':{'path':str(self.context/'packages/0001/delivery-provenance.json'),'sha256':owned.hashes['delivery-provenance.json']},'claim_ceiling':writer.CEILING})

    def final_two(self):
        self.action('RELEASE_PRIVATE')
        self.assertFalse(self.private.exists())
        self.emit('build-result.json',model.encoded({'result':'MODEL_ONLY','authority_effect':'none'}))
        self.emit('manifest.json',self.manifest())

    def assert_unknown(self):
        self.assertTrue(self.session.unknown)
        self.assertTrue(self.session.protocol.retain_attempt)
        if self.session.writer is not None:self.assertTrue(self.session.writer.unknown)

    def test_complete_40_files_39_rows_real_seqpacket_scratch(self):
        self.prefix38();self.final_two();ack=self.action('FINISH')
        self.assertEqual(ack['observation'],'SCRATCH_PACKAGE_VERIFIED')
        self.assertTrue(self.session.protocol.finished)
        self.assertFalse(self.session.unknown)
        package=self.context/'packages/0001'
        files=[p for p in package.rglob('*') if p.is_file()]
        self.assertEqual(len(files),40)
        for p in files:self.assertEqual(stat.S_IMODE(p.stat().st_mode),0o600)
        for row in self.session.writer.manifest_rows():self.assertEqual(model.sha(Path(row['path']).read_bytes()),row['sha256'])
        self.assertTrue((self.scratch/writer.MARKER).is_file())
        with self.assertRaises(writer.Refusal):self.session.receive(transport.frame(self.session,'ACTION',{'verb':'FINISH','payload':{}}))

    def test_preexisting_empty_package_is_not_adopted(self):
        (self.context/'packages/0001').mkdir(parents=True,mode=0o700)
        with self.assertRaisesRegex(writer.Refusal,'preexisting_package'):self.action('PREPARE')
        self.assert_unknown();self.assertEqual(list((self.context/'packages/0001').iterdir()),[])
        self.assertFalse((self.scratch/writer.MARKER).exists())

    def test_private_preexisting_even_empty_refuses_before_package(self):
        self.private.mkdir(mode=0o700)
        with self.assertRaisesRegex(writer.Refusal,'preexisting_private_root'):self.action('PREPARE')
        self.assert_unknown();self.assertFalse((self.context/'packages').exists())

    def test_wrong_order_never_creates_package(self):
        with self.assertRaisesRegex(writer.Refusal,'action_order'):self.action('PRIVATE_ROOT')
        self.assert_unknown();self.assertFalse((self.context/'packages').exists())

    def test_private_release_before_artifacts_refuses(self):
        self.initial()
        with self.assertRaisesRegex(writer.Refusal,'action_order'):self.action('RELEASE_PRIVATE')
        self.assert_unknown();self.assertTrue((self.private/'permission.json').is_file())

    def test_policy_extra_private_key_refuses_without_write(self):
        self.action('PREPARE');self.action('PRIVATE_ROOT')
        self.policy['private_key']='SYNTHETIC-NOT-SECRET'
        with self.assertRaisesRegex(model.Refusal,'CLOSED_FIELDS'):self.action('PROVISION',{'path':str(self.private/'permission.json'),'policy':self.policy,'policy_sha256':model.sha(model.encoded(self.policy))})
        self.assert_unknown();self.assertEqual(list(self.private.iterdir()),[])

    def test_corrupt_private_policy_prevents_release(self):
        self.prefix38()
        (self.private/'permission.json').write_bytes(b'changed')
        with self.assertRaisesRegex(writer.Refusal,'policy_changed'):self.action('RELEASE_PRIVATE')
        self.assert_unknown();self.assertTrue(self.private.exists())

    def test_manifest_changed_row_refuses_before_file(self):
        self.prefix38();self.action('RELEASE_PRIVATE');self.emit('build-result.json',b'fixture')
        raw=self.manifest().replace(self.session.writer.hashes['request.json'].encode(),b'0'*64)
        with self.assertRaisesRegex(writer.Refusal,'manifest_binding'):self.emit('manifest.json',raw)
        self.assert_unknown();self.assertFalse((self.context/'packages/0001/manifest.json').exists())

    def test_file_fsync_failure_retains_partial_and_marker(self):
        self.initial();self.blob('request.json',b'opaque')
        with mock.patch.object(writer.os,'fsync',side_effect=OSError('injected')):
            with self.assertRaises(OSError):self.action('EMIT',{'leaf':'request.json'})
        self.assert_unknown();self.assertTrue((self.context/'packages/0001/request.json').exists());self.assertTrue((self.scratch/writer.MARKER).exists())

    def test_parent_fsync_failure_does_not_ack(self):
        self.initial();self.blob('request.json',b'opaque');original=os.fsync
        def fail_dir(fd):
            if stat.S_ISDIR(os.fstat(fd).st_mode):raise OSError('injected-parent')
            return original(fd)
        with mock.patch.object(writer.os,'fsync',side_effect=fail_dir):
            with self.assertRaises(OSError):self.action('EMIT',{'leaf':'request.json'})
        self.assert_unknown();self.assertNotIn('request.json',self.session.writer.hashes)

    def test_lost_final_ack_is_unknown_even_after_complete_files(self):
        self.prefix38();self.final_two()
        raw=transport.frame(self.session,'ACTION',{'verb':'FINISH','payload':{}})
        transport.wire.send_frame(self.client,raw)
        with mock.patch.object(transport.wire,'send_frame',side_effect=transport.wire.TransportRefusal('injected-lost-ack')):
            with self.assertRaises(transport.wire.TransportRefusal):self.server.receive_one()
        self.assert_unknown();self.assertEqual(len(self.session.writer.hashes),40)

    def test_packet_replay_refuses_no_second_effect(self):
        raw=transport.frame(self.session,'ACTION',{'verb':'PREPARE','payload':{}})
        transport.wire.send_frame(self.client,raw);self.server.receive_one();transport.wire.recv_frame(self.client,self.peer)
        transport.wire.send_frame(self.client,raw)
        with self.assertRaisesRegex(writer.Refusal,'transport_ordinal'):self.server.receive_one()
        self.assert_unknown();self.assertEqual(list((self.context/'packages/0001').iterdir()),[])

    def test_scm_rights_closed_without_package(self):
        before=set(os.listdir('/proc/self/fd'))
        fd=os.open('/dev/null',os.O_RDONLY|os.O_CLOEXEC)
        try:
            self.client.sendmsg([transport.frame(self.session,'ACTION',{'verb':'PREPARE','payload':{}})],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array('i',[fd]))])
            with self.assertRaisesRegex(transport.wire.TransportRefusal,'SCM_RIGHTS'):self.server.receive_one()
        finally:os.close(fd)
        self.assert_unknown();self.assertFalse((self.context/'packages').exists())
        self.assertLessEqual(len(os.listdir('/proc/self/fd')),len(before))

    def test_wrong_pid_start_refuses_before_package(self):
        self.server.peer=(self.peer[0],self.peer[1]+1,*self.peer[2:])
        transport.wire.send_frame(self.client,transport.frame(self.session,'ACTION',{'verb':'PREPARE','payload':{}}))
        with self.assertRaisesRegex(transport.wire.TransportRefusal,'PEER_IDENTITY'):self.server.receive_one()
        self.assert_unknown();self.assertFalse((self.context/'packages').exists())

    def test_disconnect_retains_private_and_package(self):
        self.initial();self.client.close()
        with self.assertRaisesRegex(transport.wire.TransportRefusal,'DISCONNECTED'):self.server.receive_one()
        self.assert_unknown();self.assertTrue((self.private/'permission.json').exists())

    def test_out_of_order_chunk_refuses_before_leaf(self):
        self.initial();self.exchange('BLOB_BEGIN',{'leaf':'request.json','sha256':model.sha(b'x'),'size_bytes':1})
        with self.assertRaisesRegex(writer.Refusal,'chunk_order'):self.exchange('BLOB_CHUNK',{'offset':1,'bytes_base64':'eA=='})
        self.assert_unknown();self.assertFalse((self.context/'packages/0001/request.json').exists())

    def test_preexisting_symlink_leaf_preserves_target(self):
        self.initial()
        target=self.scratch/'untouched';target.write_bytes(b'unchanged')
        leaf=self.context/'packages/0001/request.json';leaf.symlink_to(target)
        with self.assertRaisesRegex(writer.Refusal,'package_extra_or_missing'):self.emit('request.json',b'new')
        self.assert_unknown();self.assertTrue(leaf.is_symlink());self.assertEqual(target.read_bytes(),b'unchanged')

    def test_preexisting_fifo_refuses_without_blocking(self):
        self.initial();leaf=self.context/'packages/0001/request.json';os.mkfifo(leaf,0o600)
        with self.assertRaisesRegex(writer.Refusal,'package_extra_or_missing'):self.emit('request.json',b'new')
        self.assert_unknown();self.assertTrue(stat.S_ISFIFO(leaf.lstat().st_mode))

    def test_equal_bytes_new_inode_refuses_next_write(self):
        self.initial();self.emit('request.json',b'original')
        leaf=self.context/'packages/0001/request.json';ino=leaf.stat().st_ino
        leaf.unlink();leaf.write_bytes(b'original');leaf.chmod(0o600)
        self.assertNotEqual(ino,leaf.stat().st_ino)
        with self.assertRaisesRegex(writer.Refusal,'emitted_leaf_changed'):self.emit('authentication-proof.json',self.proof())
        self.assert_unknown();self.assertFalse((self.context/'packages/0001/authentication-proof.json').exists())

    def test_partial_write_failure_retains_exact_prefix(self):
        self.initial();self.blob('request.json',b'partial-payload')
        original=os.write;calls=[]
        def partial(fd,raw):
            calls.append(1)
            if len(calls)==1:return original(fd,raw[:3])
            raise OSError('injected-short-write')
        with mock.patch.object(writer.os,'write',side_effect=partial):
            with self.assertRaises(OSError):self.action('EMIT',{'leaf':'request.json'})
        self.assert_unknown();self.assertEqual((self.context/'packages/0001/request.json').read_bytes(),b'par')
        with self.assertRaises(writer.Refusal):self.session.receive(transport.frame(self.session,'ACTION',{'verb':'EMIT','payload':{'leaf':'request.json'}}))

    def test_private_release_sync_failure_is_unknown(self):
        self.prefix38()
        with mock.patch.object(writer.os,'fsync',side_effect=OSError('injected-private-sync')):
            with self.assertRaises(OSError):self.action('RELEASE_PRIVATE')
        self.assert_unknown();self.assertTrue(self.private.exists());self.assertFalse((self.private/'permission.json').exists());self.assertFalse((self.context/'packages/0001/build-result.json').exists())

    def test_restrictive_umask_applies_only_to_owned_new_inodes(self):
        previous=os.umask(0o777)
        try:self.initial();self.emit('request.json',b'opaque')
        finally:os.umask(previous)
        self.assertEqual(stat.S_IMODE((self.context/'packages/0001').stat().st_mode),0o700)
        self.assertEqual(stat.S_IMODE((self.context/'packages/0001/request.json').stat().st_mode),0o600)

    def test_oversize_seqpacket_truncation_refuses(self):
        self.client.send(b'x'*65537)
        with self.assertRaisesRegex(transport.wire.TransportRefusal,'MSG_TRUNC'):self.server.receive_one()
        self.assert_unknown();self.assertFalse((self.context/'packages').exists())

    def test_close_observation_failure_stays_unknown_without_retry(self):
        self.prefix38();self.final_two();self.action('FINISH')
        selected=self.session.writer.marker_fd;original=os.close;seen=[]
        def uncertain(fd):
            original(fd)
            if fd == selected:
                seen.append(fd)
                raise OSError('injected-close-observation')
        with mock.patch.object(writer.os,'close',side_effect=uncertain):self.server.close()
        self.assertEqual(seen,[selected]);self.assert_unknown()
        self.assertEqual(self.session.writer.close_errors,1)


if __name__ == '__main__': unittest.main()
