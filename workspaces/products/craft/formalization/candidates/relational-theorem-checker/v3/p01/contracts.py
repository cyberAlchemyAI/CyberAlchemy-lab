"""Strict local transports and independently selected obligation inventories."""
from pathlib import Path
import hashlib
import json
import math
from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent


def identity(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def load_schema(name):
    schema=json.loads((HERE/'contracts'/(name+'.schema.json')).read_text())
    Draft202012Validator.check_schema(schema)
    return schema


def validate(name,value):
    Draft202012Validator(load_schema(name)).validate(value)
    return value


def decode(raw):
    if len(raw)>4194304:
        raise ValueError('input byte ceiling exceeded')
    text=raw.decode('utf-8')
    depth=0; quoted=False; escaped=False
    for c in text:
        if quoted:
            if escaped: escaped=False
            elif c=='\\': escaped=True
            elif c=='"': quoted=False
        elif c=='"': quoted=True
        elif c in '[{':
            depth+=1
            if depth>64: raise ValueError('JSON nesting ceiling exceeded')
        elif c in ']}': depth-=1
    def pairs(items):
        result={}
        for k,v in items:
            if k in result: raise ValueError('duplicate JSON key '+k)
            result[k]=v
        return result
    def constant(value): raise ValueError('nonfinite JSON number '+value)
    def number(value):
        v=float(value)
        if not math.isfinite(v): raise ValueError('nonfinite numeric overflow')
        return v
    return json.loads(text,object_pairs_hook=pairs,parse_constant=constant,parse_float=number)


def catalog():
    return json.loads((HERE/'catalog.json').read_text())


def required_inventory(change_class):
    c=catalog()
    if change_class not in c['change_classes']:
        raise ValueError('unsupported change class '+change_class)
    by_id={o['id']:o for o in c['obligations']}
    return [by_id[id] for id in c['change_classes'][change_class]]


def validate_manifest_inventory(manifest,change_class):
    validate('proof-manifest',manifest)
    expected=[o['id'] for o in required_inventory(change_class)]
    if manifest['change_class']!=change_class or manifest['obligations']!=expected:
        raise ValueError('manifest does not match independently selected obligation inventory')
    return manifest
