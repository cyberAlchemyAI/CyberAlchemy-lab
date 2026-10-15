"""Independently execute before/after authority behavior and pin observations."""
from pathlib import Path
import copy,json,sys
from dataclasses import replace
HERE=Path(__file__).resolve().parent;PACKAGE=HERE.parents[1]
sys.path.insert(0,str(PACKAGE/'workflows'));sys.path.insert(0,str(PACKAGE/'receipts/action-boundaries'))
from engineering import *
from fixtures import Fixture


def fixture_for(module,work_ref='work:lab-engineering:registered-interface-correction',*,registered=True):
    fixture=Fixture()
    fixture.by_kind['agent-assignment']['payload']['work_ref']=work_ref
    fixture.by_kind['delegation']['payload']['allowed_action_kinds']=['stage-source-correction']
    fixture.by_kind['agent-profile']['payload']['tool_class_refs']=['tool-class:bounded-source-correction']
    fixture.by_kind['tool']['payload'].update(tool_name='bounded-source-correction',interface_version=INTERFACE,
        input_contract_ref='protocol:W03-source-correction-input',output_contract_ref='protocol:W03-exact-implementation-bytes',
        failure_boundary_refs=['protocol:W03-no-retry-before-reconciliation'],evidence_route_ref='protocol:W03-engineering-action-journal')
    for kind in ['agent-assignment','delegation','agent-profile','tool']:fixture.reselect(kind)
    fixture.status['selected_work_ref']=work_ref
    fixture.status['tool_classes'][fixture.ref('tool')]='tool-class:bounded-source-correction'
    fixture.adapter_sha256=byte_sha((PACKAGE/'workflows/engineering.py').read_bytes())
    fixture.grant=replace(fixture.grant,action_kinds=frozenset({'stage-source-correction'}),max_output_bytes=65536,
        adapter_sha256=fixture.adapter_sha256)
    fixture.request['action_kind']='stage-source-correction'
    args=dict(adapter_sha256=fixture.adapter_sha256,environment_sha256=fixture.environment_sha256)
    if registered:args['registered_interfaces']=frozenset({INTERFACE})
    fixture.authority=module.HostAuthority(fixture.session,lambda ref:fixture.records.get(ref),
        lambda:copy.deepcopy(fixture.status),lambda:fixture.grant,**args)
    return fixture


def run_behavior(candidate,expected_sha,evidence_root,*,default_regression):
    evidence_root=Path(evidence_root);evidence_root.mkdir(parents=True,exist_ok=False)
    module=load_registered(candidate,expected_sha);fixture=fixture_for(module);results={}
    try:
        selected=fixture.authority.check(fixture.raw());results['selected-interface-permitted']=(selected['posture']=='permitted',selected)
        ref=fixture.ref('tool');fixture.by_kind['tool']['payload']['interface_version']='unregistered-external-tool/v1';fixture.reselect('tool')
        unselected=fixture.authority.check(fixture.raw());results['unselected-interface-denied']=(unselected['posture']=='denied',unselected)
        fixture.by_kind['tool']['payload']['interface_version']=INTERFACE;fixture.reselect('tool')
        fixture.request['action_kind']='admit-canonical';wrong=fixture.authority.check(fixture.raw());results['wrong-action-denied']=(wrong['posture']=='denied',wrong)
        fixture.request['action_kind']='stage-source-correction';fixture.status['revoked_refs']=[fixture.ref('delegation')]
        revoked=fixture.authority.check(fixture.raw());results['revoked-authority-denied']=(revoked['posture']=='denied',revoked)
        fixture.status['revoked_refs']=[];fixture.grant=replace(fixture.grant,expires_at=fixture.now[0]-1)
        expired=fixture.authority.check(fixture.raw());results['expired-authority-denied']=(expired['posture']=='denied',expired)
        results['source-bytes-exact']=(byte_sha(Path(candidate).read_bytes())==expected_sha,{'observed_sha256':byte_sha(Path(candidate).read_bytes())})
        regression_pass=(default_regression['result']=='PASS' and default_regression['tests']==42
            and default_regression.get('evaluator_sha256')==expected_sha
            and len(default_regression.get('checks',[]))==42
            and len({r['test'] for r in default_regression.get('checks',[])})==42
            and all(r['result']=='PASS' for r in default_regression.get('checks',[])))
        regression=copy.deepcopy(default_regression)
        if regression_pass:
            log=Path(regression.pop('log_path'));require(log.is_file() and not log.is_symlink(),'default regression log missing')
            raw=log.read_bytes();require(byte_sha(raw)==regression['log_sha256'],'default regression log changed')
            (evidence_root/'default-regression.log').write_bytes(raw);regression['log_path']='default-regression.log'
        results['default-regression-complete']=(regression_pass,regression)
        rows={}
        for name,(passed,value) in results.items():
            if 'grant' in value:value=public_evaluation(value)
            observed={'check':name,'result':'PASS' if passed else 'FLAG','producer':'W03-independently-executed-behavior-verifier/v1',
                'output_sha256':expected_sha,'observed':value,'actual_owner_outcome':None}
            raw=encoded(observed);path=evidence_root/(name+'.json');path.write_bytes(raw)
            rows[name]={'result':observed['result'],'evidence_path':path.name,'evidence_sha256':byte_sha(raw)}
        return rows
    finally:fixture.session.close()
