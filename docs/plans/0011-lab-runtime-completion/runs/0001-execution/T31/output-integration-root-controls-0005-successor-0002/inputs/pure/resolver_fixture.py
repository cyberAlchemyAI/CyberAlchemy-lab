"""Owned inert metadata-control fixture; no API/native/producer effects."""
import copy
from types import SimpleNamespace
class OwnResolver:
    def __init__(self,payload):self.payload=payload
    def resolve(self,view):return copy.deepcopy(self.payload)
class OwnCapsule:
    pending=False
    def __init__(self,value):
        self.value=value;self.run_binding={'ref':'OWNED-INERT:run','sha256':'1'*64};self.work_ref='OWNED-INERT:work@1';self.source_cut={'OWNED-INERT':True};self._authorization=SimpleNamespace(packet={'principal_ref':'OWNED-INERT:principal'})
    def private_view(self):return {'OWNED_INERT':True}
class OwnCarriers:
    def output(self,header,raw,*,scope_ref,transition_ref=None,scope_proof=None,invocation_lineage=None):
        assert header['scope_ref']==scope_ref
        return {'OWNED_INERT':True}
