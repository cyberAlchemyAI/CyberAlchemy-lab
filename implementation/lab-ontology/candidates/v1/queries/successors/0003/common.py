"""Exact candidate query bytes, bounded locators and deterministic identities."""
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import time
HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parents[2]
ROOT=PACKAGE.parents[3]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
PROFILE=PACKAGE/'profiles/lab-ontology-profile.json'
PROFILE_SHA='b8a5991595f3e5be575f140438b89b5a3bd3ad63453c070a2a616b6eeb850dea'
class QueryFault(ValueError):pass
def require(v,msg):
    if not v:raise QueryFault(msg)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return (json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(v):return sha(canonical(v))
def parse(raw):
    require(type(raw) is bytes,'original query bytes required')
    def pairs(items):
        result={}
        for k,v in items:require(k not in result,'duplicate JSON key');result[k]=v
        return result
    try:return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(QueryFault('nonfinite JSON')))
    except (ValueError,UnicodeError) as e:raise QueryFault('invalid original JSON: '+str(e)) from e
def load(p):return parse(Path(p).read_bytes())
def bind(p):return {'path':Path(p).relative_to(ROOT).as_posix(),'sha256':sha(Path(p).read_bytes())}
def safe_path(root,name):
    p=root/name
    require(type(name) is str and not Path(name).is_absolute() and '..' not in Path(name).parts and p.resolve().is_relative_to(root)
        and not p.is_symlink() and not any(x.is_symlink() for x in p.parents),'unsafe selected source path')
    return p
def original(b):
    require(type(b) is dict and set(b)=={'path','sha256'},'closed file binding required')
    p=safe_path(ROOT,b['path']);require(p.is_file() and sha(p.read_bytes())==b['sha256'],'original selected source differs: '+b['path']);return p.read_bytes()
def emit(p,v):
    with Path(p).open('xb') as f:f.write(encoded(v))
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def profile():
    require(sha(PROFILE.read_bytes())==PROFILE_SHA,'independent ontology profile pin differs');return load(PROFILE)
def node_key(namespace,kind,identity,version,byte_sha):
    fields=['ontology:lab-O03-query',namespace,kind,identity,version,byte_sha]
    return 'query-node:'+sha(b''.join(len(v.encode()).to_bytes(8,'big')+v.encode() for v in fields))
def source_status(bindings):
    changed=[];missing=[];unsafe=[];unchecked=[]
    for b in bindings:
        if not re.fullmatch('[0-9a-f]{64}',str(b.get('sha256',''))):unchecked.append(b.get('path','unknown'));continue
        try:p=safe_path(ROOT,b['path'])
        except QueryFault:unsafe.append(b['path']);continue
        if not p.is_file():missing.append(b['path'])
        elif sha(p.read_bytes())!=b['sha256']:changed.append(b['path'])
    return {'state':'stale' if changed or missing or unsafe else 'unknown' if unchecked else 'current',
        'changed':sorted(changed),'missing':sorted(missing),'unsafe':sorted(unsafe),'unchecked':sorted(unchecked),'checked_count':len(bindings)}
