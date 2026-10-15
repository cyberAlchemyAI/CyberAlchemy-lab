"""Full actual Source8/policy guards and effect exclusion during pure calculation."""
from contextlib import contextmanager
import importlib
import threading
from .protocol import source,compact,ROOT

_active=threading.local()


def require_outside():
    source.require(getattr(_active,'host',None) is None,'dispatch and durable writes are forbidden inside integrated pure calculation')


def is_view(view):
    if type(view).__module__!='_cal_api87_integrated_reader7.inspection':return False
    reader=source.integrated_reader()
    return type(view) is reader.Inspection and view.selected['archive_binding']==source.integrated_selection()['archive_binding']


def guard_view(view):
    reader=source.integrated_reader()
    source.require(type(view) is reader.Inspection and view.selected['archive_binding']==source.integrated_selection()['archive_binding'],
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
    source.require(policy['schema_version']=='lab-local-integrated-challenge-resolution-policy/v2-candidate'
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
