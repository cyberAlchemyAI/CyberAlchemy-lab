from pathlib import Path
import json
H=Path(__file__).resolve().parent;D=json.loads((H.parent/'e00/expression.schema.json').read_text())['$defs'];D={k:D[k] for k in ['file']}
def obj(p):return {'type':'object','properties':p,'required':list(p),'additionalProperties':False}
def arr(x,n=16):return {'type':'array','maxItems':n,'items':x}
D['json_value']={'oneOf':[{'type':'null'},{'type':'boolean'},{'type':'integer','minimum':0,'maximum':1000000000},{'type':'string','maxLength':16384},arr({'$ref':'#/$defs/json_value'},2048),{'type':'object','maxProperties':128,'additionalProperties':{'$ref':'#/$defs/json_value'}}]}
D['source']=obj({'task':{'enum':['P09','E00','E01','E02','E03','E04']},'binding':{'$ref':'#/$defs/file'},'selector':{'enum':['before-graph','extension-result']}})
D['item']=obj({'label':{'type':'string','minLength':1,'maxLength':256},'identity':{'type':'string','pattern':'^[0-9a-f]{64}$'},'value':{'$ref':'#/$defs/json_value'}})
D['result']=obj({'schema':{'const':'relational.canonical-ir-result/v1'},'profile':{'const':'canonical-typed-ir-v1'},'items':arr({'$ref':'#/$defs/item'}),'sources':arr({'$ref':'#/$defs/source'}),'assurance':{'const':'Universal canonical IR import preserves typed denotation; whole finite decoded-value witnesses; raw JSON/parser/emitter/host remain assumptions.'},'authority_effect':{'const':'none'},'application_authorized':{'const':False}})
s={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'relational.canonical-ir/v1','$defs':D,**obj({'schema':{'const':'relational.canonical-ir-request/v1'},'profile':{'const':'canonical-typed-ir-v1'},'sources':arr({'$ref':'#/$defs/source'}),'values':arr({'$ref':'#/$defs/item'})})}
(H/'ir.schema.json').write_text(json.dumps(s,indent=2)+'\n')
