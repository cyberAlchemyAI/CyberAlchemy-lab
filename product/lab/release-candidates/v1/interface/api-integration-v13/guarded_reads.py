"""Closed pure calculations with full source guards at both boundaries.

Original records, schemas, revision witnesses and permission checks remain in
use. No parent callback is replaced, no body is cached and no grant is extended.
"""
import copy
import threading
from contextlib import contextmanager
from pathlib import Path

from .protocol import source, ROOT, compact

_active = threading.local()
_integrated_batch=threading.local()


def _view_stamp(view):
    source.require(view.subjects == view.data['projection']['subjects'], 'read projection subjects differ')
    return source.sha(compact({
        'selected': view.selected,
        'data': {k: view.data[k] for k in ('config', 'baseline', 'projection', 'head', 'transactions')},
        'originals': {k: source.sha(raw) for k, raw in view.originals.items()},
    }))


def _view_guard(view, delivery):
    source.require(type(view) is delivery.reader.Inspection, 'unselected original read model')
    if hasattr(view, 'custody_signed_sources'):
        delivery.FACT_SCOPE.parent_guard(view.custody_signed_sources)
    view.handle.guard()
    source.require(view.handle.sources.freshness(ROOT, view.data['baseline'])['status'] == 'current',
                   'read model baseline source bytes are stale')
    _view_stamp(view)


def source8_view_guard(view):
    """Check an actual reader and its exact original signed prefix."""
    delivery=getattr(view,'source8_context_producer',None)
    source.require(delivery is not None,'actual Source8 producer required')
    reader=source.reader_for_view(view)
    source.require(reader is delivery.reader,'Source8 actual reader identity differs')
    reader.guard()
    origin=getattr(view,'source8_original_view',view)
    source.require(type(view) is reader.Inspection and type(origin) is reader.Inspection
        and view.handle is origin.handle and view.originals is origin.originals,
        'Source8 prefix execution origin differs')
    _view_guard(view,delivery)
    transactions=view.data['transactions'];full=origin.data['transactions']
    source.require(transactions and transactions==full[:len(transactions)]
        and view.data['config']==origin.data['config'] and view.data['baseline']==origin.data['baseline']
        and view.data['head']['sequence']==len(transactions)-1
        and view.data['head']['transaction_digest']==transactions[-1]['digest']
        and view.handle.common.digest(view.data['projection'])==transactions[-1]['projection_digest'],
        'Source8 prefix differs from original signed chain')
    return delivery,reader,_view_stamp(view)


@contextmanager
def model_read_batch(view):
    """A complete derived read succeeds only after the exit guard succeeds."""
    if getattr(view,'source8_context_producer',None) is not None:
        outer=getattr(_active,'value',None)
        if outer is not None:
            source.require(outer['view'] is view,'foreign Source8 model read batch')
            yield
            return
        delivery,reader,before=source8_view_guard(view)
        model=reader.adapter.model
        methods=(model.artifact_ref,model.record_bytes)
        _active.value={'view':view,'model':model}
        try:
            from .integrated_guard import read_effect_exclusion
            with read_effect_exclusion(view):yield
        finally:
            del _active.value
            after_delivery,after_reader,after=source8_view_guard(view)
            source.require(after_delivery is delivery and after_reader is reader
                and after_reader.adapter.model is model and methods==(model.artifact_ref,model.record_bytes)
                and after==before,'Source8 original model or prefix changed during read')
        return
    from .integrated_guard import is_view,guard_view,read_effect_exclusion
    if is_view(view):
        outer=getattr(_integrated_batch,'value',None)
        if outer is not None:
            source.require(outer['view'] is view,'nested integrated batch selects another source')
            _integrated_check(view);yield;return
        reader=source.reader_for_view(view);before=guard_view(view,reader=reader)
        model=reader.adapter.model
        value={'view':view,'reader':reader,'model':model,'thread':threading.get_ident(),
            'methods':(model.artifact_ref,model.record_bytes),'parent':getattr(view,'custody_signed_sources',None),
            'parent_guard':getattr(getattr(view,'custody_signed_sources',None),'guard',None),
            'parent_sources':getattr(getattr(view,'custody_signed_sources',None),'sources',None),
            'parent_source_callback':getattr(getattr(getattr(view,'custody_signed_sources',None),'sources',None),'current_guard',None),
            'factory':source.reader_factory(view),'factory_selector':source.reader_factory,
            'pins':(reader.adapter_pin,reader.source_pin,reader.package_pin)}
        _integrated_batch.value=value
        try:
            with read_effect_exclusion(view):yield
        finally:
            try:
                _integrated_check(view)
                source.require(guard_view(view,reader=reader)==before,'integrated read data changed during batch')
            finally:del _integrated_batch.value
        return
    if view.selected['name'] != 'custody-participation':
        yield
        return
    outer = getattr(_active, 'value', None)
    if outer is not None:
        source.require(outer['view'] is view, 'nested batch selects another read model')
        yield
        return
    delivery = source.custody_delivery()
    model = delivery.reader.adapter.model
    source.require(Path(model.__file__).resolve() == ROOT / 'product/lab/release-candidates/v1/interface/current-source-adapter-v4/model.py', 'unselected original byte model')
    _view_guard(view, delivery)
    stamp = _view_stamp(view)
    methods = (model.artifact_ref, model.record_bytes)
    _active.value = {'view': view, 'model': model}
    try:
        yield
    finally:
        del _active.value
        after = source.custody_delivery()
        source.require(after is delivery and after.reader.adapter.model is model
                       and (model.artifact_ref, model.record_bytes) == methods, 'original model selection changed')
        _view_guard(view, delivery)
        source.require(_view_stamp(view) == stamp, 'captured read data changed during batch')


