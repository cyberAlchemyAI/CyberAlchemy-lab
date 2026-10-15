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
    if name in (CURRENT_LEGACY_NAME,CURRENT_SOURCE8_NAME):
        d=current_legacy_delivery() if name==CURRENT_LEGACY_NAME else current_session_fixture_delivery()
        return d.reader.selection(d.SOURCE_PIN,d.SOURCE_PACKAGE,'custody-participation')
    if name=='legacy-session-fixture':
        d=legacy_delivery();return d.reader.selection(d.SOURCE_PIN,d.SOURCE_PACKAGE,'custody-participation')
    if name in (SOURCE8_SESSION_NAME,'source8-lesson-fixture-participation'):
        d=source8_delivery_for(name);return d.reader.selection(d.SOURCE_PIN,d.SOURCE_PACKAGE,'custody-participation')
    if name in HISTORY_NAMES:return history_selection(name)
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
    if name in HISTORY_NAMES:
        require(source_repo==ROOT,'history sources require their exact original repository')
        with history_provider().open_history(HISTORY_PROVIDER_PIN,HISTORY_SELECTION_PIN,name) as view:yield view
        return
    row=source_selection(name)
    if name in (CURRENT_LEGACY_NAME,CURRENT_SOURCE8_NAME):
        require(source_repo==ROOT,'current fixture requires exact original repository')
        d=current_legacy_delivery() if name==CURRENT_LEGACY_NAME else current_session_fixture_delivery()
        expected=CURRENT_LEGACY_STORE if name==CURRENT_LEGACY_NAME else CURRENT_SOURCE8_STORE
        with d.reader.open_signed(d.SOURCE_PIN,d.SOURCE_PACKAGE) as selected:
            require(type(selected) is d.reader.adapter.SignedSources and type(selected.view) is d.reader.Inspection
                and selected.source_cut['store_ref']==expected and selected.source_cut['branch_ref']=='branch:'+expected
                and selected.selected['name']=='custody-participation','actual current source class/cut/ABI differs')
            if name==CURRENT_LEGACY_NAME:
                selected.view.legacy_signed_sources=selected;selected.view.legacy_context_producer=d
            else:selected.view.source8_context_producer=d
            selected.view.integrated_reader=d.reader
            yield selected.view
            selected.guard();d.reader.guard()
        return
    if name=='legacy-session-fixture':
        require(source_repo==ROOT,'legacy fixture requires original source repository')
        d=legacy_delivery()
        with d.reader.open_signed(d.SOURCE_PIN,d.SOURCE_PACKAGE) as selected:
            require(type(selected) is d.reader.adapter.SignedSources and type(selected.view) is d.reader.Inspection and selected.source_cut['store_ref']=='R03-legacy-session-fixture-0257','actual distinct legacy signed source required')
            selected.view.legacy_signed_sources=selected
            selected.view.legacy_context_producer=d
            yield selected.view
            selected.guard();d.reader.guard()
        return
    if name in (SOURCE8_SESSION_NAME,'source8-lesson-fixture-participation'):
        d=source8_delivery_for(name)
        with d.reader.open_signed(d.SOURCE_PIN,d.SOURCE_PACKAGE) as selected:
            require(type(selected) is d.reader.adapter.SignedSources,'actual Source8 signed reader required')
            selected.view.source8_context_producer=d
            selected.view.integrated_reader=d.reader
            yield selected.view
            selected.guard();d.reader.guard()
        return
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
    name='_cal_api_union_custody_v2_action_0148';path=HERE.parent/'current-context-delivery-v2-action-0148'
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    module=__import__(name+'.build',fromlist=['preflight'])
    require(Path(module.__file__).resolve()==path/'build.py','unselected original Context producer')
    borrowed = module.FACT_SCOPE.active_scope()
    if borrowed is None:
        module.preflight('99e701e592490486cf64949b68d5d2e266a176424720af1a944740a1e23a6654')
    else:
        require(borrowed.producer is module, 'borrowed producer selection differs')
        pin = '99e701e592490486cf64949b68d5d2e266a176424720af1a944740a1e23a6654'
        # Existing Session scopes register verify_source, which delegates to
        # this exact preflight. Candidate calculation scopes register preflight.
        # Either original callback must have run at this scope's full boundaries.
        checker = module.preflight if any(check is module.preflight and selected == pin
                    for check, selected in borrowed.package_checks) else module.verify_source
        module.FACT_SCOPE.package_guard(borrowed.parent, checker, pin)
    return module

