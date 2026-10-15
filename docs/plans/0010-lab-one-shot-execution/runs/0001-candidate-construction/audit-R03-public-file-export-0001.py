"""Independent fresh-process public export observations against frozen API25."""
import argparse
import base64
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
PACKAGE = ROOT / 'product/lab/release-candidates/v1/interface/api-v25'
SOURCE = RUN / 'public-file-export-audit-source-0001.json'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def bind(path):
    return {'path': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path), 'sha256': sha(path.read_bytes())}

def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    assert sha(SOURCE.read_bytes()) == args.source_sha256
    frozen = json.loads(SOURCE.read_bytes())
    def guard():
        for row in frozen['files']:
            assert bind(ROOT / row['path']) == row, row['path']
    guard()
    name = '_cal_independent_public_export25'
    spec = importlib.util.spec_from_file_location(name, PACKAGE / '__init__.py', submodule_search_locations=[str(PACKAGE)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    def module(n):
        return __import__(name + '.' + n, fromlist=['*'])
    P, F, G = [module(n) for n in ('protocol', 'export_fixture', 'guard')]
    G.verify(frozen['api_source_binding']['sha256'])
    schemas = P.Schemas(frozen['api_profile_binding']['sha256'])
    checks, observations, roots = [], [], []
    def need(condition, label):
        assert condition, label
        checks.append(label)
        print(json.dumps({'check': label, 'result': 'PASS'}), flush=True)
    period = P.source.custody_delivery().reader.HERE / 'packages/0001/period.json'
    original_period = period.read_bytes()
    with P.source.replay_source('custody-participation') as view:
        selected = F.selection(view)
        originals = {}
        for header in selected['artifact_refs']:
            subject = view.subjects[header['version_ref']]
            tx_raw = view.originals[subject['source']['path']]
            enclosing = json.loads(tx_raw)
            pointer = subject['source']['record_selector'].removesuffix('/record')
            for token in pointer.split('/')[1:]:
                token = token.replace('~1', '/').replace('~0', '~')
                enclosing = enclosing[int(token)] if isinstance(enclosing, list) else enclosing[token]
            raw = base64.b64decode(enclosing['content']['data'], validate=True)
            need(sha(raw) == header['byte_sha256'], 'independent original body digest ' + header['version_ref'])
            originals[header['version_ref']] = raw
        need(len(originals) == 2, 'complete actual Intent and Goal selection')
        with tempfile.TemporaryDirectory(prefix='cal-R03-independent-public-export-') as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            roots.append(str(root))
            key, policy_path, policy_pin = F.provision(root, selected)
            policy = json.loads(policy_path.read_bytes())
            need(len(policy['allowed_operations']) == 9 and policy['session_control'] is None, 'distinct nine-operation export grant has no Session control')
            process = subprocess.Popen([sys.executable, str(PACKAGE / 'serve.py'), '--policy', str(policy_path), '--policy-sha256', policy_pin, '--source-sha256', frozen['api_source_binding']['sha256'], '--protocol-profile-sha256', frozen['api_profile_binding']['sha256']], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                challenge = json.loads(process.stdout.readline())
                signature = key.sign(P.compact(challenge))
                key.public_key().verify(signature, P.compact(challenge))
                proof = {'schema_version': 'lab-local-reader-proof/v1-candidate', 'challenge': challenge, 'signature': base64.b64encode(signature).decode()}
                process.stdin.write(P.compact(proof) + b'\n')
                process.stdin.flush()
                auth = json.loads(process.stdout.readline())
                need(auth['context']['agent_instance_ref'] is None and auth['context']['assignment_ref'] is None and auth['context']['session_ref'] is None, 'actual nonce-authenticated stdio Principal without Agent participation')
                client = SimpleNamespace(channel=SimpleNamespace(context=auth['context'], policy=policy), schemas=schemas)
                def invoke(call):
                    process.stdin.write(P.compact(call) + b'\n')
                    process.stdin.flush()
                    line = process.stdout.readline()
                    assert line, 'actual stdio process ended before reply'
                    reply = json.loads(line)
                    observations.append({'call': call, 'reply': reply, 'actual_stdio': True})
                    return reply
                output = Path(policy['export_control']['output_root'])
                # Unmanaged root entries are deliberately excluded by the grant.
                # Preserve an unrelated file beside the independently owned root.
                unmanaged = root / 'unmanaged-audit.txt'
                unmanaged.write_bytes(b'independent bytes must remain unchanged')
                for mode in ('byte-exact', 'rendered'):
                    call = F.call(client, selected, key='independent:export:' + mode, mode=mode)
                    reply = invoke(call)
                    need(reply['kind'] == 'result' and reply['message']['posture'] == 'published', 'actual public stdio export ' + mode)
                    receipt = reply['message']
                    need(receipt['request_binding']['sha256'] == sha(P.message_bytes(P.compact(call))) and not receipt['canonical_replay_source'], 'actual original API message binding and authority ceiling ' + mode)
                    generation = output / sha(P.compact(call['message']))
                    manifest_raw, receipt_raw = (generation / 'manifest.json').read_bytes(), (generation / 'receipt.json').read_bytes()
                    need(json.loads((generation / 'PUBLISHED.json').read_bytes()) == {'manifest_sha256': sha(manifest_raw), 'receipt_sha256': sha(receipt_raw)}, 'actual publication marker binds flushed files ' + mode)
                    for path, header in zip(selected['managed_relative_paths'], selected['artifact_refs'], strict=True):
                        raw = (generation / 'files' / path).read_bytes()
                        original = originals[header['version_ref']]
                        need(raw == original if mode == 'byte-exact' else json.loads(raw) == json.loads(original) and raw.endswith(b'\n'), 'independently decoded output ' + mode + ' ' + path)
                    before = {str(p.relative_to(output)): (p.stat().st_ino, sha(p.read_bytes())) for p in output.rglob('*') if p.is_file()}
                    retry = json.loads(json.dumps(call))
                    retry['call_id'] += ':retry'
                    retried = invoke(retry)
                    need(retried['kind'] == 'result' and retried['message'] == receipt, 'actual recorded stdio retry ' + mode)
                    need(before == {str(p.relative_to(output)): (p.stat().st_ino, sha(p.read_bytes())) for p in output.rglob('*') if p.is_file()}, 'retry leaves all managed bytes and inodes unchanged ' + mode)
                    if mode == 'byte-exact':
                        shutil.rmtree(generation)
                        retry['call_id'] += ':deleted'
                        refused = invoke(retry)
                        need(refused['message']['code'] == 'recovery-required' and not generation.exists(), 'deleted generation cannot be recreated by recorded public key')
                denied = F.call(client, selected, key='independent:denied-session')
                denied['operation'] = 'session.open'
                reply = invoke(denied)
                need(reply['code'] == 'unsupported-operation', 'export grant cannot extend expired Agent Session')
                need(unmanaged.read_bytes() == b'independent bytes must remain unchanged', 'unmanaged neighboring bytes preserved')
                process.stdin.close()
                code = process.wait(timeout=120)
                need(code == 0, 'actual stdio process terminal exit zero')
                observations.insert(0, {'challenge': challenge, 'proof': proof, 'authentication_reply': auth, 'public_policy': policy, 'actual_stdio': True})
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait()
                for stream in (process.stdout, process.stderr):
                    stream.close()
        need(not root.exists(), 'actual newly owned workspace and key removed')
        view.custody_signed_sources.guard()
    need(period.read_bytes() == original_period, 'expired original Assignment period preserved byte for byte')
    guard()
    need(True, 'complete frozen audit source unchanged after actual effects')
    out = RUN / 'public-file-export-independent-observations-0001.json'
    put(out, {'schema_version': 'lab-public-file-export-independent-observation/v1-candidate', 'result': 'PASS', 'checks': len(checks), 'check_names': checks, 'source_binding': bind(SOURCE), 'observations': observations, 'owned_output_roots_removed': roots, 'current_Agent_qualified': False, 'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False, 'goal_complete': False, 'observed_at': datetime.now(timezone.utc).isoformat()})
    print(json.dumps({'result': 'PASS', 'checks': len(checks), 'observation_binding': bind(out)}), flush=True)

if __name__ == '__main__':
    main()
