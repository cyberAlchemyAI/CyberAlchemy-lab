"""Exact endpoint correction postimages for final review; never apply a transaction."""
import copy
import artifact_model as model
from protocol import *

GAPS={'path':'product/lab/release-candidates/v1/interface/api-v2/receipts/connection-gaps.json',
    'sha256':'af6bfb52b98f5458742defb1c3aa9b8c0644920dafd16e0f777ec8b41b56c6e1'}
SELECTED={
    'policy:cyberalchemy-lab-operational-foundation':'foundation.1',
    'intent:establish-cyberalchemy-lab-operational-foundation':'foundation.1',
    'project:cyberalchemy-v2-to-lab-migration':'foundation.1',
    'product-capability:cyberalchemy-lab:governed-knowledge-lifecycle':'foundation.1',
    'context:cyberalchemy-v2-to-lab-migration':'foundation.1',
    'project-state:cyberalchemy-v2-to-lab-migration:decision-0071':'bootstrap.1'}


def write(path,value):
    with path.open('xb') as stream:stream.write(source.encoded(value))


def run():
    root=HERE/'connection-corrections';source.require(not root.exists(),'immutable correction candidates already materialized')
    root.mkdir();gaps=source.parse(source.original(GAPS));schemas=Schemas();rows=[]
    with source.replay_source('engineering') as view:
        for gap in gaps['connection_gaps']:
            old=view.subjects[gap['version_ref']];original=source.parse(source.original(gap['source_binding']))
            source.require(old['record']==original and old['source']==gap['source_binding'],'original relation differs')
            record=copy.deepcopy(original);changes=[];witnesses=[]
            for end in ('source','target'):
                endpoint=record['payload'][end];previous=endpoint['version_ref']
                if previous not in view.subjects:
                    source.require(previous==endpoint['ref']+'@candidate.1' and endpoint['ref'] in SELECTED,'unselected endpoint correction')
                    endpoint['version_ref']=endpoint['ref']+'@'+SELECTED[endpoint['ref']]
                    changes.append({'selector':'/payload/'+end+'/version_ref','before':previous,'after':endpoint['version_ref']})
                subject=view.subjects[endpoint['version_ref']]
                source.require(subject['identity']==endpoint['ref'] and subject['kind']==endpoint['kind'],'exact endpoint identity/kind differs')
                report=view.source_record(subject);source.require(report['original_file_is_current'],'endpoint witness unavailable')
                overlays=[]
                for path,document in view.data['baseline']['documents'].items():
                    if not path.endswith('artifact-instance-admission.json'):continue
                    for index,entry in enumerate(document.get('entries',[])):
                        if entry.get('version_ref')==subject['version_ref'] and entry.get('admitted_instance_path')==subject['source']['path']:
                            overlays.append({'binding':{'path':path,'sha256':view.data['baseline']['materials'][path]},
                                'selector':'/entries/'+str(index),'entry':entry,'decision_id':document['decision_id']})
                source.require(len(overlays)==1,'independent exact endpoint admission overlay missing or ambiguous')
                witnesses.append({'endpoint':end,'artifact':model.artifact_ref(view,subject),'semantic_kind':endpoint['kind'],
                    'effective_state':subject['effective_state'],'source_binding':subject['source'],'admission_overlay':overlays[0]})
            source.require(changes,'correction has no exact changes')
            contract=view.data['projection']['contracts'][old['carrier_ref']]
            uri=contract.get('schema_uri')
            view.handle.operations.validate_schema(record,contract['schema_path'],contract.get('schema_selector'),view.data['projection']['documents'])
            view.handle.operations.validate_relation(record,view.data['projection'],allow_historical=True)
            # Reconstituting a past connection is deliberately not a current-write alias.
            try:view.handle.operations.validate_relation(record,view.data['projection']);current_write={'result':'PASS'}
            except Exception as error:current_write={'result':'FAIL','error_class':type(error).__name__,'reason':str(error)}
            directory=root/Path(gap['source_binding']['path']).stem;directory.mkdir()
            write(directory/'record.json',record)
            signature,signature_binding=model.signature(view,record['payload']['relation_kind_ref'])
            member={'schema_version':'lab-historical-connection-correction/v1-candidate','member_ref':'candidate:R03-reference-closure:'+Path(directory).name,
                'identity_ref':old['identity'],'version_ref':old['identity']+'@R03-reference-closure.1','proposed_operation':'revise',
                'predecessor_version_ref':old['version_ref'],'record_binding':source.bind(directory/'record.json'),
                'original_source_binding':old['source'],'changes':changes,'endpoint_witnesses':witnesses,
                'signature_binding':signature_binding,'schema_binding':{'path':contract['schema_path'],'sha256':contract['schema_sha256']},
                'historical_endpoint_validation':{'result':'PASS','allow_historical':True},'current_endpoint_validation':current_write,
                'admission_posture':'candidate','intended_scope_ref':record['scope_ref'],'actual_owner_outcome':None,
                'decision_ref':None,'authority_effect':'none','canonical_effects_applied':0,'local_transactions_applied':0,
                'application_requirements':['Independently scoped owner outcome for this exact postimage and predecessor.',
                    'Declared historical reference correction write profile and exact scope authorization; unchanged current-write guard is not bypassed.',
                    'Signed application, replay and recovery evidence before claiming repair applied.'],
                'claim_ceiling':'Exact source endpoint version corrections only; original kind, identity, qualifiers, domain scope and payload fields preserved. Historical validation is not transaction admission.'}
            write(directory/'review-member.json',member);rows.append(source.bind(directory/'review-member.json'))
    write(root/'manifest.json',{'schema_version':'lab-connection-correction-set/v1-candidate','result':'PASS',
        'original_gap_binding':GAPS,'members':rows,'candidate_members':10,'authority_effect':'none','actual_owner_outcome':None,
        'canonical_effects_applied':0,'local_transactions_applied':0})
    print(json.dumps({'result':'PASS','candidate_members':len(rows),'manifest':source.bind(root/'manifest.json'),'authority_effect':'none'},sort_keys=True))


if __name__=='__main__':run()
