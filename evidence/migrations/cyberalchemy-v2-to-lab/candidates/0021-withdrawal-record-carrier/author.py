import copy
from support import ROOT, LAB, PREVIOUS, L1, PACKAGE, load, dump, sha, binding, module
TEXT={'type':'string','pattern':r'\S'}
def obj(p): return {'type':'object','additionalProperties':False,'required':sorted(p),'properties':p}
def array(item,minimum=1): return {'type':'array','minItems':minimum,'maxItems':100,'items':item}
def build():
    ref=obj({'path':TEXT,'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}})
    contract=obj({'schema_version':{'const':'cal-withdrawal-record/v1'},'artifact_type_ref':{'const':'cal.artifact-type.withdrawal-record/v1'},'record_id':TEXT,'status':{'const':'candidate-unadmitted'},'authority_effect':{'const':'none'},'owner_route':TEXT,'scope_ref':TEXT,'profile':{'const':'candidate:normalized-withdrawal-reservation/v1'},'normalization':ref,'reservations':array(obj({'retired_id':TEXT,'successor_id':TEXT,'permanently_reserved':{'const':True}})),'reason':TEXT,'challenge_route':TEXT,'source_direction':obj({'canonical':{'const':'withdrawal-record.json'},'human_projection':{'const':'WITHDRAWAL-RECORD.md'},'projection_policy':{'const':'generated-only'}}),'claim_ceiling':TEXT})
    contract['$schema']='https://json-schema.org/draft/2020-12/schema'
    allocation=obj({'withdrawal_record':ref,'scope_ref':TEXT,'proposed_ids':{'type':'array','maxItems':10000,'uniqueItems':True,'items':TEXT}})
    dump(PACKAGE/'schema.json',contract); dump(PACKAGE/'allocation.schema.json',allocation)
    dump(ROOT/'contracts.json',{'authority_effect':'none','schemas':[binding(PACKAGE/x) for x in ['schema.json','allocation.schema.json']]})
    normalization=LAB/'docs/normalizations/0001-definition-migration-model/normalization.json'
    example={'schema_version':'cal-withdrawal-record/v1','artifact_type_ref':'cal.artifact-type.withdrawal-record/v1','record_id':'WITHDRAWAL-PRESERVATION-D70-D81-001','status':'candidate-unadmitted','authority_effect':'none','owner_route':'route:migration-owner','scope_ref':'scope:normalized-legacy-identifier-reservation','profile':'candidate:normalized-withdrawal-reservation/v1','normalization':binding(normalization),'reservations':[{'retired_id':x['legacy_id'],'successor_id':x['successor_id'],'permanently_reserved':True} for x in load(normalization)['withdrawn_ids']],'reason':'Preserve every identifier already listed as withdrawn in the accepted normalization; never recycle its legacy name.','challenge_route':'route:withdrawal-lineage-review','source_direction':{'canonical':'withdrawal-record.json','human_projection':'WITHDRAWAL-RECORD.md','projection_policy':'generated-only'},'claim_ceiling':'Exact recorded reservations and allocation collision checks only; no new withdrawal, successor authority or global allocation permission.'}
    artifact=load(PREVIOUS/'artifact-types/lineage-map/v1/artifact.json')
    artifact.update(artifact_type_id='cal.artifact-type.withdrawal-record',artifact_type_ref='cal.artifact-type.withdrawal-record/v1',name='Withdrawal Record',schema_ref='cal.schema.withdrawal-record-carrier/v1',schema_digest=sha(PACKAGE/'schema.json'),semantic_definition_refs=[],semantic_definition_bindings=[],distinct_validation_purpose='Permanently reserves a retired identifier and names its successor authority.')
    artifact['classification'].update(semantic_kind='withdrawal-record',lifecycle_posture_ref='candidate:withdrawal-record-reconstruction/v1')
    artifact['instance_contract'].update(canonical_filename='withdrawal-record.json',human_filename='WITHDRAWAL-RECORD.md',identity_field='record_id',required_semantic_fields=sorted(set(contract['required'])-{'schema_version','status','authority_effect','source_direction','claim_ceiling'}))
    artifact['orthogonality_rules']=[{'rule_id':'WITHDRAWAL-01','statement':'Retired identifiers remain permanently reserved and cannot be silently recycled.'},{'rule_id':'WITHDRAWAL-02','statement':'A named successor does not inherit authority from the withdrawal record.'}]
    artifact['four_facets']={'classification':'Normalization-supported Withdrawal Record; no standalone Definition binding is asserted.','schema':'Exact accepted normalization, complete retired-identifier reservations and named successors.','machine_checkable':'Complete reservation set, successor agreement, permanent reservation and allocation collision checks.','human_continuation':'Generated WITHDRAWAL-RECORD.md preserves the existing twelve withdrawals and limits.'}
    artifact['typed_residue']=[{'residue_id':'WITHDRAWAL-R1','owner_ref':'role:migration-owner','missing':'Standalone Withdrawal Record Definition, verified successor authority, global allocation registry and enforcement.','consequence':'This candidate is supported by normalization only and checks the recorded reservation list locally.'}]; artifact['claim_ceiling']=example['claim_ceiling']
    invalid={}
    for name,key,val in [('authority','authority_effect','retire'),('empty-reservations','reservations',[]),('blank-owner','owner_route',' '),('extra-field','successor_admitted',True),('unknown-profile','profile','recycle'),('missing-route','challenge_route',' '),('blank-reason','reason',' ')]:
        bad=copy.deepcopy(example); bad[key]=val; invalid[name]=bad
    bad=copy.deepcopy(example); bad['reservations'][0]['permanently_reserved']=False; invalid['reusable-id']=bad
    artifact['validation_contract'].update(positive_witness='fixtures/valid/withdrawal-record.json',positive_projection='fixtures/valid/WITHDRAWAL-RECORD.md',negative_witnesses=['fixtures/invalid/'+x+'.json' for x in sorted(invalid)],validator_path=str((ROOT/'validate.py').relative_to(LAB)))
    dump(PACKAGE/'artifact.json',artifact); dump(PACKAGE/'fixtures/valid/withdrawal-record.json',example)
    for name,bad in invalid.items(): dump(PACKAGE/f'fixtures/invalid/{name}.json',bad)
    renderer=module(LAB/'tooling/generators/artifact_surface.py','policy_renderer'); artifact=load(PACKAGE/'artifact.json')
    (PACKAGE/'ARTIFACT.md').write_text(renderer.render_artifact(artifact)); (PACKAGE/'fixtures/valid/WITHDRAWAL-RECORD.md').write_text(renderer.render_instance(artifact,load(PACKAGE/'fixtures/valid/withdrawal-record.json')))
    dump(ROOT/'registry.json',{'authority_effect':'none','entries':[{'target_id':'type.withdrawal-record','family':'artifact-type','status':'candidate-unadmitted',**binding(PACKAGE/'artifact.json')}]})
    allocation={'withdrawal_record':binding(PACKAGE/'fixtures/valid/withdrawal-record.json'),'scope_ref':example['scope_ref'],'proposed_ids':['EXAMPLE-NEW-ID']}
    dump(ROOT/'examples/clear.json',allocation)
    collision=copy.deepcopy(allocation); collision['proposed_ids']=['CAV2-D70','CAV2-D81']; dump(ROOT/'examples/collision.json',collision)
    scaffold=ROOT.parent/'0003-review-led-reconstruction/target-candidates/artifact-type/type-withdrawal-record/v1/artifact.json'
    dump(ROOT/'dependencies.json',{'authority_effect':'none','seed_targets':[],'inputs':[binding(PREVIOUS/'manifest.json'),binding(L1/'batches.json'),binding(scaffold),binding(normalization)],'definitions':[],'selected_source_sections':[],'normalization_target':load(scaffold)['normalized_contract'],'source_lineage_residue':[]})
if __name__=='__main__': build()
