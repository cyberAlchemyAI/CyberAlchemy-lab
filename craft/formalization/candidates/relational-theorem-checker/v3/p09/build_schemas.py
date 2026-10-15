"""Closed public transport and stronger success-state metadata contracts."""
from pathlib import Path
import copy
import json
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
def obj(p,required=None):return {'type':'object','properties':p,'required':list(p) if required is None else required,'additionalProperties':False}
legacy=json.loads((BASE/'p07/result.schema.json').read_text())
legacy.pop('$id',None);legacy.pop('$schema',None)
status={'enum':['qualified-candidate','invalid','unsupported','unknown-resource','cancelled','unsupported-policy']}
public=obj({'schema':{'const':'relational.public-qualification/v3'},'status':status,'qualification':legacy,
            'diagnostic':obj({'cause':{'enum':['original','atomic-tool-deadline']},'original_status':status,'reason':{'type':'string'}}),
            'authority_effect':{'const':'none'},'application_authorized':{'const':False}})
public['allOf']=[{'if':{'properties':{'diagnostic':{'properties':{'cause':{'const':'original'}}},'status':{'const':s}}},
                 'then':{'properties':{'qualification':{'properties':{'status':{'const':s}}},'diagnostic':{'properties':{'original_status':{'const':s}}}}}}
                for s in status['enum']]
public['allOf'].append({'if':{'properties':{'diagnostic':{'properties':{'cause':{'const':'atomic-tool-deadline'}}}}},
                       'then':{'properties':{'status':{'const':'unknown-resource'},'qualification':{'properties':{'status':{'const':'invalid'},'reason':{'const':'Atomic tool deadline exceeded.'}}},'diagnostic':{'properties':{'original_status':{'const':'invalid'}}}}}})
application=json.loads((BASE/'p08/application.schema.json').read_text());application.pop('$id',None)
head=json.loads((BASE/'p08/head.schema.json').read_text());tx=json.loads((BASE/'p08/transaction.schema.json').read_text())
for clause in application['allOf']:
    name=clause['if']['properties']['status']['const']
    if name=='applied-candidate-shadow':clause['then']['properties']={'before':head,'after':head,'transaction':tx}
    if name=='initialized-candidate-shadow':clause['then']['properties']={'head':head}
for name,schema in [('public-qualification',public),('application',application)]:
    (HERE/(name+'.schema.json')).write_text(json.dumps({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:relational:v3:public-'+name,**schema},indent=2)+'\n')
