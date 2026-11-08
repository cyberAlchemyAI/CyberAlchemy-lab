"""Seal or cold-check the exact local T22 Source→Context construction chain."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat

import verify_work as work_check


ROOT = work_check.ROOT
HERE = Path(__file__).resolve().parent
FAMILY = work_check.FAMILY
PHASE = {
    'source': '9482057361c19b998902822052e6e9de79dc0f8ce761b086364f4d7fbac7f43c',
    'cold': 'a162aab2db2fd106b9108afcafcf1309990f4a2c52643dc7bb7b3ed95bdc2419',
    'reader': 'dfb8953710ba99b248fce96f61abddeeef380f10489a79daffc22a9281083265',
    'mapped': 'c5fd8199aadbc007d1618f1375dc2604fd7b1bc49bbd26b900d2cc4a4dcb4de7',
    'context': 'afe00f57ff3a22f90ca4c7d8068c55cca723b1b824b5669ef7e257e6520d22f2',
}
MAPPING = FAMILY + '/mapped/packages/0001/mapping.json'
MAPPING_SHA = '2a5179b97aacf9e6e87d2ee6c41d1692a5f9806511203d53c0d7db96e3598539'
DELIVERY = FAMILY + '/context/packages/0001/delivery.json'
DELIVERY_SHA = '58b754b8023a60f71d1d46c353edc3b8582973b91db4caef5051bbbfc79cf5b2'
PERIOD = FAMILY + '/source/packages/0001/period.json'
PERIOD_SHA = '3583bec60a5b82f62bbfa3f8420b824315f449d5aa61d2faec18c33a81cde534'
RESULT = HERE / 'CHAIN-0001.json'


def binding(path, pin): return {'path': path, 'sha256': pin}


def assess(phases, mapping, delivery, period, work):
    source, cold, reader, mapped, context = (phases[name] for name in PHASE)
    if cold['result'] != 'PASS-native-cold' or cold['independent_cold_replays'] != 2 or cold['original_byte_parity'] is not True:
        raise ValueError('native Source cold replay not proved')
    if (reader['result'] != 'PASS-current-reader' or reader['wrong_independent_pin_refusals'] != 3 or
            mapped['result'] != 'PASS-native-mapper' or context['result'] != 'PASS-native-Context-construction'):
        raise ValueError('native role chain phase refused')
    if source['source_binding'] != cold['source_binding'] or source['package_binding'] != cold['package_binding']:
        raise ValueError('cold Source does not match built Source')
    for row in (source['source_binding'], source['package_binding'], cold['period_binding'], reader['reader_binding'],
                mapped['mapper_binding'], mapped['package_binding'], context['context_binding'],
                context['package_binding'], context['implementation_binding']):
        work_check.read(row['path'], row['sha256'])
    if cold['period_binding'] != binding(PERIOD, PERIOD_SHA): raise ValueError('signed Source period differs')
    if len(mapping['rows']) != 25 or len(delivery['included_refs']) != 25:
        raise ValueError('mapped/Context closure count differs')
    selected = [row for row in delivery['included_refs'] if row['carrier_ref'] == 'cal.artifact-type.work/v1']
    if len(selected) != 1 or selected[0]['byte_sha256'] != work_check.WORK_SHA:
        raise ValueError('Context delivery omits selected API30 Work')
    if mapping['source_cut'] != delivery['source_cut'] or mapping['source_cut']['store_ref'] != 'completion-legacy-local-710362c855a8a11c':
        raise ValueError('Context/native source cut differs')
    if mapping['source_cut']['branch_ref'] != 'branch:completion-legacy-local-710362c855a8a11c':
        raise ValueError('Context branch identity differs')
    if (delivery['posture'] != 'ready' or delivery['scope_enforced'] is not True or
            period['not_before'] != '2026-10-23T04:52:49.044239+00:00' or
            period['expires_at'] != '2026-10-24T04:52:49.044239+00:00'):
        raise ValueError('Context posture or signed Source period differs')
    if work['status'] != 'PASS-exact-built-Work' or work['native_session_consumed'] is not False:
        raise ValueError('selected API30 Work assertion differs')
    return {'schema_version': 'lab-T22-native-family-chain/v1', 'status': 'PASS-native-family-construction',
            'family': FAMILY, 'source_name': 'completion-legacy:legacy-local-710362c855a8a11c',
            'source_period_binding': binding(PERIOD, PERIOD_SHA),
            'source_period_end': period['expires_at'],
            'phase_result_bindings': [binding(FAMILY + '/' + name + '-result.json', pin) for name, pin in PHASE.items()],
            'mapping_binding': binding(MAPPING, MAPPING_SHA), 'construction_delivery_binding': binding(DELIVERY, DELIVERY_SHA),
            'selected_work_binding': binding(work_check.WORK, work_check.WORK_SHA),
            'selected_work_in_delivery': True, 'mapped_subjects': 25, 'generated_context_carriers': 30,
            'cold_replays': 2, 'original_byte_parity': True, 'native_session_consumed': False,
            'api42_rebind_qualified': False, 'original_t22_complete': False, 'contest_outcome': None,
            'lesson_outcome': None, 'authority_effect': 'none'}


def calculate():
    phases = {name: json.loads(work_check.read(FAMILY + '/' + name + '-result.json', pin)) for name, pin in PHASE.items()}
    mapping = json.loads(work_check.read(MAPPING, MAPPING_SHA))
    delivery = json.loads(work_check.read(DELIVERY, DELIVERY_SHA))
    period = json.loads(work_check.read(PERIOD, PERIOD_SHA))
    return assess(phases, mapping, delivery, period, work_check.verify())


def canonical(value): return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--write', action='store_true'); parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.write == args.verify: raise ValueError('choose exactly one mode')
    raw = canonical(calculate())
    if args.write:
        fd = os.open(RESULT, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    else:
        if work_check.read(RESULT.relative_to(ROOT).as_posix(), hashlib.sha256(raw).hexdigest()) != raw:
            raise ValueError('sealed chain receipt changed')
    print(json.dumps({'status': 'PASS', 'sha256': hashlib.sha256(raw).hexdigest()}, sort_keys=True))


if __name__ == '__main__': main()
