"""Effect-disabled Mapper projection over a reviewed fresh Source and Reader."""
from __future__ import annotations

import ast
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
LOCAL = Path(__file__).resolve().parent.parent
READER_ADAPTER = LOCAL / 'reader-successor-recovery-0001/adapter.py'
READER_ADAPTER_SHA = 'c13f80e7ca778f1e8d3f56083304b5a68afc5828e9a01469f9ffbd9034e10aa2'
READER_FREEZE = LOCAL / 'reader-successor-recovery-0001/freeze.json'
READER_FREEZE_SHA = '8cff5cfca3b9488846f7c120fdfc1195560e0d262c5d8e7674cc34572da399ab'
OLD = 'product/lab/release-candidates/v1/interface/legacy-session-fixture-mapped-v2-action-0148'
SOURCE = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0002'
READER = 'product/lab/release-candidates/v1/interface/docker-reader-20261020-0002'
MAPPER = 'product/lab/release-candidates/v1/interface/docker-mapped-20261020-0002'
ATTEMPT = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/mapper-attempt')
READER_ATTEMPT = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/reader-attempt')
NATIVE = REPO / 'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/bin/lab-context-native-reader'
NATIVE_SHA = 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
VERIFIER = LOCAL / 'mapper-only-docker-release-0003/controller.py'
VERIFIER_SHA = 'aa883d697a9cfec02a4671da2a76d10c5c4b23ef0a93e63c78f31ac0667ff23b'
OLD_PINS = {'source':'f3cbec21c32dce3938460a1203e6e3f3575608f463aa3f3fffae9f9338a798f2',
            'package':'8e7b675666308e0e73fb23962b310ea3a89baa48ad6bf2c9cf1c5c9ce9e96964',
            'reader':'0ad1c974a5725d7bf0c23cc08b27c9e4e6c2b4fba512ddc0009aef337e81c0a5'}
PREIMAGES = {
    '__init__.py':'a88e78979e6f4ddfaf89055996e294a92987e42ca63526252a56defb8bc05362',
    'base.py':'02f0481cb20dd81c5e4b6228ce4657987d8960ea9930893434b364a48f5b12ad',
    'build.py':'dced09f9432318ef286475081ea5f4f7e6fa633c7cefbd9db76c0ec3c47ecbbb',
    'policy.json':'1c2ddd360e56666fec0f4ff2095f32369705cff7b96edecbc5ba0720136457ab'}
EXPECTED_PIN_COUNTS = {'__init__.py':(0,0,0),'base.py':(1,1,1),
                       'build.py':(1,1,0),'policy.json':(0,0,0)}
OUTPUT_LEAVES = tuple(f'{family}/{cursor:08d}.json'
                      for family in ('semantic','governance') for cursor in range(1,26)) + (
                      'request.json','native-output.json','mapping.json','build-result.json','manifest.json')


