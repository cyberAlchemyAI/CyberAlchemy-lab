"""Six real original-stage outputs under their unchanged candidate Work meaning."""
import copy
import json
from pathlib import Path
import sys
import profiles as P
import design_stage
T31=P.ROOT/'implementation/lab-runtime/local-host/t31-durable-output-0001'
sys.path.insert(0,str(T31))
import observed_consumer as R
import output_store as S

def header(raw,carrier,scope):
    body=json.loads(raw);identity=body['node_id']
    return {'scope_ref':scope,'identity_ref':identity,'version_ref':identity+'@'+body.get('version','candidate.1'),'carrier_ref':carrier,'byte_sha256':P.sha(raw)}
def construct(profile):
    kind=profile['kind'];base=P.RETAINED/kind;scope=profile['scope_ref'];transitions={};raws={};origins={}
    design_header,design_raw,design_receipt=design_stage.emit(profile)
    route='transition:'+kind+':designed';transitions[route]=[design_header];raws[design_header['version_ref']]=design_raw
    origins[route]={'origin':'fresh-actual-original-design-method','receipt':design_receipt}
    result=json.loads(profile['original_result_raw']);middle=next(r for r in result['new_output_transitions'] if r['transition_ref'].split(':')[1]==kind)
    middle_headers=copy.deepcopy(middle['output_artifact_refs'])
    for h,name in zip(middle_headers,middle['output_original_paths'],strict=True):
        raw=(P.RETAINED/name).read_bytes();P.need(P.sha(raw)==h['byte_sha256'],'actual retained middle output differs');raws[h['version_ref']]=raw
    transitions[middle['transition_ref']]=middle_headers
    # Independently pinned assessments/evidence, actual input/output crosslinks,
    # finite entropy and engineering limitation checked by the existing reader.
    observed=R.consume_observed(kind,[(h,raws[h['version_ref']]) for h in middle_headers],P.RETAINED)
    origins[middle['transition_ref']]={'origin':'actual-retained-original-producer','original_receipt_sha256':P.RESULT_SHA,'original_design_run_sha256':P.SPECS[kind]['run_sha256'],
      'producer_source_cut':profile['original_producer_source_cut'],'later_computation':observed,'producer_rerun':False}
    paths=['engineering/workflow/work-outcome-assessment.json'] if kind=='engineering' else ['research/finding.json','research/evaluation.json']
    carriers=['cal.artifact-type.work-outcome-assessment/v1'] if kind=='engineering' else ['cal.artifact-type.finding/v1','cal.artifact-type.evaluation/v1']
    terminal=[];selected={r['path']:r['sha256'] for r in middle['later_consumers']}
    for name,carrier in zip(paths,carriers,strict=True):
        raw=(P.RETAINED/name).read_bytes();P.need(P.sha(raw)==selected[name],'retained actual terminal consumer/output differs')
        h=header(raw,carrier,scope);terminal.append(h);raws[h['version_ref']]=raw
    route='transition:'+kind+(':assessed' if kind=='engineering' else ':evaluated');transitions[route]=terminal
    origins[route]={'origin':'actual-retained-original-assessment-producer','original_receipt_sha256':P.RESULT_SHA,
      'original_design_run_sha256':P.SPECS[kind]['run_sha256'],'producer_source_cut':profile['original_producer_source_cut'],
      'retained_observed_disposition':'unsupported' if kind=='engineering' else 'inconclusive','producer_rerun':False}
    carriers=S.original_carriers()
    for route,headers in transitions.items():
        for h in headers:carriers.output(h,raws[h['version_ref']],scope_ref=scope,transition_ref=route)
    receipt={'schema_version':'lab-original-candidate-Work-output-profile/v1','kind':kind,'original_work':profile['original_work'],
      'original_inputs_manifest_sha256':P.SPECS[kind]['sha256'],'original_producer_source_cut':profile['original_producer_source_cut'],
      'original_design_run_schema':profile['original_run']['schema_version'],'original_design_run_sha256':P.SPECS[kind]['run_sha256'],
      'coordination_does_not_promote_original_Work_to_signed_Source_current':True,'transitions':transitions,'origins':origins,
      'original_output_bytes_unchanged':True,'retained_implementation_or_experiment_rerun':False,'actual_owner_outcome':None,'authority_effect':'none'}
    return transitions,raws,receipt
