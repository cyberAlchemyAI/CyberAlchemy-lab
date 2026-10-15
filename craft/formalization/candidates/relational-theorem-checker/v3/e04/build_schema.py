from pathlib import Path
import json
H=Path(__file__).resolve().parent;D=json.loads((H.parent/'e00/expression.schema.json').read_text())['$defs'];D={k:D[k] for k in ['ref','file']}
def obj(p):return {'type':'object','properties':p,'required':list(p),'additionalProperties':False}
def arr(x,n=128):return {'type':'array','maxItems':n,'items':x}
def st():return {'type':'string','minLength':1,'maxLength':256}
r={'$ref':'#/$defs/ref'};nat={'type':'integer','minimum':0,'maximum':1000000000};ha={'type':'string','pattern':'^[0-9a-f]{64}$'}
D['state']=obj({'store':st(),'context':r,'epoch':nat,'head':r,'generation':nat,'history':{**arr(r),'minItems':1},'evidence':arr(ha)})
D['declaration']=obj({'ref':r,'predecessor':r,'successor':r,'declared':{'type':'boolean'}})
D['eligibility']=obj({'ref':r,'declaration':r,'predecessor':r,'successor':r,'context':r,'epoch':nat,'value':{'enum':['yes','no','unknown']}})
D['review']=obj({'ref':r,'head':r,'successor':r,'generation':nat,'context':r,'epoch':nat,'accepted':{'type':'boolean'}})
D['result']=obj({'schema':{'const':'relational.lifecycle-result/v1'},'profile':{'const':'candidate-lifecycle-v1'},'source_identity':ha,'eligible':{'type':'boolean'},'before':{'$ref':'#/$defs/state'},'after':{'oneOf':[{'type':'null'},{'$ref':'#/$defs/state'}]},'declaration':{'$ref':'#/$defs/declaration'},'commit':{'const':'not-performed-by-qualification'},'authority_effect':{'const':'none'},'application_authorized':{'const':False}})
s={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'relational.lifecycle/v1','$defs':D,**obj({'schema':{'const':'relational.lifecycle-request/v1'},'profile':{'const':'candidate-lifecycle-v1'},'before':{'$ref':'#/$defs/state'},'declaration':{'$ref':'#/$defs/declaration'},'eligibility':{'$ref':'#/$defs/eligibility'},'review':{'$ref':'#/$defs/review'},'source_identity':ha})}
(H/'lifecycle-transition.schema.json').write_text(json.dumps(s,indent=2)+'\n')
