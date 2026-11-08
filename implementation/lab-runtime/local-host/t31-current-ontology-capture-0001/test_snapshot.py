"""Actual selected mapping bytes with synthetic host/native transport mechanics.

Constructor authentication and genuine public projection are not inferred from
this harness. It tests the unchanged capture body against causal file changes.
"""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import ModuleType,SimpleNamespace
import unittest
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE));from snapshot import OntologySnapshot
def enc(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def binding(ref,raw):return {'ref':ref,'sha256':sha(raw)}
class SyntheticHost:pass
SyntheticHost.__module__='_ontology_snapshot_component.service'

class Snapshot(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='cal-ontology-snapshot-test-');self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name)/'generation';root.mkdir(mode=0o700)
        mapped=ROOT/'implementation/lab-runtime/local-host/t15-integrated-fixture-0001/instances/legacy-local-4636eca980a5d94d/mapped'
        package=mapped/'packages/0001';files=[]
        for family in ('semantic','governance'):
            (root/family).mkdir(mode=0o700)
            for source in sorted((package/family).glob('*.json')):
                path=root/family/source.name;path.write_bytes(source.read_bytes());path.chmod(0o600);files.append({'path':family+'/'+source.name,'sha256':sha(path.read_bytes())})
        request=root/'request.json';request.write_bytes((package/'request.json').read_bytes());request.chmod(0o600);files.append({'path':'request.json','sha256':sha(request.read_bytes())})
        mapping=(package/'mapping.json').read_bytes();policy=(mapped/'policy.json').read_bytes();native=(package/'native-output.json').read_bytes();cut=json.loads(mapping)['source_cut']
        map_binding=binding(str((mapped/'policy.json').relative_to(ROOT)),policy)
        manifest={'schema_version':'SYNTHETIC-COMPONENT-NOT-ACTUAL-PROJECTION','lab_source_cut':cut,'mapping_binding':map_binding,'native_read_sha256':sha(native),'files':files}
        mraw=enc(manifest);(root/'manifest.json').write_bytes(mraw);(root/'manifest.json').chmod(0o600)
        head={'store_ref':'owned-ontology:synthetic-snapshot','generation_sha256':sha(mraw)};hraw=enc(head)
        reply={'schema_version':'lab-ontology-projection-receipt/v1-candidate','posture':'applied','lab_source_cut':cut,'mapping_binding':map_binding,
          'ontology_applied_cut':{'store_ref':head['store_ref'],'commit_sha256':sha(hraw)}}
        raws={'head':hraw,'manifest':mraw,'native':native,'reply':enc(reply)}
        c={'schema_version':'lab-private-original-ontology-archive/v1','generation_root':str(root),'head_binding':binding('head',hraw),'manifest_binding':binding('manifest',mraw),
          'native_read_binding':binding('native',native),'projection_receipt_binding':binding('reply',raws['reply']),'mapping_binding':map_binding,
          'mapping_original_binding':binding(str((package/'mapping.json').relative_to(ROOT)),mapping),'work_ref':'work:synthetic@1','source_cut':cut,'store_ref':head['store_ref'],'authority_effect':'none'}
        self.calls=[]
        def call(args):self.calls.append(args);return native
        host=SyntheticHost();host.vault=SimpleNamespace(material=lambda b:raws[b['ref']]);host.channel=SimpleNamespace(guard=lambda:{'principal_ref':'principal:synthetic'},policy={'expires_at':'2099-01-01T00:00:00+00:00'})
        self.cap=object.__new__(OntologySnapshot);self.cap.host=host;self.cap.control=c;self.cap.mapper=SimpleNamespace(HERE=mapped,call=call)
        self.cap.P=SimpleNamespace(ROOT=ROOT,frame_parse=json.loads,compact=enc,binding=binding,source=SimpleNamespace(sha=sha));self.cap.work_ref=c['work_ref'];self.cap.guard=lambda:None
        module=ModuleType('_ontology_snapshot_component.workspace');module.read_private=lambda p:p.read_bytes();sys.modules[module.__name__]=module
        self.addCleanup(sys.modules.pop,module.__name__,None);self.root=root;self.raws=raws
    def test_exact_complete_generation_replay_correspondence(self):
        result=self.cap.capture();self.assertEqual(len(result['native_files']),60);self.assertEqual(len(self.calls),1)
        self.assertEqual(json.loads(result['cold_replay_original'])['native_read_binding'],self.cap.control['native_read_binding'])
    def test_changed_generation_semantic_original_refused_before_native_call(self):
        target=next((self.root/'semantic').iterdir());target.write_bytes(target.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'member changed'):self.cap.capture()
        self.assertEqual(self.calls,[])
    def test_extra_generation_file_and_replaced_manifest_refused(self):
        extra=self.root/'unexpected.json';extra.write_bytes(b'{}')
        with self.assertRaisesRegex(ValueError,'closure differs'):self.cap.capture()
        extra.unlink();(self.root/'manifest.json').write_bytes(b'{}')
        with self.assertRaisesRegex(ValueError,'closure differs'):self.cap.capture()
        self.assertEqual(self.calls,[])
    def test_actual_native_output_mismatch_refused(self):
        self.cap.mapper.call=lambda args:b'{}'
        with self.assertRaisesRegex(ValueError,'native replay'):self.cap.capture()
    def test_other_applied_receipt_head_refused_before_native_call(self):
        body=json.loads(self.raws['reply']);body['ontology_applied_cut']['commit_sha256']='0'*64;self.raws['reply']=enc(body)
        with self.assertRaisesRegex(ValueError,'correspondence differs'):self.cap.capture()
        self.assertEqual(self.calls,[])
if __name__=='__main__':unittest.main()
