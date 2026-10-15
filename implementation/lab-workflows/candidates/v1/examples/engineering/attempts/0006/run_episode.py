"""Execute the selected correction and stage independently assessed review members."""
from pathlib import Path
import base64,copy,json,os,sys,time,unittest
from referencing import Registry,Resource
from jsonschema import Draft202012Validator
from behavior import *


def run_default_regression(candidate,expected_sha,output):
    """Fresh preserved W02 tests with the successor's default host evaluator."""
    import fixtures,test_boundaries
    module=load_registered(candidate,expected_sha)
    old=fixtures.HostAuthority;fixtures.HostAuthority=module.HostAuthority
    from validate import Recording
    try:
        probe=fixtures.Fixture()
        try:require(type(probe.authority) is module.HostAuthority,'default regression selected wrong implementation')
        finally:probe.session.close()
        suite=unittest.defaultTestLoader.loadTestsFromModule(test_boundaries)
        count=suite.countTestCases();require(count==42,'default authority suite changed')
        start=time.perf_counter()
        with Path(output).open('w') as log:
            result=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=Recording).run(suite)
        return {'result':'PASS' if result.wasSuccessful() and result.testsRun==42 else 'FLAG',
            'tests':result.testsRun,'checks':result.checks,'duration_seconds':time.perf_counter()-start,
            'evaluator_sha256':expected_sha,'default_interfaces':sorted(module.HostAuthority.__init__.__kwdefaults__['registered_interfaces']),
            'log_path':str(Path(output).resolve()),
            'log_sha256':byte_sha(Path(output).read_bytes()),
            'claim_ceiling':'Fresh 42 preserved W02 checks under the candidate default evaluator. The preserved cold child uses its original counter adapter.'}
    finally:fixtures.HostAuthority=old


def workflow_run(workflow,result):
    """Protocol state is separate from artifact lifecycle and store admission."""
    common=ROOT/'docs/proposals/0007-lab-integrated-schema-package/schemas/common.schema.json'
    storage=ROOT/'docs/proposals/0006-lab-artifact-storage/schemas/artifact-package-manifest.schema.json'
    registry=Registry().with_resources([(read(p)['$id'],Resource.from_contents(read(p))) for p in [common,storage]])
    contract=PACKAGE/'design/transition-contracts.json'
    schema=read(PACKAGE/'schemas/workflow-run.schema.json')
    rows={r['version_ref']:r for r in workflow.manifest['records']}
    def selected(ref):
        r=rows[ref];return {'scope_ref':SCOPE,'identity_ref':r['identity_ref'],'version_ref':ref,
            'carrier_ref':carrier(r['kind'])[0]['artifact_type_ref'],'byte_sha256':r['sha256']}
    request=result['receipt']['evaluation']['request']
    selected_actors=read(workflow.output_root.parent/'selected-actor-records.json')
    actor={'principal_ref':request['principal_ref'],'role_assignment_refs':[
        {'ref':r['version_ref'],'sha256':r['sha256']} for r in selected_actors
        if r['version_ref']==request['role_assignment_ref']],
        'agent_instance_ref':request['instance_record_ref'],'session_ref':request['session_record_ref'],
        'assignment_ref':request['assignment_ref']}
    source=read(ROOT/'implementation/lab-work/candidates/v1/packages/0002/branch.snapshot')
    for row in source['files'].values():require(byte_sha(base64.b64decode(row['base64_original_bytes']))==row['sha256'],'archived source bytes drift')
    head=parse(base64.b64decode(source['files']['HEAD.json']['base64_original_bytes']))
    baseline=parse(base64.b64decode(source['files']['baseline.json']['base64_original_bytes']))
    profile_raw=(ROOT/'implementation/lab-runtime/v2/profile.json').read_bytes()
    require(parse(profile_raw)==baseline['profile'],'archived source profile differs')
    assessed=result['candidates']['work-outcome-assessment']
    value={'schema_version':schema['properties']['schema_version']['const'],
        'run_ref':'protocol:W03-engineering-run@candidate.1','workflow_type_ref':'workflow:engineering:v1-candidate',
        'definition_binding':{'ref':contract.relative_to(ROOT).as_posix(),'sha256':byte_sha(contract.read_bytes())},
        'intent':selected(workflow.manifest['intent_ref']),
        'intent_resolution':selected(workflow.manifest['resolution_ref']),
        'work':selected(workflow.manifest['work_ref']),
        'coordination_context':selected(workflow.manifest['coordination_ref']),
        'actor':actor,'source_cut':{'store_ref':'protocol:C12-owned-candidate-public-archive',
            'branch_ref':'protocol:C12-source-audit-0002','commit_sequence':head['sequence'],
            'commit_sha256':head['transaction_digest'],'source_profile_sha256':byte_sha(profile_raw),
            'streams':[]},'state':workflow.state,
        'event_bindings':[{'ref':'protocol:W03-transition-'+str(i+1),'sha256':byte_sha(encoded(e))} for i,e in enumerate(workflow.events)],
        'outcome_assessment':{'scope_ref':SCOPE,'identity_ref':identity(assessed),
            'version_ref':identity(assessed)+'@candidate.1','carrier_ref':carrier('work-outcome-assessment')[0]['artifact_type_ref'],
            'byte_sha256':byte_sha(encoded(assessed))},
        'gaps':[{'gap_ref':'protocol:W03-candidate-effects-uncommitted','subject_ref':workflow.manifest['work_ref'],
            'reason':'The source cut identifies the preserved C12 committed archive. W03 selections and proposed postimages are uncommitted candidate files.',
            'owner_route':'S02/R08/A01','blocking_use':'canonical or operational admission'}],
        'authority_effect':'none','status_axes':{'carrier_lifecycle':'candidate','admission':'candidate-unadmitted',
            'commitment':None,'outcome_satisfaction':workflow.assessment['disposition']}}
    Draft202012Validator(schema,registry=registry).validate(value)
    return value