def inspection(data,selected,originals,handle,*,origin_view=None):
    if origin_view is not None and legacy_session_view(origin_view):
        d=origin_view.legacy_context_producer;reader=d.reader
        require(selected==origin_view.selected and originals is origin_view.originals and handle is origin_view.handle,'legacy prefix selected/originals/handle identity differs')
        view=reader.Inspection(data,selected,originals,handle)
        view.legacy_context_producer=d;view.legacy_original_view=origin_view
        view.legacy_signed_sources=origin_view.legacy_signed_sources
        view.custody_signed_sources=origin_view.custody_signed_sources
        return view
    if origin_view is not None and source8_session_view(origin_view):
        reader=reader_for_view(origin_view)
        require(selected==origin_view.selected and originals is origin_view.originals and handle is origin_view.handle,
            'actual Source8 prefix source origin differs')
        view=reader.Inspection(data,selected,originals,handle)
        view.source8_context_producer=origin_view.source8_context_producer
        view.source8_original_view=origin_view
        view.integrated_reader=reader
        view.custody_signed_sources=origin_view.custody_signed_sources
        return view
    if selected['name'] in HISTORY_NAMES:
        return history_provider().inspect_view(data,selected,originals,handle,HISTORY_PROVIDER_PIN,HISTORY_SELECTION_PIN)
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
    if view.selected['name'] in HISTORY_NAMES:return view.handle.manifest['profile_binding']['sha256']
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
    if legacy_session_view(view):
        d=view.legacy_context_producer;reader=d.reader;module=sys.modules.get(type(reader).__module__)
        reader_path=ROOT/CURRENT_LEGACY_READER/'reader.py' if d.HERE==ROOT/CURRENT_LEGACY_CONTEXT else HERE.parent/'legacy-session-fixture-reader-v1-action-0148/reader.py'
        require(module is not None and Path(module.__file__).resolve()==reader_path and type(reader) is module.SelectedReader and reader.adapter is module.adapter,'actual legacy reader class/origin differs')
        return lambda:reader
    producer=getattr(view,'source8_context_producer',None)
    if producer is not None:
        reader=producer.reader
        reader_module=sys.modules.get(type(reader).__module__)
        if producer.HERE==ROOT/CURRENT_SOURCE8_CONTEXT:
            reader_path=ROOT/CURRENT_SOURCE8_READER/'reader.py';class_name='CurrentFixtureReader'
        else:
            folder='source8-lesson-fixture-reader-v4-action-0148' if reader.HERE.name=='source8-lesson-fixture-source-v4-action-0148' else 'current-source-adapter-v7'
            reader_path=HERE.parent/folder/'reader.py';class_name='FixtureReader' if folder.startswith('source8-lesson-fixture') else 'SelectedReader'
        require(reader_module is not None and Path(reader_module.__file__).resolve()==reader_path
            and type(reader) is getattr(reader_module,class_name)
            and reader.adapter is reader_module.adapter,
            'actual independently selected Source8 reader code origin differs')
        origin=getattr(view,'source8_original_view',view)
        require(type(view) is reader.Inspection and type(origin) is reader.Inspection
            and view.custody_signed_sources.view is origin
            and type(view.custody_signed_sources) is reader.adapter.SignedSources,
            'actual Source8 reader/view/signature source origin differs')
        require(getattr(origin,'source8_context_producer',None) is producer
            and view.selected==origin.selected,'actual Source8 prefix producer selection differs')
        require(getattr(view,'integrated_reader',None) is reader,'actual Source8 model reader marker differs')
        return lambda:reader
    if type(view).__module__=='_cal_api_workflow_reader9.inspection':return workflow_reader
    require(type(view).__module__=='_cal_api87_integrated_reader7.inspection','unselected integrated reader family')
    return integrated_reader
