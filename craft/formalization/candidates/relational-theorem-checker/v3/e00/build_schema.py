from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
def obj(props):return {'type':'object','properties':props,'required':list(props),'additionalProperties':False}
def string():return {'type':'string','minLength':1,'maxLength':256}
ref=obj({'id':string(),'version':string()})
frame=obj({'profile':string(),'context':{'$ref':'#/$defs/ref'},'subject':{'$ref':'#/$defs/ref'},'target':{'$ref':'#/$defs/ref'},'scope':string(),'epoch':{'type':'integer','minimum':0,'maximum':1000000000}})
key=obj({**frame['properties'],'condition':{'$ref':'#/$defs/ref'}})
file_ref=obj({'path':{'type':'string','minLength':1,'maxLength':4096},'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}})
expr={'oneOf':[obj({'op':{'const':'atom'},'condition':{'$ref':'#/$defs/ref'}}),
    obj({'op':{'enum':['and','or']},'left':{'$ref':'#/$defs/expr'},'right':{'$ref':'#/$defs/expr'}}),
    obj({'op':{'const':'not'},'operand':{'$ref':'#/$defs/expr'}})]}
entry=obj({'key':{'$ref':'#/$defs/key'},'value':{'enum':['yes','no','unknown']},'assessment':{'$ref':'#/$defs/ref'}})
request=obj({'schema':{'const':'relational.condition-expression-request/v1'},'profile':{'const':'condition-expression-v1'},
    'frame':{'$ref':'#/$defs/frame'},'condition':{'$ref':'#/$defs/ref'},'expression':{'$ref':'#/$defs/expr'},'evaluations':{'type':'array','maxItems':128,'items':{'$ref':'#/$defs/entry'}},
    'mapped':{'oneOf':[{'type':'null'},obj({'request':{'$ref':'#/$defs/file'},'result':{'$ref':'#/$defs/file'}})]}})
result=obj({'schema':{'const':'relational.condition-expression-result/v1'},'profile':{'const':'condition-expression-v1'},
    'frame':{'$ref':'#/$defs/frame'},'condition':{'$ref':'#/$defs/ref'},'expression_identity':{'type':'string','pattern':'^[0-9a-f]{64}$'},'definition_identity':{'type':'string','pattern':'^[0-9a-f]{64}$'},
    'verdict':{'enum':['yes','no','unknown']},'leaf_keys':{'type':'array','maxItems':64,'items':{'$ref':'#/$defs/key'}},
    'supports':{'type':'array','maxItems':128,'items':{'$ref':'#/$defs/entry'}},
    'potential_origins':{'type':'array','maxItems':256,'items':{'type':'string','maxLength':16384}},
    'active_origins':{'type':'array','maxItems':256,'items':{'type':'string','maxLength':16384}},
    'mapped_proof_mode':{'enum':['none','recorded-current-source-witness']},
    'fulfilled':{'const':'not-established'},'admission':{'const':'not-derived'},
    'truth_boundary':{'const':'Supplied exact leaf assessment truth; tested JSON/source bridge; pinned same Lean kernel and host/hash assumptions.'},
    'authority_effect':{'const':'none'},'application_authorized':{'const':False}})
schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'relational.condition-expression/v1',
    '$defs':{'ref':ref,'frame':frame,'key':key,'file':file_ref,'expr':expr,'entry':entry,'result':result},**request}
(HERE/'expression.schema.json').write_text(json.dumps(schema,indent=2)+'\n')
