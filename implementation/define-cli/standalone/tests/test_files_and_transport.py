import base64
from concurrent.futures import ThreadPoolExecutor
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from unittest import mock

import define_core
from define_core.contracts import check
from define_core.exact import Refusal, binding, decode, encode, read, sha, write_package
from define_core.integrity import verify
from support import Case, add_source, b64, base, materialization, no_sources, raw_members

BIN=Path(sys.executable).parent
PACKAGE=Path(define_core.__file__).parent


def command(args, *, stdin=None, cwd=None):
    return subprocess.run([str(BIN/'define-standalone'), *map(str,args)], input=stdin, capture_output=True, cwd=cwd, timeout=60)


def transport(raw, *, cwd=None):
    return subprocess.run([str(BIN/'define-api')],input=raw,capture_output=True,cwd=cwd,timeout=60)


class Transport(Case):
    def test_python_and_json_api_parity(self):
        for op,params in [('capabilities',{}),('schema',{'kind':'request'})]:
            doc={'api_version':'define.api/v1','id':'parity','operation':op,'params':params}
            process=transport(encode(doc));self.assertEqual(process.returncode,0,process.stderr)
            self.assertEqual(decode(process.stdout),define_core.call(doc))

    def test_prepare_and_reconstruct_match_python_through_stdio(self):
        r,i=base();captured=self.captured(r,i)
        params={'request_utf8':encode(r).decode(),'capture_utf8':captured['capture_utf8'],'inputs':captured['inputs']}
        doc={'api_version':'define.api/v1','id':'parity-prepare','operation':'prepare','params':params}
        p=transport(encode(doc));self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        direct=define_core.call(doc);self.assertEqual(decode(p.stdout),direct)
        restored=transport(encode({'api_version':'define.api/v1','id':'restore','operation':'reconstruct',
             'params':{'package_members':direct['data']['package_members']}}))
        self.assertEqual(restored.returncode,0)
        self.assertEqual(decode(restored.stdout)['data']['package_members'],direct['data']['package_members'])

    def test_byte_api_and_resources_do_not_use_linux_file_helpers(self):
        with mock.patch('define_core.exact.read',side_effect=AssertionError('POSIX file helper reached from byte API')):
            descriptor=self.ok(self.invoke('schema',{'kind':'definition-carrier'}))
            self.assertIn('schema_binding',descriptor)
            r,i=materialization();d=self.package(r,i)
            materialized=self.ok(self.invoke('materialize',{'package_members':d['package_members']}))
            self.assertEqual(len(materialized['report']['definitions']),1)

    def test_distribution_version_matches_runtime(self):
        from importlib.metadata import version
        self.assertEqual(version('cyberalchemy-define'),define_core.VERSION)
        self.assertEqual(decode(command(['doctor']).stdout)['version'],define_core.VERSION)

    def test_bad_transport_has_single_structured_response(self):
        for raw in (b'',b'{} {}',b'\xff',b'{"x":1,"x":2}',b'[]',b'{"x":NaN}'):
            with self.subTest(raw=raw):
                p=transport(raw);self.assertEqual(p.returncode,2)
                check(decode(p.stdout),'api-result');self.assertFalse(p.stderr)

    def test_unsupported_has_documented_exit_status(self):
        p=transport(encode({'api_version':'define.api/v999','id':'t','operation':'capabilities','params':{}}))
        self.assertEqual(p.returncode,4);self.assertEqual(decode(p.stdout)['outcome'],'unsupported')

    def test_oversize_frame_is_refused(self):
        p=transport(b' '*(32*1024*1024+1));self.assertEqual(p.returncode,2)
        self.assertEqual(decode(p.stdout)['outcome'],'invalid-input')

    def test_interrupted_stdin_has_documented_response(self):
        p=subprocess.Popen([str(BIN/'define-api')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            time.sleep(0.35);p.send_signal(signal.SIGINT)
            stdout,stderr=p.communicate(timeout=10)
            self.assertEqual(p.returncode,130,(stdout,stderr));self.assertEqual(decode(stdout)['outcome'],'interrupted')
        finally:
            if p.poll() is None:p.kill();p.communicate()

    def test_import_uses_installed_distribution(self):
        self.assertIn('site-packages',str(PACKAGE))
        self.assertTrue(PACKAGE.is_relative_to(Path(sys.prefix)))
        p=subprocess.run([sys.executable,'-I','-c','import define_core; print(define_core.__file__)'],capture_output=True,cwd='/tmp',timeout=20)
        self.assertEqual(p.returncode,0);self.assertIn(b'site-packages',p.stdout)

    def test_core_workflow_with_repository_access_denied(self):
        # Audit rejects reads below the Lab checkout without renaming real user files.
        code='''import sys,os,json,base64
blocked=os.environ.get("DEFINE_DENY_REPO",os.path.abspath("unavailable-lab-repository"))
def audit(event,args):
 if event in ("open","os.listdir","os.scandir") and args and isinstance(args[0],(str,bytes)):
  path=os.fsdecode(args[0])
  if os.path.abspath(path)==blocked or os.path.abspath(path).startswith(blocked+"/"):
   raise RuntimeError("repository-access-denied")
sys.addaudithook(audit)
from define_core import call
from define_core.example import example_members
members=example_members();request=members.pop("request.json").decode()
def invoke(op,params):
 r=call({"api_version":"define.api/v1","id":"isolated","operation":op,"params":params})
 assert r["outcome"] in ("prepared","prepared-with-gaps"),r
 return r["data"]
c=invoke("capture",{"request_utf8":request,"inputs":{k:base64.b64encode(v).decode() for k,v in members.items()},"permit_retention":True})
p=invoke("prepare",{"request_utf8":request,"capture_utf8":c["capture_utf8"],"inputs":c["inputs"]})
r=invoke("reconstruct",{"package_members":p["package_members"]})
assert r["package_members"]==p["package_members"]
print(json.dumps({"outcome":"passed","repository_access":"denied","pack_sha256":p["pack_sha256"]}))
'''
        p=subprocess.run([sys.executable,'-I','-c',code],capture_output=True,cwd='/tmp',timeout=30)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        self.assertEqual(decode(p.stdout)['repository_access'],'denied')


class LocalWorkflow(Case):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='define-installed-test-');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def save_package(self,data,name='package'):
        path=self.root/name;write_package(path,raw_members(data['package_members']));return path

    def test_cli_complete_workflow_and_new_destination_rule(self):
        example=self.root/'input'
        self.assertEqual(command(['example','--output',example],cwd=self.root).returncode,0)
        capture=self.root/'capture';package=self.root/'package';restored=self.root/'restored'
        for args in (['capture-local','--request',example/'request.json','--source-root',example,'--permit-retention','--output',capture],
                     ['prepare','--request',example/'request.json','--capture',capture,'--output',package],
                     ['inspect',package],['reconstruct',package,'--output',restored]):
            p=command(args,cwd=self.root);self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        original={str(p.relative_to(package)):p.read_bytes() for p in package.rglob('*') if p.is_file()}
        self.assertEqual(original,{str(p.relative_to(restored)):p.read_bytes() for p in restored.rglob('*') if p.is_file()})
        p=command(['reconstruct',package,'--output',restored]);self.assertEqual(p.returncode,3)
        self.assertEqual(original,{str(p.relative_to(restored)):p.read_bytes() for p in restored.rglob('*') if p.is_file()})

    def test_cli_materialization_and_observation(self):
        r,i=materialization();data=self.package(r,i);directory=self.save_package(data)
        p=command(['materialize',directory,'--output',self.root/'definitions']);self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        self.assertTrue((self.root/'definitions/definitions/000/DEFINITION.md').exists())
        p=command(['observe-use',directory,'--requested-use','inspect-preparation','--consumer','reader','--output',self.root/'observation'])
        self.assertEqual(p.returncode,0);self.assertEqual(decode(p.stdout)['outcome'],'not-evaluable')

    def test_empty_source_cli_and_api_produce_identical_package(self):
        r,i=no_sources();captured=self.captured(r,i)
        request=self.root/'request.json';request.write_bytes(encode(r))
        capture=self.root/'capture';write_package(capture,{'capture.json':captured['capture_utf8'].encode(),
             **{'inputs/'+k:v for k,v in raw_members(captured['inputs']).items()}})
        output=self.root/'package'
        p=command(['prepare','--request',request,'--capture',capture,'--output',output]);self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        expected=self.ok(self.prepared(r,i,captured))
        self.assertEqual((output/'manifest.json').read_bytes(),raw_members(expected['package_members'])['manifest.json'])

    def test_existing_and_missing_output_parent(self):
        existing=self.root/'existing';existing.mkdir();(existing/'sentinel').write_bytes(b'keep')
        for target in (existing,self.root/'missing/output'):
            with self.assertRaises(Refusal):write_package(target,{'a.json':b'{}'})
        self.assertEqual((existing/'sentinel').read_bytes(),b'keep')

    def test_symlink_inputs_and_parents_refuse(self):
        foreign=self.root/'foreign';foreign.mkdir();(foreign/'source.json').write_bytes(b'keep')
        link=self.root/'link';link.symlink_to(foreign,target_is_directory=True)
        with self.assertRaises(Refusal):read(link/'source.json')
        with self.assertRaises(Refusal):write_package(link/'output',{'x':b'change'})
        self.assertEqual((foreign/'source.json').read_bytes(),b'keep');self.assertFalse((foreign/'output').exists())

    def test_prefix_collision_is_refused_before_staging(self):
        with self.assertRaises(Refusal):write_package(self.root/'output',{'a':b'x','a/b':b'y'})
        self.assertFalse((self.root/'output').exists());self.assertFalse(list(self.root.glob('.define-*')))

    def test_two_publishers_do_not_replace_each_other(self):
        destination=self.root/'published'
        def attempt(marker):
            try:write_package(destination,{'marker':marker});return True
            except Refusal:return False
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(attempt,[b'a',b'b']))
        self.assertEqual(sum(results),1);self.assertIn((destination/'marker').read_bytes(),(b'a',b'b'))
        self.assertFalse(list(self.root.glob('.define-*')))

    def test_interruption_before_publication_cleans_staging(self):
        with mock.patch('define_core.exact.publish_directory',side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):write_package(self.root/'output',{'a':b'value'})
        self.assertFalse((self.root/'output').exists());self.assertFalse(list(self.root.glob('.define-*')))

    def test_post_commit_sync_failure_reports_unknown_and_preserves_output(self):
        from define_core import exact
        original=exact.fsync_dir
        def fail_parent(path):
            if Path(path)==self.root:raise OSError('synthetic post-commit fsync failure')
            return original(path)
        with mock.patch('define_core.exact.fsync_dir',side_effect=fail_parent):
            with self.assertRaises(Refusal) as caught:write_package(self.root/'output',{'a':b'value'})
        self.assertEqual(caught.exception.code,'publication-outcome-unknown')
        self.assertEqual((self.root/'output/a').read_bytes(),b'value')
        with self.assertRaises(Refusal):write_package(self.root/'output',{'a':b'overwrite'})
        self.assertEqual((self.root/'output/a').read_bytes(),b'value')

    def test_cli_blocked_observation_is_still_saved(self):
        directory=self.save_package(self.package());destination=self.root/'changed-use'
        p=command(['observe-use',directory,'--requested-use','governing-application','--consumer','reader','--output',destination])
        self.assertEqual(p.returncode,3);self.assertTrue((destination/'observation.json').is_file())
        self.assertEqual(decode((destination/'observation.json').read_bytes())['outcome'],'blocked')


