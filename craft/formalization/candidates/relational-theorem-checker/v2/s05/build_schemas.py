from pathlib import Path
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'s15'));import contracts as c
s=c.s;HERE=Path(__file__).resolve().parent
text={'type':'string','minLength':1};sha={'type':'string','pattern':'^[0-9a-f]{64}$'}
def obj(p):return {'type':'object','properties':p,'required':list(p),'additionalProperties':False}
def arr(p):return {'type':'array','items':p}
base=s.read(s.BASE/'s15/baseline.schema.json');base.pop('$schema',None)
ref=obj({'id':text,'version':text})
value={'oneOf':[obj({'kind':{'const':'reference'},'id':text,'version':text}),obj({'kind':{'const':'epoch'},'value':{'type':'integer','minimum':0}}),obj({'kind':{'enum':['effect','scope','text']},'value':text})]}
atom=obj({'predicate':obj({'id':text,'version':text,'hash':sha}),'values':arr(value)})
witness={'oneOf':[obj({'kind':{'enum':['conformance','existential-conformance']},'assertion_id':text,'assessment_token':text}),obj({'kind':{'const':'node-kind'},'node_ref':ref})]}
request=obj({'schema':{'const':'relational.projection-request/v2'},'operation':{'const':'project'},'baseline':base,'profile_identity':sha,'catalog_identity':sha})
support=obj({'schema':{'const':'relational.source-support/v2'},'atom':atom,'source_identity':sha,'selected_graph_identity':sha,'profile_identity':sha,'catalog_identity':sha,'context_identity':sha,'witness':witness})
for name,content in [('request',request),('support',support)]:s.write(HERE/(name+'.schema.json'),{'$schema':'https://json-schema.org/draft/2020-12/schema',**content})