class Refused(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise Refused(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()


def parse(raw):
    def pairs(rows):
        out={}
        for key,value in rows:
            need(key not in out,'DUPLICATE_JSON_KEY')
            out[key]=value
        return out
    try:
        return json.loads(raw,object_pairs_hook=pairs,
                          parse_constant=lambda _:(_ for _ in ()).throw(Refused('NONFINITE_JSON')))
    except (ValueError,UnicodeError,TypeError,RecursionError) as error:
        raise Refused('INVALID_JSON') from error


def reader_adapter():
    need(sha(READER_FREEZE.read_bytes())==READER_FREEZE_SHA and
         sha(READER_ADAPTER.read_bytes())==READER_ADAPTER_SHA,'READER_SELECTOR_DRIFT')
    spec=importlib.util.spec_from_file_location('cal_reader_successor_frozen',READER_ADAPTER)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def project_role(name, raw, pins):
    need(name in PREIMAGES and sha(raw)==PREIMAGES[name], 'MAPPER_PREIMAGE')
    need(set(pins)==set(OLD_PINS) and all(type(p) is str and len(p)==64 and
         all(c in '0123456789abcdef' for c in p) for p in pins.values()),'THREE_DYNAMIC_PINS')
    text=raw.decode('utf-8')
    for key,count in zip(('source','package','reader'),EXPECTED_PIN_COUNTS[name]):
        need(text.count(OLD_PINS[key])==count,'MAPPER_PIN_VECTOR')
    replacements=[('legacy-session-fixture-source-v1-action-0148',SOURCE.rsplit('/',1)[-1]),
                  ('legacy-session-fixture-reader-v1-action-0148',READER.rsplit('/',1)[-1]),
                  ('/tmp/cal-R03-mapped-native-build-0002/target/debug/lab-context-native-reader',
                   '/attempt/input/lab-context-native-reader')]
    if name=='build.py':
        replacements += [
          ("p.is_relative_to(HERE/'packages') or p.is_relative_to(HERE/'receipts')",
           "p.is_relative_to(HERE/'packages')"),
          ("prefix='cal-legacy-session-fixture-0257-seal-')",
           "prefix='cal-legacy-session-fixture-0257-seal-',dir='/attempt/scratch')")]
    replacements += [(OLD_PINS[key],pins[key]) for key in ('source','package','reader')]
    expected_paths={'__init__.py':(0,0,0),'base.py':(1,1,0),
                    'build.py':(0,0,1),'policy.json':(0,0,0)}
    need(tuple(text.count(old) for old,_ in replacements[:3])==expected_paths[name],
         'MAPPER_PATH_VECTOR')
    if name=='build.py':
        need(all(text.count(old)==1 for old,_ in replacements[3:5]),'MAPPER_BUILD_ROUTE')
    projected=text
    for old,new in replacements:
        projected=projected.replace(old,new)
    inverse=projected
    for old,new in reversed(replacements):
        need(inverse.count(new)>=1 or old not in text,'MAPPER_INVERSE_SPAN')
        inverse=inverse.replace(new,old)
    need(inverse==text,'MAPPER_INVERSE')
    if name.endswith('.py'):
        compile(projected,MAPPER+'/'+name,'exec',optimize=0)
        compile(projected,MAPPER+'/'+name,'exec',optimize=2)
        need(type(ast.parse(projected)) is ast.Module,'MAPPER_AST')
    else:
        need(json.loads(projected)==json.loads(text),'MAPPER_POLICY_DRIFT')
    return projected.encode()


def verify_output_template():
    raw=VERIFIER.read_bytes()
    need(sha(raw)==VERIFIER_SHA,'MAPPER_VERIFIER_DRIFT')
    tree=ast.parse(raw)
    names={node.name for node in tree.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))}
    need('verify_mapped_output' in names and len(OUTPUT_LEAVES)==55 and
         len(set(OUTPUT_LEAVES))==55 and NATIVE.is_file() and not NATIVE.is_symlink() and
         sha(NATIVE.read_bytes())==NATIVE_SHA,'MAPPER_OUTPUT_CONTRACT')
    return {'template_sha256':VERIFIER_SHA,'function':'verify_mapped_output',
            'native_sha256':NATIVE_SHA,'expected_leaves':OUTPUT_LEAVES,
            'effect_verifier_adapted':False}


