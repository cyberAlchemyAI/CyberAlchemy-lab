"""Independent Event observer, derived from the existing tested observer.

Adds in-memory corruption inputs and Unicode metadata digest compatibility;
generated code is never imported or executed here.
"""
import ast
import hashlib
import json
import pathlib
import sys

SUPPORT = '607cfb79ac50f4929834afbfd206174d912122541534755688aa703e1d53a4b0'
def require(ok, reason):
    if not ok: raise ValueError('PYTHON_EVENT_OBSERVER:' + reason)
def dump(n): return ast.dump(n, include_attributes=False)
def frozen(n):
    if isinstance(n,ast.Constant) and type(n.value) in (str,int,bool,type(None)):return n.value
    if isinstance(n,ast.Tuple):return [frozen(x) for x in n.elts]
    require(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_MappingProxyType' and len(n.args)==1 and not n.keywords and isinstance(n.args[0],ast.Dict),'frozen descriptor')
    keys=[frozen(k) for k in n.args[0].keys];require(all(type(k) is str for k in keys) and len(keys)==len(set(keys)),'descriptor keys')
    return dict(zip(keys,[frozen(v) for v in n.args[0].values]))
def relative_module(source, target):
    a,b=pathlib.PurePosixPath(source).parent.parts,pathlib.PurePosixPath(target).parts;common=0
    while common<min(len(a),len(b)) and a[common]==b[common]:common+=1
    return '.'*(len(a)-common+1)+'.'.join(b[common:])

def observe(data,m,overrides=None):
    root=pathlib.Path(data['root']);source=data['bodies'][m['selector']];d=m['descriptor']
    def read(relative): return overrides[relative] if overrides is not None and relative in overrides else (root/relative).read_bytes()
    provider=read(m['provider_path'])
    require(hashlib.sha256(provider).hexdigest()==d['provider']['sha256'],'provider digest')
    require(hashlib.sha256(read(data['runtime'])).hexdigest()==SUPPORT==d['runtime']['sha256'],'support perimeter')
    for name in ['event_type','version','occurrence_id','occurred_at_policy','payload']:require(d[name]==source[name],'source binding')
    refs=sorted(set(f['type_ref']['selector'] for f in [source['occurrence_id']]+source['payload'] if f['type_ref']['kind']=='reference'))
    require([r['selector'] for r in d['references']]==refs,'reference binding')
    for r in d['references']:
        node=data['nodes'][r['selector']]
        body=json.dumps(node['body'],sort_keys=True,separators=(',',':'),ensure_ascii=False)
        body=''.join(('\\u%04x' % ord(c)) if 0xD800 <= ord(c) <= 0xDFFF else c for c in body).encode()
        require(r['kind']==node['kind'] and r['body_sha256']==hashlib.sha256(body).hexdigest() and r['semantics']=='reference-not-embedding','reference meaning')
    fields=sorted(source['payload'],key=lambda f:f['field_id']);generated=source['occurred_at_policy']=='generated'
    def reference(selector): return next(r for r in m['reference_imports'] if r['selector']==selector)
    def type_of(f, input=False):
        t=f['type_ref']
        if t['kind']=='reference':return ('int | str' if reference(t['selector'])['identity']['scalar']=='UInt64' else 'str') if input else '_Ref'+str(refs.index(t['selector']))
        return {'string':'str','boolean':'bool','integer':'int | str' if input else 'int','decimal':'int | float' if input else 'float','timestamp':'str','uuid':'str'}[t['name']]
    def normalize(f,expr):
        t=f['type_ref']
        if t['kind']=='reference':return '_Ref'+str(refs.index(t['selector']))+'('+('_event_ref_uint64' if reference(t['selector'])['identity']['scalar']=='UInt64' else '_e.text')+'('+expr+'))'
        fn={'string':'string','boolean':'boolean','integer':'integer','decimal':'decimal','timestamp':'text','uuid':'text'}[t['name']]
        return '_e.'+fn+'('+expr+')'
    def shape(name,fs):
        text=name+'Input = _TypedDict('+repr(name+'Input')+', {'
        text+=', '.join(repr(f['field_id'])+': '+(type_of(f,True) if f['required'] else '_NotRequired['+type_of(f,True)+']') for f in fs)+'})\n'
        text+='class '+name+'(_Protocol):\n'
        for f in fs:
            if len(fs)>1:text+='    @_overload\n'
            text+='    def __getitem__(self, key: _Literal['+repr(f['field_id'])+']) -> '+type_of(f)+': ...\n'
        if len(fs)>1:text+='    def __getitem__(self, key: str) -> object: ...\n'
        if not fs:text+='    pass\n'
        return text
    runtime=relative_module(m['provider_path'],pathlib.PurePosixPath(data['runtime']).parent)
    expected='''from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from typing import Callable as _Callable, Literal as _Literal, NotRequired as _NotRequired, Protocol as _Protocol, TypedDict as _TypedDict, overload as _overload, cast as _cast
from RUNTIME import event_values as _e
'''.replace('RUNTIME',runtime)
    require([r['selector'] for r in m['reference_imports']]==refs,'reference type imports')
    for i,r in enumerate(m['reference_imports']):
        content=read(r['relative_path'])
        require(r['identity']['selector']==r['selector'] and r['identity']['scalar'] in ('String','UInt64'),'reference identity binding')
        declaration='from typing import NewType as _NewType\nEventRef = _NewType('+repr(r['selector'])+', '+('int' if r['identity']['scalar']=='UInt64' else 'str')+')\n'
        require(dump(ast.parse(content))==dump(ast.parse(declaration)),'shared reference type semantics')
        bound=next(x for x in d['references'] if x['selector']==r['selector'])
        require(hashlib.sha256(content).hexdigest()==r['sha256']==bound['type_artifact']['sha256'],'reference type digest')
        actual_module=relative_module(m['provider_path'],r['relative_path'][:-3])
        require(r['module']==actual_module,'reference import binding')
        expected+='from '+actual_module+' import EventRef as _Ref'+str(i)+'\n'
    if any(r['identity']['scalar']=='UInt64' for r in m['reference_imports']):
        expected+='''def _event_ref_uint64(value):
    if type(value) is int:
        number = value
    elif type(value) is str and 1 <= len(value) <= 20 and (value == "0" or value[0] != "0" and value.isascii() and value.isdecimal()):
        number = int(value)
    else:
        return _e.fail()
    if number < 0 or number > 18446744073709551615:
        return _e.fail()
    return number
'''
    expected+=shape('_Occurrence',[source['occurrence_id']])+shape('_Payload',fields)
    expected+='EventInput = _TypedDict("EventInput", {"occurrence": _OccurrenceInput, '+('' if generated else '"occurredAt": str, ')+'"payload": _PayloadInput})\n'
    expected+='@_dataclass(frozen=True, slots=True)\nclass EventValue:\n    type: _Literal['+repr(source['event_type'])+']\n    version: _Literal['+repr(source['version'])+']\n    occurrence: _Occurrence\n    occurredAt: str\n    payload: _Payload\n'
    expected+='def make(input: EventInput'+(', clock: _Callable[[], str]' if generated else '')+') -> EventValue:\n'
    keys=('occurrence','payload') if generated else ('occurrence','occurredAt','payload');identity=source['occurrence_id'];name=identity['field_id']
    expected+='    d = _e.data(input, '+repr(keys)+', '+repr(keys)+')\n'
    expected+='    o = _e.data(d["occurrence"], '+repr((name,))+', '+repr((name,))+')\n'
    expected+='    p = _e.data(d["payload"], '+repr(tuple(f['field_id'] for f in fields))+', '+repr(tuple(f['field_id'] for f in fields if f['required']))+')\n'
    expected+='    occurrence = _cast(_Occurrence, _MappingProxyType({'+repr(name)+': '+normalize(identity,'o['+repr(name)+']')+'}))\n'
    parts=[]
    for f in fields:
        item=repr(f['field_id'])+': '+normalize(f,'p['+repr(f['field_id'])+']')
        parts.append(item if f['required'] else '**({'+item+'} if '+repr(f['field_id'])+' in p else {})')
    expected+='    payload = _cast(_Payload, _MappingProxyType({'+', '.join(parts)+'}))\n'
    expected+=('    if not callable(clock):\n        return _e.fail()\n    occurredAt = _e.text(clock())\n' if generated else '    occurredAt = _e.text(d["occurredAt"])\n')
    expected+='    return EventValue('+repr(source['event_type'])+', '+repr(source['version'])+', occurrence, occurredAt, payload)\n'
    require(dump(ast.parse(provider))==dump(ast.parse(expected)),'Event semantics or effects')
    wrapper=ast.parse(read(m['relative_path']));require(len(wrapper.body)==9 and isinstance(wrapper.body[5],ast.Assign) and frozen(wrapper.body[5].value)==d,'descriptor binding')
    wrapper.body[5].value=ast.Constant(None)
    expected='''from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from typing import Callable as _Callable
from PROVIDER import make as _make, EventInput, EventValue
_DESCRIPTOR = None
@_dataclass(frozen=True, slots=True)
class _BoundEvent:
    @property
    def descriptor(self): return _DESCRIPTOR
    def __call__(self, input: EventInputCLOCK_ARG) -> EventValue: return _make(inputCLOCK_CALL)
CALLABLE = _BoundEvent()
__all__ = ["CALLABLE", "EventInput", "EventValue"]
'''.replace('PROVIDER',m['provider_import']).replace('CLOCK_ARG',', clock: _Callable[[], str]' if generated else '').replace('CLOCK_CALL',', clock' if generated else '').replace('CALLABLE',m['callable'])
    require(dump(wrapper)==dump(ast.parse(expected)),'frozen provider binding')
    require(not d['publication'] and not d['occurrence_registration'] and not d['distributed_exactly_once_claim'],'effect boundary')

if __name__=='__main__':
    data=json.load(sys.stdin)
    for m in data['modules']:observe(data,m)
    print(json.dumps({'observed':len(data['modules'])}))