def reader_for_view(view):return reader_factory(view)()

# Explicit original histories, independent of current Source5/Source8 Sessions.
HISTORY_NAMES=('genuine-C12-history','genuine-W06-history','genuine-W09-learning-history',
    'genuine-W09-engineering-history','genuine-W09-research-history')
HISTORY_PROVIDER_PIN='ed47332f2c879895459284ed9a056a13f60c103566c4601ee9df5bb32104024e'
HISTORY_SELECTION_PIN='4debf58e1ccf0932dd63b0f8d2fb314c76b657aea2735bf6c01b6e98dc9c0c32'
def history_provider():
    name='_cal_genuine_work_history_v1_0208';path=HERE.parent/'genuine-work-history-v1-0208'
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    module=__import__(name+'.provider',fromlist=['selection'])
    require(Path(module.__file__).resolve()==path/'provider.py','foreign original-history provider')
    module.verify(HISTORY_PROVIDER_PIN)
    return module
def history_selection(name):
    return history_provider().selection(HISTORY_PROVIDER_PIN,HISTORY_SELECTION_PIN,name)
def validate_history_policy(policy):
    return history_provider().validate_policy(policy,HISTORY_PROVIDER_PIN,HISTORY_SELECTION_PIN)
def history_evidence(view,subject):
    provider=history_provider()
    require(type(view.genuine_history) is provider.HistoryEvidence
        and view.genuine_history.source_pin==HISTORY_PROVIDER_PIN
        and view.genuine_history.selection_pin==HISTORY_SELECTION_PIN,'foreign history evidence custodian')
    return view.genuine_history.evidence(subject)


SOURCE8_SESSION_NAME='source8-session-participation'
SOURCE8_DELIVERY_PIN='0017f4455df9d829368cb6448f0063f470283ef175f5f9cdb1836043488760e3'
def source8_delivery():
    name='_cal_api13_source8_context3';path=HERE.parent/'source8-context-delivery-v3-action-0148'
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    module=__import__(name+'.build',fromlist=['preflight'])
    require(Path(module.__file__).resolve()==path/'build.py','unselected Source8 Context producer')
    scope=module.FACT_SCOPE.active_scope()
    if scope is None:module.preflight(SOURCE8_DELIVERY_PIN)
    else:
        require(scope.producer is module,'foreign borrowed Source8 producer')
        checker=module.preflight if any(check is module.preflight and pin==SOURCE8_DELIVERY_PIN for check,pin in scope.package_checks) else module.verify_source
        module.FACT_SCOPE.package_guard(scope.parent,checker,SOURCE8_DELIVERY_PIN)
    return module

def source8_session_view(view):
    selected=getattr(view,'custody_signed_sources',None)
    return getattr(view,'source8_context_producer',None) is not None and selected is not None


FIXTURE_DELIVERY_PIN='0afe7a76c15a26df9f10b0691fb240f6955f772e778e58820cc0d6dc0d0565d3'
def source8_fixture_delivery():
    name='_cal_api13_source8_fixture_context1';path=HERE.parent/'source8-lesson-fixture-context-v1-action-0148'
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    module=__import__(name+'.build',fromlist=['preflight'])
    require(Path(module.__file__).resolve()==path/'build.py','unselected fixture Context producer')
    scope=module.FACT_SCOPE.active_scope()
    if scope is None:module.preflight(FIXTURE_DELIVERY_PIN)
    else:
        require(scope.producer is module,'foreign borrowed fixture producer')
        checker=module.preflight if any(check is module.preflight and pin==FIXTURE_DELIVERY_PIN for check,pin in scope.package_checks) else module.verify_source
        module.FACT_SCOPE.package_guard(scope.parent,checker,FIXTURE_DELIVERY_PIN)
    return module


