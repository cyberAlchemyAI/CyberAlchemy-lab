"""Effect-disabled dynamic Reader selection after a fresh persistent Source run."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
LOCAL = Path(__file__).resolve().parent.parent
PROFILE = LOCAL / 'context-successor-recovery-0001'
PROFILE_FREEZE_SHA = 'bb9f9be62c606dc87ccfdab9b5497c833cf781e89170d789379167582950bf66'
SOURCE_MANIFEST_SHA = '2843a67fd28a295f5c175b8d8c2b31f701040bb8d7dedeade8d76bbdf057d1d1'
SOURCE_ATTEMPT = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/source-attempt')
READER_ATTEMPT = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/reader-attempt')
SOURCE = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0002'
READER = 'product/lab/release-candidates/v1/interface/docker-reader-20261020-0002'
OLD_READER = 'product/lab/release-candidates/v1/interface/legacy-session-fixture-reader-v1-action-0148'
OLD_PRODUCER = 'legacy-session-fixture-source-v1-action-0148'
OLD_MODULE = '_cal_legacy_session_fixture_producer_0257'
NEW_MODULE = '_cal_docker_reader_producer_20261020_0002'
ROLE = {
    '__init__.py': '1b88f99e5c0621338bf462d41cb54effcf2ec08cba8884fdf8dedc6179709529',
    'base.py': 'd677d3ab9ff523c07404ab95e3a77509b0a016323d4b8a0cd8c2c1f42e8c7d39',
    'reader.py': 'f93a1f218238c05b18a7c355f9bc1363bbf42d2b1d442d03e191e121f8e9c9b9',
    'adapter.py': '85646307fa07c768105258ef0d49226b2d06fc70af3e5993fb2f58ca2124c399',
    'inspection.py': '49770bd3c1f3c873840545a09f4ac207371b510b29e38f11a0523e0acb81cc11',
    'model.py': '687f42b643cfadaa2c9782cd1630c3ae26fff03c37d5f10ab2e9e0da4c8e70c7',
    'eligibility.py': '5d16158070ddfcdc026a59390041b11db39556435754f67623390c0bc6d4c2ba',
}


class Refused(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise Refused(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n').encode()


def parse(raw):
    def pairs(rows):
        out = {}
        for key, value in rows:
            need(key not in out, 'DUPLICATE_JSON_KEY')
            out[key] = value
        return out
    try:
        return json.loads(raw, object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(Refused('NONFINITE_JSON')))
    except (ValueError, UnicodeError, TypeError, RecursionError) as error:
        raise Refused('INVALID_JSON') from error


def current_period(period, now):
    need(type(period) is dict and set(period) >= {'not_before', 'expires_at'}, 'PERIOD_SHAPE')
    try:
        begin = datetime.fromisoformat(period['not_before'])
        end = datetime.fromisoformat(period['expires_at'])
    except (ValueError, TypeError) as error:
        raise Refused('PERIOD_SHAPE') from error
    need(begin.tzinfo is not None and end.tzinfo is not None and
         begin.utcoffset() == end.utcoffset() == timedelta(0) and
         begin <= now < end and end - begin == timedelta(hours=24) and
         begin == datetime(2026, 10, 20, 15, tzinfo=timezone.utc), 'PERIOD_CURRENT')


def project_role(name, raw):
    need(name in ROLE and sha(raw) == ROLE[name], 'READER_PREIMAGE')
    if name != 'base.py':
        return raw
    text = raw.decode('utf-8')
    for old, new in ((OLD_PRODUCER, SOURCE.rsplit('/', 1)[-1]),
                     (OLD_MODULE, NEW_MODULE)):
        need(text.count(old) == 1 and new not in text, 'READER_PROJECTION_SPAN')
        text = text.replace(old, new, 1)
    result = text.encode()
    compile(result, READER + '/base.py', 'exec', optimize=0)
    compile(result, READER + '/base.py', 'exec', optimize=2)
    inverse = text
    for old, new in ((OLD_PRODUCER, SOURCE.rsplit('/', 1)[-1]),
                     (OLD_MODULE, NEW_MODULE)):
        need(inverse.count(new) == 1, 'READER_INVERSE_SPAN')
        inverse = inverse.replace(new, old, 1)
    need(inverse.encode() == raw, 'READER_INVERSE')
    return result


def projected_roles():
    need(sha((PROFILE / 'freeze.json').read_bytes()) == PROFILE_FREEZE_SHA,
         'SOURCE_PROFILE_FREEZE_DRIFT')
    result = {}
    for name in ROLE:
        original = (REPO / OLD_READER / name).read_bytes()
        result[name] = project_role(name, original)
    return result


def select(source_raw, package_raw, terminal_raw, period_raw, review_raw,
           outside_review_sha, now):
    """Receipt/read-only selector only; no archive-body read or Reader effect."""
    need(sha((PROFILE / 'freeze.json').read_bytes()) == PROFILE_FREEZE_SHA,
         'SOURCE_PROFILE_FREEZE_DRIFT')
    need(sha(source_raw) == SOURCE_MANIFEST_SHA, 'SOURCE_MANIFEST_PIN')
    need(type(outside_review_sha) is str and sha(review_raw) == outside_review_sha,
         'OUTSIDE_EFFECT_REVIEW_PIN')
    source, package, terminal, period, review = map(parse,
        (source_raw, package_raw, terminal_raw, period_raw, review_raw))
    need(type(source) is dict and type(source.get('files')) is list and
         len(source['files']) == 940 and
         all(type(r) is dict and set(r) == {'path','sha256'} for r in source['files']) and
         len({r['path'] for r in source['files']}) == 940, 'SOURCE_PUBLIC_CLOSURE')
    package_sha, terminal_sha = sha(package_raw), sha(terminal_raw)
    need(type(package) is dict and type(package.get('files')) is list and
         len(package['files']) == 36 and
         all(type(r) is dict and set(r) == {'path','sha256'} and
             type(r['path']) is str and r['path'].startswith(SOURCE + '/packages/0001/') and
             all(part not in ('', '.', '..') for part in r['path'].split('/')) and
             type(r['sha256']) is str and len(r['sha256']) == 64 and
             all(c in '0123456789abcdef' for c in r['sha256']) for r in package['files']) and
         len({r['path'] for r in package['files']}) == 36 and
         package.get('source_manifest_binding') ==
         {'path': SOURCE + '/source-manifest.json', 'sha256': SOURCE_MANIFEST_SHA},
         'SOURCE_PACKAGE_CLOSURE')
    need(package.get('archive_binding') in package['files'] and
         package['archive_binding']['path'] == SOURCE + '/packages/0001/branch.snapshot' and
         package.get('period_binding') in package['files'] and
         package['period_binding'] ==
         {'path': SOURCE + '/packages/0001/period.json', 'sha256': sha(period_raw)},
         'SOURCE_PACKAGE_BINDINGS')
    current_period(period, now)
    need(type(terminal) is dict and
         terminal.get('overall') == terminal.get('operation') == terminal.get('cleanup') == 'PASS' and
         terminal.get('no_retry') is True and
         terminal.get('package_manifest_sha256') == package_sha,
         'SOURCE_TERMINAL')
    need(type(review) is dict and set(review) ==
         {'schema', 'verdict', 'source_manifest_sha256', 'package_manifest_sha256',
          'terminal_sha256', 'attempt'} and
         review['schema'] == 'lab-successor-source-effect-review/v1' and
         review['verdict'] == 'PASS_BOUNDED_SOURCE_ONLY_EFFECT' and
         review['source_manifest_sha256'] == SOURCE_MANIFEST_SHA and
         review['package_manifest_sha256'] == package_sha and
         review['terminal_sha256'] == terminal_sha and
         review['attempt'] == str(SOURCE_ATTEMPT), 'INDEPENDENT_SOURCE_EFFECT_JOIN')
    roles = projected_roles()
    rows = source['files'] + [{'path': SOURCE + '/source-manifest.json', 'sha256': SOURCE_MANIFEST_SHA}]
    rows += [{'path': READER + '/' + name, 'sha256': sha(raw)} for name, raw in roles.items()]
    need(len(rows) == len({r['path'] for r in rows}) == 948, 'READER_STATIC_CLOSURE')
    reader_manifest = {'schema_version': 'lab-docker-distinct-reader-source/v1-candidate',
        'files': sorted(rows, key=lambda r:r['path']),
        'environment': {'python': '3.14.4', 'jsonschema': '4.23.0', 'cryptography': '46.0.5'},
        'fixture_only': True, 'qualification': False, 'authority_effect': 'none',
        'actual_owner_outcome': None,
        'producer_source_binding': {'path': SOURCE + '/source-manifest.json', 'sha256': SOURCE_MANIFEST_SHA},
        'producer_package_binding': {'path': SOURCE + '/packages/0001/manifest.json', 'sha256': package_sha}}
    reader_raw = encoded(reader_manifest)
    return {'status':'DYNAMIC_READER_SELECTION_ONLY','source_attempt':str(SOURCE_ATTEMPT),
            'reader_attempt':str(READER_ATTEMPT),'source_manifest_sha256':SOURCE_MANIFEST_SHA,
            'source_package_manifest_sha256':package_sha,'source_terminal_sha256':terminal_sha,
            'source_effect_review_sha256':outside_review_sha,'source_archive_sha256':package['archive_binding']['sha256'],
            'reader_manifest_sha256':sha(reader_raw),'reader_manifest':reader_manifest,
            'projected_roles':roles,'effect_enabled':False}


def probe_live():
    root = SOURCE_ATTEMPT / 'root'
    paths = [root / SOURCE / 'source-manifest.json',
             root / SOURCE / 'packages/0001/manifest.json',
             SOURCE_ATTEMPT / 'evidence/source-once.terminal.json']
    return {'status':'SOURCE_EFFECT_NOT_PRESENT' if not any(p.exists() for p in paths) else
            'SOURCE_PARTIAL_OR_READY_REQUIRES_EXACT_REVIEW',
            'paths_present':[str(p) for p in paths if p.exists()], 'effect_enabled':False}


def execute_reader(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_FRESH_SOURCE_AND_READER_RELEASE_REQUIRED')
