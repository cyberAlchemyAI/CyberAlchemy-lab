"""Two actual stdio processes: live refresh, disposal and cold recorded retry."""
import argparse
import base64
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[5]; API = HERE.parent / 'api-v16'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p, value):
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as f: f.write((json.dumps(value, indent=2, sort_keys=True) + '\n').encode())
def main():
    parser = argparse.ArgumentParser()
    for name in ['source-sha256', 'profile-sha256', 'producer-sha256']: parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    assert sha(HERE / 'source-manifest.json') == args.producer_sha256
    for row in json.loads((HERE / 'source-manifest.json').read_bytes())['files']: assert sha(ROOT / row['path']) == row['sha256']
    assert sha(API / 'source-manifest.json') == args.source_sha256
    for row in json.loads((API / 'source-manifest.json').read_bytes())['files']: assert sha(ROOT / row['path']) == row['sha256']
    name = '_cal_api_v16'; spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module; spec.loader.exec_module(module)
    S = __import__(name + '.service', fromlist=['Service']); F = __import__(name + '.fixtures', fromlist=['provision']); P = __import__(name + '.projection_refresh', fromlist=['control'])
    schemas = S.Schemas(args.profile_sha256); output = HERE / 'receipts/0001'; output.mkdir(parents=True, exist_ok=False)
    frames, checks, observations, processes = [], [], [], []
    result = {'result': 'FAIL', 'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False}
    def check(value, reason):
        if not value: raise ValueError(reason)
        checks.append({'check': reason, 'result': 'PASS'})
    try:
        with tempfile.TemporaryDirectory(prefix='cal-R03-projection-process-') as temporary, S.source.replay_source('reference-corrected') as view:
            root = Path(temporary); root.chmod(0o700); grant = P.control(view)
            key, policy, pin = F.provision(root, 'reference-corrected', projection_control=grant)
            scratch = root / 'process-temp'; scratch.mkdir(mode=0o700)
            source_cut = S.cut(view); source_before = copy.deepcopy(view.data)
            command = [sys.executable, str(API / 'serve.py'), '--policy', str(policy), '--policy-sha256', pin, '--protocol-profile-sha256', args.profile_sha256]
            def start(label):
                stderr = (output / (label + '.stderr')).open('xb')
                env = dict(os.environ); env['TMPDIR'] = str(scratch)
                child = subprocess.Popen(command, cwd=ROOT, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr)
                processes.append((label, child, stderr))
                challenge_raw = child.stdout.readline(); check(bool(challenge_raw), label + ' emitted real challenge')
                challenge = S.source.parse(challenge_raw); check(schemas.valid('reader-authentication', challenge), label + ' challenge matches schema')
                proof = F.proof(key, challenge); child.stdin.write(proof + b'\n'); child.stdin.flush()
                auth_raw = child.stdout.readline(); auth = S.source.parse(auth_raw); check(schemas.valid('reader-authentication', auth) and auth['schema_version'] == 'lab-local-reader-authenticated/v1-candidate', label + ' authenticated actual nonce')
                frames.append({'process': label, 'challenge_base64': base64.b64encode(challenge_raw).decode(), 'proof_base64': base64.b64encode(proof).decode(), 'authenticated_base64': base64.b64encode(auth_raw).decode()})
                return child, auth['context']
            def invoke(label, child, context, call):
                call = copy.deepcopy(call); call['caller_context_ref'] = context['context_ref']; call['call_id'] = 'call:process:' + F.uuid.uuid4().hex
                raw = S.compact(call); child.stdin.write(raw + b'\n'); child.stdin.flush(); response_raw = child.stdout.readline()
                check(bool(response_raw), label + ' actual response exists'); response = S.source.parse(response_raw)
                check(schemas.valid('api-reply', response), label + ' exact original reply schema')
                check(response['contract_profile_binding'] == schemas.profile_binding and response['request_binding']['sha256'] == S.source.sha(raw), label + ' actual profile and outer byte binding')
                __import__(name + '.workspace', fromlist=['privacy']).privacy(response)
                frames.append({'process': label, 'original_call_base64': base64.b64encode(raw).decode(), 'original_reply_base64': base64.b64encode(response_raw).decode()})
                check(response['kind'] == 'result', label + ' operation returns actual result')
                return response['message']
            def stop(label, child):
                child.stdin.close(); code = child.wait(); observations.append({'process': label, 'pid': child.pid, 'exit_code': code, 'terminal_observed': True})
                check(code == 0, label + ' terminal exit zero')
                check(list(scratch.iterdir()) == [], label + ' EOF removed all owned replay and SQL temporary directories')
            first, context = start('live')
            status = invoke('live', first, context, F.call(context, 'lab.status', source_cut)); check(len(status['supported_operations']) == 12, 'selected live process lists all 12 actual handlers')
            opening = F.call(context, 'lab.status', source_cut); budget = opening['message']['budget']; budget['max_actions'] = 1
            opening.update(operation='projection.refresh', idempotency_key='refresh:process:original', message={
                'schema_version': 'lab-projection-refresh-request/v1-candidate', 'request_ref': 'request:process:refresh', 'source_cut': source_cut,
                'projector_binding': grant['projector_binding'], 'contract_catalog_binding': grant['contract_catalog_binding'],
                'expected_generation_binding': None, 'budget': budget, 'authority_effect': 'none'})
            ready = invoke('live', first, context, opening); check(ready['posture'] == 'ready', 'real live SQL generation ready')
            live_files = list(scratch.rglob('read-model.sqlite')); check(len(live_files) == 1, 'one real private SQLite generation materialized')
            check(live_files[0].stat().st_mode & 0o777 == 0o600, 'real SQL generation mode 600')
            retry = invoke('live', first, context, opening); check(retry == ready, 'live exact retry returns identical recorded result')
            query = F.call(context, 'artifact.query', source_cut, query_basis='projection'); rows = invoke('live', first, context, query)
            check(rows['projection_generation'] == ready['generation_binding'], 'actual query consumes exactly refreshed generation')
            stop('live', first)
            second, cold_context = start('cold')
            retry = invoke('cold', second, cold_context, opening); check(retry == ready, 'cold retry returns historical recorded result')
            check(list(scratch.rglob('read-model.sqlite')) == [], 'cold exact retry does not reconstruct vanished SQL generation')
            inspected = invoke('cold', second, cold_context, F.call(cold_context, 'operation.inspect', None, lookup={'operation': 'projection.refresh', 'idempotency_key': opening['idempotency_key']}))
            check(inspected['posture'] == 'completed', 'cold operation journal confirms historical completion')
            fresh = copy.deepcopy(opening); fresh['idempotency_key'] = 'refresh:process:new'; fresh['message']['request_ref'] += ':new'
            new = invoke('cold', second, cold_context, fresh); check(new['generation_binding'] != ready['generation_binding'], 'new authorized key creates independent fresh generation')
            check(len(list(scratch.rglob('read-model.sqlite'))) == 1, 'cold new request actually creates SQL file')
            canonical = invoke('cold', second, cold_context, F.call(cold_context, 'artifact.query', source_cut, query_basis='canonical'))
            projected = invoke('cold', second, cold_context, F.call(cold_context, 'artifact.query', source_cut, query_basis='projection'))
            check(canonical['results'] == projected['results'] and canonical['connections'] == projected['connections'], 'fresh real-process canonical and SQL query parity')
            check(projected['projection_generation'] == new['generation_binding'], 'cold query uses new generation only')
            stop('cold', second)
            check(view.data == source_before, 'original signed source replay unchanged')
        check(not Path(temporary).exists(), 'all owned policy key workspace and SQL roots removed')
        result.update(result='PASS', checks=checks, observed_processes=observations, wire_frames=sum('original_call_base64' in f for f in frames),
                      private_keys_exported=False, private_memory_exported=False, owned_roots_removed=True, new_sql_generations=2,
                      canonical_effects_applied=0, selected_profile_sha256=args.profile_sha256)
    except BaseException as error:
        result['failure'] = str(error); result['checks'] = checks; result['observed_processes'] = observations
    finally:
        for label, child, stderr in processes:
            if child.poll() is None: child.kill(); child.wait()
            stderr.close()
    emit(output / 'wire-transcripts.json', frames); emit(output / 'result.json', result)
    print(json.dumps({'result': result['result'], 'checks': len(checks), 'processes': len(observations), 'failure': result.get('failure')}), flush=True)
    return 0 if result['result'] == 'PASS' else 1
if __name__ == '__main__': raise SystemExit(main())
