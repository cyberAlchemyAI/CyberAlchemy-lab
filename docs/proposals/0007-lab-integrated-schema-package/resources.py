"""Offline schema resources selected by exact local bindings; never retrieve from network."""
import copy,json
from pathlib import Path
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def build_registry():
    registry=Registry()
    aliases={}
    deps=json.loads((HERE/'schema-dependencies.json').read_text())['bindings']
    by_source={}
    for b in deps:
        by_source.setdefault(b['source_path'],{})[b['source_ref']]=(ROOT/b['target_path']).resolve().as_uri()+('#'+b['source_ref'].split('#',1)[1] if '#' in b['source_ref'] else '')
    def normalized(path):
        value=json.loads(path.read_text());mapping=by_source.get(str(path.relative_to(ROOT)),{})
        def walk(v):
            if isinstance(v,dict):
                return {k:mapping.get(x,x) if k=='$ref' else walk(x) for k,x in v.items()}
            if isinstance(v,list):return [walk(x) for x in v]
            return v
        return walk(value)
    def add(uri, value):
        nonlocal registry
        resource=Resource.from_contents(value,default_specification=DRAFT202012)
        registry=registry.with_resource(uri,resource)
        declared=value.get('$id')
        if declared:
            if declared in aliases and aliases[declared]!=value:
                raise ValueError('conflicting schema id '+declared)
            aliases[declared]=value
            registry=registry.with_resource(declared,resource)
    for p in sorted((HERE/'schemas').glob('*.schema.json')):
        value=json.loads(p.read_text());add(value['$id'],value)
    domains=json.loads((HERE/'domain-bindings.json').read_text())
    for b in domains['bindings']:
        value=normalized(ROOT/b['schema_path'])
        add(b['schema_resource_uri'],value)
        add((ROOT/b['schema_path']).resolve().as_uri(),value)
    for p in sorted({b['target_path'] for b in deps}):
        add((ROOT/p).resolve().as_uri(),normalized(ROOT/p))
    catalog=json.loads((HERE/'schema-catalog.json').read_text())
    for b in catalog['reused_storage_schemas']:
        add(b['resource_uri'],json.loads((ROOT/b['path']).read_text()))
    b=catalog['ephemeral_memory_binding']
    add(b['resource_uri'],json.loads((ROOT/b['path']).read_text()))
    return registry.crawl()
