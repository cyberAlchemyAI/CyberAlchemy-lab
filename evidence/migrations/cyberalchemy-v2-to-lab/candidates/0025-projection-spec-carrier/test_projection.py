import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from check import assess
from generate import project
from support import ROOT, LAB, PACKAGE, load, dump, sha
class Projection(unittest.TestCase):
    def setUp(self):
        self.path=PACKAGE/'fixtures/valid/projection-spec-record.json'; self.spec=load(self.path); self.view=ROOT/'examples/view.json'
    def modified(self,edit,message):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d)/'spec.json'; edit(self.spec); dump(path,self.spec)
            with self.assertRaisesRegex(ValueError,message): project(path)
    def test_view(self):
        result=assess(self.path,self.view); self.assertEqual(result['selected_fields'],3); self.assertTrue(result['view_matches']); self.assertFalse(result['view_activated']); self.assertFalse(result['semantic_fidelity_proven'])
    def test_source_drift(self): self.modified(lambda x:x['source'].update(sha256='0'*64),'Source bytes changed')
    def test_missing_omission(self): self.modified(lambda x:x['omissions'].pop(),'partition')
    def test_extra_source_field(self): self.modified(lambda x:x['fields'].append({'source_field':'unknown','view_field':'unknown'}),'partition')
    def test_duplicate_output(self): self.modified(lambda x:x['fields'][1].update(view_field=x['fields'][0]['view_field']),'Duplicate field')
    def test_duplicate_source(self): self.modified(lambda x:x['fields'][1].update(source_field=x['fields'][0]['source_field']),'Duplicate field')
    def test_duplicate_omission(self): self.modified(lambda x:x['omissions'].append(copy.deepcopy(x['omissions'][0])),'Duplicate omission')
    def test_selected_also_omitted(self): self.modified(lambda x:x['omissions'].append({'source_field':x['fields'][0]['source_field'],'reason':'conflict'}),'partition')
    def test_rename(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            spec=Path(d)/'spec.json'; view=Path(d)/'view.json'; self.spec['fields'][0]['view_field']='receipt'; dump(spec,self.spec); dump(view,project(spec)); self.assertTrue(assess(spec,view)['view_matches'])
    def test_forged_view(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'view.json'; data=load(self.view); data['data']['exit_code']=99; dump(path,data)
            with self.assertRaisesRegex(ValueError,'differs'): assess(self.path,path)
    def test_authority_injection(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'view.json'; data=load(self.view); data['authority_effect']='admit'; dump(path,data)
            with self.assertRaisesRegex(ValueError,'differs'): assess(self.path,path)
    def test_source_unchanged(self):
        path=LAB/self.spec['source']['path']; before=sha(path); project(self.path); assess(self.path,self.view); self.assertEqual(sha(path),before)
    def test_view_source_alias(self):
        with self.assertRaisesRegex(ValueError,'separate'): assess(self.path,LAB/self.spec['source']['path'])
    def test_cli(self):
        for view,expected in [(self.view,0),(self.path,2)]:
            result=subprocess.run([sys.executable,str(ROOT/'check.py'),str(self.path),str(view)],capture_output=True,text=True)
            self.assertEqual(result.returncode,expected,result.stdout+result.stderr); json.loads(result.stdout)
if __name__=='__main__': unittest.main()