def source8_delivery_for(name):
    if name==CURRENT_SOURCE8_NAME:return current_session_fixture_delivery()
    require(name in ('source8-session-participation','source8-lesson-fixture-participation',CURRENT_SOURCE8_NAME),'unselected Source8 family')
    if name=='source8-session-participation':return source8_delivery()
    return source8_fixture_delivery()

def source8_period_path(name):
    if name==CURRENT_SOURCE8_NAME:return ROOT/CURRENT_SOURCE8_SOURCE/'packages/0001/period.json'
    require(name in ('source8-session-participation','source8-lesson-fixture-participation',CURRENT_SOURCE8_NAME),'unselected Source8 period family')
    folder='current-participation-v8' if name=='source8-session-participation' else 'source8-lesson-fixture-source-v4-action-0148'
    return HERE.parent/folder/'packages/0001/period.json'

def source8_bindings(name):
    d=source8_delivery_for(name)
    period=source8_period_path(name)
    require(period==d.reader.HERE/'packages/0001/period.json','actual Source8 reader period origin differs')
    def selected(path):return {'ref':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}
    return {'source_binding':selected(d.reader.HERE/'source-manifest.json'),
        'package_binding':selected(d.reader.HERE/'packages/0001/manifest.json'),
        'period_binding':selected(period),'context_source_binding':selected(d.HERE/'source-manifest.json')}

def source8_profile_binding(name):
    d=source8_delivery_for(name)
    row=d.reader.selection(d.SOURCE_PIN,d.SOURCE_PACKAGE,'custody-participation')
    path=HERE.parent/'custody-correction-v4/runtime/profile.json'
    require(sha(path.read_bytes())==row['engine_pins']['profile_sha256'],'Source8 selected actual native profile differs')
    return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}

LEGACY_DELIVERY_PIN='8501857f8219e0f797c323813a2857aa3e78a4b14297b44ebe7b98361102b496'
def legacy_delivery():
    name='_cal_api_distinct_legacy_context_0257';path=HERE.parent/'legacy-session-fixture-context-v1-action-0148'
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    module=__import__(name+'.build',fromlist=['preflight'])
    require(Path(module.__file__).resolve()==path/'build.py','unselected legacy Context producer')
    scope=module.FACT_SCOPE.active_scope()
    if scope is None:module.preflight(LEGACY_DELIVERY_PIN)
    else:
        require(scope.producer is module,'foreign borrowed legacy producer')
        checker=module.preflight if any(check is module.preflight and pin==LEGACY_DELIVERY_PIN for check,pin in scope.package_checks) else module.verify_source
        module.FACT_SCOPE.package_guard(scope.parent,checker,LEGACY_DELIVERY_PIN)
    return module

def legacy_session_view(view):
    if not hasattr(view,'legacy_signed_sources'):return False
    producer=view.legacy_context_producer
    current=producer.HERE==ROOT/CURRENT_LEGACY_CONTEXT
    d=current_legacy_delivery() if current else legacy_delivery();selected=view.legacy_signed_sources;origin=getattr(view,'legacy_original_view',view)
    require(view.legacy_context_producer is d and type(view) is d.reader.Inspection and type(origin) is d.reader.Inspection
        and type(selected) is d.reader.adapter.SignedSources and selected is view.custody_signed_sources
        and selected.view is origin and selected.source_cut['store_ref']==(CURRENT_LEGACY_STORE if current else 'R03-legacy-session-fixture-0257')
        and selected.selected['name']=='custody-participation','legacy marker source/type/cut differs')
    return True

def legacy_profile_binding(name='legacy-session-fixture'):
    d=legacy_delivery_for(name);row=d.reader.selection(d.SOURCE_PIN,d.SOURCE_PACKAGE,'custody-participation')
    path=HERE.parent/'custody-correction-v4/runtime/profile.json'
    require(sha(path.read_bytes())==row['engine_pins']['profile_sha256'],'legacy native profile differs')
    return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}


