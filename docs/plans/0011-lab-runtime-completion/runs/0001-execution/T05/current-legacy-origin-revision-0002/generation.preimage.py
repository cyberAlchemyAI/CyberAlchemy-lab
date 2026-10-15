"""Keep Machine Actor attribution separate from its actual policy custodian.

The original sealed fact-copy implementation and generator stay intact. Only
the registered policy host is composed with the peer's actual owner channel.
Original current policy/clock checks run on every guard; nothing grants access.
"""
from contextlib import contextmanager
import hashlib
import importlib
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
CODE_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def require(value,reason):
    if not value:raise ValueError(reason)


def selected(custodian):
    package=type(custodian).__module__.rsplit('.',1)[0]
    origin=type(custodian).__module__.rsplit('.',1)[-1]
    require(origin in ('custody_context_sessions','legacy_context_sessions'),
            'unselected Machine Context runtime origin')
    C=importlib.import_module(package+'.'+origin)
    MT=importlib.import_module(package+'.machine_transport')
    S=importlib.import_module(package+'.service')
    A=importlib.import_module(package+'.auth')
    api=HERE.parent/'api-integration-v17'
    require(all(Path(module.__file__).resolve()==api/filename
                and not Path(module.__file__).is_symlink()
                and module.__name__==package+'.'+filename[:-3]
                for module,filename in ((C,origin+'.py'),(MT,'machine_transport.py'),
                                        (S,'service.py'),(A,'auth.py'))),
            'foreign selected Machine/runtime/owner module')
    require(type(custodian) is C.MachineContextSessions
            and type(custodian.parent) is C.ContextSessions,
            'actual selected origin-specific Machine/parent classes required')
    peer=custodian.channel;owner=peer.owner
    require(type(peer) is MT.MachinePeer and type(owner) is S.Service
            and type(owner.channel) is A.ReaderChannel,'actual Machine peer and original operator required')
    require(custodian.parent is owner.sessions and custodian.source is owner.sessions.source
            and peer.resource is owner.sessions.live.get(peer.row['session_ref'])
            and peer.resource.source is custodian.source and peer.resource.bridge is owner.sessions.bridge
            and peer.resource.bridge.channel is owner.channel,'actual owner/source/live resource custody differs')
    require(type(custodian.bridge) is C.PermissionBridge and custodian.bridge.channel is peer
            and custodian.bridge.source is custodian.source,'foreign Machine permission bridge')
    require(not peer.closed and not peer.resource.closed and not owner.sessions.closed,'closed Machine cannot borrow source facts')
    require(hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==CODE_SHA,'Machine scope implementation changed')
    return C,MT,S,A,peer,owner


@contextmanager
def read_scope(custodian):
    C,MT,S,A,peer,owner=selected(custodian)
    D=C.D;K=D.FACT_SCOPE;source=custodian.source;channel=custodian.bridge
    G=importlib.import_module(D.__package__+'.generation')
    require(Path(G.__file__).resolve()==D.HERE/'generation.py' and D.generate is G.generate,
            'unselected original generator module')
    producer=importlib.import_module(D.__package__+'.build')
    original=(K.ReadScope,K.policy_scope,K.parent_guard,K.require_outside_scope,
              G._generate,D.generate,D.verify_source,channel.guard,owner.channel.guard)

    class OwnerPolicyScope(K.ReadScope):
        """Original fact-copy guard, with one explicitly bound owner host."""
        def __init__(self):
            self.policy_owner=owner
            self.policy_peer=peer
            self.policy_channel=owner.channel
            super().__init__(source,D.EL,channel,producer,((D.verify_source,C.DELIVERY_PIN),))

        @property
        def host(self):
            require(peer.owner is self.policy_owner and owner.channel is self.policy_channel
                    and self.policy_peer is peer,'Machine policy custody changed during fact scope')
            return self.policy_channel

        @host.setter
        def host(self,value):
            # Original constructor selects the peer through PermissionBridge.
            require(value is self.policy_peer,'scope selects another Machine channel')

        def check(self):
            super().check()
            selected(custodian)
            require(self.host is owner.channel,'only this actual parent policy host may borrow facts')
            require((K.ReadScope,K.policy_scope,K.parent_guard,K.require_outside_scope,
                     G._generate,D.generate,D.verify_source,channel.guard,owner.channel.guard)==original,
                    'original scope/generator/policy callbacks changed')
            return True

    K.require_outside_scope()
    source.guard();D.verify_source(C.DELIVERY_PIN);channel.guard()
    scope=OwnerPolicyScope()
    source.guard();channel.guard()
    K._active.value=scope
    try:
        channel.guard()
        yield scope.snapshot
    finally:
        del K._active.value
        errors=[]
        def checked(callback):
            try:callback()
            except BaseException as error:errors.append(error)
        checked(scope.check)
        checked(source.guard)
        checked(lambda:D.verify_source(C.DELIVERY_PIN))
        checked(channel.guard)
        scope.closed=True
        if errors:raise errors[0]


def generate(custodian,message,request_raw,mapped_pin,schemas):
    C,MT,S,A,peer,owner=selected(custodian)
    G=importlib.import_module(C.D.__package__+'.generation')
    require(schemas is custodian.schemas is owner.schemas,'foreign protocol schemas')
    require(mapped_pin==C.MAPPING_PIN,'unselected native mapping package')
    with read_scope(custodian) as facts:
        # The actual original generator consumes the actual Machine Actor.
        result=G._generate(custodian.source,custodian.bridge,message,request_raw,
                             mapped_pin,schemas,facts)
    require(C.D.now()<C.D.EL.instant(result[2]['expires_at']),'delivery expired before completion')
    peer.guard()
    return result