class InstalledIntegrity(Case):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='define-installed-drift-');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);shutil.copytree(PACKAGE,self.root/'define_core')

    def child(self,code):
        return subprocess.run([sys.executable,'-I','-c','import sys; sys.path.insert(0,'+repr(str(self.root))+'); '+code],capture_output=True,cwd=self.root,timeout=30)

    def test_changed_source_blocks_python_and_stdio_with_exit_3(self):
        source=self.root/'define_core/prepare.py';source.write_bytes(source.read_bytes()+b'\n# unsealed\n')
        p=self.child('from define_core import call; import json; print(json.dumps(call({"api_version":"define.api/v1","id":"t","operation":"capabilities","params":{}})))')
        self.assertEqual(p.returncode,0);self.assertEqual(decode(p.stdout)['outcome'],'blocked')
        p=self.child('from define_core import api_main; raise SystemExit(api_main())')
        self.assertEqual(p.returncode,3,p.stdout+p.stderr)

    def test_schema_drift_is_blocked(self):
        path=self.root/'define_core/resources/schema.json';path.write_bytes(b'{}')
        p=self.child('from define_core import call; import json; print(json.dumps(call({"api_version":"define.api/v1","id":"t","operation":"capabilities","params":{}})))')
        self.assertEqual(decode(p.stdout)['outcome'],'blocked')

    def test_unselected_source_never_executes(self):
        (self.root/'define_core/rogue.py').write_text('raise RuntimeError("ROGUE_SOURCE_EXECUTED")')
        p=self.child('from define_core import call; import json; print(json.dumps(call({"api_version":"define.api/v1","id":"t","operation":"capabilities","params":{}})))')
        self.assertNotIn(b'ROGUE_SOURCE_EXECUTED',p.stdout+p.stderr);self.assertEqual(decode(p.stdout)['outcome'],'blocked')

    def test_unselected_bytecode_is_ignored_after_bootstrap(self):
        from importlib.util import cache_from_source
        from importlib._bootstrap_external import _code_to_timestamp_pyc
        source=self.root/'define_core/exact.py';stat=source.stat()
        cache=Path(cache_from_source(str(source)));cache.parent.mkdir(exist_ok=True)
        cache.write_bytes(_code_to_timestamp_pyc(compile('raise RuntimeError("ROGUE_BYTECODE_EXECUTED")',str(source),'exec'),int(stat.st_mtime),stat.st_size))
        p=self.child('from define_core import call; import json; print(json.dumps(call({"api_version":"define.api/v1","id":"t","operation":"capabilities","params":{}})))')
        self.assertEqual(p.returncode,0,p.stdout+p.stderr);self.assertNotIn(b'ROGUE_BYTECODE_EXECUTED',p.stdout+p.stderr)
        self.assertEqual(decode(p.stdout)['outcome'],'prepared')

    def test_source_manifest_has_all_bundled_resources(self):
        manifest=decode((PACKAGE/'runtime-manifest.json').read_bytes());names={r['path'] for r in manifest['files']}
        self.assertIn('resources/schema.json',names);self.assertIn('resources/generator.py',names)
        self.assertIn('schemas/api-request.schema.json',names);self.assertGreater(verify()['checked_files'],20)
