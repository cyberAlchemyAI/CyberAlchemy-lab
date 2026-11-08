"""Cold-seal the exact technical Source8 Agent-contest construction chain."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path(__file__).absolute().parents[4]
HERE = Path(__file__).absolute().parent
FAMILY = ('implementation/lab-runtime/local-host/source8-current-fixture/'
          'instances/legacy-local-d3537e8c3cb77a71')
PINS = {
    'source': 'a5b83bf399f233c48896d9509c32dd7c59db877ba5736b580e3810739a5e2bea',
    'cold': '162de4acfa283ff460885ccbff6d1b440be2c67f765ef8b5504d8c9971b900be',
    'reader': '49aefcbf9b52ca7d24e0a4827cca400cabb41084ca67f65089e4ac9ceaf25b02',
    'mapped': 'b1a5c4536b4d2264f16617c823e0090f6f7290aaae7458e8d3b0f017a816f07b',
    'context': 'dc567b9025613502c0b58b2f6f7105d0f61c50dcc52e99ca641b4f8a18c4524e',
}
MAPPING = 'ef4803d75eedf7f9289642833b2e852daa034754df66c9a967da7b7a0aad97ec'
DELIVERY = 'ad877497abd7919b0e655bdbed39c23c58b2c674a3c061430b1cbe7d6b0a9d69'
PERIOD = '08666a08b68287efa34818c80b619308f75fa6e595b991771d0a6c5aaf65bb1d'
WORK = 'a2c312abba8f824f986cbe906fc0a5ef99c09259658bef7424b15dd8986a6bbf'
CONTRACT = 'e739fdd30a6a8732cb709b139579b133f5fbb24e62bfaadf3ea7848e384e43fb'
INDEX = 'ac1b6dfa244e30e745b3c15b8e643926e579c29266e3e8bc7708f6848fbf567f'
RESULT = HERE / 'CHAIN-0001.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(relative, digest):
    path = Path(relative)
    if (not relative or path.is_absolute() or '..' in path.parts
            or path.as_posix() != relative):
        raise ValueError('selected path is not canonical')
    directory = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in ROOT.parts[1:] + path.parts[:-1]:
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                            dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise ValueError('selected input is not regular')
            with os.fdopen(fd, 'rb', closefd=False) as stream:
                raw = stream.read()
        finally:
            os.close(fd)
    except OSError as error:
        raise ValueError('selected path missing or linked') from error
    finally:
        os.close(directory)
    if sha(raw) != digest:
        raise ValueError('selected bytes changed')
    return raw


def binding(path, digest):
    return {'path': path, 'sha256': digest}


def selected(row):
    if type(row) is not dict or set(row) != {'path', 'sha256'}:
        raise ValueError('selected binding shape differs')
    return read(row['path'], row['sha256'])


def manifest_rows(row):
    manifest = json.loads(selected(row))
    files = manifest['files']
    if type(files) is not list or len(files) != len({f['path'] for f in files}):
        raise ValueError('selected manifest rows missing or duplicated')
    for file in files:
        selected(file)
    return len(files)


def assess(phases, mapping, delivery, period, index):
    source, cold, reader, mapped, context = (phases[n] for n in PINS)
    if (cold['result'] != 'PASS-native-cold' or cold['independent_cold_replays'] != 2
            or cold['original_byte_parity'] is not True
            or cold['source_binding'] != source['source_binding']
            or cold['package_binding'] != source['package_binding']):
        raise ValueError('signed Source/cold join differs')
    if (reader['result'] != 'PASS-current-reader'
            or reader['wrong_independent_pin_refusals'] != 3
            or mapped['result'] != 'PASS-native-mapper'
            or context['result'] != 'PASS-native-Context-construction'):
        raise ValueError('native phase result differs')
    for row in (source['source_binding'], source['package_binding'], cold['period_binding'],
                reader['reader_binding'], mapped['mapper_binding'], mapped['package_binding'],
                context['context_binding'], context['package_binding'], context['implementation_binding']):
        selected(row)
    if cold['period_binding'] != binding(FAMILY + '/source/packages/0001/period.json', PERIOD):
        raise ValueError('selected Source period differs')
    if (mapping['source_package_binding'] != source['package_binding']
            or mapping['source_cut'] != delivery['source_cut']
            or mapping['source_cut']['store_ref'] != 'completion-legacy-local-d3537e8c3cb77a71'
            or mapping['source_cut']['branch_ref'] != 'branch:completion-legacy-local-d3537e8c3cb77a71'):
        raise ValueError('native Source cut differs')
    if (len(mapping['rows']) != 25 or len(delivery['included_refs']) != 25
            or delivery['posture'] != 'ready' or delivery['scope_enforced'] is not True):
        raise ValueError('Context delivery closure differs')
    work = [r for r in delivery['included_refs'] if r['carrier_ref'] == 'cal.artifact-type.work/v1']
    if len(work) != 1 or work[0]['byte_sha256'] != WORK:
        raise ValueError('exact Work absent from Context delivery')
    if type(index) is not list or len(index) != 22:
        raise ValueError('signed original record index differs')
    selected_originals = {}
    for kind, digest in (('work', WORK), ('challenge-contract', CONTRACT)):
        rows = [row for row in index if row['kind'] == kind]
        if len(rows) != 1 or rows[0]['original_binding']['sha256'] != digest:
            raise ValueError('selected Work or Contract original differs')
        selected(rows[0]['original_binding'])
        selected_originals[kind] = rows[0]['original_binding']
    if (period['not_before'] != '2026-10-23T17:54:44.262511+00:00'
            or period['expires_at'] != '2026-10-24T17:54:44.262511+00:00'
            or period['authority_effect'] != 'none'):
        raise ValueError('signed Source period differs')
    return {
        'schema_version': 'lab-T22-agent-contest-native-chain/v2-fixture',
        'status': 'PASS-native-family-construction', 'family': FAMILY,
        'source_name': 'completion-legacy:legacy-local-d3537e8c3cb77a71',
        'phase_result_bindings': [binding(FAMILY + '/' + name + '-result.json', pin)
                                  for name, pin in PINS.items()],
        'source_period_binding': cold['period_binding'],
        'source_period_end': period['expires_at'],
        'mapping_binding': binding(FAMILY + '/mapped/packages/0001/mapping.json', MAPPING),
        'construction_delivery_binding': binding(FAMILY + '/context/packages/0001/delivery.json', DELIVERY),
        'source_record_index_binding': binding(FAMILY + '/source/packages/0001/record-index.json', INDEX),
        'selected_work_binding': selected_originals['work'],
        'selected_contract_binding': selected_originals['challenge-contract'],
        'source_cut': mapping['source_cut'],
        'mapped_subjects': 25, 'generated_context_carriers': 30,
        'cold_replays': 2, 'original_byte_parity': True,
        'live_agent_session_consumed': False, 'challenge_submitted': False,
        'challenge_resolved': False, 'contest_outcome': None,
        'owner_decision': None, 'public_API_qualified': False,
        'authority_effect': 'none',
    }


def calculate():
    phases = {name: json.loads(read(FAMILY + '/' + name + '-result.json', pin))
              for name, pin in PINS.items()}
    mapping = json.loads(read(FAMILY + '/mapped/packages/0001/mapping.json', MAPPING))
    delivery = json.loads(read(FAMILY + '/context/packages/0001/delivery.json', DELIVERY))
    period = json.loads(read(FAMILY + '/source/packages/0001/period.json', PERIOD))
    index = json.loads(read(FAMILY + '/source/packages/0001/record-index.json', INDEX))
    result = assess(phases, mapping, delivery, period, index)
    for name, row in (('source', phases['source']['source_binding']),
                      ('reader', phases['reader']['reader_binding']),
                      ('mapped', phases['mapped']['mapper_binding']),
                      ('context', phases['context']['context_binding'])):
        result[name + '_selected_file_count'] = manifest_rows(row)
    for name, row in (('source', phases['source']['package_binding']),
                      ('mapped', phases['mapped']['package_binding']),
                      ('context', phases['context']['package_binding'])):
        result[name + '_package_file_count'] = manifest_rows(row)
    return result


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.write == args.verify:
        raise ValueError('choose write or verify')
    raw = canonical(calculate())
    if args.write:
        fd = os.open(RESULT, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    elif read(RESULT.relative_to(ROOT).as_posix(), sha(raw)) != raw:
        raise ValueError('chain receipt changed')
    print(json.dumps({'status': 'PASS', 'sha256': sha(raw)}, sort_keys=True))


if __name__ == '__main__':
    main()
