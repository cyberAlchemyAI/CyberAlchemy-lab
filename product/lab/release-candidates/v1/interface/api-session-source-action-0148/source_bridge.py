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
    if name=='workflow-participation':return workflow_selection()
    if name=='integrated-participation':return integrated_reader().selection(INTEGRATED_SOURCE_PIN,INTEGRATED_PACKAGE_PIN,'custody-participation')
    if name=='custody-participation':
        d=custody_delivery();return d.reader.selection(d.SOURCE_PIN,d.SOURCE_PACKAGE,name)
    if name=='fresh-participation':
        return fresh_reader().selection(FRESH_SOURCE_PIN,FRESH_PACKAGE_PIN,name)
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
    if name=='workflow-participation':
        reader=workflow_reader()
        with reader.open_signed(WORKFLOW_SOURCE_PIN,WORKFLOW_PACKAGE_PIN) as selected:
            selected.view.integrated_reader=reader
            yield selected.view
        return
    if name=='integrated-participation':
        reader=integrated_reader()
        with reader.open_signed(INTEGRATED_SOURCE_PIN,INTEGRATED_PACKAGE_PIN) as selected:
            selected.view.integrated_reader=reader
            yield selected.view
            selected.guard();reader.guard()
        return
    if name=='custody-participation':
        d=custody_delivery()
        with d.reader.open_signed(d.SOURCE_PIN,d.SOURCE_PACKAGE) as selected:
            selected.view.custody_signed_sources=selected
            yield selected.view
            selected.guard()
        return
    if name=='fresh-participation':
        with fresh_reader().open_signed(FRESH_SOURCE_PIN,FRESH_PACKAGE_PIN) as selected:
            selected.view.fresh_signed_sources=selected
            yield selected.view
            selected.guard()
        return
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

FRESH_SOURCE_PIN='f82b3813bc9b674c3f018997414f33a918b4d625fa85f0a36c8ff41e1978f368'
FRESH_PACKAGE_PIN='95479689686c63590d8e98960a297455f9d3fa053ae11847d0c7d3965a1b2ad3'
def fresh_reader():
    # Deferred import preserves this API's exact protocol module selection.
    path=HERE.parent/'session-participation-v2'
    saved=sys.path[:]
    sys.path.insert(0,str(path))
    try:import reader
    finally:sys.path[:]=saved
    require(Path(reader.__file__).resolve()==path/'reader.py','unselected fresh source reader')
    return reader


def custody_delivery():
    """Explicit same-package new-source selection; no bare global reader import."""
    name='_cal_api_union_custody_action_0148';path=HERE.parent/'current-context-delivery-action-0148'
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    module=__import__(name+'.build',fromlist=['preflight'])
    require(Path(module.__file__).resolve()==path/'build.py','unselected original Context producer')
    borrowed = module.FACT_SCOPE.active_scope()
    if borrowed is None:
        module.preflight('589a1525ecd5af370f8be57e8deb871420a049413579a8ff5e0c3cce00625589')
    else:
        require(borrowed.producer is module, 'borrowed producer selection differs')
        pin = '589a1525ecd5af370f8be57e8deb871420a049413579a8ff5e0c3cce00625589'
        # Existing Session scopes register verify_source, which delegates to
        # this exact preflight. Candidate calculation scopes register preflight.
        # Either original callback must have run at this scope's full boundaries.
        checker = module.preflight if any(check is module.preflight and selected == pin
                    for check, selected in borrowed.package_checks) else module.verify_source
        module.FACT_SCOPE.package_guard(borrowed.parent, checker, pin)
    return module

def inspection(data,selected,originals,handle):
    integrated_path='product/lab/release-candidates/v1/interface/current-participation-v8/packages/0001/branch.snapshot'
    workflow_path='product/lab/release-candidates/v1/interface/current-participation-v11/packages/0001/branch.snapshot'
    if selected['archive_binding']['path']==workflow_path:
        require(selected['archive_binding']==workflow_selection()['archive_binding'],'workflow archive pin differs')
        cls=workflow_reader().Inspection
    elif selected['archive_binding']['path']==integrated_path:
        require(selected['archive_binding']==integrated_selection()['archive_binding'],'integrated archive pin differs')
        cls=integrated_reader().Inspection
    else:cls=custody_delivery().reader.Inspection if selected['name']=='custody-participation' else Inspection
    return cls(data,selected,originals,handle)

