"""Fresh complete Source5/Reader4 union; facts deduplicated only inside this invocation."""
from dataclasses import asdict
import importlib.metadata,platform
from .base import *
from .bulk import _verify_files
SOURCE_PIN='dc0462ce29d24bf571b56c0c0eeafad0511812a8464ce66e52914671256e7cb4'
PACKAGE_PIN='8c34a37e1dfa185fc21f323aa08d99c4f097b413c3e0fcf90c0da6d98c731aaf'
PARENT_PIN='be0e1857cf667100ea2dd9c6b115d11032f28fbfdfba4e9234d94aff84f19fee'
def boundary(adapter_pin,source_pin,package_pin,*,additional_rows=()):
    require(source_pin==SOURCE_PIN and package_pin==PACKAGE_PIN,'independent original Source5 pins differ')
    ownraw=(ADAPTER_ROOT/'source-manifest.json').read_bytes()
    require(sha(ownraw)==adapter_pin,'independent selected union adapter differs')
    own=parse(ownraw)
    source_raw=(PRODUCER_ROOT/'source-manifest.json').read_bytes()
    parent_raw=(PARENT_ROOT/'source-manifest.json').read_bytes()
    package_raw=(PRODUCER_ROOT/'packages/0001/manifest.json').read_bytes()
    require(sha(source_raw)==source_pin and sha(parent_raw)==PARENT_PIN and sha(package_raw)==package_pin,'original source/adapter/package bytes changed')
    source_manifest=parse(source_raw);parent_manifest=parse(parent_raw);package_manifest=parse(package_raw)
    environment={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')}
    require(source_manifest['environment']==own['environment']==environment,'independent source environment differs')
    for m in [source_manifest,parent_manifest,package_manifest,own]:require(m['authority_effect']=='none' and m['actual_owner_outcome'] is None,'source grants no authority')
    require(own['original_source_binding']==binding(PRODUCER_ROOT/'source-manifest.json') and own['original_package_binding']==binding(PRODUCER_ROOT/'packages/0001/manifest.json') and own['original_adapter_binding']==binding(PARENT_ROOT/'source-manifest.json'),'selected original source family differs')
    rows={}
    for row in [*source_manifest['files'],*parent_manifest['files'],*package_manifest['files'],*own['files'],*additional_rows]:
        require(type(row) is dict and set(row)=={'path','sha256'},'closed exact source binding required')
        require(row['path'] not in rows or rows[row['path']]==row,'conflicting selected source digest')
        rows[row['path']]=row
    _verify_files(ROOT,[rows[name] for name in sorted(rows)])
    require(parent_manifest['producer_source_binding']==binding(PRODUCER_ROOT/'source-manifest.json') and parent_manifest['producer_package_binding']==binding(PRODUCER_ROOT/'packages/0001/manifest.json'),'original parent reader producer differs')
    declared=B.episode();value=package_manifest;path=PRODUCER_ROOT/'packages/0001/manifest.json'
    require(set(value)==set('schema_version files source_manifest_binding archive_binding expected_replay_binding period_binding episode_contract_binding visibility public_package_export_allowed authority_effect actual_owner_outcome'.split()),'closed current episode package required')
    require(value['schema_version']=='lab-owned-current-participation-package/v1-candidate' and value['source_manifest_binding']==binding(PRODUCER_ROOT/'source-manifest.json') and value['episode_contract_binding']==binding(PRODUCER_ROOT/'episode-contract.json'),'current episode package source differs')
    require(value['visibility']=='private-candidate-original-custody' and value['public_package_export_allowed'] is False,'original source public export not authorized')
    prefix=(PRODUCER_ROOT/'packages/0001').relative_to(ROOT).as_posix()+'/'
    names=[row['path'] for row in value['files']]
    require(len(names)==len(set(names)) and all(name.startswith(prefix) for name in names),'current package closure escaped')
    require(set(names)=={p.relative_to(ROOT).as_posix() for p in path.parent.rglob('*') if p.is_file() and p!=path},'complete current package tree differs')
    period=parse(original(value['period_binding']));C.validate_period(period,declared)
    expected=parse(original(value['expected_replay_binding']))
    require(expected['engine_pins']==asdict(B.selected_pins()),'original exact executable pins differ')
    require((ADAPTER_ROOT/'source-manifest.json').read_bytes()==ownraw and (PRODUCER_ROOT/'source-manifest.json').read_bytes()==source_raw and (PARENT_ROOT/'source-manifest.json').read_bytes()==parent_raw and path.read_bytes()==package_raw,'selected manifest changed during verification')
    return source_manifest,value,expected,own