# Independently captured current technical fixture selections; no old renewal.
CURRENT_LEGACY_NAME='completion-legacy:legacy-diagnostic-0001'
CURRENT_SOURCE8_NAME='completion-current-participation:diagnostic-0004'
CURRENT_LEGACY_STORE='completion-legacy-diagnostic-0001'
CURRENT_SOURCE8_STORE='completion-current-session-0001-diagnostic-0004'
CURRENT_LEGACY_CONTEXT='product/lab/release-candidates/v1/interface/current-session-fixtures-v1-completion-0001/instances/legacy-diagnostic-0001/context'
CURRENT_SOURCE8_CONTEXT='product/lab/release-candidates/v1/interface/current-session-fixtures-v1-completion-0001/instances/diagnostic-0004/context'
CURRENT_LEGACY_READER='product/lab/release-candidates/v1/interface/current-session-fixtures-v1-completion-0001/instances/legacy-diagnostic-0001/reader'
CURRENT_SOURCE8_READER='product/lab/release-candidates/v1/interface/current-session-fixtures-v1-completion-0001/instances/diagnostic-0004/reader'
CURRENT_LEGACY_SOURCE='product/lab/release-candidates/v1/interface/current-session-fixtures-v1-completion-0001/instances/legacy-diagnostic-0001/source'
CURRENT_SOURCE8_SOURCE='product/lab/release-candidates/v1/interface/current-session-fixtures-v1-completion-0001/instances/diagnostic-0004/source'
CURRENT_LEGACY_DELIVERY_PIN='c73235f7c7b26d897a6ddc2e19c0ec9bdcf71a424738fc492699e7f1f11d1993'
CURRENT_SOURCE8_DELIVERY_PIN='6f1fb3fcd9f487b76f5e1708a7bda1b157a4bbbb42bfef1e3baae9f350410071'

def _current_delivery(name,path,pin):
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
        package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    module=__import__(name+'.build',fromlist=['preflight'])
    require(Path(module.__file__).resolve()==path/'build.py' and module.HERE==path,'current Context producer origin differs')
    scope=module.FACT_SCOPE.active_scope()
    if scope is None:module.preflight(pin)
    else:
        require(scope.producer is module,'foreign current borrowed producer')
        checker=module.preflight if any(check is module.preflight and selected==pin for check,selected in scope.package_checks) else module.verify_source
        module.FACT_SCOPE.package_guard(scope.parent,checker,pin)
    return module
def current_legacy_delivery():return _current_delivery('_cal_api17_current_legacy_diagnostic0001',ROOT/CURRENT_LEGACY_CONTEXT,CURRENT_LEGACY_DELIVERY_PIN)
def current_session_fixture_delivery():return _current_delivery('_cal_api17_current_source8_diagnostic0004',ROOT/CURRENT_SOURCE8_CONTEXT,CURRENT_SOURCE8_DELIVERY_PIN)
def legacy_delivery_for(name):
    require(name in ('legacy-session-fixture',CURRENT_LEGACY_NAME),'unselected legacy family')
    return current_legacy_delivery() if name==CURRENT_LEGACY_NAME else legacy_delivery()
def legacy_period_path(name):
    require(name in ('legacy-session-fixture',CURRENT_LEGACY_NAME),'unselected legacy period family')
    return ROOT/CURRENT_LEGACY_SOURCE/'packages/0001/period.json' if name==CURRENT_LEGACY_NAME else HERE.parent/'legacy-session-fixture-source-v1-action-0148/packages/0001/period.json'
def current_legacy_view(view):
    if not hasattr(view,'legacy_signed_sources'):return False
    if view.legacy_context_producer.HERE!=ROOT/CURRENT_LEGACY_CONTEXT:return False
    return legacy_session_view(view)
def current_source8_view(view):
    if getattr(view,'source8_context_producer',None) is None:return False
    if view.source8_context_producer.HERE!=ROOT/CURRENT_SOURCE8_CONTEXT:return False
    reader_for_view(view);return source8_session_view(view)
