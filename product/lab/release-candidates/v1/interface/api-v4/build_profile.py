"""Declare exact catalog representations and a versioned reader wire contract."""
import copy
from protocol import *


def write(path,value):path.write_bytes(source.encoded(value))


def build():
    rows=[];branches=[];sources={}
    def remember(path,digest):sources[path]={'path':path,'sha256':digest};source.original(sources[path])
    with source.replay_source('engineering') as view:
        for ref,contract in sorted(view.data['projection']['contracts'].items()):
            doc=contract['artifact'];path=contract['artifact_path'];digest=contract['artifact_sha256'];remember(path,digest)
            identity=ref.rsplit('/',1)[0];selector='';kind='source-file-descriptor';body=doc
            if doc.get('artifact_type_id')!=identity:
                matches=[(i,value) for i,value in enumerate(doc.get('registered_types',[])) if value['artifact_type_ref']==ref]
                source.require(len(matches)==1,'exact registered contract entry missing or ambiguous: '+ref)
                i,body=matches[0];selector='/registered_types/'+str(i);kind='embedded-contract-declaration'
                source.require(body['schema_path']==contract['schema_path'] and body['schema_sha256']==contract['schema_sha256']
                    and body.get('schema_selector')==contract.get('schema_selector'),'embedded contract binding differs from admitted registry')
            meta=doc['classification']['artifact_type_ref']
            source.require(meta in view.data['projection']['contracts'],'declared metatype outside captured catalog')
            raw=view.handle.common.encoded(body) if selector else source.original({'path':path,'sha256':digest})
            locator=path+('#'+selector if selector else '')
            row={'represented_contract_ref':ref,'identity_ref':identity,'meta_carrier_ref':meta,'representation_kind':kind,
                'source_binding':{'path':path,'sha256':digest},'selector':selector,'byte_sha256':source.sha(raw),'size_bytes':len(raw),
                'source_locator':locator,'body_structural_sha256':view.handle.common.digest(body),
                'admission_decision_ref':contract['admission_decision_ref'],'lifecycle_state':contract['lifecycle_state'],
                'instance_schema_binding':{'ref':contract['schema_path'],'sha256':contract['schema_sha256']},
                'instance_schema_selector':contract.get('schema_selector')}
            rows.append(row)
            header={'$ref':'urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/artifact_ref',
                'properties':{key:{'const':value} for key,value in {'identity_ref':identity,'version_ref':ref,'carrier_ref':meta,'byte_sha256':source.sha(raw)}.items()}}
            properties={'schema_version':{'const':'lab-catalog-representation-envelope/v1-candidate'},'artifact':header,
                'represented_contract_ref':{'const':ref},'representation_kind':{'const':kind},'body':{'const':body},
                'source_cut':{'$ref':'urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/source_cut'},
                'content':{'const':{'content_ref':locator,'byte_sha256':source.sha(raw),'size_bytes':len(raw),'media_type':'application/json'}},
                'source_locator':{'const':locator},'enclosing_source_binding':{'const':{'ref':path,'sha256':digest}},
                'representation_profile_binding':{'$ref':'urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/binding'},
                'effective_admission_basis':{'type':'array','items':{'$ref':'urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/binding'}},
                'claim_ceiling':{'type':'string','minLength':1},'authority_effect':{'const':'none'}}
            branches.append({'type':'object','additionalProperties':False,'required':list(properties),'properties':properties})
    mapping={'schema_version':'lab-catalog-representation-map/v1-candidate','scope':'Exact captured admitted contract catalog; a declaration is not a domain instance.',
        'identity_rule':'A catalog declaration uses its exact represented carrier reference stem; original descriptor/container identity remains in original source bytes.',
        'rows':rows,'source_bindings':sorted(sources.values(),key=lambda b:b['path']),'authority_effect':'none','actual_owner_outcome':None}
    write(HERE/'catalog-representations.json',mapping)
    map_binding=binding(str((HERE/'catalog-representations.json').relative_to(ROOT)),(HERE/'catalog-representations.json').read_bytes())
    for branch in branches:branch['properties']['representation_profile_binding']={'const':map_binding}
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:cyberalchemy-lab:protocol:catalog-representation-envelope:v1-candidate',
        'title':'Exact captured descriptor or registered contract entry; distinct from domain instance envelope','oneOf':branches}
    write(HERE/'schemas/catalog-envelope.schema.json',schema)
    inspected=source.parse((SCHEMAS/'schemas/artifact-inspect-result.schema.json').read_bytes())
    inspected['$id']='urn:cyberalchemy-lab:protocol:artifact-inspect-result:v2-candidate'
    inspected['properties']['schema_version']['const']='lab-artifact-inspect-result/v2-candidate'
    envelopes={'anyOf':[{'$ref':'urn:cyberalchemy-lab:protocol:artifact-envelope:v1-candidate'},
        {'$ref':schema['$id']}]}
    inspected['properties']['envelope']={'anyOf':[*envelopes['anyOf'],{'type':'null'}]}
    for condition in inspected['allOf']:
        if 'envelope' in condition.get('then',{}).get('properties',{}):condition['then']['properties']['envelope']=envelopes
    write(HERE/'schemas/artifact-inspect-result.schema.json',inspected)
    for name in ['api-call','api-reply']:
        value=source.parse((API/'schemas'/ (name+'.schema.json')).read_bytes())
        value['$id']=value['$id'].replace('v1-candidate','v2-candidate')
        for branch in value['oneOf']:
            branch['properties']['schema_version']['const']='lab-'+name+'/v2-candidate'
            key='expected_contract_profile_binding' if name=='api-call' else 'contract_profile_binding'
            branch['required'].append(key)
            branch['properties'][key]=({'anyOf':[{'$ref':'urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/binding'},{'type':'null'}]}
                if name=='api-call' else {'$ref':'urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/binding'})
            if name=='api-reply' and branch['properties']['operation']['const']=='artifact.inspect' and branch['properties']['kind']['const']=='result':
                branch['properties']['message']={'$ref':inspected['$id']}
        write(HERE/'schemas'/(name+'.schema.json'),value)
    files=[source.bind(p) for p in sorted((HERE/'schemas').glob('*.json'))]+[source.bind(HERE/'catalog-representations.json')]
    files+=[source.bind(HERE/name) for name in ['protocol.py','auth.py','handlers.py','service.py','serve.py','artifact_model.py','projection.py','representations.py','authentication.schema.json','source_bridge.py','source-selection.json']]
    profile={'schema_version':'lab-reader-contract-profile/v2-candidate','wire_call_version':'lab-api-call/v2-candidate',
        'wire_reply_version':'lab-api-reply/v2-candidate','implemented_operations':list(SUPPORTED),
        'original_operation_catalog_binding':source.bind(API/'api-contracts.json'),'original_schema_inputs_binding':source.bind(INPUTS),
        'files':files,'authority_effect':'none','actual_owner_outcome':None,
        'claim_ceiling':'Exact source-specific catalog read representation and original domain instance contracts; no new source admission or general prospective descriptor validator.'}
    write(HERE/'contract-profile.json',profile)
    print(json.dumps({'result':'PASS','catalog_versions':len(rows),'embedded_declarations':sum(r['selector']!='' for r in rows),
        'contract_profile_binding':source.bind(HERE/'contract-profile.json'),'authority_effect':'none'},sort_keys=True))


if __name__=='__main__':build()
