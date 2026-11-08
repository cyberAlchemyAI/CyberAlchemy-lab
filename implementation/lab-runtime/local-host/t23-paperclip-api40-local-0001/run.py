"""Run one disposable cached Paperclip process adapter to API40 Base."""

import hashlib
import importlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import time

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001'
RUNNER = ROOT / 'product/lab/release-candidates/v1/interface/paperclip-runner-v3/runner.py'
CACHE = Path('/home/vlad_/.npm/_npx/2516d3db5aacea45/node_modules')
EXECUTE = CACHE / '@paperclipai/server/dist/adapters/process/execute.js'
NODE = Path('/home/vlad_/.local/share/node-v26.8.1-linux-x64/bin/node')
SOURCE_NAME = 'completion-legacy:legacy-local-947e6c2a5b3d10f8'
READER_BOOTSTRAP = (
    "import hashlib,pathlib,sys\n"
    "expected=sys.argv.pop(1); filename=sys.argv.pop(1)\n"
    "raw=pathlib.Path(filename).read_bytes()\n"
    "if hashlib.sha256(raw).hexdigest()!=expected: raise SystemExit('selected reader bytes differ')\n"
    "scope={'__name__':'__main__','__file__':filename}\n"
    "exec(compile(raw,filename,'exec'),scope)\n"
)
NODE_BOOTSTRAP = (
    "import{createHash}from'node:crypto';import{readFile}from'node:fs/promises';"
    "const[expected,path,...rest]=process.argv.slice(1);"
    "const raw=await readFile(path);"
    "if(createHash('sha256').update(raw).digest('hex')!==expected)"
    "throw new Error('selected invoker bytes differ');"
    "process.argv=[process.execPath,path,...rest];"
    "await import('data:text/javascript;base64,'+raw.toString('base64'));"
)
PINS = {
    API / 'source-manifest.json': '45412c382dc0cc9c807dd2bf4ec67037c7ae58854fcbb42cb15a96f0f7f3a219',
    API / 'contract-profile.json': 'cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614',
    RUNNER: 'a1de38b075fc40f137e51785f7841990f4aaf83fa445cb2f5ea06bc3d27b60b9',
    EXECUTE: 'c4b1170b02b7272cba475e90d95aa727246485c1853b2e4ad0274b7553bd7cb4',
    CACHE / 'paperclipai/package.json': '1049902e3628726e55efe3835e984d5453e229468cca2b840661c9636c42b9fa',
    CACHE / '@paperclipai/server/package.json': '72c6650955a273a9f0646802f97af3105716c745974078f91facc20ce56b8a63',
    HERE / 'read-plan.json': '585e223a079d7bfedf2d5cd5fd6d3ea2870b39fb3510dad0e5e2c32573a49298',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def need(value, reason):
    if not value:
        raise ValueError(reason)


def exact(path, expected):
    path = Path(path)
    state = path.lstat()
    need(stat.S_ISREG(state.st_mode) and not any(p.is_symlink() for p in (path, *path.parents)),
         'selected path linked or nonregular')
    raw = path.read_bytes()
    need(sha(raw) == expected, 'selected byte changed')
    return raw


def put(path, raw):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def preflight():
    for path, digest in PINS.items():
        exact(path, digest)
    need(json.loads((CACHE / 'paperclipai/package.json').read_bytes())['version'] == '2026.1005.0'
         and json.loads((CACHE / '@paperclipai/server/package.json').read_bytes())['version'] == '2026.1005.0',
         'cached Paperclip version differs')
    source = json.loads((API / 'source-manifest.json').read_bytes())
    rows = {row['path']: row['sha256'] for row in source['files']}
    fixture = API / 'fixtures.py'
    need(rows.get(fixture.relative_to(ROOT).as_posix()) == sha(fixture.read_bytes()),
         'API40 fixture constructor not selected')


def prepare(control, reader_sha=None):
    preflight()
    base = control / 'base'
    base.mkdir(mode=0o700)
    sys.path.insert(0, str(API.parent))
    fixtures = importlib.import_module(API.name + '.fixtures')
    principal = fixtures.source.current_legacy_delivery().records.PRINCIPAL
    key, policy_path, policy_sha = fixtures.provision(base, source_name=SOURCE_NAME,
                                                      principal=principal, max_actions=1)
    key = None
    key_path = base / 'reader.pem'
    key_sha = sha(key_path.read_bytes())
    policy = json.loads(policy_path.read_bytes())
    need(policy['workspace']['max_actions'] == 1 and policy['source_name'] == SOURCE_NAME
         and policy['authority_effect'] == 'none', 'technical Base policy differs')
    selection = {'policy': str(policy_path), 'policy_sha256': policy_sha,
                 'reader_key': str(key_path), 'reader_key_sha256': key_sha,
                 'plan': str(HERE / 'read-plan.json'),
                 'plan_sha256': PINS[HERE / 'read-plan.json'], 'timeout_seconds': 900}
    selection_path = control / 'selection.json'
    put(selection_path, (json.dumps(selection, sort_keys=True) + '\n').encode())
    reader_sha = reader_sha or sha((HERE / 'reader.py').read_bytes())
    adapter = {'command': sys.executable,
               'args': ['-I', '-B', '-c', READER_BOOTSTRAP, reader_sha,
                        str(HERE / 'reader.py'), '--config', str(selection_path)],
               'cwd': str(ROOT), 'timeoutSec': 930, 'graceSec': 5}
    adapter_path = control / 'adapter.json'
    put(adapter_path, (json.dumps(adapter, sort_keys=True) + '\n').encode())
    return adapter_path, policy_sha, key_sha


def run():
    started = time.monotonic()
    own = HERE / 'run.py'
    own_sha = sha(own.read_bytes())
    reader_sha = sha((HERE / 'reader.py').read_bytes())
    adapter_sha = sha((HERE / 'adapter.mjs').read_bytes())
    with tempfile.TemporaryDirectory(prefix='cal-T23-paperclip-api40-') as directory:
        control = Path(directory)
        need(stat.S_IMODE(control.stat().st_mode) == 0o700, 'private scratch mode differs')
        adapter_path, policy_sha, key_sha = prepare(control, reader_sha)
        env = {'PATH': str(NODE.parent) + ':/usr/bin:/bin', 'HOME': str(control), 'LC_ALL': 'C',
               'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONNOUSERSITE': '1'}
        process = subprocess.run([str(NODE), '--input-type=module', '--eval', NODE_BOOTSTRAP,
                                  adapter_sha, str(HERE / 'adapter.mjs'), str(EXECUTE),
                                  PINS[EXECUTE], str(adapter_path)],
                                 cwd=ROOT, env=env, capture_output=True, timeout=980)
        need(process.returncode == 0 and not process.stderr, 'Paperclip process adapter refused')
        adapter = json.loads(process.stdout)
        need(adapter['schema_version'] == 'lab-t23-paperclip-process-adapter-result/v1'
             and adapter['exit_code'] == 0 and adapter['timed_out'] is False
             and adapter['signal'] is None and adapter['paperclip_server_started'] is False
             and adapter['paperclip_api_called'] is False,
             'Paperclip process result differs')
        child = json.loads(adapter['result_json']['stdout'])
        need(child['result'] == 'PASS' and child['api40_child_exit_code'] == 0
             and child['api_source_sha256'] == PINS[API / 'source-manifest.json']
             and child['api_profile_sha256'] == PINS[API / 'contract-profile.json']
             and child['runner_v3_sha256'] == PINS[RUNNER]
             and [(r['operation'], r['case'], r['kind'], r['code']) for r in child['observations']] ==
             [('lab.status', 'positive', 'result', None),
              ('catalog.get', 'positive', 'result', None),
              ('lab.status', 'wrong-scope', 'error', 'unauthorized')]
             and child['workspace_before'] == {'objects': 0, 'effect_journal': 0,
                                                'session_custody_lock': 0}
             and child['workspace_after'] == {'objects': 0, 'effect_journal': 0,
                                               'session_custody_lock': 1}
             and child['lab_mutations_requested'] == 0 and child['human_usefulness_observed'] is False,
             'actual API40 Base read/refusal journey differs')
        preflight()
        need(sha(own.read_bytes()) == own_sha and sha((HERE / 'reader.py').read_bytes()) == reader_sha
             and sha((HERE / 'adapter.mjs').read_bytes()) == adapter_sha,
             'journey code changed during run')
        result = {'schema_version': 'lab-T23-paperclip-api40-local-journey/v1', 'status': 'PASS',
                  'paperclip_version': '2026.1005.0', 'paperclip_process_adapter_sha256': PINS[EXECUTE],
                  'api_source_sha256': PINS[API / 'source-manifest.json'],
                  'api_profile_sha256': PINS[API / 'contract-profile.json'],
                  'runner_v3_sha256': PINS[RUNNER], 'reader_sha256': reader_sha,
                  'adapter_invoker_sha256': adapter_sha, 'orchestrator_sha256': own_sha,
                  'policy_sha256': policy_sha, 'reader_key_sha256': key_sha,
                  'private_key_exported': False, 'paperclip_server_started': False,
                  'paperclip_api_called': False, 'process_agent_invoked': True,
                  'actual_lab_calls': child['observations'], 'source_cut_sha256': child['source_cut_sha256'],
                  'api40_child_exit_code': 0, 'paperclip_process_exit_code': 0,
                  'workspace_before': child['workspace_before'],
                  'workspace_after': child['workspace_after'],
                  'lab_mutations_requested': 0, 'human_usefulness_observed': False,
                  'authority_effect': 'none', 'elapsed_seconds': round(time.monotonic() - started, 3),
                  'claim_ceiling': 'One disposable cached Paperclip process-adapter invocation drove API40 Base status/catalog and wrong-scope refusal in one authenticated child; no Paperclip server, persistent service, human pilot, Source8 session or whole API qualification.'}
    need(not control.exists(), 'disposable control not removed')
    result['disposable_control_removed'] = True
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', required=True)
    args = parser.parse_args()
    receipt = HERE / args.receipt
    need(receipt.parent == HERE and receipt.name.startswith('RUN-') and receipt.suffix == '.json'
         and not receipt.exists(), 'new task-local receipt required')
    try:
        result = run()
    except Exception as error:
        result = {'schema_version': 'lab-T23-paperclip-api40-local-journey/v1', 'status': 'REFUSED',
                  'error_class': type(error).__name__, 'authority_effect': 'none',
                  'human_usefulness_observed': False, 'paperclip_server_started': False,
                  'claim_ceiling': 'No complete Paperclip/API40 local read journey established.'}
    put(receipt, (json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
    print(json.dumps(result, sort_keys=True))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
