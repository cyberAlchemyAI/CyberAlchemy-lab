"""First emit a private framing declaration over unchanged original Work."""
import tempfile
import json
from pathlib import Path
import profiles as P
import bundle as B

def construct(profile,capsule,coordination_originals):
    P.guard(profile);P.need(profile['kind']=='engineering','exact original engineering frame required')
    with tempfile.TemporaryDirectory(prefix='cal-original-Work-prepare-') as folder:
        cls=profile['module'].EngineeringWorkflow
        workflow=cls(profile['inputs'],P.SPECS['engineering']['sha256'],Path(folder)/'prepared')
        P.need(type(workflow) is cls and workflow.state=='prepared' and workflow.events==[],
               'actual original input resolver did not prepare this Work')
    m=profile['manifest'];resolution=capsule['records']['intent-resolution'];ir=capsule['artifacts']['intent-resolution'];work=profile['original_work']
    P.need(json.loads(coordination_originals[ir['version_ref']])==resolution,'captured framing original differs from declaration')
    P.need(capsule['original_work']==work and resolution['payload']['intent_ref']==profile['headers'][m['intent_ref']]['version_ref']
           and work['version_ref'] in resolution['payload']['selected_subject_refs']
           and work['version_ref'] not in resolution['payload']['excluded_subject_refs'],
           'new framing declaration does not select exact unchanged original Work')
    transitions={'transition:intent-framing:resolved':[ir],'transition:intent-framing:prepared':[work]}
    raws={ir['version_ref']:coordination_originals[ir['version_ref']],work['version_ref']:profile['raws'][work['version_ref']]}
    for transition,headers in transitions.items():
        for header in headers:B.S.original_carriers().output(header,raws[header['version_ref']],scope_ref=profile['scope_ref'],transition_ref=transition)
    receipt={'schema_version':'lab-private-original-Work-framing-first-emission/v1','original_work':work,
      'original_input_manifest_sha256':P.SPECS['engineering']['sha256'],'original_input_resolver_code_sha256':P.SPECS['engineering']['code_sha256'],
      'actual_original_constructor':'EngineeringWorkflow.__init__','actual_original_resolver_prepared':True,
      'original_producer_source_cut':profile['original_producer_source_cut'],'current_coordinating_source_cut':capsule['current_coordinating_source_cut'],
      'new_private_IntentResolution':ir,'selected_current_project':capsule['current_project'],'transitions':transitions,
      'original_Work_body_unchanged':True,'original_Work_promoted_to_Source_current':False,
      'human_Intent_resolution_or_actual_owner_outcome':None,'canonical_admissions':0,'authority_effect':'none',
      'claim_ceiling':'Actual original resolver validates unchanged candidate engineering Work; a new bounded private framing declaration selects it. No original human framing, old governance capability, Source-current Work admission or implementation execution.'}
    P.guard(profile);return transitions,raws,receipt
