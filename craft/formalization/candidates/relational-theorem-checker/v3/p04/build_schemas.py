"""Closed public query and explanation variants."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
def obj(p):return {'type':'object','properties':p,'required':list(p),'additionalProperties':False}
def arr(p,**limits):return {'type':'array','items':p,**limits}
def nullable(p):return {'anyOf':[p,{'type':'null'}]}
string={'type':'string','minLength':1};sha={'type':'string','pattern':'^[0-9a-f]{64}$'}
nat={'type':'integer','minimum':0};boolean={'type':'boolean'}
ref=obj({'id':string,'version':string})
key=obj({'id':string,'version':string,'hash':sha})
value={'oneOf':[obj({'kind':{'const':'reference'},'id':string,'version':string})]+[obj({'kind':{'const':k},'value':nat if k=='epoch' else string}) for k in ['effect','scope','epoch','text']]}
atom=obj({'predicate':key,'values':arr(value,maxItems=4)})
support=obj({'schema':{'const':'relational.source-support/v2'},'atom':atom,**{k:sha for k in ['source_identity','selected_graph_identity','profile_identity','catalog_identity','context_identity']},'witness':{'oneOf':[obj({'kind':{'enum':['conformance','existential-conformance']},'assertion_id':string,'assessment_token':string}),obj({'kind':{'const':'node-kind'},'node_ref':ref})]}})
node=obj({'index':nat,'atom':atom,'kind':{'enum':['base','apply']},'rule':nullable(key),'substitution':arr(obj({'slot':nat,'sort':{'enum':['reference','effect','scope','epoch','text']},'value':value})),'premises':arr(nat),'leaf':{'enum':[None,'source-observation','independent-root','supplied-truth']},'supports':arr(support),'truth':nullable(string)})
trace=nullable(obj({'root':nat,'nodes':arr(node,maxItems=4096),'truncated':boolean,'omitted_indices':arr(nat)}))
base={'schema':{'const':'relational.explanation/v3'},'claim_scope':string,'truth_assumptions':arr(string),'text':string,'application_authorized':{'const':False},'authority_effect':{'const':'none'}}
recursive=obj({**base,'variant':{'const':'recursive'},'outcome':{'enum':['summary','present','absent-in-complete-profile','outside-profile','invalid-query','incomplete']},'inspection':{'enum':['recorded-current','incomplete']},'model_class':nullable(string),'trace':trace,'supports':arr(support),'source_support_count':nat})
inheritance=obj({'id':string,'subject':ref,'contract':ref,'binding':ref,'scope':string,'condition':string})
fact=obj({'edge':inheritance,'norm':obj({'mode':{'enum':['require','forbid','permit']},'action':string})})
evaluation_key=obj({'profile':string,'condition':ref,'context':ref,'subject':ref,'target':ref,'scope':string,'epoch':nullable(nat)})
mapped={**base,'verdict':{'enum':['yes','no','unknown','invalid']},'source_assertion':string,'inspection':{'const':'recorded-current'}}
norm=obj({**mapped,'variant':{'const':'inheritance'},'condition_key':evaluation_key,'condition_status':{'enum':['yes','no','unknown','invalid']},'potential_norms':arr(fact),'active_norms':arr(fact),'active_conflicts':arr(arr(fact,minItems=2,maxItems=2)),'fulfilled':{'const':'not-established'},'admission':{'const':'not-derived'},'potential_scope':string,'certificate_scope':string})
period=obj({'start':nat,'stop':nat});assessment=obj({'ref':ref,'accepted':boolean})
snapshot=obj({'ref':ref,'epoch':nat,'policies':arr(assessment),'gates':arr(assessment)})
edge=obj({'id':string,'agent':ref,'principal':ref,'delegation':ref,'scope':string,'period':period,'revokedAt':nullable(nat)})
delegation=obj({**mapped,'variant':{'const':'delegation'},'delegation':obj({'edge':edge,'action':string,'snapshot':snapshot,'redelegated':boolean})})
for name,schema in [('query',atom),('explanation',{'oneOf':[recursive,norm,delegation]})]:
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:relational:v3:'+name,**schema}
    (HERE/(name+'.schema.json')).write_text(json.dumps(schema,indent=2)+'\n')
