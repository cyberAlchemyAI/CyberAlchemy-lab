"""One-operation API33 diagnostic; records only exception class and code location."""
from __future__ import annotations

from datetime import datetime, timezone
import importlib
import json
from pathlib import Path
import sys
import time

from run_successor import OUTPUT, digest, package_at


def stamp():
    return datetime.now(timezone.utc).isoformat()


def main():
    script = Path(__file__).resolve()
    script_sha = digest(script)
    package = package_at(OUTPUT)
    module = importlib.import_module(package + '.test_custody_sessions')
    module.PROFILE = digest(OUTPUT / 'contract-profile.json')
    cls = module.Sessions
    case = cls('test_00_all_eleven_actual_operations')
    result = {'started_at_utc': stamp(), 'script_sha256': script_sha,
              'successor_manifest_sha256': digest(OUTPUT / 'source-manifest.json'),
              'phases': [], 'exceptions': [], 'result': 'FAIL'}

    def phase(name, action):
        began = time.monotonic()
        started = stamp()
        try:
            return action()
        finally:
            row = {'name': name, 'started_at_utc': started,
                   'completed_at_utc': stamp(),
                   'monotonic_elapsed_seconds': round(time.monotonic() - began, 3)}
            result['phases'].append(row)
            print('PHASE', name, row['monotonic_elapsed_seconds'], flush=True)

    def trace(frame, event, arg):
        if event != 'call':
            return None
        filename = Path(frame.f_code.co_filename)
        if filename.parent != OUTPUT or filename.name not in {
                'service.py', 'handlers.py', 'guarded_reads.py',
                'artifact_model.py', 'integrated_guard.py'}:
            return None
        def local(inner, kind, payload):
            if kind == 'exception' and len(result['exceptions']) < 100:
                typ, _, tb = payload
                result['exceptions'].append({
                    'type': typ.__name__, 'module': filename.name,
                    'function': frame.f_code.co_name, 'line': inner.f_lineno,
                    'origin_module': Path(tb.tb_frame.f_code.co_filename).name,
                    'origin_line': tb.tb_lineno})
            return local
        return local

    try:
        phase('setUpClass', cls.setUpClass)
        phase('setUp', case.setUp)
        call = module.call(case.channel.context, 'artifact.query', module.cut(case.view))
        raw = module.compact(call)
        before = time.monotonic()
        sys.settrace(trace)
        try:
            reply = case.service.call(raw)
        finally:
            sys.settrace(None)
        result['phases'].append({'name': 'artifact.query', 'completed_at_utc': stamp(),
                                 'monotonic_elapsed_seconds': round(time.monotonic() - before, 3)})
        result['reply_kind'] = reply.get('kind')
        result['reply_code'] = reply.get('message', {}).get('code')
        result['result'] = 'PASS' if reply.get('kind') == 'result' else 'FAIL'
    finally:
        try:
            if hasattr(case, 'service'):
                case.tearDown()
            case.doCleanups()
        finally:
            cls.doClassCleanups()
        result['completed_at_utc'] = stamp()
        result['script_unchanged_during_run'] = digest(script) == script_sha
        out = script.parent / 'working' / 'diagnose-query-result.json'
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        print('RESULT', result['result'], 'exceptions', len(result['exceptions']), flush=True)
    return result


if __name__ == '__main__':
    raise SystemExit(0 if main()['result'] == 'PASS' else 1)
