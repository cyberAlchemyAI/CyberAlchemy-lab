"""Freeze new public typed cases and strict successors of original count checks."""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v48'
TYPED = BASE / 'api48-typed-checks-v1'
STRICT = BASE / 'api48-current-checks-v1'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def main():
    assert not STRICT.exists() and not (TYPED / 'source-manifest.json').exists()
    source = API / 'source-manifest.json'
    assert bind(source)['sha256'] == 'a7329574c52004e476fd822da9177375a484ffc380e27c84f437ffc8f66d08e6'
    selected = json.loads(source.read_bytes())
    for row in selected['files']:
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
    STRICT.mkdir()
    corrections = []
    for name in ('test_current_controls.py', 'run_session_checks.py', 'test_custody_sessions.py'):
        original = (API / name).read_text()
        old = 'self.assertEqual(len(SUPPORTED),15)'
        assert original.count(old) == 1
        revised = original.replace(old, 'self.assertEqual(len(SUPPORTED),17)')
        (STRICT / name).write_text(revised)
        old_ast, new_ast = ast.parse(original), ast.parse(revised)
        count = 0
        for node in ast.walk(new_ast):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'assertEqual' \
                    and len(node.args) == 2 and ast.unparse(node.args[0]) == 'len(SUPPORTED)':
                assert isinstance(node.args[1], ast.Constant) and node.args[1].value == 17
                node.args[1].value = 15
                count += 1
        assert count == 1 and ast.dump(old_ast, include_attributes=False) == ast.dump(new_ast, include_attributes=False)
        corrections.append({'original_binding': bind(API / name), 'successor_binding': bind(STRICT / name),
                            'only_AST_change': 'Exact supported handler count 15 -> 17.'})
    (STRICT / 'checks.py').write_text('''"""All original146 cases or all original11 controls, with exact count successors."""
import argparse,hashlib,importlib.util,json,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];API=HERE.parent/'api-v48'
SOURCE='a7329574c52004e476fd822da9177375a484ffc380e27c84f437ffc8f66d08e6'
PROFILE='080eaba1d670b1f660073a0554a601b3ee4eabd3be60d47dbe427df4ea4229f9'
def main():
 p=argparse.ArgumentParser();p.add_argument('--check-source-sha256',required=True);p.add_argument('--suite',choices=['full','controls'],required=True);a=p.parse_args()
 manifest=HERE/'source-manifest.json';assert hashlib.sha256(manifest.read_bytes()).hexdigest()==a.check_source_sha256
 selected=json.loads(manifest.read_bytes())
 def source_guard():
  for row in selected['files']:
   path=ROOT/row['path'];assert path.is_file() and not path.is_symlink() and not any(parent.is_symlink() for parent in path.parents)
   assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
 source_guard();name='_cal_API48_strict_current_'+a.suite
 spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)]);package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
 guard=__import__(name+'.guard',fromlist=['verify']);guard.verify(SOURCE)
 def versioned(filename):
  module_name=name+'.versioned_'+filename.removesuffix('.py');spec=importlib.util.spec_from_file_location(module_name,HERE/filename)
  module=importlib.util.module_from_spec(spec);sys.modules[module_name]=module;spec.loader.exec_module(module);module.PROFILE=PROFILE;return module
 if a.suite=='controls':
  suite=unittest.defaultTestLoader.loadTestsFromTestCase(versioned('test_current_controls.py').CurrentControls);expected=11
 else:
  modules=[__import__(name+'.'+n,fromlist=['*']) for n in ['test_preparation','test_preparation_corrected','test_custody_api','test_guarded_reads']]
  for module in modules:module.PROFILE=PROFILE
  sessions=[versioned('run_session_checks.py'),versioned('test_custody_sessions.py')]
  suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(modules[3]),unittest.defaultTestLoader.loadTestsFromModule(modules[2]),unittest.defaultTestLoader.loadTestsFromTestCase(modules[1].CorrectedPreparation),unittest.defaultTestLoader.loadTestsFromModule(sessions[0]),unittest.defaultTestLoader.loadTestsFromModule(sessions[1])]);expected=146
 assert suite.countTestCases()==expected;cases=[]
 class Result(unittest.TextTestResult):
  def addSuccess(self,test):super().addSuccess(test);cases.append({'test':test.id(),'result':'PASS'})
  def addFailure(self,test,error):
   super().addFailure(test,error);detail=self._exc_info_to_string(error,test);cases.append({'test':test.id(),'result':'FAIL','detail':detail});self.stream.write('\\n'+detail);self.stream.flush()
  def addError(self,test,error):
   super().addError(test,error);detail=self._exc_info_to_string(error,test);cases.append({'test':test.id(),'result':'ERROR','detail':detail});self.stream.write('\\n'+detail);self.stream.flush()
 result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite);source_guard();guard.verify(SOURCE)
 report={'schema_version':'lab-current-strict-full-checks/v1-candidate','result':'PASS' if result.wasSuccessful() and result.testsRun==expected else 'FAIL','actual_cases':result.testsRun,'expected_cases':expected,'cases':cases,'failures':len(result.failures),'errors':len(result.errors),'source_sha256':SOURCE,'profile_sha256':PROFILE,'exact_handler_count':17,'all_original_cases_retained':True,'only_test_AST_revision':'Exact len(SUPPORTED)15 -> 17 in three separately versioned methods.','whole_API_qualified':False,'task_complete':False,'authority_effect':'none','actual_owner_outcome':None}
 receipts=HERE/'receipts';receipts.mkdir(exist_ok=True)
 with (receipts/(a.suite+'-0001.json')).open('x') as stream:json.dump(report,stream,sort_keys=True,indent=2);stream.write('\\n')
 print(json.dumps({'result':report['result'],'actual_cases':result.testsRun,'suite':a.suite}),flush=True)
 raise SystemExit(0 if report['result']=='PASS' else 1)
if __name__=='__main__':main()
''')
    context = RUN / 'context-R03-API48-public-qualification-0001.json'
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate', 'strict_coverage': 'PASS',
        'task': 'R03 complete authenticated typed operation and strict current source qualifications',
        'source_bindings': [bind(source), bind(API / 'contract-profile.json'), bind(RUN / 'authorization.json')],
        'write_scope': [TYPED.relative_to(ROOT).as_posix(), STRICT.relative_to(ROOT).as_posix()],
        'constraints': ['Run all eight new typed cases with actual ReaderChannel and owned temporary fixtures.',
            'Run all original146 cases and11 controls; only exact count assertion15->17 changes in three successors.',
            'No production function, original test or policy/clock callback is patched.',
            'All original deadlines, absolute participation periods, source/custody and cleanup assertions remain.',
            'Synthetic coupled change and pending review provide no genuine semantic verdict or operational grant.',
            'Heavy public execution remains serialized after same full API47 failure18 job.'],
        'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False})
    for package, label in ((TYPED, 'new-eight-public-typed-cases'), (STRICT, 'strict-original-146-and-11-controls')):
        paths = [p for p in package.rglob('*') if p.is_file() and not {'receipts', '__pycache__'} & set(p.parts)]
        for path in paths:
            if path.suffix == '.py':
                ast.parse(path.read_bytes())
        rows = {row['path']: row for row in selected['files']}
        for path in paths + [source, API / 'contract-profile.json', context, Path(__file__).resolve(),
                             RUN / 'typed-scope-diagnostic-profile-0001.json']:
            row = bind(path)
            rows[row['path']] = row
        put(package / 'source-manifest.json', {'schema_version': 'lab-API48-qualified-checks-source/v1-candidate',
            'suite': label, 'files': [rows[k] for k in sorted(rows)], 'source_binding': bind(source),
            'original_count_corrections': corrections if package == STRICT else [],
            'original_tests_unchanged_in_API_source': True, 'runtime_executed': False,
            'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False})
    print(json.dumps({'result': 'FROZEN', 'typed_checks_source_binding': bind(TYPED / 'source-manifest.json'),
                     'strict_checks_source_binding': bind(STRICT / 'source-manifest.json'),
                     'original_cases': 146, 'original_controls': 11, 'new_typed_cases': 8,
                     'runtime_executed': False}), flush=True)


if __name__ == '__main__':
    main()
