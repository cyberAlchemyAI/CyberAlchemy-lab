"""Build closed local protocol schemas from the exact preparation shape."""
from package import *

def union(schemas):
 unique={json.dumps(s,sort_keys=True):s for s in schemas}
 values=list(unique.values());return values[0] if len(values)==1 else {'anyOf':values}

def shape(value):
 if value is None:return {'type':'null'}
 if type(value) is bool:return {'const':value}
 if type(value) is str:return {'type':'string'}
 if type(value) is int:return {'type':'integer','minimum':0}
 if type(value) is list:return {'type':'array','items':union([shape(v) for v in value]) if value else False}
 if type(value) is dict:
  if set(value)=={'path','sha256'}:return {'$ref':'#/$defs/binding'}
  return {'type':'object','additionalProperties':False,'required':sorted(value),'properties':{k:shape(v) for k,v in value.items()}}
 raise ValueError('unsupported protocol shape')

def definitions():
 return {'binding':{'type':'object','additionalProperties':False,'required':['path','sha256'],'properties':{
  'path':{'type':'string','pattern':r'^(?!/)(?!.*(?:^|/)\.\.?(?:/|$))(?!.*\\)[^\s]+$'},
  'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}}}}

def build_schema(value):
 s=shape(value);s['$schema']='https://json-schema.org/draft/2020-12/schema';s['$defs']=definitions()
 for field in ['schema_version','task','status','final_checkpoint','application_task','admitted_coherence_task','candidate_coherence_task','authority_effect','admission_posture']:
  if field in value:s['properties'][field]={'const':value[field]}
 if 'members' in value:
  kinds={}
  for m in value['members']:kinds.setdefault(m['member_class'],[]).append(m)
  variants=[]
  for kind,items in kinds.items():
   variant=shape(items[0]);variant['properties']['scope']=union([shape(m['scope']) for m in items]);variant['properties']['member_class']={'const':kind}
   variant['properties']['requested_axes']=union([shape(m['requested_axes']) for m in items])
   variant['properties']['authority_effect']={'const':'none'};variant['properties']['admission_posture']={'const':'candidate-unadmitted'}
   variant['properties']['member_ref']={'type':'string','pattern':'^protocol:O06:'}
   for field in ['targets','evidence']:variant['properties'][field]={'type':'array','minItems':1,'uniqueItems':True,'items':{'$ref':'#/$defs/binding'}}
   variant['properties']['dependencies']={'type':'array','uniqueItems':True,'items':{'type':'string','pattern':'^protocol:O06:'}}
   variant['properties']['postimage_binding']={'anyOf':[{'type':'null'},{'$ref':'#/$defs/binding'}]}
   variants.append(variant)
  s['properties']['members']={'type':'array','minItems':len(value['members']),'maxItems':len(value['members']),'items':{'type':'object','required':['member_class'],'properties':{'member_class':{'enum':list(kinds)}},'allOf':[{'if':{'properties':{'member_class':{'const':variant['properties']['member_class']['const']}},'required':['member_class']},'then':variant} for variant in variants]}}
  s['properties']['counts']={'const':value['counts']}
 return s

def main():
 require(not (HERE/'manifest.json').exists(),'frozen schema source cannot change')
 def save(p,v):p.write_bytes(encoded(v))
 v,files=expected(HERE/'packages/0001')
 save(HERE/'preparation.schema.json',build_schema(v))
 exemplars={}
 for p,raw in files.items():
  if p.parent.name=='adoption':exemplars.setdefault('adoption-intent',parse(raw))
  elif p.parent.name=='proposals':exemplars[p.stem]=parse(raw)
 for name,value in exemplars.items():
  target=HERE/'schemas'/f'{name}.schema.json';target.parent.mkdir(exist_ok=True)
  save(target,build_schema(value))
 print(json.dumps({'result':'PASS','protocol_schemas':len(exemplars)+1,'members':len(v['members']),'authority_effect':'none'}))

if __name__=='__main__':main()
