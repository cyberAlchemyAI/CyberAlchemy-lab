"""One pure Machine setup calculation; original source and policy boundaries.

Only select/proof/authentication borrow sealed source facts. The original
FactScope v2 owns registration/cleanup, full parent/package entry and exit,
and uncached private ReaderChannel policy/nonce/revocation/clock checks.
No public dispatch, durable writer, Session period or timer is changed.
"""
from contextlib import contextmanager
import hashlib
import importlib
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
CODE_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
RUNTIMES={
    'source8_context_sessions.py':('source8-context-delivery-v3-action-0148',
        '0017f4455df9d829368cb6448f0063f470283ef175f5f9cdb1836043488760e3'),
    'fixture_context_sessions.py':('source8-lesson-fixture-context-v1-action-0148',
        '0afe7a76c15a26df9f10b0691fb240f6955f772e778e58820cc0d6dc0d0565d3'),
}

def require(value,reason):
    if not value:raise ValueError(reason)


def selected(owner):
    package=__package__
    S=importlib.import_module(package+'.service')
    A=importlib.import_module(package+'.auth')
    require(type(owner) is S.Service and Path(S.__file__).resolve()==HERE/'service.py'
            and type(owner.channel) is A.ReaderChannel,'actual selected original Machine owner required')
    require(owner.schemas is owner.channel.schemas and owner.handlers.channel is owner.channel,
            'Machine owner schema/handler channel identity differs')
    MT=importlib.import_module(package+'.machine_transport')
    require(Path(MT.__file__).resolve()==HERE/'machine_transport.py'
            and owner.code_files.get('machine_transport.py')==hashlib.sha256(Path(MT.__file__).read_bytes()).hexdigest(),
            'selected Machine transport source changed')
    sessions=owner.sessions
    if sessions is None:return None
    C=sys.modules.get(type(sessions).__module__)
    require(C is not None and Path(C.__file__).resolve().parent==HERE
            and type(sessions) is C.ContextSessions,'actual selected parent Session runtime required')
    filename=Path(C.__file__).name
    if filename in ('custody_context_sessions.py','legacy_context_sessions.py'):return None
    require(filename in RUNTIMES,'unselected Machine source-fact family')
    D=C.D;directory,pin=RUNTIMES[filename]
    require(Path(D.__file__).resolve()==HERE.parent/directory/'build.py'
            and D.HERE==HERE.parent/directory and C.DELIVERY_PIN==pin
            and C.EL is D.EL is D.reader.adapter.eligibility,
            'actual independently selected Source8 producer/eligibility differs')
    require(owner.code_files.get('machine_auth_scope.py')==CODE_SHA
            and hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==CODE_SHA
            and owner.code_files.get(filename)==hashlib.sha256(Path(C.__file__).read_bytes()).hexdigest(),
            'selected Machine authentication helper/runtime source changed')
    source=sessions.source;bridge=sessions.bridge
    require(type(source) is D.reader.adapter.SignedSources and not source.closed
            and source.view is owner.handlers.view
            and owner.handlers.view.custody_signed_sources is source
            and owner.handlers.view.source8_context_producer is D
            and owner.handlers.view.integrated_reader is D.reader,
            'actual original SignedSources/reader/view/producer identity differs')
    require(type(bridge) is C.PermissionBridge and bridge.source is source
            and bridge.channel is owner.channel and bridge.schemas is owner.schemas
            and sessions.schemas is owner.schemas and not sessions.closed,
            'actual owner PermissionBridge and source custody differ')
    B=C.BOUNDARIES;K=D.FACT_SCOPE
    require(Path(B.__file__).resolve()==HERE.parent/'fact-read-scope-v2/scope.py'
            and B.K is K is A.FACT_SCOPE and B.REGISTRY is K._active
            and B.policy_scope is K.policy_scope and B.parent_guard is K.parent_guard,
            'actual unchanged v2 composition/original registry required')
    return C,D,B,K,source,bridge,pin


def peer_current(peer):
    MT=importlib.import_module(__package__+'.machine_transport')
    require(type(peer) is MT.MachinePeer,'actual selected Machine peer required')
    state=selected(peer.owner)
    if state is None:return
    C,D,B,K,source,bridge,pin=state
    require(type(peer.resource) is C.LiveReader and not peer.closed and not peer.resource.closed
            and peer.owner.sessions.live.get(peer.row['session_ref']) is peer.resource
            and peer.resource.source is source and peer.resource.bridge is bridge
            and peer.A.now()<min(peer.expires,peer.resource.expires),
            'Machine or actual parent Session closed/expired/changed at source boundary')


@contextmanager
def source_facts(owner):
    state=selected(owner)
    if state is None:
        # Original legacy select/proof/authentication and guards remain intact.
        yield
        return
    C,D,B,K,source,bridge,pin=state
    K.require_outside_scope()
    before=(B.read_scope,B.guard,K.ReadScope,K.policy_scope,K.parent_guard,
        K.package_guard,K.require_outside_scope,D.verify_source,D.generate,
        source.guard,source.sources.current_guard,bridge.guard,owner.channel.guard,
        owner.channel.policy_guard,owner.channel.termination_guard)
    try:
        with B.read_scope(source,D.EL,bridge,producer=D,
                          package_checks=((D.verify_source,pin),)):
            require(selected(owner)==state,'Machine setup source custody changed')
            yield
            require(selected(owner)==state,'Machine setup source custody changed')
    finally:
        K.require_outside_scope()
        require((B.read_scope,B.guard,K.ReadScope,K.policy_scope,K.parent_guard,
            K.package_guard,K.require_outside_scope,D.verify_source,D.generate,
            source.guard,source.sources.current_guard,bridge.guard,owner.channel.guard,
            owner.channel.policy_guard,owner.channel.termination_guard)==before,
            'Machine setup changed an original source, scope or live policy callback')
