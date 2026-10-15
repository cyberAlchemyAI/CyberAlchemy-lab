"""Pure candidate calculation with full source checks before evidence writes."""
from contextlib import contextmanager
import importlib
import importlib.util
from pathlib import Path
import sys

from .protocol import source, ROOT
from .workspace import Vault, privacy

HERE = Path(__file__).resolve().parent
BUFFER = HERE.parent / 'staged-evidence-v1'
NAME = '_cal_lab_staged_evidence_v1'
if NAME not in sys.modules:
    spec = importlib.util.spec_from_file_location(NAME, BUFFER / '__init__.py',
                                                submodule_search_locations=[str(BUFFER)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[NAME] = package
    spec.loader.exec_module(package)
B = importlib.import_module(NAME + '.buffer')
source.require(Path(B.__file__).resolve() == BUFFER / 'buffer.py', 'unselected evidence buffer')


@contextmanager
def selection(host):
    """Group read-only handler selection and preflight before the durable claim.

    Full original source and producer checks run at entry and exit. Every policy
    call still reads its actual bytes and real clock; only sealed source facts
    are borrowed. Original dispatch and durable writers refuse this scope.
    """
    from .integrated_guard import pure
    if host.channel.policy['source_name'] in ('integrated-participation','workflow-participation'):
        with pure(host):yield
        return
    service = importlib.import_module(__package__ + '.service')
    auth = importlib.import_module(__package__ + '.auth')
    source.require(type(host) is service.Service and type(host.vault) is Vault
                   and type(host.channel) is auth.ReaderChannel,
                   'actual selected metadata Service, Vault and ReaderChannel required')
    name=host.channel.policy['source_name']
    if name in ('legacy-session-fixture',source.CURRENT_LEGACY_NAME):
        delivery=source.legacy_delivery_for(name);leaf='current_legacy_context_sessions' if name==source.CURRENT_LEGACY_NAME else 'legacy_context_sessions'
        runtime=importlib.import_module(__package__+'.'+leaf)
        source.require(Path(runtime.__file__).resolve()==HERE/(leaf+'.py'),'unselected legacy calculation runtime')
        PermissionBridge,BOUNDARIES,DELIVERY_PIN=runtime.PermissionBridge,runtime.BOUNDARIES,runtime.DELIVERY_PIN
    elif name in ('source8-session-participation','source8-lesson-fixture-participation',source.CURRENT_SOURCE8_NAME):
        delivery=source.source8_delivery_for(name)
        leaf='current_context_sessions' if name==source.CURRENT_SOURCE8_NAME else 'source8_context_sessions' if name=='source8-session-participation' else 'fixture_context_sessions'
        runtime=importlib.import_module(__package__+'.'+leaf)
        source.require(Path(runtime.__file__).resolve()==HERE/(leaf+'.py'),'unselected Source8 calculation runtime')
        PermissionBridge,BOUNDARIES,DELIVERY_PIN=runtime.PermissionBridge,runtime.BOUNDARIES,runtime.DELIVERY_PIN
    else:
        delivery=source.custody_delivery()
        from .custody_context_sessions import PermissionBridge,BOUNDARIES,DELIVERY_PIN
    parent=host.handlers.view.custody_signed_sources
    bridge = PermissionBridge(parent, host.channel, host.schemas)
    host.schemas.guard()
    host.vault.guard()
    with BOUNDARIES.read_scope(parent, delivery.EL, bridge, producer=delivery,
                              package_checks=[(delivery.preflight, DELIVERY_PIN)]):
        yield
    host.schemas.guard()
    host.vault.guard()


@contextmanager
def calculation(host):
    """No durable effects occur while source facts are borrowed.

The original SignedSources and channel callbacks remain unchanged. Every policy
check still reads its original file and real clock. Candidate evidence is staged
in a bounded buffer and written only after full source and policy exit checks.
Any calculation or exit-check error discards the unpublished staged output.
"""
    from .integrated_guard import pure,guard_host,require_outside
    if host.channel.policy['source_name'] in ('integrated-participation','workflow-participation'):
        buffer=B.EvidenceBuffer(host.vault.manifest['workspace_ref'],lambda raw:privacy(source.parse(raw)))
        try:
            with pure(host):yield buffer
            guard_host(host)
            buffer.commit(host.vault.object,require_outside)
            host.channel.guard()
        finally:buffer.discard()
        return
    service = importlib.import_module(__package__ + '.service')
    source.require(type(host) is service.Service and type(host.vault) is Vault,
                   'actual selected Service and Vault required')
    name=host.channel.policy['source_name']
    if name in ('legacy-session-fixture',source.CURRENT_LEGACY_NAME):
        delivery=source.legacy_delivery_for(name);leaf='current_legacy_context_sessions' if name==source.CURRENT_LEGACY_NAME else 'legacy_context_sessions'
        runtime=importlib.import_module(__package__+'.'+leaf)
        source.require(Path(runtime.__file__).resolve()==HERE/(leaf+'.py'),'unselected legacy calculation runtime')
        PermissionBridge,BOUNDARIES,DELIVERY_PIN=runtime.PermissionBridge,runtime.BOUNDARIES,runtime.DELIVERY_PIN
    elif name in ('source8-session-participation','source8-lesson-fixture-participation',source.CURRENT_SOURCE8_NAME):
        delivery=source.source8_delivery_for(name)
        leaf='current_context_sessions' if name==source.CURRENT_SOURCE8_NAME else 'source8_context_sessions' if name=='source8-session-participation' else 'fixture_context_sessions'
        runtime=importlib.import_module(__package__+'.'+leaf)
        source.require(Path(runtime.__file__).resolve()==HERE/(leaf+'.py'),'unselected Source8 calculation runtime')
        PermissionBridge,BOUNDARIES,DELIVERY_PIN=runtime.PermissionBridge,runtime.BOUNDARIES,runtime.DELIVERY_PIN
    else:
        delivery=source.custody_delivery()
        from .custody_context_sessions import PermissionBridge,BOUNDARIES,DELIVERY_PIN
    parent=host.handlers.view.custody_signed_sources
    bridge = PermissionBridge(parent, host.channel, host.schemas)
    host.schemas.guard()
    buffer = B.EvidenceBuffer(host.vault.manifest['workspace_ref'],
                              lambda raw: privacy(source.parse(raw)))
    try:
        with BOUNDARIES.read_scope(parent, delivery.EL, bridge, producer=delivery,
                                  package_checks=[(delivery.preflight, DELIVERY_PIN)]):
            yield buffer
        host.schemas.guard()
        host.vault.guard()
        buffer.commit(host.vault.object, delivery.FACT_SCOPE.require_outside_scope)
        host.channel.guard()
    finally:
        buffer.discard()
