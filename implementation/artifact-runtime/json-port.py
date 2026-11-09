#!/usr/bin/env python3
"""Generic one-call byte/JSON port. Domain policy belongs to the calling model."""
import base64
import sys
from pathlib import Path
from exact_io import Refusal, bound, decode, encode, leaves, logical, pointer, read, require, sha, write_package

VALUES={}
VALUE_BYTES=0
def perform(value):
    global VALUE_BYTES
    operation=value['operation']
    if operation in ('store-bytes','read-file','view-bytes','probe-bytes','publish-refs','encode-ref'):
        from byte_store import BUFFERS,store,original,probe,publish
        if operation=='store-bytes':return store(base64.b64decode(value['bytes_base64'],validate=True))
        if operation=='read-file':return original(value['root'],value['path'],value['maximum'])
        if operation=='probe-bytes':return probe(BUFFERS[value['ref']],value['markers'],value['keys'])
        if operation=='publish-refs':return publish(value['destination'],value['members'])
        if operation=='encode-ref':return store(encode(value['value']))
        selected=pointer(decode(BUFFERS[value['ref']],source=value.get('source',True)),value.get('selector',''))
        if value.get('register'):
            raw=encode(selected);identity=sha(raw)
            if identity not in VALUES:
                require(len(VALUES)<256 and VALUE_BYTES+len(raw)<=67108864,'value-session-bound')
                VALUES[identity]=selected;VALUE_BYTES+=len(raw)
            return {'value_ref':identity,'canonical_value_sha256':identity}
        return {'canonical_value_sha256':sha(encode(selected)),**({} if value.get('metadata_only') else {'value':selected})}
    if operation == 'render-provider':
        selected=value['binding'];logical(selected['path'])
        root=Path(value['root']).absolute();require(root.resolve()==root,'unsafe-root')
        raw=read(root/selected['path']);require(sha(raw)==selected['sha256'] and len(raw)==selected['bytes'] and selected['digest_kind']=='original-file-sha256','provider-binding-mismatch')
        export=value['export'];require(isinstance(export,str) and export.isidentifier() and not export.startswith('_'),'provider-export-invalid')
        namespace={'__name__':'_bound_artifact_provider_','__file__':str(root/selected['path'])}
        exec(compile(raw,str(root/selected['path']),'exec'),namespace)
        function=namespace.get(export);require(callable(function),'provider-export-missing')
        rendered=function(value['value']);require(isinstance(rendered,str),'provider-result-type')
        from byte_store import store
        return store(rendered.encode('utf-8'))
    if operation == 'validate-value':
        from json_representation import closed_schema
        from jsonschema import Draft202012Validator
        schema=decode(value['schema'].encode());closed_schema(schema);Draft202012Validator.check_schema(schema)
        return {'valid':Draft202012Validator(schema).is_valid(value['value'])}
    if operation == 'value-leaves':
        document=VALUES[value['ref']] if 'ref' in value else value['value']
        result=list(leaves(document));require(len(result)<=65536,'leaf-observation-bound')
        return {'selectors':result,'count':str(len(result))}
    if operation == 'column-observations':
        from json_construction import uint
        document=VALUES[value['ref']];table=pointer(document,value['collection']);require(isinstance(table,list) and len(table)<=256,'column-row-bound')
        offset=uint(value['offset']);count=uint(value['count']);require(count<=100 and offset<=len(table),'column-slice-bound')
        return {'source_digest':value['ref'],'offset':str(offset),'ids':[sha(encode(pointer(row,value['selector']))) for row in table[offset:offset+count]]}
    if operation == 'json-shape':
        selected=value['value']
        kind='null' if selected is None else 'boolean' if isinstance(selected,bool) else 'integer' if isinstance(selected,int) else 'string' if isinstance(selected,str) else 'array' if isinstance(selected,list) else 'object' if isinstance(selected,dict) else 'unsupported'
        size=len(selected) if isinstance(selected,(str,list,dict)) else 0
        return {'kind':kind,'size':str(size),'non_null':selected is not None,'nonempty_string':isinstance(selected,str) and len(selected)>0}
    if operation == 'observe-index':
        from json_construction import uint
        rows=value['values'];require(isinstance(rows,list) and len(rows)<=65536,'index-observation-bound');index=uint(value['index'])
        if index>=len(rows):return {'present':False,'value':None,'canonical_value_sha256':None}
        selected=pointer(rows[index],value.get('selector',''))
        return {'present':True,'value':selected,'canonical_value_sha256':sha(encode(selected))}
    if operation == 'read-member-ref':
        from byte_store import BUFFERS,store
        from exact_io import binding
        from json_construction import uint
        rows=value['members'];require(isinstance(rows,list) and len(rows)<=1024,'member-reference-bound');logical(value['path'])
        selected=[row for row in rows if row['path']==value['path']];require(len(selected)==1,'member-reference-unavailable')
        raw=BUFFERS[selected[0]['ref']];require(len(raw)<=uint(value['maximum']),'byte-read-bound')
        return {**store(raw),'binding':binding(raw,value['path'])}
    if operation == 'export-bytes':
        from byte_store import BUFFERS
        return {'bytes_base64':base64.b64encode(BUFFERS[value['ref']]).decode()}
    if operation == 'merge-objects':
        rows=value['values'];require(isinstance(rows,list) and len(rows)<=256,'merge-object-bound');merged={}
        for row in rows:
            require(isinstance(row,dict),'merge-object-shape');require(not (set(row)&set(merged)),'merge-object-overwrite');merged.update(row)
        return {'value':merged}
    if operation == 'observe-field':
        document=value['value'];key=value['key'];require(isinstance(document,dict) and isinstance(key,str),'field-observation-shape')
        return {'present':key in document,'value':document.get(key)}
    if operation == 'first-field':
        document=value['value'];keys=value['keys'];require(isinstance(keys,list) and len(keys)<=100 and all(isinstance(key,str) for key in keys),'field-selection-bound')
        if isinstance(document,dict):
            for key in keys:
                if key in document:return {'present':True,'value':document[key]}
        return {'present':False,'value':None}
    if operation == 'lookup-records':
        rows=value['rows'];require(isinstance(rows,list) and len(rows)<=256,'lookup-record-bound')
        selected=[row for row in rows if encode(pointer(row,value['selector']))==encode(value['key'])]
        return {'values':selected,'count':str(len(selected))}
    if operation == 'object-keys':
        require(isinstance(value['value'],dict),'object-observation-shape')
        return {'keys':sorted(value['value'])}
    if operation == 'schema-validity':
        from jsonschema import Draft202012Validator
        from jsonschema.exceptions import SchemaError
        try:Draft202012Validator.check_schema(value['value']);return {'valid':True}
        except SchemaError:return {'valid':False}
    if operation == 'byte-metadata':
        from byte_store import BUFFERS
        raw=BUFFERS[value['ref']]
        return {'ref':value['ref'],'sha256':sha(raw),'bytes':len(raw)}
    if operation == 'put-value':
        raw=encode(value['value']);identity=sha(raw)
        if identity not in VALUES:
            require(len(VALUES)<256 and VALUE_BYTES+len(raw)<=67108864,'value-session-bound')
            VALUES[identity]=value['value'];VALUE_BYTES+=len(raw)
        return {'ref':identity,'bytes':len(raw)}
    if operation == 'pointer-metadata':
        selector=value['selector'];require(isinstance(selector,str) and (not selector or selector.startswith('/')),'invalid-json-pointer')
        parts=selector.split('/')[1:] if selector else []
        return {'depth':len(parts),'collection':parts[0].replace('~1','/').replace('~0','~') if parts else ''}
    if operation == 'get-value':
        return {'value':VALUES[value['ref']]}
    if operation == 'check-member-paths':
        from exact_io import member_paths
        member_paths(value['paths']);return {'valid':True}
    if operation == 'collect-json':
        from json_representation import closed_schema
        from jsonschema import Draft202012Validator
        document=VALUES[value['ref']] if 'ref' in value else value['value']
        schema=decode(value['schema'].encode());closed_schema(schema);Draft202012Validator.check_schema(schema)
        validator=Draft202012Validator(schema);skip=value.get('skip_fields',[])
        require(isinstance(skip,list) and len(skip)<=100,'collection-skip-bound')
        output=[];pending=[document];seen=set();visited=0
        order=value.get('order','reverse');require(order in ('reverse','document'),'collection-order-invalid')
        while pending:
            node=pending.pop();visited+=1;require(visited<=4194304,'collection-node-bound')
            if validator.is_valid(node):
                encoded=encode(node)
                if not value.get('unique') or encoded not in seen:
                    require(len(output)<65536,'collection-result-bound');output.append(node);seen.add(encoded)
            elif isinstance(node,dict):
                children=[child for key,child in node.items() if key not in skip];pending.extend(reversed(children) if order=='document' else children)
            elif isinstance(node,list):pending.extend(reversed(node) if order=='document' else node)
        return {'values':output,'count':str(len(output))}
    if operation in ('column-values','describe-column'):
        from json_construction import uint
        document=VALUES[value['ref']] if 'ref' in value else value['value']
        table=pointer(document,value['collection'])
        rows=[table[key] for key in sorted(table)] if isinstance(table,dict) else table
        require(isinstance(rows,list) and len(rows)<=256,'column-row-bound')
        selected=[pointer(row,value['selector']) for row in rows]
        if operation=='describe-column':return {'count':str(len(selected)),'distinct_count':str(len({encode(item) for item in selected}))}
        if value.get('encoding')=='uint-decimal':selected=[str(uint(item)) for item in selected]
        parts=[selected[index:index+100] for index in range(0,len(selected),100)]
        return {'parts':parts,'count':str(len(selected))}
    if operation == 'observe-graph':
        from graph_observation import observe
        document=VALUES[value['ref']] if 'ref' in value else value['value']
        return observe(document,value['layout'],value['query'])
    if operation == 'encode':
        raw=encode(value['value']);return {'bytes_base64':base64.b64encode(raw).decode(),'sha256':sha(raw),'bytes':len(raw)}
    if operation == 'decode':
        return {'value':decode(base64.b64decode(value['bytes_base64'],validate=True),source=value.get('source',False))}
    if operation in ('observe','observe-many','leaves','schema-check'):
        root=Path(value['root']).absolute();require(root.resolve()==root,'unsafe-root')
        raw=bound(root,value['binding']);document=decode(raw,source=True)
        if operation == 'leaves':return {'selectors':list(leaves(document))}
        if operation == 'observe-many':
            require(isinstance(value['selectors'],list) and len(value['selectors'])<=1024,'selector-budget')
            return {'observations':[{'selector':selector,'value':pointer(document,selector),'canonical_value_sha256':sha(encode(pointer(document,selector)))} for selector in value['selectors']]}
        if operation == 'observe':
            selected=pointer(document,value.get('selector',''))
            return {'value':selected,'canonical_value_sha256':sha(encode(selected)),'original_binding':value['binding']}
        schema=decode(bound(root,value['schema_binding']))
        from json_representation import closed_schema
        closed_schema(schema)
        from jsonschema import Draft202012Validator
        Draft202012Validator.check_schema(schema)
        errors=list(Draft202012Validator(schema).iter_errors(document))
        return {'valid':not errors,'error_count':len(errors)}
    if operation == 'construct-value':
        from json_construction import construct
        document,raw=construct(value['batches'],value['documents'])
        return {'value':document,'bytes_base64':base64.b64encode(raw).decode(),'sha256':sha(raw),'bytes':len(raw),'source_posture':'computed-values-only'}
    if operation == 'select-value':
        selected=pointer(value['value'],value['selector'])
        return {'canonical_value_sha256':sha(encode(selected)),**({} if value.get('metadata_only') else {'value':selected})}
    if operation == 'expand-variants':
        from variant_encoding import expand
        return {'values':expand(value['groups'],value['documents'])}
    if operation == 'validate-json':
        from json_representation import closed_schema
        from jsonschema import Draft202012Validator
        root=Path(value['root']).absolute();require(root.resolve()==root,'unsafe-root')
        schema=pointer(decode(bound(root,value['schema_binding'])),value.get('schema_selector',''))
        closed_schema(schema);Draft202012Validator.check_schema(schema)
        errors=list(Draft202012Validator(schema).iter_errors(value['value']))
        return {'valid':not errors,'error_count':len(errors)}
    if operation == 'represent-json':
        from json_representation import represent
        document=represent(value['value'],value['plan']);raw=encode(document)
        return {'value':document,'bytes_base64':base64.b64encode(raw).decode(),'sha256':sha(raw),'bytes':len(raw)}
    if operation == 'construct-json':
        from json_construction import construct, read_sources
        root=Path(value['root']).absolute();require(root.resolve()==root,'unsafe-root')
        documents=read_sources(root,value['sources'])
        document,raw=construct(value['batches'],documents)
        return {'value':document,'bytes_base64':base64.b64encode(raw).decode(),'sha256':sha(raw),'bytes':len(raw)}
    if operation == 'publish':
        members={row['path']:base64.b64decode(row['bytes_base64'],validate=True) for row in value['members']}
        require(len(members)==len(value['members']),'duplicate-member-path')
        write_package(value['destination'],members)
        return {'published':True,'members':len(members)}
    raise Refusal('unsupported-generic-operation','Unsupported generic operation')

def response(raw):
    try:
        result=perform(decode(raw,maximum=67108864))
        return encode({'result':result,'authority_effect':'none'}),0
    except Exception as error:
        return encode({'error':getattr(error,'code','generic-port-refused-'+type(error).__name__),'authority_effect':'none'}),getattr(error,'exit_code',2)

if __name__=='__main__':
    if sys.argv[1:]==['--stream']:
        while True:
            raw=sys.stdin.buffer.readline(67108866)
            if not raw:break
            if len(raw)>67108864 or not raw.endswith(b'\n'):
                sys.stdout.buffer.write(encode({'error':'frame-budget','authority_effect':'none'}));sys.stdout.buffer.flush();break
            output,_=response(raw)
            sys.stdout.buffer.write(output);sys.stdout.buffer.flush()
    else:
        output,status=response(sys.stdin.buffer.read())
        sys.stdout.buffer.write(output)
        raise SystemExit(status)
