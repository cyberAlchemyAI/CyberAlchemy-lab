"""Batch decoder component cases; signed native replays are separate evidence."""
import copy,importlib,importlib.util,json,tempfile,types,unittest
from pathlib import Path
import cold_original_batch_0001 as B
H=Path(__file__).resolve().parent;R=H.parents[3]
folder=R/'implementation/lab-runtime/local-host/t15-integrated-fixture-0001/engine-v3/runtime/lab_runtime';name='_batch_actual_custody_component';spec=importlib.util.spec_from_file_location(name,folder/'__init__.py',submodule_search_locations=[str(folder)]);module=importlib.util.module_from_spec(spec)
import sys
sys.modules[name]=module;spec.loader.exec_module(module);C=importlib.import_module(name+'.custody');COMMON=importlib.import_module(name+'.common')
class Batch(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='cal-cold-batch-component-');self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.store=self.root/'store';self.store.mkdir();(self.store/'transactions').mkdir();self.originals={'HEAD.json':b'original head','transactions/0000000001.json':b'original signed transaction'}
  for path,raw in self.originals.items():(self.store/path).write_bytes(raw)
  targets=[];self.raw={};self.index=[];subjects={}
  for number in range(26):
   identity='fixture:'+str(number);version=identity+'@1';record={'node_id':identity,'kind':'fixture','payload':{'value':number}};raw=(' \r\n'+json.dumps(record,indent=3)+'\r\n').encode();digest=COMMON.byte_digest(raw);path='body-'+str(number);self.raw[path]=raw
   self.index.append({'version_ref':version,'encoding':C.ENCODING,'original_binding':{'path':path,'sha256':digest}});targets.append({'operation':'admit','version_ref':version,'record':record,'content':C.content_entry(raw)})
   subjects[version]={'record':record,'source':{'sha256':digest,'encoding':C.ENCODING,'path':'transactions/0000000001.json'}}
  tx={'sequence':1,'proposal':{'schema_version':C.EXACT_SCHEMA_PROPOSAL_VERSION,'targets':targets,'schemas':{}}};data={'head':{'transaction_digest':'verified-cut'},'projection':{'subjects':subjects},'transactions':[{'sequence':0},tx]}
  expected={'expected_head':'verified-cut','projection_sha256':COMMON.digest(data['projection']),'transaction_sha256s':[COMMON.digest(t)for t in data['transactions']]}
  self.view=types.SimpleNamespace(store=self.store,originals=self.originals,data=data,expected=expected,handle=types.SimpleNamespace(custody=C,common=COMMON))
  self.base=types.SimpleNamespace(load=lambda path:self.index,original=lambda row:self.raw[row['path']],sha=COMMON.byte_digest,parse=json.loads)
 def test_all26_exact_noncanonical_originals_use_actual_decoder(self):self.assertEqual(B.verify(self.view,self.base,self.root)['original_records'],26)
 def test_changed_index_binding_refuses(self):
  self.index[0]['original_binding']['sha256']='0'*64
  with self.assertRaises(ValueError):B.verify(self.view,self.base,self.root)
 def test_changed_original_body_refuses(self):
  self.raw['body-0']=b'{"different":"body"}'
  with self.assertRaises(ValueError):B.verify(self.view,self.base,self.root)
 def test_changed_semantic_record_refuses(self):
  self.view.data['projection']['subjects']['fixture:0@1']['record']={'different':'semantic record'}
  with self.assertRaises(ValueError):B.verify(self.view,self.base,self.root)
 def test_changed_archive_during_batch_refuses(self):
  def changed(data):
   rows=C.content_rows(data);(self.store/'HEAD.json').write_bytes(b'changed');return rows
  self.view.handle.custody=types.SimpleNamespace(content_rows=changed)
  with self.assertRaisesRegex(ValueError,'archive changed'):B.verify(self.view,self.base,self.root)
 def test_changed_cut_or_missing_revision_refuses(self):
  self.view.expected['expected_head']='different'
  with self.assertRaisesRegex(ValueError,'replay cut changed'):B.verify(self.view,self.base,self.root)
if __name__=='__main__':unittest.main()
