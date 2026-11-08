"""Stage exact serial qualification workers after the final integrated cut.

This constructor does not launch a test. It retains the original 21-class,
345-method inventory and checks every method AST against API53 before staging.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
ORIGINAL = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v53-t16-challenge-source-0001'
PRIOR = ROOT / 'implementation/lab-runtime/local-host/t16-abi-coherent-successor-0001'
INSTALL = '/home/vlad_/.local/share/cyberalchemy-lab/native-install/t22-0001'
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()


def methods(folder):
    rows = {}
    for path in [*folder.glob('test_*.py'), *folder.glob('run_*checks.py')]:
        for cls in ast.parse(path.read_text()).body:
            if isinstance(cls, ast.ClassDef):
                for node in cls.body:
                    if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                        rows[path.name+':'+cls.name+'.'+node.name] = ast.dump(node, include_attributes=False)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api', required=True)
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--profile-sha256', required=True)
    parser.add_argument('--label', required=True)
    args = parser.parse_args()
    api = ROOT / args.api
    if api.parent != ORIGINAL.parent or not api.is_dir() or not args.label.isalnum():
        raise ValueError('closed selected API and alphanumeric label required')
    if sha(api/'source-manifest.json') != args.source_sha256 or sha(api/'contract-profile.json') != args.profile_sha256:
        raise ValueError('selected API source/profile differs')
    current, original = methods(api), methods(ORIGINAL)
    if current != original or len(current) != 345:
        raise ValueError('original345 inherited method ASTs differ')
    manifest = json.loads((api/'source-manifest.json').read_bytes())
    prefix = api.relative_to(ROOT).as_posix()+'/'
    python_rows = [row for row in manifest['files'] if row['path'].startswith(prefix) and row['path'].endswith('.py')]
    worker = HERE / ('run_bucket_'+args.label+'.py')
    coordinator = HERE / ('run_regression_'+args.label+'.py')
    if worker.exists() or coordinator.exists():
        raise ValueError('staged worker already exists')
    replacements = {
        'api-integration-v64-t16-abi423-disposition-0001': api.name,
        '440f21c46ec20910e371765c32152bb0a18efead7a147724b762a0a46965a675': args.source_sha256,
        'a4c08349d84a5f8f654eda62fa5ec109ffd6610b5fe8aa474e2197f101aaaf71': args.profile_sha256,
        '/tmp/cal-T03-native-install-20261023/0001': INSTALL,
        'run_bucket_api64.py': worker.name,
        'api64': args.label,
        'API64': args.label.upper(),
        "len(manifest['files']) != 210": "len(manifest['files']) != "+str(len(manifest['files'])),
        'len(code) != 145': 'len(code) != '+str(len(python_rows)),
    }
    import re
    matcher = re.compile('|'.join(re.escape(key) for key in sorted(replacements, key=len, reverse=True)))
    for source, destination in [(PRIOR/'run_bucket_api64.py', worker), (PRIOR/'run_regression_api64.py', coordinator)]:
        text = matcher.sub(lambda item: replacements[item.group(0)], source.read_text())
        ast.parse(text)
        with destination.open('x') as stream:
            stream.write(text)
    receipt = {'schema_version':'lab-integrated-serial-worker-staging/v1', 'result':'STAGED-NOT-RUN',
               'api_source':{'path':str((api/'source-manifest.json').relative_to(ROOT)), 'sha256':args.source_sha256},
               'api_profile':{'path':str((api/'contract-profile.json').relative_to(ROOT)), 'sha256':args.profile_sha256},
               'source_manifest_rows':len(manifest['files']), 'captured_python_modules':len(python_rows),
               'inherited_method_asts':345, 'changed_method_asts':0, 'class_buckets':21,
               'worker':{'path':str(worker.relative_to(ROOT)), 'sha256':sha(worker)},
               'coordinator':{'path':str(coordinator.relative_to(ROOT)), 'sha256':sha(coordinator)},
               'max_concurrency':1, 'stop_after_first_failed_class':True,
               'all_python_children_no_bytecode':True, 'authority_effect':'none', 'full345_qualified':False}
    out = HERE / ('SERIAL-WORKER-STAGING-'+args.label+'.json')
    with out.open('x') as stream:
        stream.write(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps(receipt,sort_keys=True))


if __name__ == '__main__':
    main()
