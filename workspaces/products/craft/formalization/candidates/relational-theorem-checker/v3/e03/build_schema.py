import json
from pathlib import Path
H=Path(__file__).resolve().parent;D=json.loads((H.parent/'e00/expression.schema.json').read_text())['$defs'];D={k:D[k] for k in ['ref','frame','file']}
def obj(p):return {'type':'object','properties':p,'required':list(p),'additionalProperties':False}
def arr(x,n=64):return {'type':'array','maxItems':n,'items':x}
r={'$ref':'#/$defs/ref'};truth={'enum':['yes','no','unknown']}
D['action']=obj({'ref':r,'request':r,'requirement':r,'frame':{'$ref':'#/$defs/frame'},'outputs':arr(r),'accepted':{'type':'boolean'}})
D['output']=obj({'ref':r,'action':r,'accepted':{'type':'boolean'}})
D['evaluation']=obj({'ref':r,'criterion':r,'request':r,'requirement':r,'action':r,'output':r,'frame':{'$ref':'#/$defs/frame'},'value':truth})
D['source']=obj({'revision':r,'frame':{'$ref':'#/$defs/frame'},'request':r,'requirement':r,'linked':{'type':'boolean'},'criteria':{**arr(r,32),'minItems':1},'actions':arr({'$ref':'#/$defs/action'}),'outputs':arr({'$ref':'#/$defs/output'}),'evaluations':arr({'$ref':'#/$defs/evaluation'})})
D['criterion_result']=obj({'criterion':r,'verdict':truth,'supports':arr({'$ref':'#/$defs/evaluation'})})
D['result']=obj({'schema':{'const':'relational.fulfillment-result/v1'},'profile':{'const':'verified-fulfillment-v1'},'source_identity':{'type':'string','pattern':'^[0-9a-f]{64}$'},'request':r,'requirement':r,'linked':{'type':'boolean'},'fulfilled':{'type':'boolean'},'verdict':truth,'criteria':arr({'$ref':'#/$defs/criterion_result'},32),'truth_boundary':{'const':'All named criteria under supplied exact action/output/evaluation truth; no real-world authenticity or execution proof.'},'authority_effect':{'const':'none'},'application_authorized':{'const':False}})
s={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'relational.fulfillment/v1','$defs':D,**obj({'schema':{'const':'relational.fulfillment-request/v1'},'profile':{'const':'verified-fulfillment-v1'},'source':{'$ref':'#/$defs/source'},'source_identity':{'type':'string','pattern':'^[0-9a-f]{64}$'}})}
(H/'fulfillment.schema.json').write_text(json.dumps(s,indent=2)+'\n')
