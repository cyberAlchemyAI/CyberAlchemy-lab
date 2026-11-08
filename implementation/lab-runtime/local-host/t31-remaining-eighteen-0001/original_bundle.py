"""One-time original engineering/research output capture and cold selection.

The original design method runs once in `prepare`. `consume` reads only the
exact retained originals; a later workflow guard never redispatches it.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

ROOT = Path(__file__).resolve().parents[4]
WORK = ROOT / 'implementation/lab-runtime/local-host/t31-retained-work-0001'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def enc(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def original_modules():
    need(WORK.is_dir() and not WORK.is_symlink(), 'selected original Work package absent')
    sys.path.insert(0, str(WORK))
    import profiles as P
    import bundle as B
    need(Path(P.__file__).resolve() == WORK / 'profiles.py'
         and Path(B.__file__).resolve() == WORK / 'bundle.py',
         'original Work helper origin differs')
    return P, B


def write_new(path, raw):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def prepare(kind, directory):
    need(kind in ('engineering', 'research'), 'supported original Work kind required')
    directory = Path(directory).absolute()
    need(not directory.exists() and directory.parent.is_dir()
         and not directory.is_relative_to(ROOT)
         and not any(p.is_symlink() for p in directory.parents),
         'fresh external private original bundle required')
    P, B = original_modules()
    profile = P.load(kind)
    P.guard(profile)
    transitions, raws, receipt = B.construct(profile)
    need(set(transitions) == {'transition:' + kind + ':' + phase for phase in
                              (('designed', 'implemented', 'assessed')
                               if kind == 'engineering' else ('designed', 'executed', 'evaluated'))},
         'three original stage outputs required')
    records = {}
    for header in [header for rows in transitions.values() for header in rows]:
        ref = header['version_ref']
        need(ref not in records and header['byte_sha256'] == sha(raws[ref]),
             'unique exact original output bytes required')
        records[ref] = (header, raws[ref], 'original-stage-output')
    for ref, header in profile['headers'].items():
        raw = profile['raws'][ref]
        need(header['byte_sha256'] == sha(raw), 'exact original input bytes required')
        if ref in records:
            # Research's pure design method validates and reuses the original
            # ready ExperimentDesign byte for byte as its first stage output.
            need(records[ref][:2] == (header, raw),
                 'original input/output revision differs')
        else:
            records[ref] = (header, raw, 'original-selected-input')
    need(receipt['kind'] == kind and receipt['original_work'] == profile['original_work']
         and receipt['original_producer_source_cut'] == profile['original_producer_source_cut']
         and receipt['transitions'] == transitions
         and receipt['original_output_bytes_unchanged'] is True
         and receipt['retained_implementation_or_experiment_rerun'] is False,
         'original provenance/transition receipt differs')
    directory.mkdir(mode=0o700)
    rows = []
    for ref, (header, raw, origin) in sorted(records.items()):
        name = sha(raw) + '.json'
        path = directory / name
        if not path.exists():
            write_new(path, raw)
        else:
            need(path.read_bytes() == raw, 'digest-named original collision')
        rows.append({'artifact': header, 'path': name, 'origin': origin,
                     'sha256': sha(raw), 'size_bytes': len(raw)})
    receipt_raw = enc(receipt)
    write_new(directory / 'ORIGINAL-RECEIPT.json', receipt_raw)
    manifest = {'schema_version': 'lab-t31-original-work-bundle/v1',
                'kind': kind, 'original_work': profile['original_work'],
                'original_producer_source_cut': profile['original_producer_source_cut'],
                'original_input_manifest_sha256': P.SPECS[kind]['sha256'],
                'original_code_sha256': P.SPECS[kind]['code_sha256'],
                'original_run_sha256': P.SPECS[kind]['run_sha256'],
                'original_result_sha256': P.RESULT_SHA,
                'receipt_sha256': sha(receipt_raw), 'records': rows,
                'transitions': transitions, 'authority_effect': 'none',
                'actual_owner_outcome': None}
    raw = enc(manifest)
    write_new(directory / 'MANIFEST.json', raw)
    return {'manifest_path': str(directory / 'MANIFEST.json'),
            'manifest_sha256': sha(raw), 'kind': kind,
            'record_count': len(rows), 'transition_count': len(transitions),
            'authority_effect': 'none'}


def consume(selection):
    import retained as R
    need(type(selection) is dict and set(selection) == {'kind', 'manifest_path', 'manifest_sha256'},
         'closed original Work selection required')
    kind = selection['kind']
    need(kind in ('engineering', 'research'), 'supported original Work kind required')
    path = Path(selection['manifest_path'])
    need(path.is_absolute() and path.name == 'MANIFEST.json', 'exact original Work manifest required')
    folder = path.parent
    st = folder.stat()
    need(folder.is_dir() and not folder.is_symlink() and st.st_uid == os.getuid()
         and stat.S_IMODE(st.st_mode) == 0o700,
         'owned private original Work bundle required')
    raw = R.read(path)
    need(sha(raw) == selection['manifest_sha256'], 'selected original Work manifest differs')
    manifest = json.loads(raw)
    need(type(manifest) is dict and set(manifest) == {
        'schema_version', 'kind', 'original_work', 'original_producer_source_cut',
        'original_input_manifest_sha256', 'original_code_sha256',
        'original_run_sha256', 'original_result_sha256', 'receipt_sha256',
        'records', 'transitions', 'authority_effect', 'actual_owner_outcome'}
        and manifest['schema_version'] == 'lab-t31-original-work-bundle/v1'
        and manifest['kind'] == kind and manifest['authority_effect'] == 'none'
        and manifest['actual_owner_outcome'] is None,
        'closed original Work manifest differs')
    P, B = original_modules()
    profile = P.load(kind)
    P.guard(profile)
    need(manifest['original_work'] == profile['original_work']
         and manifest['original_producer_source_cut'] == profile['original_producer_source_cut']
         and manifest['original_input_manifest_sha256'] == P.SPECS[kind]['sha256']
         and manifest['original_code_sha256'] == P.SPECS[kind]['code_sha256']
         and manifest['original_run_sha256'] == P.SPECS[kind]['run_sha256']
         and manifest['original_result_sha256'] == P.RESULT_SHA,
         'original Work producer/source provenance differs')
    receipt_raw = R.read(folder / 'ORIGINAL-RECEIPT.json')
    need(sha(receipt_raw) == manifest['receipt_sha256'], 'original Work receipt changed')
    receipt = json.loads(receipt_raw)
    need(receipt['kind'] == kind and receipt['original_work'] == profile['original_work']
         and receipt['original_producer_source_cut'] == profile['original_producer_source_cut']
         and receipt['transitions'] == manifest['transitions']
         and receipt['original_output_bytes_unchanged'] is True
         and receipt['retained_implementation_or_experiment_rerun'] is False,
         'actual original Work receipt differs')
    records = {}
    names = {'MANIFEST.json', 'ORIGINAL-RECEIPT.json'}
    for row in manifest['records']:
        need(type(row) is dict and set(row) == {'artifact', 'path', 'origin', 'sha256', 'size_bytes'},
             'closed original Work record row required')
        name = row['path']
        need(type(name) is str and name == row['sha256'] + '.json'
             and Path(name).name == name, 'digest-named original Work body required')
        body = R.read(folder / name)
        header = row['artifact']
        need(sha(body) == row['sha256'] == header['byte_sha256']
             and len(body) == row['size_bytes']
             and header['scope_ref'] == profile['scope_ref']
             and row['origin'] in ('original-stage-output', 'original-selected-input'),
             'original Work record/header differs')
        ref = header['version_ref']
        need(ref not in records or records[ref] == (header, body),
             'ambiguous original Work revision')
        if row['origin'] == 'original-selected-input':
            need(ref in profile['headers'] and profile['headers'][ref] == header
                 and profile['raws'][ref] == body,
                 'selected original Work input differs from pinned profile')
        records[ref] = (header, body)
        names.add(name)
    need({p.name for p in folder.iterdir()} == names
         and not any(p.is_symlink() for p in folder.iterdir()),
         'original Work bundle file closure differs')
    for transition, headers in manifest['transitions'].items():
        need(transition.startswith('transition:' + kind + ':') and headers,
             'original Work transition set differs')
        for header in headers:
            need(header['version_ref'] in records
                 and records[header['version_ref']][0] == header,
                 'original Work transition output missing')
            B.S.original_carriers().output(header, records[header['version_ref']][1],
                                           scope_ref=profile['scope_ref'],
                                           transition_ref=transition)
    return {'records': records, 'transitions': manifest['transitions'],
            'receipt_raw': receipt_raw, 'manifest_raw': raw,
            'manifest_binding': {'ref': str(path), 'sha256': sha(raw)}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--kind', choices=('engineering', 'research'), required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.kind, args.output), sort_keys=True))
