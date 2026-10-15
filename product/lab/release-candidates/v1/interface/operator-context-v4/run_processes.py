"""Actual independent cold source processes and exact metadata parity."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(HERE))
from source_adapter import verify_package


def binding(path): return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def guard(package_pin, controller_pin):
    verify_package(package_pin)
    raw = (HERE / 'process-source-manifest.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != controller_pin: raise ValueError('independently selected controller differs')
    for b in json.loads(raw)['files']:
        if binding(ROOT / b['path']) != b: raise ValueError('frozen process source differs')


def main(package_pin, controller_pin):
    guard(package_pin, controller_pin)
    out = HERE / 'receipts/processes/0001'
    if out.exists(): raise ValueError('process proof destination already exists')
    out.mkdir(parents=True);children = [];reports = [];checks = []
    for name, source in [('warm', 'reference-corrected'), ('cold', 'reference-corrected'), ('engineering', 'engineering')]:
        guard(package_pin, controller_pin)
        command = [sys.executable, '-B', str(HERE / 'observe_source.py'), '--source', source, '--package-sha256', package_pin]
        tick = time.monotonic()
        process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try: stdout, stderr = process.communicate(timeout=300)
        except subprocess.TimeoutExpired:
            process.kill();stdout, stderr = process.communicate()
        (out / (name + '.stdout')).write_bytes(stdout);(out / (name + '.stderr')).write_bytes(stderr)
        children.append({'name': name, 'pid': process.pid, 'exit_code': process.returncode,
            'duration_seconds': time.monotonic() - tick, 'source': source, 'command': command,
            'stdout_binding': binding(out / (name + '.stdout')), 'stderr_binding': binding(out / (name + '.stderr'))})
        (out / 'children.json').write_text(json.dumps(children, indent=2) + '\n')
        if process.returncode != 0: raise ValueError('actual signed source child failed: ' + name)
        value = json.loads(stdout)
        if value['source_name'] != source or value['authority_effect'] != 'none' or value['actual_owner_outcome'] is not None:
            raise ValueError('source metadata posture differs')
        if value['fresh_Session_participation_established'] or value['native_domain_mapping_supplied'] or value['context_or_ontology_views_generated']:
            raise ValueError('reader inferred unperformed operational integration')
        reports.append(value);checks.append({'test': name + ' actual terminal signed source read and explicit scope', 'result': 'PASS'})
        print(json.dumps({'process': name, 'exit_code': process.returncode, 'duration_seconds': children[-1]['duration_seconds'], 'result': 'PASS'}), flush=True)
    if reports[0] != reports[1]: raise ValueError('independent cold same-cut metadata differs')
    if reports[0]['source_cut'] == reports[2]['source_cut']: raise ValueError('different signed branch cuts were collapsed')
    checks += [{'test': 'independent same-cut cold metadata byte parity', 'result': 'PASS'},
        {'test': 'engineering branch and corrected branch cuts remain distinct', 'result': 'PASS'}]
    guard(package_pin, controller_pin)
    result = {'schema_version': 'lab-same-cut-real-process-proof/v1-candidate', 'result': 'PASS',
        'children': children, 'checks': checks, 'actual_terminal_processes': 3,
        'same_cut_cold_metadata_parity': True, 'distinct_branch_cuts_preserved': True,
        'package_manifest_sha256': package_pin, 'controller_manifest_sha256': controller_pin,
        'authority_effect': 'none', 'actual_owner_outcome': None, 'active_Agents_created': 0,
        'public_API_operations_added': 0, 'recorded_at': datetime.now(timezone.utc).isoformat()}
    (out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser();p.add_argument('--package-sha256', required=True)
    p.add_argument('--controller-sha256', required=True);a = p.parse_args();main(a.package_sha256, a.controller_sha256)
