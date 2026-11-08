from pathlib import Path
import copy
import json
HERE=Path(__file__).resolve().parent
d=copy.deepcopy(json.loads((HERE.parent/'e00/expression.schema.json').read_text())['$defs'])
def obj(props):return {'type':'object','properties':props,'required':list(props),'additionalProperties':False}
def string():return {'type':'string','minLength':1,'maxLength':256}
d={k:d[k] for k in ['ref','frame','file']}
d['evidence_ref']=obj({'token':string(),'source_identity':{'type':'string','pattern':'^[0-9a-f]{64}$'}})
d['assessment']=obj({'ref':string(),'mode':string(),'subject':{'$ref':'#/$defs/ref'},'target':{'$ref':'#/$defs/ref'},'scope':{'type':'string','maxLength':256},'role':{'type':'string'},'output_digest':{'type':'string'},'accepted':{'type':'boolean'}})
d['result']=obj({'schema':{'const':'relational.evidence-collection-result/v1'},'profile':{'enum':['evidence-collection-v1','legacy-single-token-adapter-v1']},
    'policy':{'const':'any-current-accepted-exact-match; all-valid-supports-in-source-order'},'frame':{'$ref':'#/$defs/frame'},'source_identity':{'type':'string','pattern':'^[0-9a-f]{64}$'},
    'source_assertion':string(),'references':{'type':'array','minItems':1,'maxItems':64,'items':{'$ref':'#/$defs/evidence_ref'}},
    'conforms':{'type':'boolean'},'supports':{'type':'array','maxItems':256,'items':{'$ref':'#/$defs/assessment'}},
    'roots_before':{'type':'array','items':{'type':'string'}},'roots_after':{'type':'array','items':{'type':'string'}},
    'claim_scope':{'const':'Exact selected source assertion/evidence-collection projection; no whole graph qualification or external assessment truth.'},
    'authority_effect':{'const':'none'},'application_authorized':{'const':False}})
request=obj({'schema':{'const':'relational.evidence-collection-request/v1'},'profile':{'enum':['evidence-collection-v1','legacy-single-token-adapter-v1']},
    'source':{'$ref':'#/$defs/file'},'source_assertion':string(),'frame':{'$ref':'#/$defs/frame'},
    'references':{'type':'array','maxItems':64,'items':{'$ref':'#/$defs/evidence_ref'}},'legacy_token':{'type':'string','maxLength':256}})
schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'relational.evidence-collection/v1','$defs':d,**request}
(HERE/'evidence-collection.schema.json').write_text(json.dumps(schema,indent=2)+'\n')
