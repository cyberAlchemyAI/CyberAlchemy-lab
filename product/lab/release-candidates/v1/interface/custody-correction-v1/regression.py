"""All original v2 assertions against the separate candidate executable.

Only test host paths and explicit CLI --repo arguments are adapted. Original
test and runtime files remain unchanged. The exact adapted source is retained.
"""
import ast
import types
import unittest
from loader import *


def adapted_source():
    source=ROOT/'implementation/lab-runtime/v2/tests/test_runtime.py';raw=source.read_text()
    replacements=[('sys.path.insert(0, str(Path(__file__).resolve().parents[1]))',
        'sys.path.insert(0, '+repr(str(ENGINE))+')'),
        ('PACKAGE = Path(__file__).resolve().parents[1]', 'PACKAGE = Path('+repr(str(ENGINE))+')'),
        ('REPO = PACKAGE.parents[2]', 'REPO = Path('+repr(str(ROOT))+')'),
        ('PACKAGE.parent / "v1"', 'Path('+repr(str(ROOT/'implementation/lab-runtime/v1'))+')'),
        ('PACKAGE.parent / "v1/profile.json"', 'Path('+repr(str(ROOT/'implementation/lab-runtime/v1/profile.json'))+')'),
        ('str(PACKAGE / "lab.py"),', 'str(PACKAGE / "lab.py"), "--repo", str(REPO),')]
    edits=[]
    for before,after in replacements:
        count=raw.count(before);require(count>=1,'selected original regression adaptation anchor absent')
        raw=raw.replace(before,after);edits.append({'before':before,'after':after,'occurrences':count})
    tree=ast.parse(raw);count=sum(isinstance(n,ast.FunctionDef) and n.name.startswith('test_') for n in ast.walk(tree))
    require(count==38,'all original 38 runtime cases required')
    return raw,edits,bind(source)


if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: regression.py retained-source-directory')
    output=Path(sys.argv[1]);require(output.resolve().is_relative_to(HERE),'regression logs outside selected candidate interface')
    output.mkdir(parents=True,exist_ok=True);raw,edits,source=adapted_source()
    with (output/'adapted-test-runtime.py').open('x') as stream:stream.write(raw)
    with (output/'adaptation.json').open('xb') as stream:stream.write(encoded({'authority_effect':'none',
        'original_source_binding':source,'adapted_source_sha256':sha(raw.encode()),'edits':edits,'assertions_changed':False,'tests':38}))
    module=types.ModuleType('R03_candidate_full_runtime_regression');module.__file__=str(output/'adapted-test-runtime.py')
    sys.modules[module.__name__]=module;exec(compile(raw,module.__file__,'exec'),module.__dict__)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
    print(json.dumps({'result':'PASS' if result.wasSuccessful() else 'FLAG','tests':result.testsRun,
        'failures':len(result.failures),'errors':len(result.errors),'assertions_changed':False,'authority_effect':'none'},sort_keys=True))
    sys.exit(0 if result.wasSuccessful() else 1)