def execute_episode(inputs,selection_sha,output,default_regression):
    output=Path(output);require(not output.exists(),'episode output already exists')
    output.mkdir(mode=0o700)
    manifest,records=resolve_inputs(inputs,selection_sha)
    candidate=Path(inputs)/'registered_evaluator.py'
    module=load_registered(candidate,manifest['output_source_sha256'])
    original=sys.modules['evaluator']
    before=fixture_for(original,registered=False)
    try:
        baseline=public_evaluation(before.authority.check(before.raw()))
        require(baseline['posture']=='denied' and any('interface' in c['check'] for c in baseline['checks']),'original limitation not observed')
    finally:before.session.close()
    (output/'before.json').write_bytes(encoded(baseline))
    f=fixture_for(module,work_ref=identity(records[manifest['work_ref']]))
    try:
        w=EngineeringWorkflow(inputs,selection_sha,output/'workflow');w.design()
        inp=encoded({'original_sha256':manifest['original_source_sha256'],
            'output_sha256':manifest['output_source_sha256'],'correction_id':'host-interface-registry/v1'})
        f.request['input_sha256']=byte_sha(inp)
        w.execute(f.authority,f.raw(),inp)
        checks=run_behavior(w.tool.output,manifest['output_source_sha256'],output/'evidence',default_regression=default_regression)
        w.assess(checks,output/'evidence');result=w.materialize()
        (output/'selected-actor-records.json').write_bytes(encoded([
            {'version_ref':r.version_ref,'sha256':r.expected_sha256,'posture':r.posture,
             'original_record':parse(r.original)} for r in f.records.values()]))
        protocol=workflow_run(w,result);(output/'workflow-run.json').write_bytes(encoded(protocol))
        (output/'transitions.json').write_bytes(encoded(w.events))
        (output/'action-receipt.json').write_bytes(encoded(w.receipt))
        (output/'assessment.json').write_bytes(encoded(w.assessment))
        return result
    finally:f.session.close()
