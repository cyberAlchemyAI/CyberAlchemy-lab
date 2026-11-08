"""Bounded prototype compiler for the Alch http-contract-v1 profile.

Contract-owned field definitions are imported, never duplicated in Alch.
No dependency on the deployed semantic-host-v1 compiler is implied.
"""
import argparse
import hashlib
import json
import re
import shlex
from pathlib import Path

METHODS = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options'}

def compile_source(source):
    source = Path(source).resolve()
    text = source.read_text()
    top, blocks, current = {}, [], None
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if not line.startswith(' '):
            match = re.fullmatch(r'(integration|api) ([A-Za-z][A-Za-z0-9]*):', line)
            if match:
                current = {'kind': match[1], 'id': match[2], 'fields': {}, 'exclude': []}
                blocks.append(current)
                continue
            words = shlex.split(line)
            if len(words) != 2 or words[0] not in {'profile', 'domain', 'owner'} or words[0] in top:
                raise ValueError(f'ALCH_HTTP_SYNTAX line {number}')
            top[words[0]] = words[1]
            current = None
        else:
            if not current or not line.startswith('  ') or line.startswith('   '):
                raise ValueError(f'ALCH_HTTP_INDENT line {number}')
            words = shlex.split(line)
            if len(words) == 3 and words[0] == 'exclude' and current['kind'] == 'api':
                current['exclude'].append((words[1], words[2]))
            elif len(words) == 2 and words[0] not in current['fields']:
                current['fields'][words[0]] = words[1]
            else:
                raise ValueError(f'ALCH_HTTP_CLAUSE line {number}')
    if set(top) != {'profile', 'domain', 'owner'} or top['profile'] != 'http-contract-v1':
        raise ValueError('ALCH_HTTP_PROFILE')
    integrations, apis, routes, excluded, digests = {}, {}, [], [], {}
    digests[source.name] = hashlib.sha256(source.read_bytes()).hexdigest()
    for block in blocks:
        if block['kind'] != 'integration':
            continue
        fields = block['fields']; identity = block['id']
        if identity in integrations or set(fields) != {'transport','url-env','payment','timeout-seconds','max-request-bytes','max-response-bytes'}:
            raise ValueError('ALCH_HTTP_INTEGRATION_FIELDS')
        if fields['transport'] != 'http-proxy' or fields['payment'] != 'forward-x402' or not re.fullmatch(r'[A-Z][A-Z0-9_]*', fields['url-env']):
            raise ValueError('ALCH_HTTP_INTEGRATION')
        for key, ceiling in [('timeout-seconds',300),('max-request-bytes',104857600),('max-response-bytes',1073741824)]:
            fields[key] = int(fields[key])
            if not 1 <= fields[key] <= ceiling:
                raise ValueError('ALCH_HTTP_LIMIT')
        integrations[identity] = fields
    for block in blocks:
        if block['kind'] != 'api':
            continue
        fields = block['fields']; identity = block['id']
        if identity in apis or set(fields) != {'contract','mount','integration'} or fields['integration'] not in integrations:
            raise ValueError('ALCH_HTTP_API')
        if not re.fullmatch(r'/[A-Za-z0-9_-]+', fields['mount']):
            raise ValueError('ALCH_HTTP_MOUNT')
        file = (source.parent / fields['contract']).resolve()
        if not file.is_relative_to(source.parent) or file.suffix != '.json':
            raise ValueError('ALCH_HTTP_CONTRACT_PATH')
        raw = file.read_bytes(); spec = json.loads(raw)
        if spec.get('openapi') != '3.0.3':
            raise ValueError('ALCH_HTTP_OPENAPI_VERSION')
        digests[str(file.relative_to(source.parent))] = hashlib.sha256(raw).hexdigest()
        found = set()
        for path, item in spec['paths'].items():
            if not path.startswith('/') or '?' in path or '#' in path:
                raise ValueError('ALCH_HTTP_CONTRACT_ROUTE')
            for method, operation in item.items():
                if method not in METHODS:
                    continue
                key = (method.upper(), path)
                if key in block['exclude']:
                    found.add(key)
                    excluded.append({'api':identity,'method':key[0],'path':fields['mount']+path})
                    continue
                if any('internalSecret' in s for s in operation.get('security', spec.get('security',[]))):
                    raise ValueError('ALCH_HTTP_INTERNAL_ROUTE_MUST_BE_EXCLUDED')
                full = fields['mount']+path
                pattern = re.escape(full)
                for parameter in re.findall(r'\{([^}]+)\}', full):
                    pattern = pattern.replace(re.escape('{'+parameter+'}'), '.+' if parameter == 'proxyPath' else '[^/]+')
                routes.append({'api':identity,'integration':fields['integration'],'method':key[0],'path':full,'upstream_path':path,'pattern':'^'+pattern+'$','operation_id':operation.get('operationId',method+path),'contract':operation})
        if found != set(block['exclude']):
            raise ValueError('ALCH_HTTP_UNKNOWN_EXCLUSION')
        apis[identity] = {'mount':fields['mount'],'contract':spec,'integration':fields['integration']}
    if not apis or len({(r['method'],r['path']) for r in routes}) != len(routes):
        raise ValueError('ALCH_HTTP_DUPLICATE_OR_EMPTY_ROUTES')
    if len({v['mount'] for v in apis.values()}) != len(apis):
        raise ValueError('ALCH_HTTP_DUPLICATE_MOUNT')
    routes.sort(key=lambda r: ('{' in r['path'], r['path'].count('{'), -len(r['path']),r['method']))
    return {'profile':top['profile'],'domain':top['domain'],'owner':top['owner'],'integrations':integrations,'apis':apis,'routes':routes,'excluded':excluded,'source_digests':digests}

def build(source, output):
    model = compile_source(source)
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    (output/'application.json').write_text(json.dumps(model,indent=2)+'\n')
    ontology = {'status':'prototype-navigation-only','authority_effect':'none','domain':model['domain'],
        'nodes':[{'id':name,'type':'Integration','transport':b['transport']} for name,b in model['integrations'].items()]+[
            {'id':r['api']+'.'+r['operation_id'],'type':'Operation','method':r['method'],'path':r['path']} for r in model['routes']],
        'relations':[{'from':r['api']+'.'+r['operation_id'],'type':'usesIntegration','to':r['integration']} for r in model['routes']],
        'open_questions_ref':'../README.md#open-questions'}
    (output/'ontology.json').write_text(json.dumps(ontology,indent=2)+'\n')
    (output/'coverage.json').write_text(json.dumps({'http_operations':len(model['routes']),'excluded':model['excluded'],'source_digests':model['source_digests'],'claim':'HTTP route preparation; not upstream semantic or payment conformance','open_questions_ref':'../README.md#open-questions'},indent=2)+'\n')
    return model

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('source');parser.add_argument('--out',required=True)
    args=parser.parse_args();model=build(args.source,args.out)
    print(json.dumps({'status':'PASS','http_operations':len(model['routes']),'excluded':len(model['excluded'])}))
