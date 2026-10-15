"""Independently selected legacy and exact correction histories; public reads only."""
import base64
from contextlib import contextmanager
import importlib.util
from pathlib import Path
import sys
import tempfile

HERE=Path(__file__).resolve().parent
def imported(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module

legacy=imported('_R03_immutable_operator_reader',HERE.parent/'inspection/lab_operator.py')
correction=imported('_R03_correction_reader_loader',HERE.parent/'corrections-v1/loader.py')
ROOT=legacy.ROOT
sha=legacy.sha;parse=legacy.parse;encoded=legacy.encoded;original=legacy.original;require=legacy.require;bind=legacy.bind
Inspection=legacy.Inspection;facets=legacy.facets;differences=legacy.differences
PINS=legacy.PINS
SELECTION=HERE/'source-selection.json'
SELECTION_SHA='2d0e1a91acd2266e5cf2ff98f1cc426f48c7ec54adbfbc877366ea1cc908813d'
MAX_ARCHIVE=legacy.MAX_ARCHIVE
CLAIM='Exact private independently selected signed candidate history; correction authority is limited to its owned fixture. No canonical admission, human pilot or live runtime outcome.'


def source_selection(name):
    require(sha(SELECTION.read_bytes())==SELECTION_SHA,'independent corrected reader source selection differs')
    value=parse(SELECTION.read_bytes())
    require(value['schema_version']=='lab-R03-inspection-selection/v2-candidate' and value['authority_effect']=='none'
        and value['actual_owner_outcome'] is None,'source selection cannot grant owner authority')
    rows=[r for r in value['sources'] if r['name']==name];require(len(rows)==1,'selected source not found')
    row=rows[0]
    if name!='reference-corrected':require(row==legacy.source_selection(name),'immutable predecessor source selection differs')
    return row


@contextmanager
def replay_source(name,*,source_repo=ROOT):
    row=source_selection(name)
    if name!='reference-corrected':
        with legacy.replay_source(name,source_repo=source_repo) as view:yield view
        source_selection(name);return
    pins=correction.EnginePins(**row['engine_pins']);correction.verify_engine(pins)
    archive_path=ROOT/row['archive_binding']['path'];require(archive_path.stat().st_size<=MAX_ARCHIVE,'selected archive exceeds bounded input')
    archive=parse(original(row['archive_binding']));expected=parse(original(row['expected_replay_binding']))
    proof=parse(original(row['correction_proof_binding']))
    require(proof['result']=='PASS' and proof['task_complete'] is False and proof['actual_owner_outcome'] is None
        and proof['authority_effect']=='none' and proof['canonical_effects_applied']==proof['source_effects_applied']==0,
        'exact correction evidence does not establish candidate read basis')
    require(archive['schema_version']=='lab-reference-correction-archive/v1-candidate' and archive['authority_effect']=='none'
        and archive['actual_owner_outcome'] is None and archive['private_keys_exported'] is False,'archive includes forbidden authority or key state')
    require(archive['engine_pins']==expected['engine_pins']==row['engine_pins'],'selected corrected executable differs')
    for key in ['config_sha256','baseline_snapshot_digest','expected_head']:
        require(archive[key]==expected[key]==row[key],'independent corrected cut differs')
    require(expected['archive_sha256']==row['archive_binding']['sha256'],'independent expected archive differs')
    head=parse(base64.b64decode(archive['files']['HEAD.json']['base64_original_bytes'],validate=True))
    require(type(head['sequence']) is int and 0<=head['sequence']<=100,'reader transaction budget exceeded')
    names={'config.json','baseline.json','HEAD.json'}|{f'transactions/{i:010d}.json' for i in range(head['sequence']+1)}
    require(set(archive['files'])==names,'closed original corrected store files required')
    with tempfile.TemporaryDirectory(prefix='cal-R03-corrected-reader-') as temporary,correction.engine(pins) as handle:
        store=Path(temporary)/'store';store.mkdir();(store/'transactions').mkdir();originals={}
        for name,b in archive['files'].items():
            require(set(b)=={'sha256','base64_original_bytes'},'closed original archive byte binding required')
            raw=base64.b64decode(b['base64_original_bytes'],validate=True);require(sha(raw)==b['sha256'],'corrected original bytes differ')
            parse(raw)
            with (store/name).open('xb') as stream:stream.write(raw)
            originals[name]=raw
        require(sha(originals['config.json'])==row['config_sha256'],'independently pinned corrected configuration differs')
        config=parse(originals['config.json'])
        require(config['correction_engine_id']==pins.engine_id and config['correction_profile_binding']==handle.manifest['correction_profile_binding']
            and config['endpoint_mapping_binding']==handle.manifest['mapping_binding'],'selected correction profile/configuration differs')
        data=handle.store_module.Store(store,Path(source_repo)).replay()
        require(data['head']['transaction_digest']==row['expected_head'] and data['baseline']['snapshot_digest']==row['baseline_snapshot_digest']
            and handle.common.digest(data['projection'])==expected['projection_sha256']
            and [handle.common.digest(t) for t in data['transactions']]==expected['transaction_sha256s'],'original corrected signature/projection replay differs')
        yield Inspection(data,row,originals,handle)
        source_selection('reference-corrected')
        require(all((store/name).read_bytes()==raw for name,raw in originals.items()),'reader changed original corrected store bytes')
        require({p.relative_to(store).as_posix() for p in store.rglob('*') if p.is_file()}==names,'reader created store or Session state')
