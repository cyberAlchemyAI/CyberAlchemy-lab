"""Run the selected research episode and bind workflow/actor protocol evidence."""
from pathlib import Path
import sys,base64
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'workflows'))
from research import *
from referencing import Registry,Resource
from jsonschema import Draft202012Validator


def protocol_run(workflow,result,actors):
    schema=read(PACKAGE/'schemas/workflow-run.schema.json')
    common=ROOT/'docs/proposals/0007-lab-integrated-schema-package/schemas/common.schema.json'
    storage=ROOT/'docs/proposals/0006-lab-artifact-storage/schemas/artifact-package-manifest.schema.json'
    resources=Registry().with_resources([(read(p)['$id'],Resource.from_contents(read(p))) for p in [common,storage]])
    selection=workflow.selection;rows={r['version_ref']:r for r in selection['records']}
    def binding(version_ref):
        row=rows[version_ref];return {'scope_ref':SCOPE,'identity_ref':row['identity_ref'],'version_ref':version_ref,
            'carrier_ref':carrier(row['kind'])[0]['artifact_type_ref'],'byte_sha256':row['sha256']}
    request=result['receipt']['evaluation']['request']
    archive=read(ARCHIVE);head=parse(base64.b64decode(archive['files']['HEAD.json']['base64_original_bytes']))
    baseline=parse(base64.b64decode(archive['files']['baseline.json']['base64_original_bytes']))
    profile_raw=(ROOT/'implementation/lab-runtime/v2/profile.json').read_bytes();require(parse(profile_raw)==baseline['profile'],'archive source profile differs')
    definition=PACKAGE/'design/transition-contracts.json'
    value={'schema_version':schema['properties']['schema_version']['const'],'authority_effect':'none',
        'run_ref':'protocol:W04-research-run@candidate.1','workflow_type_ref':'workflow:research:v1-candidate',
        'definition_binding':{'ref':definition.relative_to(ROOT).as_posix(),'sha256':byte_sha(definition.read_bytes())},
        'intent':binding(selection['intent_ref']),'intent_resolution':binding(selection['resolution_ref']),
        'work':binding(selection['work_ref']),'coordination_context':binding(selection['coordination_ref']),
        'actor':{'principal_ref':request['principal_ref'],'agent_instance_ref':request['instance_record_ref'],
            'session_ref':request['session_record_ref'],'assignment_ref':request['assignment_ref'],
            'role_assignment_refs':[{'ref':r['version_ref'],'sha256':r['sha256']} for r in actors if r['version_ref']==request['role_assignment_ref']]},
        'source_cut':{'store_ref':'protocol:C12-owned-candidate-public-archive','branch_ref':'protocol:C12-source-audit-0002',
            'commit_sequence':head['sequence'],'commit_sha256':head['transaction_digest'],'source_profile_sha256':byte_sha(profile_raw),'streams':[]},
        'state':workflow.state,'event_bindings':[{'ref':'protocol:W04-transition-'+str(i+1),'sha256':byte_sha(encoded(e))} for i,e in enumerate(workflow.events)],
        'outcome_assessment':None,'gaps':[{'gap_ref':'protocol:W04-candidate-effects-uncommitted','subject_ref':selection['work_ref'],
            'reason':'The source cut is the preserved C12 committed archive. W04 inputs and proposed postimages are uncommitted candidate files; hypothesis evaluation is not Work satisfaction.',
            'owner_route':'S02/R08/A01','blocking_use':'canonical or operational admission'}],
        'status_axes':{'carrier_lifecycle':'candidate','admission':'candidate-unadmitted','commitment':None,'outcome_satisfaction':None}}
    Draft202012Validator(schema,registry=resources).validate(value);return value


def execute_episode(inputs,selection_sha,output):
    workflow=ResearchWorkflow(inputs,selection_sha,output);workflow.design()
    f=fixture(workflow.selection,workflow.records)
    try:
        original=encoded({'selection_sha256':selection_sha,'procedure_sha256':workflow.selection['procedure']['sha256']})
        f.request['input_sha256']=byte_sha(original)
        receipt=workflow.execute(f.authority,f.raw(),original)
        require(receipt['posture']=='completed','research episode requires observed completion; preserve indeterminate journal')
        workflow.assess();result=workflow.materialize()
        actors=[{'version_ref':r.version_ref,'sha256':r.expected_sha256,'posture':r.posture,'original_record':parse(r.original)} for r in f.records.values()]
        (workflow.output/'selected-actor-records.json').write_bytes(encoded(actors))
        (workflow.output/'workflow-run.json').write_bytes(encoded(protocol_run(workflow,result,actors)))
        (workflow.output/'action-receipt.json').write_bytes(encoded(receipt))
        return result
    finally:f.session.close()
