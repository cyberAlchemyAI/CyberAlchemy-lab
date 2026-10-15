"""Retain original Work membership in the positive export fixture.

The first fixture incorrectly removed a required relation_refs entry. This check
successor changes fixture construction only, retaining all12 original test bodies
and the frozen API58 handler, schemas, source checks and public contracts.
"""
import ast
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v58';CHECK=BASE/'api58-export-checks-v2'
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def methods(text):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(text))
    if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert not CHECK.exists();CHECK.mkdir()
    fixture=(API/'package_export_fixture.py').read_text()
    before="record.update(node_id='work:R03-public-package-export',name='Candidate package export Work',relation_refs=[])"
    after="record.update(node_id='work:R03-public-package-export',name='Candidate package export Work')"
    assert fixture.count(before)==1;fixture=fixture.replace(before,after,1)
    (CHECK/'fixture.py').write_text(fixture)
    original=(API/'test_package_export.py').read_text()
    revised=original.replace('from . import protocol as P, package_export_fixture as F','from . import protocol as P, versioned_export_fixture as F',1)
    assert methods(original)==methods(revised) and len(methods(original))==12
    (CHECK/'tests.py').write_text(revised)
    runner=(API/'checks_package_export.py').read_text()
    runner=runner.replace("HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]", "HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]\nAPI=HERE.parent/'api-v58'")
    runner=runner.replace("parser.add_argument('--suite',choices=['focused','full'],required=True);args=parser.parse_args()", "parser.add_argument('--suite',choices=['focused','full'],required=True);parser.add_argument('--check-source-sha256',required=True);args=parser.parse_args()\n    def check_source():\n        assert sha(HERE/'source-manifest.json')==args.check_source_sha256\n        for row in json.loads((HERE/'source-manifest.json').read_bytes())['files']:\n            assert sha(ROOT/row['path'])==row['sha256'],row['path']\n    check_source()")
    runner=runner.replace("HERE/'__init__.py',submodule_search_locations=[str(HERE)]", "API/'__init__.py',submodule_search_locations=[str(API)]")
    runner=runner.replace("module=__import__(name+'.test_package_export',fromlist=['PackageExportAPI'])", "fixture_spec=importlib.util.spec_from_file_location(name+'.versioned_export_fixture',HERE/'fixture.py')\n    fixture=importlib.util.module_from_spec(fixture_spec);sys.modules[fixture_spec.name]=fixture;fixture_spec.loader.exec_module(fixture)\n    test_spec=importlib.util.spec_from_file_location(name+'.versioned_export_tests',HERE/'tests.py')\n    module=importlib.util.module_from_spec(test_spec);sys.modules[test_spec.name]=module;test_spec.loader.exec_module(module)")
    runner=runner.replace("sha(HERE/'contract-profile.json')", "sha(API/'contract-profile.json')")
    runner=runner.replace("guard.verify(args.source_sha256);assert", "check_source();guard.verify(args.source_sha256);assert")
    runner=runner.replace("bind(HERE/'source-manifest.json'),bind(HERE/'contract-profile.json')", "bind(HERE/'source-manifest.json'),bind(API/'source-manifest.json'),bind(API/'contract-profile.json')")
    (CHECK/'checks.py').write_text(runner)
    for path in CHECK.glob('*.py'):ast.parse(path.read_bytes())
    files=[bind(p) for p in sorted(CHECK.glob('*.py'))]
    files.extend(bind(p) for p in (API/'source-manifest.json',API/'contract-profile.json',API/'test_package_export.py',
        API/'package_export_fixture.py',ROOT/'authority/artifact-types/work/v1/schema.json',Path(__file__).resolve()))
    selection={'schema_version':'lab-export-check-source/v1-candidate','files':files,
        'fixture_change':'Retain original required Work relation_refs membership; independent native schema/core validation stays mandatory.',
        'original_export_test_method_ASTs_unchanged':True,'retained_export_test_methods':12,
        'actual_runtime_qualified':False,'authority_effect':'none','actual_owner_outcome':None}
    with (CHECK/'source-manifest.json').open('x') as stream:json.dump(selection,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'FROZEN-CHECK-SUCCESSOR','check_source_binding':bind(CHECK/'source-manifest.json'),
        'retained_original_test_bodies':12,'host_source_unchanged':True,'actual_runtime_qualified':False}),flush=True)
if __name__=='__main__':main()
