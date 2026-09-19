import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from check import assess
from support import ROOT, LAB, PACKAGE, load, dump, binding
class Residue(unittest.TestCase):
    def setUp(self): self.record=load(PACKAGE/'fixtures/valid/residue-record.json')
    def reject(self,message):
        with self.assertRaisesRegex(ValueError,message): assess(self.record)
    def pair(self,source,result):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT); self.addCleanup(self.temp.cleanup)
        for name,value in [('source',source),('result',result)]:
            path=Path(self.temp.name)/(name+'.json'); dump(path,value); self.record[name]=binding(path)
    def test_remainder(self):
        result=assess(self.record); self.assertEqual(result['preserved_fields'],['id']); self.assertEqual(len(result['observed_remainder']),2)
        for key in ['treatment_executed','closure_accepted','semantic_preservation_proven','promotion_authorized']: self.assertFalse(result[key])
    def test_omitted_remainder(self):
        self.record['observed_remainder'].pop(); self.reject('differs from bound evidence')
    def test_invented_remainder(self):
        self.record['observed_remainder'].append({'field':'id','issue':'changed'}); self.reject('differs from bound evidence')
    def test_wrong_issue(self):
        self.record['observed_remainder'][0]['issue']='changed'; self.reject('differs from bound evidence')
    def test_duplicate_remainder(self):
        self.record['observed_remainder'].append(copy.deepcopy(self.record['observed_remainder'][0])); self.reject('Duplicate remainder')
    def test_source_drift(self):
        self.record['source']['sha256']='0'*64; self.reject('Bound bytes changed')
    def test_result_drift(self):
        self.record['result']['sha256']='0'*64; self.reject('Bound bytes changed')
    def test_absent_source_field(self):
        self.record['preservation_condition']['required_fields'].append('unknown'); self.reject('absent from source')
    def test_no_loss(self):
        self.record['result']=self.record['source']; self.reject('No residue')
    def test_changed_value(self):
        source=load(LAB/self.record['source']['path']); target=copy.deepcopy(source); target['owner']='other'; self.pair(source,target)
        self.record['observed_remainder']=[{'field':'owner','issue':'changed'}]; self.assertTrue(assess(self.record)['remainder_verified'])
    def test_boolean_not_integer(self):
        self.pair({'value':True},{'value':1}); self.record['preservation_condition']['required_fields']=['value']; self.record['observed_remainder']=[{'field':'value','issue':'changed'}]; self.assertTrue(assess(self.record)['remainder_verified'])
    def test_object_order_irrelevant(self):
        self.pair({'value':{'a':1,'b':2}},{'value':{'b':2,'a':1}}); self.record['preservation_condition']['required_fields']=['value']; self.reject('No residue')
    def test_all_treatments_stay_open(self):
        for treatment in ['repair','type','gate','climb','accept','defer']:
            self.record['treatment']=treatment; result=assess(self.record); self.assertFalse(result['closure_accepted']); self.assertFalse(result['treatment_executed'])
    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'record.json'
            for expected in [0,2]:
                if expected==2: self.record['observed_remainder'].pop()
                dump(path,self.record); result=subprocess.run([sys.executable,str(ROOT/'check.py'),str(path)],capture_output=True,text=True)
                self.assertEqual(result.returncode,expected,result.stdout+result.stderr); json.loads(result.stdout)
if __name__=='__main__': unittest.main()
