"""Full adapted builder through reviewed real transport and held scratch writer."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest

from t35_external_v1.phase_scoped_v2 import mapper_package_integration_0005 as integration
from t35_external_v1.phase_scoped_v2 import mapper_package_transport_0001 as transport
from t35_external_v1.phase_scoped_v2 import mapper_package_writer_0001 as writer
from t35_external_v1.phase_scoped_v2 import mapper_package_ipc_model_0004 as wire

T=Path(__file__).parent
spec=importlib.util.spec_from_file_location('selected_mapper_client_fixture',T/'test_mapper_package_client_0004.py')
fixture=importlib.util.module_from_spec(spec);sys.modules[spec.name]=fixture;spec.loader.exec_module(fixture)
P=fixture.P


class IntegrationTests(unittest.TestCase):
    def run_case(self,scenario):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-mapper-writer-',dir='/tmp') as name:
            root=Path(name);config,roles,rows,projection=fixture.make_fixture(root/'output')
            mapped=Path(config['mapped']);package=mapped/'packages/0001'
            for p in (root,root/'output',mapped.parent,mapped):p.chmod(0o700)
            config['logical_family']=writer.plan.FAMILY
            (root/'output/config.json').write_bytes(fixture.encoded(config))
            roles['fixture_base']=str(T/'mapper_package_fixture_base_0005.py')
            roles['bridge']=str(P/'mapper_package_bridge_0005.py')
            if scenario=='direct-write':
                injected=root/'injected-base.py'
                injected.write_bytes((T/'mapper_package_fixture_base_0005.py').read_bytes()+b"\nPath(FIXTURE_CONFIG['root']).joinpath('forbidden-direct-write').write_bytes(b'forbidden')\n")
                roles['fixture_base']=str(injected)
            selected_paths={Path(r['path']) for r in rows}|{Path(p) for p in roles.values()}|{P/'mapper_package_runner_0005.py'}
            rows=[fixture.binding(p) for p in sorted(selected_paths)]
            parent,child=transport.socket_pair()
            pins={'mapper':config['mapper_pin'],'source':config['source_pin'],'reader':config['reader_pin'],'adapter':fixture.binding(P/'mapper_package_adapter_0004.py')['sha256']}
            selection={'posture':'synthetic-only','integration_version':'held-writer-fixture/v1','bindings':rows,'roles':roles,'preimage_sha256':fixture.sha((root/'output/preimage.py').read_bytes()),'cache':fixture.binding(fixture.CACHE),'interpreter':fixture.binding('/usr/bin/python3.14'),'inherited_fd':child.fileno(),'attempt_id':'held-writer-fixture','begin_pins':pins,'peer':[os.getpid(),os.getuid(),os.getgid()],'package':str(package),'logical_package':writer.plan.PACKAGE,'logical_source_binding':{'path':writer.plan.FAMILY+'/mapped/source-manifest.json','sha256':pins['mapper']}}
            manifest=root/'selection.json';manifest.write_bytes(fixture.encoded(selection));selected=fixture.binding(manifest)
            need_child=scenario not in ('wrong-manifest-digest','wrong-wire-digest')
            command=['/usr/bin/python3.14','-I','-B','-S','-X','pycache_prefix='+str(fixture.CACHE)]
            if sys.flags.optimize:command.append('-O')
            command +=[str(P/'mapper_package_runner_0005.py'),str(manifest),selected['sha256'],str(selected['size_bytes'])]
            process=None;server=None;out=err=b'';failure=None;events=[];started=time.monotonic();changed=False
            try:
                if scenario=='wrong-manifest-digest':
                    with self.assertRaises(RuntimeError):integration.selected_manifest(manifest,'f'*64,selected['size_bytes'])
                    self.assertFalse(package.exists());self.assertFalse((root/writer.ATTEMPT).exists());return
                if scenario=='wrong-wire-digest':
                    peer=(os.getpid(),transport.process_start(os.getpid()),os.getuid(),os.getgid())
                    server=integration.Mediator(parent,peer,manifest,selected['sha256'],selected['size_bytes'])
                    transport.send_frame(child,wire.encode(wire.envelope(selection['attempt_id'],'a'*64,0,'BEGIN',pins)))
                    with self.assertRaises(wire.Refusal):server.prepare_one()
                    self.assertFalse(package.exists());self.assertTrue(server.failed);return
                process=subprocess.Popen(command,pass_fds=(child.fileno(),),stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},cwd=str(root));child.close()
                peer=(process.pid,transport.process_start(process.pid),os.getuid(),os.getgid())
                server=integration.Mediator(parent,peer,manifest,selected['sha256'],selected['size_bytes'])
                self.assertEqual(server.selection_hash,hashlib.sha256(manifest.read_bytes()).hexdigest())
                while not server.finished:
                    try:event=server.prepare_one()
                    except BaseException as error:
                        failure=type(error).__name__;break
                    events.append(event)
                    if scenario=='lost-ack' and event['action']=='EMIT':
                        self.assertTrue(event['durable_receipt']['durable_observed'])
                        self.assertEqual(server.writer.index,1)
                        process.kill();process.wait(timeout=5)
                        server.close() # An unsent durable ACK is UNKNOWN even on explicit teardown.
                        try:server.send_pending()
                        except Exception as error:failure=type(error).__name__
                        self.assertTrue(server.failed);self.assertTrue(server.writer.unknown)
                        break
                    server.send_pending()
                    if event['action']=='BEGIN' and not changed:
                        if scenario=='source-drift':
                            (root/'output/config.json').write_bytes(b'{}\n');changed=True
                        elif scenario=='child-crash':
                            process.kill();process.wait(timeout=5);changed=True
                        elif scenario=='ancestor-detach':
                            mapped.rename(mapped.with_name('mapped-detached'));mapped.mkdir(mode=0o700);changed=True
                        elif scenario=='package-detach':
                            package.parent.rename(mapped/'packages-detached');package.parent.mkdir(mode=0o700);changed=True
                    if scenario=='extra-leaf' and event['action']=='EMIT' and not changed:
                        (package/'extra.json').write_bytes(b'{}\n');changed=True
                if failure is not None and process.poll() is None:
                    server.close()
                out,err=process.communicate(timeout=10)
                if scenario=='positive':
                    self.assertIsNone(failure);self.assertEqual(process.returncode,0,(out,err))
                    self.assertTrue(server.finished);self.assertTrue(server.writer.finished);self.assertFalse(server.writer.unknown)
                    self.assertEqual(server.writer.index,55);self.assertEqual(set(server.writer.hashes),set(writer.SCHEDULE))
                    receipts=[x['receipt'] for x in server.records if x['action']=='EMIT']
                    self.assertEqual(len(receipts),55);self.assertTrue(all(x['durable_observed'] for x in receipts))
                    self.assertEqual([(x['verb'],x['target']) for x in server.protocol.trace],wire.schedule())
                    manifest_value=json.loads((package/'manifest.json').read_bytes());self.assertEqual(len(manifest_value['files']),54)
                    self.assertEqual(manifest_value['source_manifest_binding'],selection['logical_source_binding'])
                    for row in manifest_value['files']:
                        leaf=row['path'].removeprefix(writer.plan.PACKAGE+'/');self.assertEqual(row['sha256'],fixture.sha((package/leaf).read_bytes()))
                    self.assertEqual(len(json.loads((package/'mapping.json').read_bytes())['rows']),25)
                    for row in rows:self.assertEqual(fixture.binding(Path(row['path'])),row)
                    self.assertTrue(all(x['selection_sha256']==selected['sha256'] for x in [wire.decode(server._response(wire.encode(wire.envelope(selection['attempt_id'],selected['sha256'],0,'BEGIN',pins)),{'kind':'ACK'}))]))
                else:
                    self.assertIsNotNone(failure);self.assertNotEqual(process.returncode,0)
                    self.assertTrue(server.failed);self.assertFalse(server.finished)
                    if server.writer is not None:
                        self.assertTrue(server.writer.unknown)
                        expected_count=1 if scenario in ('extra-leaf','lost-ack') else 0
                        self.assertEqual(server.writer.index,expected_count)
                        self.assertTrue((root/writer.ATTEMPT).is_file())
                    self.assertFalse((root/'output/forbidden-direct-write').exists())
                    if scenario=='ancestor-detach':self.assertEqual(list(mapped.iterdir()),[])
                    if scenario=='package-detach':self.assertEqual(list(package.parent.iterdir()),[])
                    if scenario=='lost-ack':
                        leaf=package/'semantic/00000001.json';self.assertEqual(fixture.sha(leaf.read_bytes()),server.writer.hashes['semantic/00000001.json'])
                        with self.assertRaises(writer.Refusal):server.writer.emit('semantic/00000002.json',b'{}')
                        with self.assertRaises(Exception):writer.PackageWriter(mapped,selection['logical_source_binding'])
            finally:
                if process is not None and process.poll() is None:process.kill();out,err=process.communicate()
                if server is not None:server.close()
                parent.close();child.close()
                evidence=Path(os.environ['MAPPER_FIXTURE_EVIDENCE'])/scenario;evidence.mkdir()
                for path in (manifest,root/'output/preimage.py',root/'output/build.py'):
                    if path.exists():fixture.write(evidence/path.name,path.read_bytes())
                fixture.write(evidence/'child.stdout',out);fixture.write(evidence/'child.stderr',err)
                fixture.write(evidence/'observation.json',fixture.encoded({'scenario':scenario,'manifest_binding':selected,'argv':command if need_child else [],'os_exit':process.returncode if process else None,'elapsed_seconds':time.monotonic()-started,'peer':server.peer if server else None,'failure_class':failure,'events':events,'acknowledged':server.records if server else [],'writer_index':server.writer.index if server and server.writer else None,'writer_unknown':server.writer.unknown if server and server.writer else None,'fixture_only':True,'native_processes':0,'protected_reads':0,'os_confinement':False}))
                if package.exists():shutil.copytree(package,evidence/'synthetic-package')

    def test_full_builder_real_digest_durable_55_leaf_writer(self):self.run_case('positive')
    def test_wrong_manifest_digest_before_writer_claim(self):self.run_case('wrong-manifest-digest')
    def test_wrong_wire_selection_digest_before_begin(self):self.run_case('wrong-wire-digest')
    def test_lost_ack_retains_durable_leaf_and_fences_reuse(self):self.run_case('lost-ack')
    def test_extra_leaf_fences_next_emission(self):self.run_case('extra-leaf')
    def test_selected_source_drift_fences_before_emission(self):self.run_case('source-drift')
    def test_child_crash_retains_attempt_and_unknown(self):self.run_case('child-crash')
    def test_ancestor_detach_never_writes_replacement(self):self.run_case('ancestor-detach')
    def test_package_detach_never_writes_replacement(self):self.run_case('package-detach')
    def test_selected_fixture_direct_write_is_detected(self):self.run_case('direct-write')
