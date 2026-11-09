import sys,json,unittest,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'implementation/artifact-runtime'))
from json_construction import construct,read_sources
from exact_io import Refusal,encode
V=lambda tag,**fields:{'tag':tag,'fields':fields}
F=lambda name:V('Field',name=name)
I=lambda index:V('Index',value=str(index))
S=lambda path,tag,**fields:{'target':path,'value':V(tag,**fields)}
base=[S([],'Object',marker=True)]
checks=[]
def reject(name,steps,documents=None):
 try:construct(steps,documents or {})
 except Refusal:checks.append(name);return
 raise AssertionError(name+' unexpectedly accepted')
raw=b'{ "n": 7, "s": "source", "empty": {} }\n'
b={'path':'sample.json','sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'digest_kind':'original-file-sha256'}
documents=read_sources({'sample.json':raw},[{'id':'source','binding':b}])
plan=base+[S([F('copied')],'Copy',document='source',selector='/n'),S([F('items')],'Array',marker=True),S([F('items'),I(0)],'Text',value='example'),S([V('FieldParts',parts=[V('Text',value='m'),V('UInt',value='2',width='4')])],'Object',marker=True),S([F('flag')],'Bool',value=True)]
value,encoded=construct([plan],documents)
assert value=={'copied':7,'items':['example'],'m0002':{},'flag':True}
assert encoded==encode(value);checks.append('bound-source-and-native-values-encode-exactly')
reject('duplicate-write',[base+[S([F('a')],'Text',value='one'),S([F('a')],'Text',value='two')]])
reject('sparse-array',[[S([],'Array',marker=True),S([I(1)],'Text',value='value')]])
reject('missing-parent',[base+[S([F('missing'),F('child')],'Null',marker=True)]])
reject('scalar-parent',[base+[S([F('scalar')],'Text',value='value'),S([F('scalar'),F('child')],'Null',marker=True)]])
reject('missing-source',[base+[S([F('value')],'Copy',document='absent',selector='')]])
reject('missing-selector',[base+[S([F('value')],'Copy',document='source',selector='/absent')]],documents)
reject('inexact-new-number',[base+[S([F('value')],'UInt',value=str(2**53))]])
reject('noncanonical-integer',[base+[S([F('value')],'UInt',value='01')]])
reject('boolean-as-integer',[base+[S([F('value')],'UInt',value=True)]])
reject('executable-op-rejected',[base+[S([F('value')],'Evaluate',value='arbitrary-code')]])
reject('per-batch-bound',[[S([],'Object',marker=True)]*101])
reject('source-numeric-bound',[base+[S([F('value')],'Copy',document='large',selector='')]],{'large':2**53})
reject('composed-name-collision',[base+[S([F('m0002')],'Null',marker=True),S([V('FieldParts',parts=[V('Text',value='m'),V('UInt',value='2',width='4')])],'Object',marker=True)]])
try:read_sources({'sample.json':raw+b' '},[{'id':'source','binding':b}])
except Refusal:checks.append('original-byte-change-rejected')
else:raise AssertionError('Changed source bytes accepted')
print(json.dumps({'status':'PASS','checks':checks,'check_count':len(checks),'scope':'Portable encoder and in-memory original-byte bindings only; no Linux file publication or Define workflow qualification.'}))