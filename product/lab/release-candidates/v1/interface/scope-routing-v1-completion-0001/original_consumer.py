"""Unmodified O.prepare scope-gate probe; no actual body or consumer success claim."""
import copy
import importlib.util
import sys
from routing import ROOT,CONSUMER

def selected_operations():
    name='_T11_original_custody_correction_consumer'
    package=CONSUMER.parent
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,package/'__init__.py',submodule_search_locations=[str(package)])
        value=importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value)
    operations=__import__(name+'.operations',fromlist=['prepare'])
    assert operations.prepare.__code__.co_filename==str(CONSUMER)
    return operations

def probe(router,route,proposal_scope):
    operations=selected_operations();config=copy.deepcopy(router.config)
    head=router.base['original_head']['transaction_digest']
    projection={'subjects':{},'contracts':{},'documents':{}}
    before=copy.deepcopy(projection)
    target={'category':route.category,'operation':route.operation,'version_ref':route.version_ref,'carrier_ref':route.carrier_ref,'record':{'scope_ref':route.body_scope_ref},'predecessor_ref':None,'decision_ref':route.decision_ref,'contract':None}
    proposal={'schema_version':'lab-runtime-proposal/v1','proposal_id':'T11-literal-scope-probe','expected_head':head,'source_snapshot_digest':config['source_snapshot_digest'],'scope_ref':proposal_scope,'policy_ref':config['policy_ref'],'challenge_route':config['challenge_route'],'targets':[target],'schemas':{}}
    expected='target outside authorized scope' if proposal_scope==config['scope_ref'] else 'proposal outside provisioned scope'
    try:operations.prepare(projection,proposal,head,config)
    except operations.RuntimeFault as error:
        assert str(error)==expected,str(error)
        frames=[];tb=error.__traceback__
        while tb:
            if tb.tb_frame.f_code.co_filename==str(CONSUMER):frames.append({'function':tb.tb_frame.f_code.co_name,'line':tb.tb_lineno})
            tb=tb.tb_next
        assert frames and frames[-1]['function']=='prepare'
        assert projection==before and config==router.config
        return {'result':'EXPECTED-ORIGINAL-CONSUMER-REFUSAL','message':expected,'source_frames':frames,'proposal_scope_ref':proposal_scope,'literal_body_scope_ref':route.body_scope_ref,'actual_body_loaded':False,'actual_full_body_schema_or_consumer_success':False,'historical_config_reused_as_current_authority':False,'projection_mutated':False,'config_mutated':False}
    raise AssertionError('original consumer unexpectedly accepted missing domain grant')
