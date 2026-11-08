"""Cold privacy check of the selected public API42 Session observation."""

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import types

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
OLD = ROOT / 'implementation/lab-runtime/local-host/t20-local-privacy-0001/scan.py'
SESSION = ROOT / 'implementation/lab-runtime/local-host/t22-native-source8-successor-0004'
RECEIPT = SESSION / 'LIVE-SESSION-0002.json'
VERIFIER = SESSION / 'verify_live_v2.py'
PINS = {
    OLD: '8d01bcb71ade520f9fc8a168e4708bf3509a1a4cbdba1424ade2eddd0296e76b',
    RECEIPT: 'ff8a148e377df505d0d24f67d3f3348e174401c9ba2f2814a4bd032116edd645',
    VERIFIER: '4b6d996d0c29dc558e7a3e7976f484a67fb9eb6be34240fcfd32a90176305fb6',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def selected(path):
    need(path.is_file() and not path.is_symlink(), 'selected public file unavailable')
    raw = path.read_bytes()
    need(sha(raw) == PINS[path], 'selected public file changed')
    return raw


def scanner_from_selected_bytes(raw):
    scanner = types.ModuleType('_cal_t20_selected_public_scanner')
    scanner.__file__ = str(OLD)
    exec(compile(raw, str(OLD), 'exec', dont_inherit=True), scanner.__dict__)
    return scanner


def assess(raw, scanner):
    value = scanner.strict_json(raw)
    need(value['schema_version'] == 'lab-T22-native-session-inspection/v2'
         and value['status'] == 'PASS-native-Session-consumption'
         and value['authority_effect'] == 'none'
         and value['original_t22_complete'] is False,
         'selected public Session claim differs')
    scanner.scan_json(value)
    def check_extended(item):
        if isinstance(item, dict):
            for key, child in item.items():
                normalized = re.sub(r'[^a-z0-9]', '', str(key).lower())
                sensitive = (any(fragment in normalized for fragment in (
                    'privatekey', 'secret', 'credential', 'password', 'apikey',
                    'accesstoken', 'refreshtoken', 'bearertoken', 'signingkey',
                    'keymaterial', 'cookie'))
                    or normalized in ('token', 'authtoken', 'authorization')
                    or normalized.endswith('authorization'))
                empty = (child is None or child is False or child == '' or child == [] or child == {})
                need(not sensitive or empty, 'extended credential field populated')
                check_extended(child)
        elif isinstance(item, list):
            for child in item:
                check_extended(child)
        elif isinstance(item, str):
            need(re.search(r'\b(?:Bearer|Basic|Token)\s+\S+', item, re.I) is None,
                 'credential scheme in public Session observation')
    check_extended(value)
    need(not scanner.PRIVATE_BLOCK.search(raw), 'private key block in public Session observation')
    need(not scanner.PRIVATE_LOCATOR.search(raw), 'private runtime locator in public Session observation')
    need(len(value['api_call_observations']) == 4 and value['session_closed'] is True
         and value['memory_zeroed'] is True,
         'selected Session output boundary differs')
    return {'api_replies_checked': 4, 'public_receipt_bytes_checked': len(raw),
            'credential_fields_populated': 0, 'credential_schemes': 0,
            'private_key_blocks': 0,
            'private_runtime_locators': 0}


def run():
    scanner = scanner_from_selected_bytes(selected(OLD))
    raw = selected(RECEIPT)
    counts = assess(raw, scanner)
    verifier_raw = selected(VERIFIER)
    captured_entry = (
        "import sys\n"
        "sys.path.insert(0,sys.argv[1])\n"
        "sys.argv=[sys.argv[2],'--receipt-sha256',sys.argv[3]]\n"
        "source=sys.stdin.buffer.read()\n"
        "scope={'__name__':'__main__','__file__':sys.argv[0]}\n"
        "exec(compile(source,sys.argv[0],'exec'),scope)\n"
    )
    checked = subprocess.run(
        [sys.executable, '-I', '-B', '-c', captured_entry,
         str(SESSION), str(VERIFIER), PINS[RECEIPT]],
        cwd=ROOT, input=verifier_raw, capture_output=True, timeout=60, check=False,
        env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'PYTHONDONTWRITEBYTECODE': '1'})
    need(checked.returncode == 0, 'selected Session cold verification refused')
    replay = scanner.strict_json(checked.stdout)
    need(replay['status'] == 'PASS-cold-public-output-replay'
         and replay['receipt_sha256'] == PINS[RECEIPT]
         and replay['api_operations'] == ['context.get', 'session.open', 'session.inspect', 'session.close'],
         'Session cold verifier result differs')
    result = {'schema_version': 'lab-T20-API42-live-session-public-privacy/v3',
              'status': 'PASS-BOUNDED', 'selected_session_sha256': PINS[RECEIPT],
              'selected_verifier_sha256': PINS[VERIFIER],
              'selected_scanner_sha256': PINS[OLD], 'counts': counts,
              'cold_replay': replay['status'],
              'cold_verifier_entry_captured': True,
              'cold_verifier_imported_helper_origin_qualified': False,
              'authority_effect': 'none',
              'final_family_privacy_qualified': False,
              'claim_ceiling': 'Exact retained public API42 Session observation under named credential patterns only; verifier entrypoint captured but imported helpers host-loaded; transient private controls, encoded secrets, protected source and final shared runtime remain untested.'}
    HERE.mkdir(mode=0o700, exist_ok=True)
    output = HERE / 'RESULT-0003.json'
    raw_result = (json.dumps(result, sort_keys=True, indent=2) + '\n').encode()
    if output.exists():
        need(output.read_bytes() == raw_result, 'retained T20 result changed')
    else:
        output.write_bytes(raw_result)
    print(json.dumps({'status': result['status'], **counts}, sort_keys=True))
    return result


if __name__ == '__main__':
    run()
