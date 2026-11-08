"""Pure, effect-disabled selection of the original Context and API projections."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath

LOCAL = Path(__file__).resolve().parent.parent
STAGE = LOCAL / 'context-stage-0001/generated'
JIT = LOCAL / 'context-jit-provision-0001'
MAPPER_ADAPTER = LOCAL / 'mapper-successor-recovery-0001/adapter.py'
MAPPER_ADAPTER_SHA = '083a24b9c40dc27fbf40ce3fd49e41b2821470e223a3b9e783681e9aa7cf2c99'
MAPPER_FREEZE = LOCAL / 'mapper-successor-recovery-0001/freeze.json'
MAPPER_FREEZE_SHA = 'a927eab2573e2474f0bf5450fcfa58d6d7ab82eb220fb776af0037865e1f86a6'
STAGE_FREEZE = LOCAL / 'context-stage-0001/freeze.json'
STAGE_FREEZE_SHA = '8e7194585a4a98ce4a6ed906ef349449457335aba2060229c1d105eac36021b8'
JIT_CONTROL_SHA = 'ebd63979ce378070e6d5647c240234548a9fb38d141b6ed0d57885925f66c7e1'
JIT_BUILD_SHA = '30149a0388f3eb32fb30dd5b07bc11a8309ed7ab3fafa56ef8b5d714d39f93f0'
BASE = 'product/lab/release-candidates/v1/interface/'
SOURCE, READER, MAPPER = (BASE + 'docker-' + role + '-20261020-0002'
                          for role in ('source', 'reader', 'mapped'))
CONTEXT = BASE + 'docker-context-20261020-0002'
API = BASE + 'api-v25'
ATTEMPT = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/context-attempt')
MAPPER_ATTEMPT = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/mapper-attempt')
OLD = {'source':'7e0938e70ac00b5308851b5a5a7c7bdb92041efab3be17296998acb4160395c1',
       'source_package':'f132b3e1908e9e116464ad29c3db7f56ca17d4dee080e60ffa62547dd9588a5b',
       'reader':'4b61293453ec763f1c3567d3dac114e0d0782a2c58b85bc941ca34a0c974d251',
       'mapper':'0bd6696a1e33750bca01cdeae65d3a5ae977b433c0e0b608009422161b3c1358',
       'mapper_package':'0b3635dc9896034203e9e318ad99d58f2c37ca5acd419841d338f6ec9e4a1aea',
       'api_profile':'2ef0657841ba21ba2b68c7987654817ea39deda669bf89207fa406aa89279d64'}
PRE = {'api-v25/source_bridge.py':'05f5d12d86ca3cd02614c009e405ca3a290b78ed6c46a13864f81657b124edc2',
       'api-v25/source-selection.json':'31a47762df698258d34b4bdf26e57a452d56f96c2f5ef9fc0b16f297eb93ff76',
       'api-v25/contract-profile.json':OLD['api_profile'],
       'api-v25/source-manifest.json':'00a1ad634a0e73506047531144587249412a92f66b15cd6ee7c155018b1fb0d0',
       'api-v25/protocol.py':'6cf6d1ee8dd591ddba22e4b4470ba43a70470557710957687820208746856dad',
       'context/__init__.py':'e7211de83b6c2c67aba3feb7fb0d1fc4446ec98f600d0223a55051bc183f7c93',
       'context/base.py':'99c160092b57237f6445fd7902b9f1e0e57046653a188abed81e341b5b97b8d8',
       'context/generation.py':'727e1d96c68cf2cf2aa7235335b672f0656d17a7f96b72c544db44aaa581780b',
       'context/lifetime-policy.json':'57f1a7b4757b551aefd05ed6efeada6ce416988d14b3aab73a4119f2b3f31e4a',
       'context/implementation-binding.json':'9d504f5d967cb9ad044fa2e5dd5ec9f9f6246af3fe75b47bb6f0b683e7ef5303'}


class Refused(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise Refused(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + '\n').encode()


def parse(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            need(key not in value, 'DUPLICATE_JSON_KEY')
            value[key] = item
        return value
    try:
        return json.loads(raw, object_pairs_hook=pairs,
                          parse_constant=lambda _ : (_ for _ in ()).throw(Refused('NONFINITE_JSON')))
    except (ValueError, UnicodeError, TypeError, RecursionError) as error:
        raise Refused('INVALID_JSON') from error


def exact_preimage(relative):
    raw = (STAGE / relative).read_bytes()
    need(sha(raw) == PRE[relative], 'CONTEXT_PREIMAGE_DRIFT:' + relative)
    return raw


def replace_one(raw, old, new, label):
    need(raw.count(old) == 1, 'PROJECTION_SPAN:' + label)
    result = raw.replace(old, new)
    need(result.replace(new, old) == raw, 'PROJECTION_INVERSE:' + label)
    return result


def mapper_adapter():
    need(sha(MAPPER_ADAPTER.read_bytes()) == MAPPER_ADAPTER_SHA and
         sha(MAPPER_FREEZE.read_bytes()) == MAPPER_FREEZE_SHA and
         sha(STAGE_FREEZE.read_bytes()) == STAGE_FREEZE_SHA,
         'SELECTOR_OR_STAGE_DRIFT')
    spec = importlib.util.spec_from_file_location('cal_mapper_successor_frozen', MAPPER_ADAPTER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def select(*, mapper_manifest_raw, mapper_package_raw, mapper_terminal_raw,
           mapper_external_raw, mapper_review_raw, outside_mapper_review_sha,
           **reader_selection):
    M = mapper_adapter()
    selected = M.select(**reader_selection)
    pins = {'source': M.reader_adapter().SOURCE_MANIFEST_SHA,
            'source_package': selected['source_package_manifest_sha256'],
            'reader': selected['reader_manifest_sha256'],
            'mapper': selected['mapper_manifest_sha256'],
            'mapper_package': sha(mapper_package_raw)}
    need(mapper_manifest_raw == M.encoded(selected['mapper_manifest']) and
         sha(mapper_manifest_raw) == pins['mapper'], 'MAPPER_MANIFEST_DYNAMIC_JOIN')
    package, terminal, external, review = map(parse,
        (mapper_package_raw, mapper_terminal_raw, mapper_external_raw, mapper_review_raw))
    need(type(package) is dict and
         package.get('schema_version') == 'lab-mapped-context-package/v1-candidate' and
         package.get('authority_effect') == 'none' and
         package.get('actual_owner_outcome') is None and
         package.get('source_manifest_binding') ==
         {'path':MAPPER + '/source-manifest.json','sha256':pins['mapper']},
         'MAPPER_PACKAGE_BINDING')
    files = package.get('files')
    prefix = MAPPER + '/packages/0001/'
    expected = {prefix + name for name in selected['expected_package_members'] if name != 'manifest.json'}
    need(type(files) is list and len(files) == 54 and
         all(type(row) is dict and set(row) == {'path','sha256'} and
             type(row['path']) is str and type(row['sha256']) is str and
             len(row['sha256']) == 64 and
             all(c in '0123456789abcdef' for c in row['sha256']) and
             PurePosixPath(row['path']).as_posix() == row['path'] for row in files) and
         {row['path'] for row in files} == expected, 'MAPPER_55_LEAF_PACKAGE')
    need(type(terminal) is dict and terminal.get('overall') ==
         terminal.get('operation') == terminal.get('cleanup') == 'PASS' and
         terminal.get('no_retry') is True and
         terminal.get('package_manifest_sha256') == pins['mapper_package'],
         'MAPPER_TERMINAL_JOIN')
    need(type(external) is dict and external.get('schema') ==
         'lab-successor-mapper-external-exit/v1' and external.get('exit_code') == 0 and
         external.get('attempt') == str(MAPPER_ATTEMPT), 'MAPPER_EXTERNAL_OS_JOIN')
    need(type(outside_mapper_review_sha) is str and
         sha(mapper_review_raw) == outside_mapper_review_sha, 'OUTSIDE_MAPPER_REVIEW_PIN')
    need(type(review) is dict and set(review) ==
         {'schema','verdict','attempt','source_manifest_sha256','source_package_manifest_sha256',
          'reader_manifest_sha256','mapper_manifest_sha256','mapper_package_manifest_sha256',
          'terminal_sha256','external_sha256'} and
         review['schema'] == 'lab-successor-mapper-effect-review/v1' and
         review['verdict'] == 'PASS_BOUNDED_MAPPER_COLD_NATIVE' and
         review['attempt'] == str(MAPPER_ATTEMPT) and
         all(review[field] == pins[key] for field,key in (
             ('source_manifest_sha256','source'),
             ('source_package_manifest_sha256','source_package'),
             ('reader_manifest_sha256','reader'),
             ('mapper_manifest_sha256','mapper'),
             ('mapper_package_manifest_sha256','mapper_package'))) and
         review['terminal_sha256'] == sha(mapper_terminal_raw) and
         review['external_sha256'] == sha(mapper_external_raw),
         'INDEPENDENT_MAPPER_EFFECT_JOIN')
    for relative in PRE:
        exact_preimage(relative)
    need(sha((JIT / 'projected-control.py').read_bytes()) == JIT_CONTROL_SHA and
         sha((JIT / 'projected-build.py').read_bytes()) == JIT_BUILD_SHA,
         'JIT_GUARD_DRIFT')
    api = project_api(pins)
    reader_manifest = parse(reader_selection['reader_manifest_raw'])
    reader_code_rows = [r for r in reader_manifest['files']
                        if r['path'] == READER + '/reader.py']
    need(len(reader_code_rows) == 1, 'READER_CODE_BINDING')
    context = project_context(pins, sha(api['contract-profile.json']),
                              reader_code_rows[0]['sha256'])
    return {'status':'CONTEXT_DYNAMIC_SELECTION_ONLY','effect_enabled':False,
            'attempt':str(ATTEMPT),'pins':pins,
            'mapper_effect_review_sha256':outside_mapper_review_sha,
            'api_profile_sha256':sha(api['contract-profile.json']),
            'api_source_manifest_sha256':sha(api['source-manifest.json']),
            'projected_api':api,'projected_context':context,
            'context_source_manifest':'REFUSED','context_launch':'REFUSED',
            'protected_inputs_read':False}


def project_api(pins):
    bridge = exact_preimage('api-v25/source_bridge.py')
    for old, new in [('docker-mapped-20261020-0001', MAPPER.rsplit('/',1)[-1]),
                     ('docker-source-20261020-0001', SOURCE.rsplit('/',1)[-1]),
                     ('docker-reader-20261020-0001', READER.rsplit('/',1)[-1])]:
        bridge = replace_one(bridge, old.encode(), new.encode(), 'API_BRIDGE_ROLE')
    selection = parse(exact_preimage('api-v25/source-selection.json'))
    for key, role, suffix, pin in (
        ('source_manifest_binding',SOURCE,'source-manifest.json','source'),
        ('source_package_binding',SOURCE,'packages/0001/manifest.json','source_package'),
        ('reader_manifest_binding',READER,'source-manifest.json','reader'),
        ('mapper_manifest_binding',MAPPER,'source-manifest.json','mapper'),
        ('mapper_package_binding',MAPPER,'packages/0001/manifest.json','mapper_package')):
        need(selection[key]['sha256'] == OLD[pin], 'API_SELECTION_PREIMAGE')
        selection[key] = {'path':role + '/' + suffix, 'sha256':pins[pin]}
    selection['claim_ceiling'] = 'Fresh same-family Context API selection only; no API effect.'
    selection_raw = encoded(selection)
    profile = parse(exact_preimage('api-v25/contract-profile.json'))
    rows = {r['path']:r for r in profile['files']}
    need(len(rows) == len(profile['files']) == 30, 'API_PROFILE_CLOSURE')
    for name, raw in (('source_bridge.py',bridge),('source-selection.json',selection_raw)):
        need(rows[API + '/' + name]['sha256'] == PRE['api-v25/' + name], 'API_PROFILE_PREIMAGE')
        rows[API + '/' + name]['sha256'] = sha(raw)
    profile['claim_ceiling'] = 'Fresh same-family API.Schemas projection only; full API suite and effect not run.'
    profile_raw = encoded(profile)
    manifest = parse(exact_preimage('api-v25/source-manifest.json'))
    manifest_rows = {r['path']:r for r in manifest['files']}
    need(len(manifest_rows) == len(manifest['files']) == 33, 'API_SOURCE_CLOSURE')
    for name, raw in (('source_bridge.py',bridge),('source-selection.json',selection_raw),
                      ('contract-profile.json',profile_raw)):
        need(manifest_rows[API + '/' + name]['sha256'] == PRE['api-v25/' + name],
             'API_SOURCE_PREIMAGE')
        manifest_rows[API + '/' + name]['sha256'] = sha(raw)
    manifest['source_family'] = {'source_sha256':pins['source'],
                                 'reader_sha256':pins['reader'],
                                 'mapper_source_sha256':pins['mapper'],
                                 'mapper_package_sha256':pins['mapper_package']}
    manifest['claim_ceiling'] = 'Fresh API.Schemas import projection; no full API or Context effect.'
    result = {'source_bridge.py':bridge,'source-selection.json':selection_raw,
              'contract-profile.json':profile_raw,
              'source-manifest.json':encoded(manifest),
              'protocol.py':exact_preimage('api-v25/protocol.py')}
    for name in ('source_bridge.py','protocol.py'):
        compile(result[name], API + '/' + name, 'exec', optimize=0)
        compile(result[name], API + '/' + name, 'exec', optimize=2)
    return result


def project_context(pins, api_profile_sha, reader_code_sha):
    roles = {}
    for name in ('__init__.py','base.py','build.py','control.py','generation.py'):
        raw = (JIT / ('projected-' + name)).read_bytes() if name in ('build.py','control.py') else exact_preimage('context/' + name)
        if name in ('build.py','control.py'):
            need(sha(raw) == (JIT_BUILD_SHA if name == 'build.py' else JIT_CONTROL_SHA),
                 'JIT_ROLE_DRIFT')
        if name == 'base.py':
            for key, value in (('mapper',pins['mapper']),('mapper_package',pins['mapper_package']),
                               ('api_profile',api_profile_sha)):
                raw = replace_one(raw, OLD[key].encode(), value.encode(), 'CONTEXT_BASE_PIN:' + key)
            raw = replace_one(raw,b'docker-mapped-20261020-0001',MAPPER.rsplit('/',1)[-1].encode(),
                              'CONTEXT_MAPPER_ROLE')
        elif name == 'build.py':
            for key in ('source','source_package'):
                raw = replace_one(raw, OLD[key].encode(), pins[key].encode(), 'CONTEXT_BUILD_PIN:' + key)
        elif name == 'control.py':
            old = b'docker-source-20261020-0001'
            need(raw.count(old) == 2, 'CONTEXT_AUTH_PATH_SPANS')
            raw = raw.replace(old,SOURCE.rsplit('/',1)[-1].encode())
        elif name == 'generation.py':
            raw = replace_one(raw, OLD['mapper'].encode(), pins['mapper'].encode(),
                              'CONTEXT_GENERATION_PIN')
        need(raw.count(b'def _t35_effect_refused():') == 1 and
             raw.count(b"raise RuntimeError('Generated T35 role effects require the uninstalled T02 custody gate')") == 1,
             'CONTEXT_EFFECT_REFUSAL_LOST')
        compile(raw, CONTEXT + '/' + name, 'exec', optimize=0)
        compile(raw, CONTEXT + '/' + name, 'exec', optimize=2)
        roles[name] = raw
    roles['lifetime-policy.json'] = exact_preimage('context/lifetime-policy.json')
    binding = parse(exact_preimage('context/implementation-binding.json'))
    old_ref = BASE + 'docker-reader-20261020-0001/reader.py'
    for field in ('code_binding','entrypoint_ref'):
        if field == 'code_binding':
            need(binding[field]['ref'].endswith(old_ref), 'CONTEXT_READER_BINDING')
            binding[field]['ref'] = '/workspace/' + READER + '/reader.py'
        else:
            need(binding[field].endswith(old_ref + '#SelectedReader.open_signed'),
                 'CONTEXT_READER_ENTRYPOINT')
            binding[field] = '/workspace/' + READER + '/reader.py#SelectedReader.open_signed'
    need(type(reader_code_sha) is str and len(reader_code_sha) == 64 and
         all(c in '0123456789abcdef' for c in reader_code_sha),
         'READER_CODE_DIGEST')
    binding['code_binding']['sha256'] = reader_code_sha
    roles['implementation-binding.json'] = (json.dumps(binding,sort_keys=True,
        separators=(',',':'),ensure_ascii=False,allow_nan=False)+'\n').encode()
    return roles


def execute_context(*_args, **_kwargs):
    raise Refused('EFFECT_DISABLED_CONTEXT_SOURCE_MANIFEST_AND_JIT_ISSUER_REQUIRED')
