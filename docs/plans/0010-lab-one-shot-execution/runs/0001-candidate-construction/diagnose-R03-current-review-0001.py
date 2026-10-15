"""Observe one actual review attempt; passive trace, no uncertain redispatch."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v32'
SOURCE = RUN / 'current-review-diagnostic-source-0001.json'

def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

def put(path, value):
    assert not path.exists()
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')
    path.chmod(0o600)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    assert bind(SOURCE)['sha256'] == args.source_sha256
    selected = json.loads(SOURCE.read_bytes())
    def guard():
        for row in selected['files']:
            assert bind(ROOT / row['path']) == row, row['path']
    guard()
    name = '_cal_current_review_diagnostic'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    P = __import__(name + '.protocol', fromlist=['*'])
    F = __import__(name + '.review_fixture', fromlist=['*'])
    H = __import__(name + '.handlers', fromlist=['*'])
    W = __import__(name + '.workspace', fromlist=['*'])
    fixtures = __import__(name + '.fixtures', fromlist=['*'])
    schemas = P.Schemas(bind(API / 'contract-profile.json')['sha256'])
    observed, wire = [], []
    targets = {str(API / n) for n in ['service.py', 'review_preparation.py']}
    # Only frozen literal refusal reasons may be emitted, never exception values
    # containing caller material, keys, RAM or arbitrary source bodies.
    literals = {node.value for n in ['service.py', 'review_preparation.py']
                for node in ast.walk(ast.parse((API / n).read_bytes()))
                if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    def trace(frame, event, arg):
        if frame.f_code.co_filename not in targets:
            return None
        if event == 'exception':
            kind, error, _ = arg
            row = {'function': frame.f_code.co_name, 'line': frame.f_lineno,
                   'source_path': str(Path(frame.f_code.co_filename).relative_to(ROOT)),
                   'exception_class': kind.__name__}
            if len(error.args) == 1 and isinstance(error.args[0], str) and error.args[0] in literals:
                row['frozen_literal_reason'] = error.args[0]
            observed.append(row)
        return trace
    with P.source.replay_source('custody-participation') as view:
        with F.example(view, schemas) as (service, request, witness):
            call = request()
            raw = P.compact(call)
            previous = sys.gettrace()
            assert previous is None
            try:
                sys.settrace(trace)
                reply = service.call(raw)
            finally:
                sys.settrace(previous)
            W.privacy(reply)
            wire.append({'call': call, 'reply': reply})
            put(RUN / 'current-review-diagnostic-wire-0001.json',
                {'observations': wire, 'trace': observed, 'source_binding': bind(SOURCE),
                 'authority_effect': 'none', 'actual_owner_outcome': None})
            # Inspection observes the durable namespace. It never calls build
            # again and never attempts reconciliation or effect replay.
            inspect = fixtures.call(service.channel.context, 'operation.inspect', H.cut(view))
            inspect['message']['lookup'] = {'operation': 'proposal.review', 'idempotency_key': 'fixture:review'}
            inspected = service.call(P.compact(inspect))
            W.privacy(inspected)
            wire.append({'call': inspect, 'reply': inspected})
            result = {'schema_version': 'lab-review-diagnostic-observation/v1-candidate',
                      'result': 'OBSERVED', 'review_reply_kind': reply.get('kind'),
                      'review_error_code': reply.get('message', {}).get('code'),
                      'trace': observed, 'source_binding': bind(SOURCE),
                      'uncertain_operation_redispatched': False,
                      'authority_effect': 'none', 'actual_owner_outcome': None,
                      'whole_API_qualified': False, 'task_complete': False}
        guard()
    put(RUN / 'current-review-diagnostic-0001.json', result)
    put(RUN / 'current-review-diagnostic-complete-wire-0001.json',
        {'observations': wire, 'authority_effect': 'none', 'actual_owner_outcome': None})
    print(json.dumps({'result': 'OBSERVED', 'review_reply_kind': result['review_reply_kind'],
                      'review_error_code': result['review_error_code'], 'trace': observed}), flush=True)

if __name__ == '__main__':
    main()
