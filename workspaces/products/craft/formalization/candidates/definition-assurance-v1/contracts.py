"""Closed candidate input decoder. Structural validity never means assurance.

The installed jsonschema runtime validates one fixed local schema. No input may
choose a schema or fetch external references. Source authenticity, typing of
logical symbols and semantic readiness belong to later, separate checks.
"""
import argparse
import json
import math
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError
except ImportError:
    Draft202012Validator=None
    SchemaError=ValueError

HERE=Path(__file__).resolve().parent
SCHEMA_PATH=HERE/'schemas/input-envelope.json'
MAX_BYTES=1_000_000
MAX_DEPTH=64
MAX_NODES=50_000
KINDS={'source','interpretation','relation','assumption','population','result','obligation-manifest'}
IDENTITY_COLLECTIONS={'sources':('definition_id',),'historical_sources':('definition_id','version_ref'),
    'depends_on':('definition_id','version_ref'),'source_refs':('definition_id','version_ref'),
    'declarations':('scope','symbol_id'),'clauses':('clause_id',),'relations':('relation_id',),
    'assumptions':('assumption_id',),'populations':('population_id',),'obligations':('obligation_id',)}


class InputError(ValueError):
    def __init__(self,code,path=''):
        self.code=code;self.path=path


def outcome(status,diagnostics=(),data=None):
    result={'status':status,'authority_effect':'none','semantic_assurance':'not-assessed','diagnostics':list(diagnostics)}
    if data is not None:result['data']=data
    return result


def diagnostic(code,path=''):
    return {'code':code,'path':path}


def pointer(parts):
    return ''.join('/'+str(p).replace('~','~0').replace('/','~1') for p in parts)


def pairs(items):
    result={}
    for key,value in items:
        if key in result:raise InputError('duplicate-json-key',pointer([key]))
        result[key]=value
    return result


def finite_float(token):
    number=float(token)
    if not math.isfinite(number):raise InputError('nonfinite-number')
    return number


def invalid_constant(token):raise InputError('nonfinite-number')


def bounded_tree(data):
    stack=[(data,(),0)];count=0
    while stack:
        value,path,depth=stack.pop();count+=1
        if count>MAX_NODES:raise InputError('node-limit',pointer(path))
        if depth>MAX_DEPTH:raise InputError('depth-limit',pointer(path))
        if isinstance(value,str):
            try:value.encode('utf-8')
            except UnicodeEncodeError:raise InputError('invalid-unicode-scalar',pointer(path))
        elif isinstance(value,dict):
            for key,item in value.items():
                if not isinstance(key,str):raise InputError('non-string-key',pointer(path))
                try:key.encode('utf-8')
                except UnicodeEncodeError:raise InputError('invalid-unicode-scalar',pointer(path))
                stack.append((item,(*path,key),depth+1))
        elif isinstance(value,list):
            stack.extend((item,(*path,index),depth+1) for index,item in enumerate(value))
        elif isinstance(value,float) and not math.isfinite(value):raise InputError('nonfinite-number',pointer(path))
        elif value is not None and type(value) not in (bool,int,float):raise InputError('not-json-value',pointer(path))


def local_schema():
    if Draft202012Validator is None:raise InputError('missing-jsonschema-runtime')
    try:schema=json.loads(SCHEMA_PATH.read_text())
    except (OSError,ValueError):raise InputError('unavailable-local-schema')
    stack=[schema]
    while stack:
        node=stack.pop()
        if isinstance(node,dict):
            for key in ('$ref','$dynamicRef','$recursiveRef'):
                if key in node:
                    target=node[key]
                    if not isinstance(target,str) or not target.startswith('#/$defs/'):
                        raise InputError('external-schema-reference-prohibited')
                    if target[len('#/$defs/'):] not in schema.get('$defs',{}):
                        raise InputError('unbound-local-schema-reference')
            stack.extend(node.values())
        elif isinstance(node,list):stack.extend(node)
    try:Draft202012Validator.check_schema(schema)
    except SchemaError:raise InputError('invalid-local-schema')
    return schema


def identity_diagnostics(data):
    failures=[];stack=[(data,())]
    while stack:
        value,path=stack.pop()
        if isinstance(value,dict):
            if {'definition_id','version_ref','path','sha256'}<=set(value):
                if not value['version_ref'].startswith(value['definition_id']+'@'):
                    failures.append(diagnostic('source-version-identity-mismatch',pointer((*path,'version_ref'))))
            for key,item in value.items():
                if key in IDENTITY_COLLECTIONS and isinstance(item,list):
                    keys=IDENTITY_COLLECTIONS[key];seen=set()
                    for index,row in enumerate(item):
                        if not isinstance(row,dict) or not all(k in row for k in keys):continue
                        identity=tuple(row[k] for k in keys)
                        if identity in seen:failures.append(diagnostic('duplicate-identity',pointer((*path,key,index))))
                        seen.add(identity)
                stack.append((item,(*path,key)))
        elif isinstance(value,list):stack.extend((item,(*path,index)) for index,item in enumerate(value))
    return failures


def validate(data,expected_kind=None):
    try:
        bounded_tree(data)
        schema=local_schema()
    except InputError as error:
        status='unsupported-runtime' if error.code in {'missing-jsonschema-runtime','unavailable-local-schema','external-schema-reference-prohibited','unbound-local-schema-reference','invalid-local-schema'} else 'malformed'
        return outcome(status,[diagnostic(error.code,error.path)])
    if expected_kind is not None and expected_kind not in KINDS:
        return outcome('malformed',[diagnostic('unknown-requested-kind','/kind')])
    validator=Draft202012Validator(schema)
    errors=list(validator.iter_errors(data))
    if errors:
        return outcome('malformed',[diagnostic('schema-'+str(e.validator),pointer(e.absolute_path)) for e in errors[:50]])
    if expected_kind is not None and data['kind']!=expected_kind:
        return outcome('malformed',[diagnostic('unexpected-input-kind','/kind')])
    failures=identity_diagnostics(data)
    if failures:return outcome('malformed',failures[:50])
    return outcome('structurally-valid',data=data)


def decode(raw,expected_kind=None):
    if not isinstance(raw,bytes):return outcome('malformed',[diagnostic('utf8-bytes-required')])
    if len(raw)>MAX_BYTES:return outcome('malformed',[diagnostic('byte-limit')])
    try:
        text=raw.decode('utf-8',errors='strict')
        data=json.loads(text,object_pairs_hook=pairs,parse_constant=invalid_constant,parse_float=finite_float)
    except UnicodeDecodeError:return outcome('malformed',[diagnostic('invalid-utf8')])
    except InputError as error:return outcome('malformed',[diagnostic(error.code,error.path)])
    except RecursionError:return outcome('malformed',[diagnostic('parse-depth-limit')])
    except (ValueError,OverflowError):return outcome('malformed',[diagnostic('invalid-json-or-number')])
    return validate(data,expected_kind)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['validate'])
    parser.add_argument('--kind',choices=sorted(KINDS))
    parser.add_argument('--input',required=True)
    args=parser.parse_args()
    try:raw=Path(args.input).read_bytes()
    except OSError:
        print(json.dumps(outcome('malformed',[diagnostic('unreadable-input')]),indent=2));return 2
    result=decode(raw,args.kind)
    result.pop('data',None)
    print(json.dumps(result,indent=2))
    return 0 if result['status']=='structurally-valid' else 2


if __name__=='__main__':raise SystemExit(main())
