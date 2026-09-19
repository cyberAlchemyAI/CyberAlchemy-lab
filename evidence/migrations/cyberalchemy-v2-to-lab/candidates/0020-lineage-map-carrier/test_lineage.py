import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from check import assess
from support import ROOT, PACKAGE, load, dump
class Lineage(unittest.TestCase):
    def setUp(self): self.record=load(PACKAGE/'fixtures/valid/lineage-map-record.json')
    def reject(self,message):
        with self.assertRaisesRegex(ValueError,message): assess(self.record)
    def test_map(self):
        result=assess(self.record); self.assertEqual([len(x['successors']) for x in result['mappings']],[2,5]); self.assertTrue(all(x['selection_required'] for x in result['mappings']))
        for key in ['authority_transferred','identity_equivalence_proven','current_admission_resolved']: self.assertFalse(result[key])
    def test_missing_successor(self):
        self.record['mappings'][1]['successors'].pop(); self.reject('Successor set differs')
    def test_extra_successor(self):
        self.record['mappings'][0]['successors'].append(copy.deepcopy(self.record['mappings'][1]['successors'][0])); self.reject('Successor set differs')
    def test_duplicate_successor(self):
        self.record['mappings'][0]['successors']*=2; self.reject('Duplicate successor')
    def test_disposition(self):
        self.record['mappings'][0]['disposition']='split'; self.reject('Disposition differs')
    def test_missing_mapping(self):
        self.record['mappings'].pop(); self.reject('Coverage mismatch')
    def test_duplicate_mapping(self):
        self.record['mappings'].append(copy.deepcopy(self.record['mappings'][0])); self.reject('Duplicate legacy')
    def test_unknown_legacy(self):
        self.record['coverage'][0]='CAV2-UNKNOWN'; self.record['mappings'][0]['legacy_id']='CAV2-UNKNOWN'; self.reject('Unknown legacy')
    def test_target_digest(self):
        self.record['mappings'][0]['successors'][0]['binding']['sha256']='0'*64; self.reject('Bound bytes changed')
    def test_index_digest(self):
        self.record['target_index']['sha256']='0'*64; self.reject('Bound bytes changed')
    def test_normalization_digest(self):
        self.record['normalization']['sha256']='0'*64; self.reject('Bound bytes changed')
    def test_wrong_target_binding(self):
        self.record['mappings'][0]['successors'][0]['binding']=self.record['mappings'][0]['successors'][1]['binding']; self.reject('differs from indexed')
    def test_subset_explicit(self):
        self.record['coverage']=['CAV2-D9']; self.record['mappings']=self.record['mappings'][:1]; self.assertEqual(len(assess(self.record)['mappings']),1)
    def test_cli_lookup(self):
        path=PACKAGE/'fixtures/valid/lineage-map-record.json'
        for legacy,expected in [('CAV2-D34',0),('CAV2-UNKNOWN',2)]:
            result=subprocess.run([sys.executable,str(ROOT/'check.py'),str(path),legacy],capture_output=True,text=True)
            self.assertEqual(result.returncode,expected,result.stdout+result.stderr); data=json.loads(result.stdout)
            if expected==0: self.assertEqual(len(data['mappings'][0]['successors']),5)
if __name__=='__main__': unittest.main()
