"""Execute unchanged constructor selection and exact successor guard predicates."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import tempfile
from types import SimpleNamespace
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v75-current-fixtures-0001'
POST=HERE/'api75-flat-constructor-inputs-postimages-0002/guard.py'
PINNED=json.loads((HERE/'api75-flat-constructor-inputs-postimages-0002/PINS.json').read_bytes())['required_flat_rows']

def need(ok,reason):
    if not ok:raise ValueError(reason)

def segment(function,start,end):
    nodes=ast.parse(function.read_text()).body
    node=next(n for n in nodes if isinstance(n,ast.FunctionDef) and n.name=='verify')
    first=next(i for i,n in enumerate(node.body) if start(n))
    last=next(i for i,n in enumerate(node.body[first:],first) if end(n))
    return node.body[first:last+1]

class FlatConstructorSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        selected=segment(POST,lambda n:isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='package' for t in n.targets),
                         lambda n:isinstance(n,ast.If) and ast.unparse(n.test)=='actual_helpers != helper_paths')
        cls.guard_code=compile(ast.Module(body=selected,type_ignores=[]),str(POST),'exec')
        declaration=selected[:next(i for i,n in enumerate(selected) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='actual_helpers' for t in n.targets))]
        declared={'HERE':API,'ROOT':ROOT};exec(compile(ast.Module(body=declaration,type_ignores=[]),str(POST),'exec'),declared)
        cls.rows=[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in sorted(declared['helper_paths'])]
        fn=next(n for n in ast.parse(POST.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='_verify_files')
        space={'Path':Path,'PurePosixPath':PurePosixPath,'os':os,'stat':stat,'hashlib':hashlib}
        exec(compile(ast.Module(body=[fn],type_ignores=[]),str(POST),'exec'),space)
        cls.physical=staticmethod(space['_verify_files'])
    def guard(self,rows):exec(self.guard_code,{'HERE':API,'ROOT':ROOT,'rows':rows,'re':re})
    def constructors(self,rows):
        for helper in ('classification-preparation-v9','failure-preparation-v5'):
            path=API.parent/helper/'preparation.py'
            tree=ast.parse(path.read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name.endswith('Preparation'))
            init=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
            first=next(i for i,n in enumerate(init.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='selected_inputs' for t in n.targets))
            selected=init.body[first:first+3]
            self.assertIsInstance(selected[1],ast.For)
            self.assertIn("host_manifest['files']",ast.unparse(selected[2]))
            space={'ROOT':ROOT,'HERE':path.parent,'__file__':str(path),'Path':Path,'sha':lambda b:hashlib.sha256(b).hexdigest(),'require':need,'host_manifest':{'files':rows}}
            exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),space)
        path=ROOT/'implementation/lab-runtime/local-host/t31-current-ontology-capture-0001/external-postimages-0002/external_ontology_capture.py'
        cls=next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.ClassDef) and n.name=='OntologyTypedCapture')
        method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='produce')
        first=next(i for i,n in enumerate(method.body) if isinstance(n,ast.Assign) and isinstance(n.value,ast.Call) and ast.unparse(n.value.func)=='self.read_public')
        selected=method.body[first:first+2]
        self.assertIn("in self.source_rows",ast.unparse(selected[1]))
        template=PINNED[-1];host=SimpleNamespace(read_public=lambda row:(ROOT/row['path']).read_bytes(),source_rows={(r['path'],r['sha256']) for r in rows})
        exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),{'self':host,'p':{'view_template_binding':template},'sha':lambda b:hashlib.sha256(b).hexdigest(),'need':need})
    def test_actual_four_rows_meet_both_original_constructors_and_closed_guard(self):
        self.assertEqual(len(PINNED),5);self.guard(self.rows);self.constructors(self.rows)
        for row in PINNED:self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['sha256'])
    def test_each_missing_row_refused_without_broadening_allowlist(self):
        for row in PINNED:
            changed=[r for r in self.rows if r['path']!=row['path']]
            with self.subTest(path=row['path']),self.assertRaisesRegex(ValueError,'closure differs'):self.guard(changed)
            with self.assertRaisesRegex(ValueError,'outside the selected host source|template changed/absent'):self.constructors(changed)
    def test_wrong_pin_and_foreign_helper_refused(self):
        changed=copy.deepcopy(self.rows);next(r for r in changed if r['path']==PINNED[0]['path'])['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'outside the selected host source'):self.constructors(changed)
        with self.assertRaisesRegex(ValueError,'foreign successor'):self.guard(self.rows+[{'path':'product/foreign-helper.py','sha256':'f'*64}])
    def test_actual_physical_capture_rejects_changed_helper(self):
        with tempfile.TemporaryDirectory(prefix='cal-flat-helper-capture-') as folder:
            root=Path(folder)
            for row in PINNED:
                path=root/row['path'];path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['path'],path)
            self.physical(root,PINNED)
            path=root/PINNED[0]['path'];path.write_bytes(path.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'source changed'):self.physical(root,PINNED)

if __name__=='__main__':unittest.main()
