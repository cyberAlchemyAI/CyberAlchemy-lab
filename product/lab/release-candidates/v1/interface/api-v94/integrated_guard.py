"""Full actual Source8/policy guards and effect exclusion during pure calculation."""
from contextlib import contextmanager
import importlib
import threading
import sys
from pathlib import Path
from .protocol import source,compact,ROOT

_active=threading.local()


def require_outside():
    source.require(getattr(_active,'host',None) is None and getattr(_active,'read_view',None) is None,
        'dispatch and durable writes are forbidden inside integrated pure calculation/read batch')

@contextmanager
def read_effect_exclusion(view):
    prior=getattr(_active,'read_view',None)
    source.require(prior is None or prior is view,'foreign integrated effect-exclusion scope')
    _active.read_view=view
    try:yield
    finally:_active.read_view=prior


def is_view(view):
    if type(view).__module__!='_cal_api87_integrated_reader7.inspection':return False
    module=sys.modules.get('_cal_api87_integrated_reader7.inspection')
    return module is not None and Path(module.__file__).resolve()==ROOT/'product/lab/release-candidates/v1/interface/current-source-adapter-v7/inspection.py'\
        and type(view) is module.Inspection


def guard_view(view,*,reader=None):
    if reader is None:reader=source.integrated_reader()
    actual=sys.modules.get('_cal_api87_integrated_reader7.reader')
    source.require(actual is not None and type(reader) is actual.SelectedReader
        and Path(actual.__file__).resolve()==ROOT/'product/lab/release-candidates/v1/interface/current-source-adapter-v7/reader.py',
        'actual independently selected integrated Reader required')
    source.require((reader.adapter_pin,reader.source_pin,reader.package_pin)==
        (source.INTEGRATED_ADAPTER_PIN,source.INTEGRATED_SOURCE_PIN,source.INTEGRATED_PACKAGE_PIN),
        'independent integrated Reader pins differ')
    selected=reader.selection(source.INTEGRATED_SOURCE_PIN,source.INTEGRATED_PACKAGE_PIN,'custody-participation')
    source.require(type(view) is reader.Inspection and view.selected['archive_binding']==selected['archive_binding'],
                   'exact integrated source view required')
    reader.guard();view.handle.guard()
    if hasattr(view,'custody_signed_sources'):view.custody_signed_sources.guard()
    source.require(view.subjects==view.data['projection']['subjects'],'integrated subject projection changed')
    source.require(view.handle.sources.freshness(ROOT,view.data['baseline'])['status']=='current','integrated source baseline changed')
    return source.sha(compact({'selected':view.selected,'data':{key:view.data[key] for key in ('config','baseline','projection','head','transactions')},
                              'originals':{key:source.sha(raw) for key,raw in view.originals.items()}}))


def guard_host(host):
    service=importlib.import_module(__package__+'.service');auth=importlib.import_module(__package__+'.auth')
    source.require(type(host) is service.Service and type(host.channel) is auth.ReaderChannel,'actual integrated operator host required')
    host.channel.guard();policy=host.channel.policy_guard()
    source.require(policy['schema_version'] in ('lab-local-integrated-challenge-resolution-policy/v2-candidate','lab-local-integrated-challenge-resolution-policy/v3-candidate')
        and policy['source_name']=='integrated-participation'
        and policy['integrated_source_control']==source.integrated_bindings(),'private integrated source selection differs')
    host.schemas.guard();host.vault.guard()
    return guard_view(host.handlers.view)


@contextmanager
def pure(host):
    require_outside();before=guard_host(host);_active.host=host
    try:
        yield
        source.require(guard_host(host)==before,'integrated source changed during pure calculation')
    finally:_active.host=None
