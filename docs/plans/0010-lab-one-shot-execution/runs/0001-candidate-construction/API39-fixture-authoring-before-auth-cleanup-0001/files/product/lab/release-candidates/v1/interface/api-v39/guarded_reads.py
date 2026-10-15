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
        view.custody_signed_sources.guard()
    view.handle.guard()
    source.require(view.handle.sources.freshness(ROOT, view.data['baseline'])['status'] == 'current',
                   'read model baseline source bytes are stale')
    _view_stamp(view)


@contextmanager
def model_read_batch(view):
    """A complete derived read succeeds only after the exit guard succeeds."""
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
    source.require(Path(model.__file__).resolve() == ROOT / 'product/lab/release-candidates/v1/interface/current-source-adapter-v3/model.py', 'unselected original byte model')
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
    current = getattr(_active, 'value', None)
    if current is None:
        return source.custody_delivery().reader.adapter.model
    source.require(current['view'] is view, 'artifact lookup selects another batched read model')
    return current['model']


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
