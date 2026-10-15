"""Owned inert metadata-control fixture; no API/native/producer effects."""
import copy
class OwnResolver:
    def __init__(self,payload):self.payload=payload
    def resolve(self,view):return copy.deepcopy(self.payload)
class OwnCapsule:
    pending=False
    def __init__(self,value):self.value=value
    def private_view(self):return {'OWNED_INERT':True}
class OwnCarriers:
    def output(self,header,raw,*,scope_ref):
        assert header['scope_ref']==scope_ref
        return {'OWNED_INERT':True}
