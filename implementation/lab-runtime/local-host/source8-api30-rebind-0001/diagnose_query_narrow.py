"""One-operation API33 diagnostic with narrow in-memory exception wrappers."""
from __future__ import annotations

from datetime import datetime, timezone
import importlib
import json
from pathlib import Path
import time
import traceback
from unittest.mock import patch

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

    catalog = importlib.import_module(package + '.source8_catalog')
    handlers = importlib.import_module(package + '.handlers')
    selected = catalog.selection
    original_query = handlers.ReadHandlers.query
    safe_messages = {
        'local declaration requires independently selected Source8',
        'fixture current native declaration differs from original exact bytes',
        'declaration outside selected signed source',
        'current declaration body differs',
        'signed declaration instance schema differs',
    }

    def record(stage, error):
        frames = traceback.extract_tb(error.__traceback__)
        row = {'stage': stage, 'type': type(error).__name__,
               'code_locations': [{'module': Path(frame.filename).name, 'line': frame.lineno}
                                  for frame in frames if Path(frame.filename).parent == OUTPUT]}
        if str(error) in safe_messages:
            row['static_predicate'] = str(error)
        result['exceptions'].append(row)

    def selection_probe(view, subject):
        try:
            return selected(view, subject)
        except Exception as error:
            record('source8_catalog.selection', error)
            raise

    def query_probe(self, message, request_binding, outer):
        try:
            return original_query(self, message, request_binding, outer)
        except Exception as error:
            record('ReadHandlers.query', error)
            raise

    try:
        phase('setUpClass', cls.setUpClass)
        phase('setUp', case.setUp)
        call = module.call(case.channel.context, 'artifact.query', module.cut(case.view))
        raw = module.compact(call)
        before = time.monotonic()
        with patch.object(catalog, 'selection', selection_probe), patch.object(
                handlers.ReadHandlers, 'query', query_probe):
            reply = case.service.call(raw)
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
        out = script.parent / 'working' / 'diagnose-query-narrow-result.json'
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        print('RESULT', result['result'], 'exceptions', len(result['exceptions']), flush=True)
    return result


if __name__ == '__main__':
    raise SystemExit(0 if main()['result'] == 'PASS' else 1)
