"""Document the local R03 transport; runtime policy still derives exact scope."""
import bundle_contract as b


def obj(properties):
 return {'type':'object','additionalProperties':False,'properties':properties,'required':list(properties)}


def schemas():
 text={'type':'string','minLength':1};sha={'type':'string','pattern':'^[a-f0-9]{64}$'}
 binding=obj({'path':text,'sha256':sha})
 artifact_map={'type':'object','additionalProperties':False,'properties':{role:binding for role in b.ROLE_SCHEMA}}
 entry=obj({'id':text,'name':text,'hard':{'const':True},'scope':{'enum':['L2','L3']},
  'method':{'enum':['builtin','proof-submission','checked-model-witness','bounded-search']},'artifacts':artifact_map})
 entry['allOf']=[]
 for method,role in [('builtin',None),('proof-submission','proof-submission'),('checked-model-witness','model-witness'),('bounded-search','search-result')]:
  fields={} if role is None else {role:binding}
  entry['allOf'].append({'if':{'properties':{'method':{'const':method}}},'then':{'properties':{'artifacts':obj(fields)}}})
 dependencies=obj({'schema':{'const':'relational.bundle-dependencies/v1-candidate'},'proposal_identity':sha,
  'baseline_identity':sha,'proof_dependencies':{'type':'object'},'bundle_policy_identity':sha,
  'bindings':{'type':'array','items':binding,'minItems':1,'uniqueItems':True},'authority_effect':{'const':'none'},'dependency_identity':sha})
 bundle=obj({'schema':{'const':b.SCHEMA},'proposal_identity':sha,'baseline_identity':sha,'policy_identity':sha,
  'dependencies':dependencies,'obligations':{'type':'array','items':entry,'minItems':1}})
 bundle['description']='Transport shape only. Runtime recomputes full dependencies, exact required IDs/scopes/methods and truth. A valid JSON document does not establish readiness.'
 model=obj({'schema':{'const':b.ROLE_SCHEMA['model-witness']},'proposal_identity':sha,'witness':binding})
 model['description']='Local successor binding raw registry-model or inference-model bytes. The actual claim and context are checked independently; this wrapper is not a theorem.'
 search={'type':'object','properties':{'schema':{'const':b.ROLE_SCHEMA['search-result']},'proposal_identity':sha},
  'required':['schema','proposal_identity'],'additionalProperties':True,
  'description':'Untrusted bounded provider output. Additional provider flags are preserved as data and cannot discharge any hard obligation without a checked witness.'}
 result={'evidence-bundle-schema.json':bundle,'scoped-model-schema.json':model,'bounded-search-schema.json':search}
 for name,schema in result.items():
  schema['$schema']='https://json-schema.org/draft/2020-12/schema'
  schema['$id']='https://cyberalchemy.local/schemas/relational-checker/'+name
 return result


def main():
 import jsonschema
 for name,schema in schemas().items():
  jsonschema.Draft202012Validator.check_schema(schema);b.s.write(b.HERE/name,schema)
 for name in ['unchanged','instance-only','fresh-kind-extension','fresh-kind-empty-pairs','rule-only-extension']:
  jsonschema.validate(b.s.read(b.HERE/(name+'-bundle.json')),schemas()['evidence-bundle-schema.json'])
 print('R03 schema contracts validated against five complete cases across four computed profiles')


if __name__=='__main__':main()
