"""Locate the first public subject rejected by the selected native artifact adapter."""
from __future__ import annotations

from datetime import datetime, timezone
import importlib
import json
from pathlib import Path
import time
import traceback

from run_successor import OUTPUT, digest, package_at


def stamp():
    return datetime.now(timezone.utc).isoformat()


def main():
    script = Path(__file__).resolve()
    script_sha = digest(script)
    package = package_at(OUTPUT)
    fixture = importlib.import_module(package + '.test_custody_sessions')
    started = time.monotonic()
    result = {'started_at_utc': stamp(), 'script_sha256': script_sha,
              'successor_manifest_sha256': digest(OUTPUT / 'source-manifest.json'),
              'result': 'FAIL', 'eligible_count': 0, 'native_adapter_count': 0}
    try:
        with fixture.source.replay_source(fixture.PUBLIC_SOURCE_NAME) as view:
            print('PHASE source replay', round(time.monotonic() - started, 3), flush=True)
            reader = fixture.source.reader_for_view(view)
            model = reader.adapter.model
            result['selected_model_module'] = Path(model.__file__).name
            for _, subject in sorted(view.subjects.items()):
                if subject['effective_state'] not in ('admitted-current', 'admitted-historical',
                                                      'local-admitted-current', 'local-admitted-historical'):
                    continue
                result['eligible_count'] += 1
                if view.selected['name'] != 'custody-participation' or subject['category'] in ('artifact-type', 'relation-kind', 'definition'):
                    continue
                result['native_adapter_count'] += 1
                try:
                    model.artifact_ref(view, subject)
                except Exception as error:
                    result['failure'] = {
                        'type': type(error).__name__,
                        'static_predicate': str(error) if str(error) in
                            {'unknown source content encoding', 'captured carrier unavailable'} else None,
                        'category': subject['category'],
                        'version_ref': subject['version_ref'],
                        'carrier_ref': subject['carrier_ref'],
                        'source_encoding': subject['source'].get('encoding'),
                        'carrier_in_projection_contracts': subject['carrier_ref'] in view.data['projection']['contracts'],
                        'native_encoding': getattr(view.handle.custody, 'ENCODING', None),
                        'code_locations': [{'module': Path(row.filename).name, 'line': row.lineno}
                                           for row in traceback.extract_tb(error.__traceback__)],
                    }
                    break
            else:
                result['result'] = 'PASS'
    finally:
        result['completed_at_utc'] = stamp()
        result['monotonic_elapsed_seconds'] = round(time.monotonic() - started, 3)
        result['script_unchanged_during_run'] = digest(script) == script_sha
        out = script.parent / 'working' / 'diagnose-model-ref-result.json'
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        print('RESULT', result['result'], result.get('failure', {}).get('static_predicate'), flush=True)
    return result


if __name__ == '__main__':
    raise SystemExit(0 if main()['result'] == 'PASS' else 1)
