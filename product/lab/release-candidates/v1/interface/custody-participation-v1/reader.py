"""Externally pinned read-only archive replay and original body context adapter."""
import base64,copy,re,tempfile
from contextlib import contextmanager
from dataclasses import asdict
from .base import *
from . import adapter
from .inspection import Inspection
def package(source_pin,package_pin):
    control=verify_source(source_pin);path=HERE/'packages/0001/manifest.json'
    require(sha(path.read_bytes())==package_pin,'independent participation package differs');m=load(path)
    require(set(m)==set('schema_version files source_manifest_binding archive_binding expected_replay_binding period_binding visibility public_package_export_allowed authority_effect actual_owner_outcome'.split())
        and m['schema_version']=='lab-owned-custody-participation-package/v1-candidate','closed source package required')
    require(m['authority_effect']=='none' and m['actual_owner_outcome'] is None and m['public_package_export_allowed'] is False
        and m['visibility']=='private-candidate-original-custody','source package cannot grant authority or export')
    require(m['source_manifest_binding']==binding(HERE/'source-manifest.json'),'package source closure differs')
    paths=set();prefix=(HERE/'packages/0001').relative_to(ROOT).as_posix()+'/'
    for b in m['files']:
        require(b['path'].startswith(prefix) and b['path'] not in paths,'source package file closure escaped');original(b);paths.add(b['path'])
    actual={p.relative_to(ROOT).as_posix() for p in (HERE/'packages/0001').rglob('*') if p.is_file() and p!=path}
    require(actual==paths,'source package original file closure differs')
    expected=parse(original(m['expected_replay_binding']))
    require(expected['engine_pins']==asdict(selected_pins()),'independent source engine pins differ')
    require((ROOT/m['archive_binding']['path']).stat().st_size<=64*1024*1024,'source archive exceeds byte bound')
    period=parse(original(m['period_binding']));prior=parse(original(period['inherited_validity_binding']))
    require(period['not_before']==prior['not_before'] and period['expires_at']==prior['expires_at'],'original absolute validity interval changed')
    return control,m,expected
def selection(source_pin,package_pin,name):
    require(name=='custody-participation','owned source nickname is closed');_,m,e=package(source_pin,package_pin)
    return {'name':name,'archive_binding':m['archive_binding'],'expected_replay_binding':m['expected_replay_binding'],
        'config_sha256':e['config_sha256'],'baseline_snapshot_digest':e['baseline_snapshot_digest'],'expected_head':e['expected_head'],
        'engine_pins':e['engine_pins'],'review_binding':binding(HERE/'packages/0001/review.json'),'candidate_selection_basis':{'manifest_sha256':package_pin,'source_manifest_sha256':source_pin},
        'authority_effect':'none','actual_owner_outcome':None}
@contextmanager
def open_signed(source_pin,package_pin):
    control,m,expected=package(source_pin,package_pin);row=selection(source_pin,package_pin,'custody-participation');a=parse(original(m['archive_binding']))
    require(a['schema_version']=='lab-owned-custody-participation-archive/v1-candidate' and a['private_keys_exported'] is False
        and a['Session_memory_rehydrated'] is False and a['authority_effect']=='none' and a['actual_owner_outcome'] is None,'archive contains forbidden authority/key/runtime state')
    require(a['engine_pins']==expected['engine_pins'],'archive executable differs')
    for key in ['config_sha256','baseline_snapshot_digest','expected_head']:require(a[key]==expected[key],'independent archive cut differs')
    head=parse(base64.b64decode(a['files']['HEAD.json']['base64_original_bytes'],validate=True))
    require(type(head['sequence']) is int and 0<=head['sequence']<=100,'transaction count bound exceeded')
    names={'config.json','baseline.json','HEAD.json'}|{f'transactions/{i:010d}.json' for i in range(head['sequence']+1)}
    require(set(a['files'])==names,'closed archived original store files required')
    pins=selected_pins()
    with tempfile.TemporaryDirectory(prefix='cal-R03-original-cold-source-') as temporary,loader.engine(pins) as handle:
        root=Path(temporary);store=root/'store';store.mkdir(mode=0o700);(store/'transactions').mkdir(mode=0o700);originals={}
        for name,b in a['files'].items():
            require(set(b)=={'sha256','base64_original_bytes'},'closed original archive entry required')
            raw=base64.b64decode(b['base64_original_bytes'],validate=True)
            require(base64.b64encode(raw).decode()==b['base64_original_bytes'] and sha(raw)==b['sha256'],'archive original bytes differ')
            fd=os.open(store/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'wb') as f:f.write(raw)
            originals[name]=raw
        data=handle.replay_owned(store,expected['config_sha256'],expected['baseline_snapshot_digest'],expected['expected_head'])
        require(handle.common.digest(data['projection'])==expected['projection_sha256']
            and [handle.common.digest(t) for t in data['transactions']]==expected['transaction_sha256s'],'cold signature/core/consequence/projection replay differs')
        view=Inspection(data,row,originals,handle)
        selected=adapter.SignedSources(view,source_pin,selection_reader=lambda name:selection(source_pin,package_pin,name))
        try:
            yield selected;selected.guard()
            require(all((store/name).read_bytes()==raw for name,raw in originals.items()),'cold reader changed original files')
            require({p.relative_to(store).as_posix() for p in store.rglob('*') if p.is_file()}==names,'cold reader created state or Session memory')
        finally:selected.close()
    require(not root.exists(),'owned cold read workspace remains')