def selected_model(view):
    if getattr(view,'source8_context_producer',None) is not None:
        current=getattr(_active,'value',None)
        if current is not None:
            source.require(current['view'] is view,'foreign Source8 batched lookup')
            return current['model']
        _,reader,_=source8_view_guard(view)
        return reader.adapter.model
    from .integrated_guard import is_view
    if is_view(view):
        current=getattr(_integrated_batch,'value',None)
        if current is not None:
            _integrated_check(view);return current['model']
        return source.reader_for_view(view).adapter.model
    current = getattr(_active, 'value', None)
    if current is None:
        return source.custody_delivery().reader.adapter.model
    source.require(current['view'] is view, 'artifact lookup selects another batched read model')
    return current['model']

def _integrated_check(view):
    value=getattr(_integrated_batch,'value',None)
    source.require(value is not None and value['view'] is view and value['thread']==threading.get_ident(),
        'closed or foreign-thread integrated read batch')
    source.require(value['reader'].adapter.model is value['model']
        and source.reader_factory is value['factory_selector'] and source.reader_factory(view) is value['factory']
        and (value['reader'].adapter_pin,value['reader'].source_pin,value['reader'].package_pin)==
            value['pins']
        and (value['model'].artifact_ref,value['model'].record_bytes)==value['methods']
        and getattr(view,'custody_signed_sources',None) is value['parent']
        and getattr(value['parent'],'guard',None)==value['parent_guard']
        and getattr(value['parent'],'sources',None) is value['parent_sources']
        and getattr(value['parent_sources'],'current_guard',None)==value['parent_source_callback'],
        'original integrated source/model callbacks changed')


@contextmanager
def participation_snapshot(parent, delivery):
    """Use the original ExactSources implementation over sealed copied facts.

Full parent guards run before copying, after copying and after the entire pure
preflight. Original get/resolve checks validate every reference, schema, witness,
privacy rule and version. PermissionBridge continues checking the actual parent.
"""
    source.require(type(parent) is delivery.reader.adapter.SignedSources, 'verified signed source required')
    parent.guard()
    original = parent.sources
    eligibility = delivery.EL
    records = copy.deepcopy(list(original.records.values()))
    schemas = copy.deepcopy(list(original.schemas.values()))
    scope = original.scope_ref
    cut = copy.deepcopy(original.source_cut)
    expected_records = parent.record_stamp(records)
    expected_schemas = parent.schema_stamp(schemas)
    box = {'source': None, 'closed': False}

    def local_guard():
        source.require(not box['closed'], 'closed participation snapshot cannot serve facts')
        snapshot = box['source']
        if snapshot is None:
            return True
        source.require(snapshot.scope_ref == scope and snapshot.source_cut == cut
                       and snapshot.current_guard is local_guard, 'participation snapshot scope or guard changed')
        source.require(parent.record_stamp(snapshot.records.values()) == expected_records,
                       'participation snapshot original records changed')
        source.require(parent.schema_stamp(snapshot.schemas.values()) == expected_schemas
                       and set(snapshot.validators) == set(snapshot.schemas)
                       and all(source.encoded(v.schema) == source.encoded(source.parse(snapshot.schemas[k].original_schema))
                               for k, v in snapshot.validators.items()), 'participation snapshot schemas changed')
        return True

    snapshot = eligibility.ExactSources(scope, cut, records, schemas, local_guard)
    box['source'] = snapshot
    local_guard()
    parent.guard()
    try:
        yield snapshot
    finally:
        try:
            local_guard()
        finally:
            box['closed'] = True
            parent.guard()


def fact_scope_kernel():
    # The producer selects one closed helper namespace shared with this API.
    delivery=source.custody_delivery()
    return delivery.FACT_SCOPE
