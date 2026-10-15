"""Compile a closed local evidence contract without changing the A01 schema."""
import copy
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[7]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1'


def build():
    raw=(IMPL/'schemas/input-envelope.json').read_bytes();base=json.loads(raw);defs=copy.deepcopy(base['$defs'])
    ref=lambda name:{'$ref':'#/$defs/'+name}
    obj=lambda fields:{'type':'object','properties':fields,'required':list(fields),'additionalProperties':False}
    arr=lambda items,minimum=0:{'type':'array','items':items,'minItems':minimum,'uniqueItems':True}
    nullable=lambda value:{'anyOf':[value,{'type':'null'}]}
    enum=lambda values:{'type':'string','enum':values}
    text={'type':'string','minLength':1};sha=copy.deepcopy(defs['binding']['properties']['sha256']);identifier=copy.deepcopy(defs['obligation']['properties']['obligation_id'])
    native={'type':'object','minProperties':1}
    defs['evidence-gate']=obj({'gate_id':identifier,'check':text,'subject':{'type':'object'},'minimum_strength':defs['obligation']['properties']['minimum_strength'],'prerequisites':arr(identifier),'status':{'const':'required'}})
    defs['evidence-query-requirement']=obj({'obligation_id':identifier,'query_type':text,'statement_sha256':sha,'prerequisites':arr(identifier),'scope':text})
    defs['evidence-required-set']=obj({'schema_version':{'const':'definition-assurance-required-set/v1-candidate'},'authority_effect':{'const':'none'},'logical_manifest':ref('obligation-manifest'),'administrative_and_semantic_gates':arr(ref('evidence-gate')),'query_requirements':arr(ref('evidence-query-requirement')),'signature_sha256':sha,'change_class':enum(['initial','additive','meaning-change','constraint-change']),'candidate_policy_review_sha256':sha,'required_set_sha256':sha,'prerequisite_use':text,'claim_ceiling':text})
    defs['evidence-interpretation']=obj({'source':ref('source-ref'),'scope':text,'status':enum(['present','missing','unsupported','unresolved']),'correspondence_ref':nullable(ref('binding')),'typed_ir_ref':nullable(ref('binding'))})
    defs['evidence-interpretation']['allOf']=[{'if':{'properties':{'status':{'const':'present'}}},'then':{'properties':{'correspondence_ref':ref('binding'),'typed_ir_ref':ref('binding')}}},{'if':{'properties':{'status':{'const':'missing'}}},'then':{'properties':{'correspondence_ref':{'type':'null'},'typed_ir_ref':{'type':'null'}}}}]
    defs['evidence-native-result']=obj({'binding':ref('binding'),'data':native})
    defs['evidence-logical-record']=obj({'obligation':ref('obligation'),'result':ref('result'),'provider_kind':enum(['finite-static','smt-static','proof-kernel','structural-check','source-review','unresolved']),'native_input_ref':nullable(ref('binding')),'native_result':nullable(ref('evidence-native-result')),'profile_ref':nullable(ref('binding')),'toolchain_ref':nullable(ref('binding'))})
    defs['evidence-logical-record']['allOf']=[{'if':{'properties':{'result':{'properties':{'verdict':{'enum':['supported','counterexample','inconsistent','vacuous']}}}}},'then':{'properties':{'native_input_ref':ref('binding'),'native_result':ref('evidence-native-result'),'profile_ref':ref('binding'),'toolchain_ref':ref('binding'),'result':{'properties':{'execution':{'const':'completed'},'strength':{'not':{'const':'none'}},'evidence_refs':{'minItems':1}}}}}}]
    defs['evidence-gate-record']=obj({'gate':ref('evidence-gate'),'execution':enum(['completed','not-run','timeout','cancelled','error']),'currentness':enum(['current','stale','unknown']),'reported_status':enum(['reported-supported','pending','rejected','unsupported','missing','unknown','stale']),'evidence_refs':arr(ref('binding')),'native_result':nullable(ref('evidence-native-result')),'readiness':{'const':'not-assessed'}})
    defs['evidence-gate-record']['allOf']=[{'if':{'properties':{'reported_status':{'const':'reported-supported'}}},'then':{'properties':{'execution':{'const':'completed'},'currentness':{'const':'current'},'evidence_refs':{'minItems':1},'native_result':ref('evidence-native-result')}}}]
    fields={'schema_version':{'const':'definition-assurance-evidence-bundle/v1-candidate'},'authority_effect':{'const':'none'},'upstream_schema_sha256':{'const':hashlib.sha256(raw).hexdigest()},'snapshot_ref':ref('binding'),'sources':arr(ref('source-ref'),1),'interpretations':arr(ref('evidence-interpretation'),1),'dependency_graph_ref':ref('binding'),'theory_ref':ref('binding'),'assumption_set_ref':ref('binding'),'coupling_refs':arr(ref('binding')),'required_set_ref':ref('binding'),'required_set':ref('evidence-required-set'),'logical_results':arr(ref('evidence-logical-record')),'gate_results':arr(ref('evidence-gate-record')),'readiness':{'const':'not-assessed'},'semantic_ready':{'const':False},'verification':{'const':'pending-independent-verification'},'claim_ceiling':text}
    return {'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:cyberalchemy-lab:definition-assurance:evidence:v1-candidate',**obj(fields),'$defs':defs,'description':'Closed submitted candidate evidence. Exact required-set/row comparison and native byte binding are separate from source-fidelity, provider semantics and independent readiness verification.'}


if __name__=='__main__':
    value=build();path=IMPL/'schemas/evidence.json'
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'schema':str(path.relative_to(ROOT)),'local_definitions':len(value['$defs']),'authority_effect':'none'}))
