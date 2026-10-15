"""Explicit request/response compilation from the bound written C1 contract."""
from common import *
QUERY_IDS=['lifecycle-slice','authority-explanation','capability-provenance']
SCOPES={'d75-selected-source':'decision:0075','historical-d73-slice':'decision:0073','O05-source-interpretation':'candidate:O05'}
OBLIGATIONS=['current-state','separate-project-histories','exact-predecessor-path','state-admission','recorded-admission','exact-authorization','effect-scope','exact-lineage','implementation-bridge','effectiveness','new-action-permission','ontology-event-join']
def compile_contract():
    p=HERE/'contracts'
    request={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:lab:O03:query-request:v1-candidate','type':'object','additionalProperties':False,
        'required':['schema_version','query_id','root','scope_ref','admission_as_of','view','direction','edge_selection','limits','obligations'],
        'properties':{'schema_version':{'const':'lab-three-lens-query/v1-candidate'},'query_id':{'enum':QUERY_IDS},'root':{'type':'string','minLength':1,'maxLength':2048},
        'scope_ref':{'enum':list(SCOPES)},'admission_as_of':{'type':'string','minLength':1},'view':{'enum':['current','historical']},
        'direction':{'enum':['incoming','outgoing','both']},'edge_selection':{'type':'array','uniqueItems':True,'maxItems':100,'items':{'type':'string','minLength':1}},
        'obligations':{'type':'array','minItems':1,'maxItems':len(OBLIGATIONS),'uniqueItems':True,'items':{'enum':OBLIGATIONS}},
        'limits':{'type':'object','additionalProperties':False,'required':['depth','nodes','edges'],'properties':{
            'depth':{'type':'integer','minimum':0,'maximum':20},'nodes':{'type':'integer','minimum':1,'maximum':1000},'edges':{'type':'integer','minimum':1,'maximum':4000}}}}}
    response={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:lab:O03:query-response:v1-candidate','type':'object','additionalProperties':False,
        'required':['schema_version','query','result_status','source_snapshot','freshness','subjects','state_tracks','connections','explanation_paths','claims','gaps','coverage','authority_effect','replay_source','claim_ceiling'],
        'properties':{'schema_version':{'const':'lab-three-lens-response/v1-candidate'},'query':{'type':'object'},'result_status':{'enum':['complete','partial','blocked']},
            'source_snapshot':{'type':'object'},'freshness':{'type':'object'},'subjects':{'type':'array'},'state_tracks':{'type':'array'},'connections':{'type':'array'},
            'explanation_paths':{'type':'array'},'claims':{'type':'array'},'gaps':{'type':'array'},'coverage':{'type':'object'},'authority_effect':{'const':'none'},'replay_source':{'const':False},'claim_ceiling':{'type':'string','minLength':1}}}
    response['properties']['query']=request
    response['properties']['freshness']={'type':'object','additionalProperties':False,'required':['state','changed','missing','unsafe','unchecked','checked_count'],
        'properties':{'state':{'enum':['current','historical','stale','unknown']},**{k:{'type':'array','items':{'type':'string'}} for k in ['changed','missing','unsafe','unchecked']},'checked_count':{'type':'integer','minimum':0}}}
    for field,required in {'source_snapshot':['manifest_digest','source_cut_digest','graph_digest','admission_epoch','bindings','histories','historical_source_relocations','check_time_rule','canonical_ontology_cut'],
        'coverage':['scope_ref','selected_subjects','partition','subject_rows','required_obligations','selected_nodes','selected_edges','truncated','omitted_frontier','continuation','source_item_accounting','excluded_areas']}.items():
        response['properties'][field]={'type':'object','required':required,'additionalProperties':False,'properties':{k:{} for k in required}}
    for field,required in {'subjects':['graph_id','namespace','kind','identity_ref','version_ref','source_binding'],
        'connections':['edge_id','source','target','predicate','mode','direction','qualifiers','evidence','relation_subject_ref','effective_admission','version_resolution','confirmed','endpoint_semantics','profile_posture'],
        'claims':['obligation','status','scope_ref','basis','authority_effect'],'explanation_paths':['root','target','steps']}.items():
        response['properties'][field]={'type':'array','items':{'type':'object','required':required}}
    response['properties']['connections']['items']['additionalProperties']=False
    response['properties']['connections']['items']['properties']={k:{} for k in response['properties']['connections']['items']['required']}
    response['properties']['connections']['items']['properties'].update(direction={'enum':['directed','symmetric']},version_resolution={'const':'exact'},confirmed={'type':'boolean'})
    response['properties']['connections']['items']['allOf']=[{'if':{'properties':{'direction':{'const':'symmetric'}}},'then':{'properties':{'mode':{'const':'source-local-interpretation'}}}}]
    emit(p/'request.schema.json',request);emit(p/'response.schema.json',response)
    emit(p/'query-contract.json',{'schema_version':'lab-three-lens-contract/v1-candidate','source_binding':bind(ROOT/'docs/plans/0007-governance-architecture-ontology/C1-QUERY-CONTRACT.md'),
        'empty_historical_machine_contract_binding':bind(ROOT/'docs/plans/0007-governance-architecture-ontology/c1-query-contract.json'),'historical_file_repaired':False,
        'scopes':SCOPES,'query_ids':QUERY_IDS,'defaults':{'depth':4,'nodes':100,'edges':200},'obligations':OBLIGATIONS,
        'request_schema_binding':bind(p/'request.schema.json'),'response_schema_binding':bind(p/'response.schema.json'),
        'direction_rule':'Navigation may be incoming; original edges remain directed with original source/target tuples.',
        'currentness_rule':'Changed, missing or unchecked evidence excludes confirmed current traversal; original observations remain historically inspectable.',
        'business_system_rule':'Both endpoint bindings and exact alignment evidence are necessary. Source discovery and declared realization are independently labeled.',
        'native_graph_acceleration':'not selected; deterministic Python query graph is normative. Existing native library verifies original ontology event joins only.',
        'authority_effect':'none','actual_owner_outcome':None,'replay_source':False})
if __name__=='__main__':compile_contract()
