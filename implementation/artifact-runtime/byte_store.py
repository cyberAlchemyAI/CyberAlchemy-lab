"""Immutable byte storage and literal observations; no artifact/domain policies."""
import base64
from pathlib import Path
from json_construction import uint
from exact_io import bound,binding,decode,encode,logical,read,require,sha,write_package,Refusal

BUFFERS={}
TOTAL=0

def store(raw):
    global TOTAL
    require(isinstance(raw,bytes) and len(raw)<=33554432,'byte-value-bound')
    identity=sha(raw)
    if identity not in BUFFERS:
        require(len(BUFFERS)<4096 and TOTAL+len(raw)<=67108864,'byte-store-bound')
        BUFFERS[identity]=raw;TOTAL+=len(raw)
    return {'ref':identity,'sha256':identity,'bytes':len(raw)}

def original(root,path,maximum):
    root=Path(root).absolute();require(root.resolve()==root,'unsafe-root');logical(path)
    maximum=uint(maximum)
    require(maximum<=16777216,'byte-read-bound')
    raw=read(root/path,maximum=maximum)
    result=store(raw);result['binding']=binding(raw,path)
    return result

def probe(raw,markers,keys):
    require(isinstance(markers,list) and len(markers)<=256 and all(isinstance(v,str) and len(v)<=4096 for v in markers),'probe-marker-bound')
    require(isinstance(keys,list) and len(keys)<=256 and all(isinstance(v,str) and len(v)<=512 for v in keys),'probe-key-bound')
    matched=sum(1 for text in markers if text.encode() in raw)
    try:raw.decode('utf-8',errors='strict');utf8=True
    except UnicodeError:utf8=False
    try:document=decode(raw,source=True);error=None
    except Refusal as failure:document=None;error=failure.code
    count=0
    if error is None:
        pending=[document]
        while pending:
            value=pending.pop()
            if isinstance(value,dict):
                count+=sum(1 for key in value if key.lower() in keys)
                pending.extend(value.values())
            elif isinstance(value,list):pending.extend(value)
    return {'marker_matches':str(matched),'key_matches':str(count),'utf8':utf8,'json_error':error}

def publish(destination,rows):
    require(isinstance(rows,list) and len(rows)<=1024,'byte-publication-bound')
    members={row['path']:BUFFERS[row['ref']] for row in rows}
    require(len(members)==len(rows),'duplicate-member-path')
    write_package(destination,members)
    return {'published':True,'members':len(members)}