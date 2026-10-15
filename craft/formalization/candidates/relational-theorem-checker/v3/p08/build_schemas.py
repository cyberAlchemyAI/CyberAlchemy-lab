"""Closed mediated-shadow metadata; IO probes are explicitly unqualified."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
def obj(p,required=None):return {'type':'object','properties':p,'required':list(p) if required is None else required,'additionalProperties':False}
def nullable(s):return {'oneOf':[s,{'type':'null'}]}
def arr(s):return {'type':'array','items':s}
text={'type':'string','minLength':1};sha={'type':'string','pattern':'^[0-9a-f]{64}$'}
nat={'type':'integer','minimum':0};token={'type':'string','pattern':'^[0-9a-f]{32}$'}
ref=obj({'path':{'type':'string','pattern':r'^(?!/)(?!.*(?:^|/)\.\.(?:/|$))[^\\]+$'},'sha256':sha})
none={'authority_effect':{'const':'none'},'application_authorized':{'const':False}}
mode={'enum':['fixture-shadow','io-probe-unqualified']}
baseline=json.loads((HERE.parent/'p01/contracts/request.schema.json').read_text())['properties']['proposal']['properties']['before']
policy=obj({'schema':{'const':'relational.shadow-policy/v3'},'writers':{'const':'exclusively-mediated-cooperating-writers'},'store_kind':mode,'scope':{'const':'bounded-local-candidate'},**none})
owner=obj({'schema':{'const':'relational.shadow-owner/v3'},'store_id':token,'root':text,'policy':policy,**none})
head=obj({'schema':{'const':'relational.shadow-head/v3'},'store_id':token,'store_kind':mode,'generation':nat,'baseline_identity':sha,'snapshot':ref,'registration':nullable(ref),'transaction_id':nullable(token),**none})
snapshot=obj({'schema':{'const':'relational.shadow-snapshot/v3'},'store_id':token,'transaction_id':nullable(token),'baseline_identity':sha,'baseline':baseline,**none})
review=obj({'schema':{'const':'relational.shadow-review/v3'},'store_id':token,'expected_head':head,'request_bytes_sha256':sha,'request_identity':sha,'proposal_identity':sha,'successor_identity':sha,'reviewer':{'enum':['author-integration-fixture','actual-user-review']},'assessment':{'enum':['reviewed-candidate','declined']},'context_identity':sha,'mappings_identity':sha,'mapped_contexts':arr(sha),**none})
registration=obj({'schema':{'const':'relational.shadow-registration/v3'},'store_id':token,'transaction_id':token,'baseline_identity':sha,'snapshot':ref,'proof_mode':{'enum':['fresh-independent-successor-registration','io-probe-unqualified']},'request':nullable(ref),'qualification':nullable(ref),'completion':nullable(ref),'owned_run':nullable(ref),'required_inventory':arr(text),'fresh_at_creation':{'type':'boolean'},**none})
registration['allOf']=[{'if':{'properties':{'proof_mode':{'const':'fresh-independent-successor-registration'}}},'then':{'properties':{'request':ref,'qualification':ref,'completion':ref,'owned_run':ref,'fresh_at_creation':{'const':True}}},'else':{'properties':{'request':{'type':'null'},'qualification':{'type':'null'},'completion':{'type':'null'},'owned_run':{'type':'null'},'fresh_at_creation':{'const':False},'required_inventory':{'const':[]}}}}]
transaction=obj({'schema':{'const':'relational.shadow-transaction/v3'},'store_id':token,'transaction_id':token,'store_kind':mode,'phase':{'enum':['prepared','committed','aborted','reconciliation-required']},'progress':{'enum':['journal','snapshot','registration','metadata-head','complete']},'before_head':head,'after_head':head,'review':nullable(ref),'proposal_qualification':nullable(ref),'mapped_checks':arr(ref),'registration':ref,'snapshot':ref,'fresh_run_id':text,'reason':{'type':'string'},**none})
statuses=['initialized-candidate-shadow','prepared-candidate-shadow','applied-candidate-shadow','stale-head','invalid','unsupported','unsupported-policy','unknown-resource','cancelled','reconciliation-required']
application=obj({'schema':{'const':'relational.shadow-application/v3'},'status':{'enum':statuses},'reason':{'type':'string'},
                 'store':text,'head':nullable(head),'before':nullable(head),'after':nullable(head),'transaction':nullable(transaction),
                 'qualification':ref,'handle':token,'expected_head':head,'proposal_qualification':ref,'successor_registration':ref,
                 'mapped_checks':arr(ref),'contexts':obj({'horn':sha,'mapped':arr(sha)}),'seconds':{'type':'number','minimum':0},**none},
                ['schema','status','reason','authority_effect','application_authorized'])
application['allOf']=[{'if':{'properties':{'status':{'const':status}}},'then':{'required':fields}} for status,fields in [
    ('initialized-candidate-shadow',['store','head','qualification','seconds']),
    ('prepared-candidate-shadow',['handle','expected_head','proposal_qualification','successor_registration','mapped_checks','contexts','seconds']),
    ('applied-candidate-shadow',['before','after','transaction','seconds'])]]
recovery=obj({'schema':{'const':'relational.shadow-recovery/v3'},'status':{'enum':['head-current','reconciliation-required']},
              'head':head,'events':arr(obj({'kind':text,'detail':text})),'reason':text,'proof_scope':mode,'fresh_qualification':{'const':False},**none},
             ['schema','status','proof_scope','fresh_qualification','authority_effect','application_authorized'])
recovery['allOf']=[{'if':{'properties':{'status':{'const':'head-current'}}},'then':{'required':['head','events']},'else':{'required':['reason']}}]
for name,schema in [('policy',policy),('owner',owner),('head',head),('snapshot',snapshot),('review',review),('registration',registration),('transaction',transaction),('application',application),('recovery',recovery)]:
    (HERE/(name+'.schema.json')).write_text(json.dumps({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:relational:v3:shadow-'+name,**schema},indent=2)+'\n')
