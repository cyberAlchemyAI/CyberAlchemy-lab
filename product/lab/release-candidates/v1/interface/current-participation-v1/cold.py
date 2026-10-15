"""Exact signed read-only source for a separately bounded new episode."""
import base64
from contextlib import contextmanager
from dataclasses import asdict
import tempfile
from types import SimpleNamespace
from .base import *
from . import records

def validate_period(value, declared):
    require(set(value)==set('schema_version period_ref not_before expires_at principal_ref assignment_version_ref episode_contract_binding original_expired_period_binding constructed_at authority_effect actual_owner_outcome claim_ceiling'.split()),'closed new episode period required')
    require(value['schema_version']=='lab-owned-absolute-participation-period/v1-candidate' and value['authority_effect']=='none' and value['actual_owner_outcome'] is None,'new period cannot claim authority')
    require(all(value[key]==declared[key] for key in ['period_ref','not_before','expires_at','principal_ref','assignment_version_ref']),'new fixed period or identity differs')
    require(value['episode_contract_binding']==binding(HERE/'episode-contract.json') and value['original_expired_period_binding']==declared['old_episode_period_binding'],'new episode/original expired source bindings differ')
    require(value['principal_ref']==records.PRINCIPAL and value['assignment_version_ref']==records.ASSIGNMENT+'@'+records.VERSION and value['period_ref']==records.PERIOD,'new independent episode identities differ')

def package(source_pin, package_pin):
    verify_source(source_pin);declared=episode();path=HERE/'packages/0001/manifest.json'
    require(sha(path.read_bytes())==package_pin,'independent current episode package differs')
    value=load(path)
    require(set(value)==set('schema_version files source_manifest_binding archive_binding expected_replay_binding period_binding episode_contract_binding visibility public_package_export_allowed authority_effect actual_owner_outcome'.split()),'closed current episode package required')
    require(value['schema_version']=='lab-owned-current-participation-package/v1-candidate' and value['source_manifest_binding']==binding(HERE/'source-manifest.json') and value['episode_contract_binding']==binding(HERE/'episode-contract.json'),'current episode package source differs')
    require(value['visibility']=='private-candidate-original-custody' and value['public_package_export_allowed'] is False and value['authority_effect']=='none' and value['actual_owner_outcome'] is None,'current source does not authorize public export or admission')
    prefix=(HERE/'packages/0001').relative_to(ROOT).as_posix()+'/'
    paths=set()
    for row in value['files']:
        require(row['path'].startswith(prefix) and row['path'] not in paths,'current package closure escaped')
        original(row);paths.add(row['path'])
    require(paths=={p.relative_to(ROOT).as_posix() for p in path.parent.rglob('*') if p.is_file() and p!=path},'complete current episode package closure differs')
    period=parse(original(value['period_binding']));validate_period(period,declared)
    expected=parse(original(value['expected_replay_binding']))
    require(expected['engine_pins']==asdict(selected_pins()),'current source exact executable pins differ')
    return value,expected,period

@contextmanager
def open_source(source_pin, package_pin):
    manifest,expected,period=package(source_pin,package_pin)
    require((ROOT/manifest['archive_binding']['path']).stat().st_size<=64*1024*1024,'bounded original source archive required')
    archive=parse(original(manifest['archive_binding']))
    require(archive['private_keys_exported'] is False and archive['Session_memory_rehydrated'] is False and archive['authority_effect']=='none' and archive['actual_owner_outcome'] is None,'new source archive contains forbidden state')
    require(archive['engine_pins']==expected['engine_pins'],'new source archive engine differs')
    for key in ['config_sha256','baseline_snapshot_digest','expected_head']:
        require(archive[key]==expected[key],'new source archive cut differs')
    head=parse(base64.b64decode(archive['files']['HEAD.json']['base64_original_bytes'],validate=True))
    require(type(head['sequence']) is int and 0<=head['sequence']<=100,'bounded source transaction closure required')
    names={'config.json','baseline.json','HEAD.json'}|{f'transactions/{i:010d}.json' for i in range(head['sequence']+1)}
    require(set(archive['files'])==names,'complete original source files required')
    with tempfile.TemporaryDirectory(prefix='cal-R03-current-episode-cold-0001-') as temporary,loader.engine(selected_pins()) as handle:
        root=Path(temporary);store=root/'store';store.mkdir(mode=0o700);(store/'transactions').mkdir(mode=0o700);originals={}
        for name,row in archive['files'].items():
            require(set(row)=={'sha256','base64_original_bytes'},'closed original archive entry required')
            raw=base64.b64decode(row['base64_original_bytes'],validate=True)
            require(sha(raw)==row['sha256'] and base64.b64encode(raw).decode()==row['base64_original_bytes'],'new source original bytes differ')
            descriptor=os.open(store/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(descriptor,'wb') as stream:stream.write(raw)
            originals[name]=raw
        data=handle.replay_owned(store,expected['config_sha256'],expected['baseline_snapshot_digest'],expected['expected_head'])
        require(handle.common.digest(data['projection'])==expected['projection_sha256'] and [handle.common.digest(t) for t in data['transactions']]==expected['transaction_sha256s'],'new source signed cold replay differs')
        yield SimpleNamespace(root=root,store=store,data=data,originals=originals,handle=handle,period=period,expected=expected,manifest=manifest)
        require(all((store/name).read_bytes()==raw for name,raw in originals.items()),'cold reader changed signed original source')
        require({p.relative_to(store).as_posix() for p in store.rglob('*') if p.is_file()}==names,'cold reader created Agent or Session state')
        package(source_pin,package_pin)
    require(not root.exists(),'new independently owned cold workspace remains')
