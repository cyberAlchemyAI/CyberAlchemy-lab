"""Reproduce the pinned OpenAPI projections. Requires PyYAML for this import step."""
import hashlib
import json
import posixpath
import urllib.request
from pathlib import Path
import yaml

HERE=Path(__file__).resolve().parent

def prepare():
    sources=json.loads((HERE/'sources.json').read_text())
    expected={item['path']:item['sha256'] for item in sources['files']}
    cache={}
    def load(name):
        if name not in expected:raise ValueError('Unpinned source reference: '+name)
        if name not in cache:
            url='https://raw.githubusercontent.com/telegraphprotocol/telegraph-api-docs/'+sources['commit']+'/'+name
            with urllib.request.urlopen(url,timeout=30) as response:raw=response.read()
            if hashlib.sha256(raw).hexdigest()!=expected[name]:raise ValueError('Source digest mismatch: '+name)
            cache[name]=yaml.safe_load(raw)
        return cache[name]
    def expand(obj,file,stack=()):
        if isinstance(obj,list):return [expand(value,file,stack) for value in obj]
        if not isinstance(obj,dict):return obj
        if '$ref' in obj:
            name,_,pointer=obj['$ref'].partition('#')
            target=posixpath.normpath(posixpath.join(posixpath.dirname(file),name)) if name else file
            key=(target,pointer)
            if key in stack:raise ValueError('Recursive schema requires a named component')
            value=load(target)
            if pointer:
                for part in pointer.lstrip('/').split('/'):value=value[part.replace('~1','/').replace('~0','~')]
            return expand(value,target,stack+(key,))
        return {key:expand(value,file,stack) for key,value in obj.items() if key not in {'description','summary','example','examples','contact','externalDocs'}}
    for name in ['engine','miner-dispatcher']:
        file='openapi/'+name+'.yaml';spec=expand(load(file),file)
        spec['info']['title']='Alch compatibility contract: '+name
        spec['servers']=[{'url':'/'+name}]
        (HERE/'contracts'/f'{name}.json').write_text(json.dumps(spec,indent=2)+'\n')

if __name__=='__main__':prepare()