def selected_profile_sha(view):
    return view.handle.manifest['profile_binding']['sha256'] if view.selected['name']=='custody-participation' else PINS.profile_sha256

INTEGRATED_SOURCE_PIN='cc484b86ba0e8a2d1e07f1e8d640db055250f5aa5075450c8e8b7acc7cdebf36'
INTEGRATED_PACKAGE_PIN='c0a01500743d01c5b487b83b219b184fbc14259bc49dde2f36cad684a70e4f4f'
INTEGRATED_ADAPTER_PIN='78d8150086ed41f6f2c2218805a2387caab1e5931b2619a894330557cb30d23c'
def integrated_reader():
    name='_cal_api87_integrated_reader7';path=HERE.parent/'current-source-adapter-v7'
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    module=__import__(name+'.reader',fromlist=['SelectedReader'])
    require(Path(module.__file__).resolve()==path/'reader.py','foreign integrated reader code')
    return module.SelectedReader(INTEGRATED_ADAPTER_PIN,INTEGRATED_SOURCE_PIN,INTEGRATED_PACKAGE_PIN)
def integrated_selection():return integrated_reader().selection(INTEGRATED_SOURCE_PIN,INTEGRATED_PACKAGE_PIN,'custody-participation')
def integrated_bindings():
    paths={'adapter_binding':HERE.parent/'current-source-adapter-v7/source-manifest.json','source_binding':HERE.parent/'current-participation-v8/source-manifest.json','package_binding':HERE.parent/'current-participation-v8/packages/0001/manifest.json'}
    expected={'adapter_binding':INTEGRATED_ADAPTER_PIN,'source_binding':INTEGRATED_SOURCE_PIN,'package_binding':INTEGRATED_PACKAGE_PIN}
    result={key:{'ref':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())} for key,path in paths.items()}
    require(all(result[key]['sha256']==expected[key] for key in result),'integrated independent selection changed')
    return result

# Filled only by the integration freezer after the exact owned source and
# adapter packages have completed construction and independent checks.
WORKFLOW_SOURCE_PIN='4e321b369c6d8052fd8ff71dad45346cfa512d67e34ed55847dff3b6234288a9'
WORKFLOW_PACKAGE_PIN='690119f3a3d4f832fe5b2502385e1f490623f042500e2c41c952de42a1ccc32a'
WORKFLOW_ADAPTER_PIN='6156264caac4ce8c91b68ca39076c3582afbfee4363f9ec64221e82d3f4b5d72'
def workflow_reader():
    require(isinstance(WORKFLOW_PACKAGE_PIN,str) and isinstance(WORKFLOW_ADAPTER_PIN,str),
        'workflow source/adapter selection is not frozen')
    name='_cal_api_workflow_reader9';path=HERE.parent/'current-source-adapter-v9'
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    selected=__import__(name+'.reader',fromlist=['SelectedReader'])
    require(Path(selected.__file__).resolve()==path/'reader.py','foreign workflow reader code')
    return selected.SelectedReader(WORKFLOW_ADAPTER_PIN,WORKFLOW_SOURCE_PIN,WORKFLOW_PACKAGE_PIN)
def workflow_selection():return workflow_reader().selection(WORKFLOW_SOURCE_PIN,WORKFLOW_PACKAGE_PIN,'custody-participation')
def workflow_bindings():
    paths={'adapter_binding':HERE.parent/'current-source-adapter-v9/source-manifest.json',
        'source_binding':HERE.parent/'current-participation-v11/source-manifest.json',
        'package_binding':HERE.parent/'current-participation-v11/packages/0001/manifest.json'}
    pins={'adapter_binding':WORKFLOW_ADAPTER_PIN,'source_binding':WORKFLOW_SOURCE_PIN,'package_binding':WORKFLOW_PACKAGE_PIN}
    result={key:{'ref':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())} for key,p in paths.items()}
    require(all(result[k]['sha256']==pins[k] for k in result),'independent workflow source selection changed')
    return result
def reader_factory(view):
    if type(view).__module__=='_cal_api_workflow_reader9.inspection':return workflow_reader
    require(type(view).__module__=='_cal_api87_integrated_reader7.inspection','unselected integrated reader family')
    return integrated_reader
def reader_for_view(view):return reader_factory(view)()
