"""Build a disjoint API76 code successor from exact API75 staged originals."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
API75 = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v75-current-fixtures-0001'
API76 = API75.parent / 'api-integration-v76-current-repairs-0001'
REPORT = HERE / 'API75-CODE-PREPARATION-0014.json'
REPORT_SHA = 'fd257f1d56d77960ee1ca8983d4772003875c0b1afc11cd47861ad48e01fc299'
RESOLVER = ROOT / 'implementation/lab-runtime/local-host/t03-lesson-domain-resolver-0001/lesson_application_references.py'
# Freeze this after independent resolver review; a different byte must refuse.
RESOLVER_SHA = '6c9155c9f8d43f099400ba3124fb041727898cc0bc014832547a801d2a688a26'
CLASSIFIER = ROOT / 'product/lab/release-candidates/v1/interface/classification-preparation-v10/preparation.py'
CLASSIFIER_SHA = '29fc7de3d3abe064707b529743af43f0acbd9706e240a1e4e977ddb2fcf876fb'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def methods(directory):
    result = {}
    for path in [*directory.glob('test_*.py'), *directory.glob('run_*checks.py')]:
        for cls in ast.parse(path.read_bytes()).body:
            if isinstance(cls, ast.ClassDef):
                for member in cls.body:
                    if isinstance(member, ast.FunctionDef) and member.name.startswith('test_'):
                        result[path.name + ':' + cls.name + '.' + member.name] = ast.dump(member, include_attributes=False)
    return result


def replace_once(path, before, after):
    value = path.read_text()
    need(value.count(before) == 1, 'API75 successor seam differs: ' + str(path))
    path.write_text(value.replace(before, after))


def build(destination):
    destination = Path(destination)
    need(destination.is_absolute() and destination == API76 and not destination.exists(),
         'fresh exact API76 destination required')
    need(sha(REPORT.read_bytes()) == REPORT_SHA, 'reviewed API75 code input report differs')
    source = json.loads(REPORT.read_bytes())
    need(source['status'] == 'CODE-REBUILT-NOT-RUN' and source['inherited_case_count'] == 345
         and len(source['files']) == 214, 'API75 staged method/file inventory differs')
    prefix = API75.relative_to(ROOT)
    destination.mkdir(mode=0o755)
    for row in source['files']:
        path = ROOT / row['path']
        relative = path.relative_to(API75)
        need(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == row['sha256'],
             'reviewed API75 staged source differs: ' + row['path'])
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        need(sha(target.read_bytes()) == row['sha256'], 'copied API75 original differs')
    replace_once(destination / 'failure_preparation.py', 'failure-preparation-v5', 'failure-preparation-v6')
    replace_once(destination / 'failure_preparation.py', '_failure_preparation_v5', '_failure_preparation_v6')
    need(sha(CLASSIFIER.read_bytes()) == CLASSIFIER_SHA,
         'independently reviewed classification v10 differs')
    replace_once(destination / 'classification_preparation.py', 'classification-preparation-v9', 'classification-preparation-v10')
    replace_once(destination / 'classification_preparation.py', '_classification_preparation_v9', '_classification_preparation_v10')
    replace_once(destination / 'workflow_output_registry.py', 'failure-preparation-v5/preparation.py',
                 'failure-preparation-v6/preparation.py')
    replace_once(destination / 'guard.py', "('classification-preparation-v9', 'failure-preparation-v5')",
                 "('classification-preparation-v10', 'failure-preparation-v6')")
    replace_once(destination / 'guard.py', "    helper_paths.add('authority/artifact-types/ontology-view/v1/fixtures/valid/record.json')",
                 "    helper_paths.add('product/lab/release-candidates/v1/interface/classification-preparation-v10/__init__.py')\n"
                 "    helper_paths.add('product/lab/release-candidates/v1/interface/failure-preparation-v6/__init__.py')\n"
                 "    helper_paths.add('authority/artifact-types/ontology-view/v1/fixtures/valid/record.json')")
    replace_once(destination / 'service.py', "'candidate.py','jcs.py'",
                 "'candidate.py','lesson_application_references.py','jcs.py'")
    replace_once(destination / 'workflow_composition.py',
                 'class WorkflowCandidateHandlers(GeneratedCandidateHandlers):\n    def needed(self,message):',
                 "class WorkflowCandidateHandlers(GeneratedCandidateHandlers):\n"
                 "    def __init__(self,host):\n"
                 "        super().__init__(host)\n"
                 "        if host.channel.policy['schema_version']=='lab-local-lesson-application-policy/v2-candidate':\n"
                 "            from .lesson_application_references import LessonApplicationReferences\n"
                 "            self.resolution_references=LessonApplicationReferences(host)\n"
                 "    def needed(self,message):")
    need(sha(RESOLVER.read_bytes()) == RESOLVER_SHA, 'independently reviewed Lesson resolver differs')
    shutil.copy2(RESOLVER, destination / 'lesson_application_references.py')
    for path in destination.rglob('*.py'):
        compile(path.read_bytes(), str(path), 'exec', dont_inherit=True)
    before, after = methods(API75), methods(destination)
    need(len(before) == len(after) == 345 and before == after,
         'inherited 345 maintained method ASTs changed')
    files = [{'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}
             for path in sorted(destination.rglob('*')) if path.is_file()]
    need(len(files) == 215, 'API76 selected code file count differs')
    old = {path.relative_to(API75).as_posix(): sha(path.read_bytes()) for path in API75.rglob('*') if path.is_file()}
    deltas = [{'relative_path': path.relative_to(destination).as_posix(),
               'predecessor_sha256': old.get(path.relative_to(destination).as_posix()),
               'successor_sha256': sha(path.read_bytes())}
              for path in sorted(destination.rglob('*')) if path.is_file()
              and old.get(path.relative_to(destination).as_posix()) != sha(path.read_bytes())]
    need({row['relative_path'] for row in deltas} == {
        'classification_preparation.py', 'failure_preparation.py', 'workflow_output_registry.py', 'guard.py', 'service.py',
        'workflow_composition.py', 'lesson_application_references.py'}, 'API76 delta set differs')
    return {'schema_version': 'lab-maintained-current-repairs-code-stage/v1',
            'status': 'CODE-REBUILT-NOT-RUN', 'predecessor_report_sha256': REPORT_SHA,
            'files': files, 'deltas': deltas, 'inherited_case_count': 345,
            'unchanged_method_asts': 345, 'source_profile_generated_per_install': True,
            'authority_effect': 'none'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('destination', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    need(not args.report.exists(), 'fresh API76 preparation report required')
    result = build(args.destination)
    args.report.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'files': len(result['files']),
                      'maintained_cases': result['inherited_case_count'],
                      'deltas': len(result['deltas'])}, sort_keys=True))
