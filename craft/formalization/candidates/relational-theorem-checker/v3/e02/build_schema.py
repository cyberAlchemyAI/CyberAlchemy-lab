import json
from pathlib import Path
H=Path(__file__).resolve().parent
D=json.loads((H.parent/'e00/expression.schema.json').read_text())['$defs'];D={k:D[k] for k in ['ref','frame','file']}
def obj(p):return {'type':'object','properties':p,'required':list(p),'additionalProperties':False}
def arr(items,n=64):return {'type':'array','maxItems':n,'items':items}
def st():return {'type':'string','minLength':1,'maxLength':256}
r={'$ref':'#/$defs/ref'};nat={'type':'integer','minimum':0,'maximum':1000000000};truth={'enum':['yes','no','unknown']}
D['principal']=obj({'ref':r,'roles':arr({'enum':['principal','agent']},2)})
D['hop']=obj({'ref':r,'principal':r,'agent':r,'scopes':arr(st(),32),'actions':arr(st(),32),'start':nat,'finish':nat,'redelegate':{'type':'boolean'}})
D['assessment']=obj({'ref':r,'hop':r,'kind':{'enum':['gate','revocation']},'frame':{'$ref':'#/$defs/frame'},'value':truth})
D['source']=obj({'profile':{'const':'bounded-redelegation-v1'},'revision':r,'frame':{'$ref':'#/$defs/frame'},'principals':arr({'$ref':'#/$defs/principal'},32),'hops':arr({'$ref':'#/$defs/hop'}),'assessments':arr({'$ref':'#/$defs/assessment'},128)})
D['query']=obj({'principal':r,'agent':r,'scope':st(),'action':st(),'epoch':nat,'max_depth':{'type':'integer','minimum':1,'maximum':4}})
D['result']=obj({'schema':{'const':'relational.chain-result/v1'},'profile':{'const':'bounded-redelegation-v1'},'source_identity':{'type':'string','pattern':'^[0-9a-f]{64}$'},'frame':{'$ref':'#/$defs/frame'},'query':{'$ref':'#/$defs/query'},'verdict':truth,'enumerated_words':{'type':'integer','minimum':0,'maximum':4096},'supported_paths':arr(arr(r,4),4096),'unknown_paths':arr(arr(r,4),4096),'completeness':{'const':'All source edge words of length 1..max_depth; joined simple paths only.'},'admission':{'const':'not-derived'},'authority_effect':{'const':'none'},'application_authorized':{'const':False}})
s={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'relational.chain/v1','$defs':D,**obj({'schema':{'const':'relational.chain-request/v1'},'profile':{'const':'bounded-redelegation-v1'},'source':{'$ref':'#/$defs/source'},'source_identity':{'type':'string','pattern':'^[0-9a-f]{64}$'},'query':{'$ref':'#/$defs/query'}})}
(H/'chain.schema.json').write_text(json.dumps(s,indent=2)+'\n')