def select(*,source_manifest_raw,source_package_raw,source_terminal_raw,period_raw,
           source_review_raw,outside_source_review_sha,reader_manifest_raw,
           reader_receipt_raw,reader_terminal_raw,reader_external_raw,
           reader_review_raw,outside_reader_review_sha,now:datetime):
    A=reader_adapter()
    selected=A.select(source_manifest_raw,source_package_raw,source_terminal_raw,
                      period_raw,source_review_raw,outside_source_review_sha,now)
    expected_reader_raw=A.encoded(selected['reader_manifest'])
    need(reader_manifest_raw==expected_reader_raw and
         sha(reader_manifest_raw)==selected['reader_manifest_sha256'],
         'READER_MANIFEST_DYNAMIC_JOIN')
    package_sha=sha(source_package_raw)
    reader_sha=sha(reader_manifest_raw)
    receipt,terminal,external,review=map(parse,
        (reader_receipt_raw,reader_terminal_raw,reader_external_raw,reader_review_raw))
    need(type(receipt) is dict and
         receipt.get('schema_version')=='lab-disposable-reader-receipt/v1-private' and
         receipt.get('reader_manifest_sha256')==reader_sha and
         receipt.get('source_manifest_sha256')==A.SOURCE_MANIFEST_SHA and
         receipt.get('source_package_manifest_sha256')==package_sha and
         receipt.get('authority_effect')=='none' and receipt.get('actual_owner_outcome') is None,
         'READER_RECEIPT_JOIN')
    need(type(terminal) is dict and terminal.get('overall')==terminal.get('operation')==
         terminal.get('cleanup')=='PASS' and terminal.get('reader_effect')==
         'DISPOSABLE_READER_DIAGNOSTIC' and terminal.get('receipt_sha256')==sha(reader_receipt_raw)
         and terminal.get('no_retry') is True,'READER_TERMINAL_JOIN')
    need(type(external) is dict and external.get('schema')==
         'lab-successor-reader-external-exit/v1' and external.get('exit_code')==0 and
         external.get('attempt')==str(READER_ATTEMPT),'READER_EXTERNAL_OS_JOIN')
    need(type(outside_reader_review_sha) is str and sha(reader_review_raw)==outside_reader_review_sha,
         'OUTSIDE_READER_REVIEW_PIN')
    need(type(review) is dict and set(review)==
         {'schema','verdict','attempt','source_manifest_sha256','source_package_manifest_sha256',
          'reader_manifest_sha256','receipt_sha256','terminal_sha256','external_sha256'} and
         review['schema']=='lab-successor-reader-effect-review/v1' and
         review['verdict']=='PASS_BOUNDED_READER_COLD_OPEN' and
         review['attempt']==str(READER_ATTEMPT) and
         review['source_manifest_sha256']==A.SOURCE_MANIFEST_SHA and
         review['source_package_manifest_sha256']==package_sha and
         review['reader_manifest_sha256']==reader_sha and
         review['receipt_sha256']==sha(reader_receipt_raw) and
         review['terminal_sha256']==sha(reader_terminal_raw) and
         review['external_sha256']==sha(reader_external_raw),
         'INDEPENDENT_READER_EFFECT_JOIN')
    pins={'source':A.SOURCE_MANIFEST_SHA,'package':package_sha,'reader':reader_sha}
    roles={name:project_role(name,(REPO/OLD/name).read_bytes(),pins) for name in PREIMAGES}
    rows=selected['reader_manifest']['files']+[
        {'path':READER+'/source-manifest.json','sha256':reader_sha}]+[
        {'path':MAPPER+'/'+name,'sha256':sha(raw)} for name,raw in roles.items()]
    need(len(rows)==len({r['path'] for r in rows})==953 and
         all(not r['path'].endswith('/branch.snapshot') for r in rows),'MAPPER_STATIC_CLOSURE')
    manifest={'schema_version':'lab-docker-distinct-mapper-source/v1-candidate',
              'authority_effect':'none','actual_owner_outcome':None,
              'fixture_only':True,'qualification':False,
              'environment':{'python':'3.14.4','jsonschema':'4.23.0','cryptography':'46.0.5'},
              'original_source_binding':{'path':SOURCE+'/source-manifest.json','sha256':pins['source']},
              'original_package_binding':{'path':SOURCE+'/packages/0001/manifest.json','sha256':pins['package']},
              'adapter_source_binding':{'path':READER+'/source-manifest.json','sha256':pins['reader']},
              'selected_native_executable':{'path':'/attempt/input/lab-context-native-reader','sha256':NATIVE_SHA},
              'files':sorted(rows,key=lambda r:r['path'])}
    verification=verify_output_template()
    return {'status':'MAPPER_DYNAMIC_SELECTION_ONLY','effect_enabled':False,
            'attempt':str(ATTEMPT),'source_package_manifest_sha256':package_sha,
            'reader_manifest_sha256':reader_sha,'reader_effect_review_sha256':outside_reader_review_sha,
            'mapper_manifest_sha256':sha(encoded(manifest)),'mapper_manifest':manifest,
            'projected_roles':roles,'output_contract':verification,
            'expected_package_members':OUTPUT_LEAVES}


def execute_mapper(*_args,**_kwargs):
    raise Refused('EFFECT_DISABLED_REVIEWED_FRESH_READER_AND_MAPPER_RELEASE_REQUIRED')
