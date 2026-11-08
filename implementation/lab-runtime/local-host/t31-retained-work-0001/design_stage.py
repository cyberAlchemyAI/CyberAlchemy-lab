"""First-emit typed design outputs after real unchanged original design methods."""
from datetime import datetime,timezone
import json
from pathlib import Path
import tempfile
import profiles as P
from jsonschema import Draft202012Validator

def emit(profile):
    P.guard(profile)
    kind=profile['kind'];module=profile['module'];m=profile['manifest']
    with tempfile.TemporaryDirectory(prefix='cal-original-design-stage-') as folder:
        output=Path(folder)/'original'
        cls=module.EngineeringWorkflow if kind=='engineering' else module.ResearchWorkflow
        work=cls(profile['inputs'],P.SPECS[kind]['sha256'],output)
        P.need(work.state=='prepared' and work.events==[],'actual original design preimage differs')
        method=work.design;P.need(type(work) is cls and method.__func__ is cls.design,'actual selected original method identity differs')
        method()
        P.need(work.state=='designed' and len(work.events)==1 and work.events[0]['from']=='prepared' and work.events[0]['to']=='designed','actual original design stage did not occur')
        event=work.events[0]
        provenance={'schema_version':'lab-original-design-first-emission/v1','kind':kind,'observed_at':datetime.now(timezone.utc).isoformat(),
         'original_code_binding':{'path':(P.ORIGINAL/(kind+'.py')).relative_to(P.ROOT).as_posix(),'sha256':P.SPECS[kind]['code_sha256']},
         'original_input_manifest_sha256':P.SPECS[kind]['sha256'],'actual_original_method':cls.__name__+'.design',
         'actual_original_method_invoked':True,'actual_original_stage_event':event,'original_work':profile['original_work'],
         'original_retained_producer_source_cut':profile['original_producer_source_cut'],'actual_owner_outcome':None,'execution_rerun':False,'authority_effect':'none'}
    if kind=='research':
        # The method validates precisely this ready design. Capture its original
        # bytes rather than rewriting the protocol/question or old identities.
        h=profile['headers'][m['design_ref']];raw=profile['raws'][h['version_ref']]
        Draft202012Validator(module.carrier('experiment-design')[1]).validate(json.loads(raw))
    else:
        generator=module.artifact('implementation','original-design-method',{
          'implementation_kind':'original-pure-design-stage',
          'conforms_to_schema_refs':['lab-original-design-first-emission/v1'],
          'realizes_capability_refs':[module.CAPABILITY+'@foundation.1'],
          'execution_entrypoint_ref':provenance['original_code_binding']['path']+':EngineeringWorkflow.design@'+P.SPECS[kind]['code_sha256'],
          'environment_contract_ref':'selected-private-Python-3.14.4-jsonschema-4.23'},
          [{'relation_kind_ref':'relation.realizes','direction':'source','counterpart_kind':'product-capability','counterpart_ref':module.CAPABILITY}])
        generator['claim_ceiling']='New private candidate description of the exact original pure design method; no Tool permission, full Product realization or Source admission.'
        genraw=P.enc(generator);genref=generator['node_id']+'@'+P.SPECS[kind]['code_sha256']
        provenance['generator_artifact']={'scope_ref':profile['scope_ref'],'identity_ref':generator['node_id'],'version_ref':genref,
          'carrier_ref':'cal.artifact-type.implementation/v1','byte_sha256':P.sha(genraw)}
        provenance['generator_original']=generator
        manifest=P.enc(provenance);body=module.artifact('generated-output','observed-original-design',{
          'generator_ref':genref,
          'input_refs':[m['work_ref'],m['intent_ref'],m['original_implementation_ref']],
          'output_digest':'sha256:'+P.sha(manifest),'reproducibility_receipt_ref':'original-design-stage:'+P.sha(manifest)},
          [{'relation_kind_ref':'relation.produces','direction':'target','counterpart_kind':'agent-action','counterpart_ref':'original-design-stage:'+P.sha(manifest)}])
        body['claim_ceiling']='Typed first emission of the actual original pure design stage; no implementation execution, native Source-current Work admission or satisfaction claim.'
        raw=P.enc(body);h={'scope_ref':profile['scope_ref'],'identity_ref':body['node_id'],'version_ref':body['node_id']+'@'+P.sha(manifest)[:24],
             'carrier_ref':'cal.artifact-type.generated-output/v2','byte_sha256':P.sha(raw)}
    P.guard(profile);provenance['output']=h
    return h,raw,provenance
