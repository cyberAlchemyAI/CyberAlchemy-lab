"""Exact candidate engineering transitions, bounded correction and assessment."""
from __future__ import annotations
import ast
import base64
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[3]
AUTHORITY = PACKAGE/'authority'; sys.path.insert(0,str(AUTHORITY))
from evaluator import BoundaryFault, HostAuthority, SelectedRecord, byte_sha, encoded, parse, require
from dispatch import public_evaluation
sys.path.insert(0,str(PACKAGE/'tools'))
from counter import atomic, regular_json, fsync_directory
from jsonschema import Draft202012Validator

REGISTRY = ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'
PAIRS = ROOT/'implementation/lab-runtime/candidates/repeatable-operation/design/contract-impact.json'
INTERFACE = 'bounded-local-source-correction/v1-candidate'
ORIGINAL = AUTHORITY/'evaluator.py'
EXAMPLE = PACKAGE/'examples/engineering'
SCOPE = 'project:cyberalchemy-v2-to-lab-migration'
CAPABILITY = 'product-capability:cyberalchemy-lab:governed-knowledge-lifecycle'
EXPECTED_CHECKS = ('selected-interface-permitted','unselected-interface-denied',
    'wrong-action-denied','revoked-authority-denied','expired-authority-denied',
    'source-bytes-exact','default-regression-complete')


def read(path):return parse(Path(path).read_bytes())
def identity(record):return record.get('node_id',record.get('goal_id',record.get('coordination_context_id',record.get('project_id'))))

def semantic_kind(record):
    if record.get('schema_version')=='cyberalchemy-lab-project-identity/v1':
        validate_record(record,'project-identity');return 'project'
    return record['kind']


def carrier(kind):
    registry=read(REGISTRY);current=set(registry['current_by_identity'].values())
    rows=[r for r in registry['admitted_contracts'] if r['semantic_kind']==kind and r['artifact_type_ref'] in current]
    require(len(rows)==1,'current carrier ambiguous or absent')
    row=rows[0];require(row['schema_selector'] is None,'explicit schema selector required')
    raw=(ROOT/row['schema_path']).read_bytes();require(byte_sha(raw)==row['schema_sha256'],'carrier original bytes drift')
    return row,parse(raw)


def validate_record(record,kind):
    _,schema=carrier(kind);errors=list(Draft202012Validator(schema).iter_errors(record))
    require(not errors,'invalid '+kind+' carrier: '+(errors[0].message if errors else ''))


def artifact(kind,name,payload,relation_refs=None):
    schema=carrier(kind)[1]
    value={'schema_version':schema['properties']['schema_version']['const'],'kind':kind,
        'node_id':kind+':lab-engineering:'+name,'name':'Candidate engineering '+name,
        'lifecycle_state':'candidate','authority_effect':'none','owner_ref':'principal:repository-owner@candidate.1',
        'scope_ref':SCOPE,'evidence_refs':['protocol:W03-exact-candidate-evidence'],
        'challenge_route':'protocol:W03-engineering-challenge','successor_refs':[],
        'relation_refs':relation_refs if relation_refs is not None else [{'relation_kind_ref':'relation.challenges','direction':'target',
             'counterpart_kind':'challenge-event','counterpart_ref':'protocol:W03-deferred-challenge'}],
        'payload':payload,'claim_ceiling':'Scoped candidate engineering carrier; actual owner outcome and admission remain R08/A01.'}
    validate_record(value,kind);return value


def corrected_source(original):
    """An exact interface correction, generated from the pinned W02 class body."""
    text=original.decode();tree=ast.parse(text)
    node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='HostAuthority')
    body='\n'.join(text.splitlines()[node.lineno-1:node.end_lineno])+'\n'
    edits=[('class HostAuthority:', 'class HostAuthority(_OriginalHostAuthority):'),
        ('*, adapter_sha256, environment_sha256):',
         "*, adapter_sha256, environment_sha256, registered_interfaces=frozenset({'bounded-local-counter/v1-candidate'})):\n        require(type(registered_interfaces) is frozenset and registered_interfaces and all(type(v) is str and v for v in registered_interfaces), 'closed host interface registry required')\n        self.registered_interfaces = registered_interfaces"),
        ("tool['interface_version'] == 'bounded-local-counter/v1-candidate'", "tool['interface_version'] in self.registered_interfaces")]
    for before,after in edits:
        require(body.count(before)==1,'selected correction edit no longer exact');body=body.replace(before,after)
    header='"""Candidate registered Tool evaluator; exact W02 actor guards preserved."""\nfrom evaluator import *\nfrom evaluator import HostAuthority as _OriginalHostAuthority\n\n'
    raw=(header+body).encode();ast.parse(raw);return raw


def load_registered(path,expected_sha):
    raw=Path(path).read_bytes();require(byte_sha(raw)==expected_sha,'registered evaluator code differs')
    name='lab_W03_registered_'+uuid.uuid4().hex
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module);return module


def resolve_inputs(directory,expected_manifest_sha):
    directory=Path(directory);raw=(directory/'input-manifest.json').read_bytes()
    require(byte_sha(raw)==expected_manifest_sha,'independent engineering selection pin mismatch')
    manifest=parse(raw);require(manifest['authority_effect']=='none' and manifest['scope_ref']==SCOPE,'engineering scope differs')
    require(manifest['actual_owner_outcome'] is None and manifest['owner_decision_status']=='explicitly-deferred-R08','owner outcome cannot be supplied by development inputs')
    records={}
    for row in manifest['records']:
        require(Path(row['path']).name==row['path'],'input outside selected scope')
        path=directory/row['path'];require(path.is_file() and not path.is_symlink(),'input missing or unsafe')
        raw=path.read_bytes();require(byte_sha(raw)==row['sha256'],'selected input original bytes changed')
        value=parse(raw);validate_record(value,row['kind'])
        require(row['posture']=='isolated-candidate-current','input posture outside isolated development scope')
        require(identity(value)==row['identity_ref'],'input identity differs')
        require(row['version_ref'].startswith(row['identity_ref']+'@'),'input exact revision differs')
        if 'version' in value:require(row['version_ref']==row['identity_ref']+'@'+value['version'],'body and selected version differ')
        require(row['version_ref'] not in records,'duplicate selected revision');records[row['version_ref']]=value
    work=records[manifest['work_ref']];intent=records[manifest['intent_ref']];resolution=records[manifest['resolution_ref']]
    require(resolution['payload']['intent_ref']==identity(intent),'Intent Resolution differs')
    require(identity(work) in resolution['payload']['selected_subject_refs'],'Work not selected')
    require(work['payload']['project_ref']==SCOPE,'Work outside Project')
    require(work['payload']['goal_refs']==[manifest['goal_ref']],'Work goal differs')
    require(intent['satisfaction_refs']==[],'pre-execution Intent cannot claim satisfaction')
    require(set(resolution['payload']['satisfaction_test_refs'])==set(EXPECTED_CHECKS),'declared satisfaction obligations differ')
    coordination=records[manifest['coordination_ref']]
    require(coordination['goal_ref']==manifest['goal_ref'] and coordination['project_ref']==SCOPE,'single-goal coordination differs')
    for name in ['define','design','plan']:
        row=manifest[name];require(Path(row['path']).name==row['path'],'design/plan input outside selected scope')
        path=directory/row['path'];require(path.is_file() and not path.is_symlink(),'design/plan input unsafe')
        raw=path.read_bytes()
        require(byte_sha(raw)==row['sha256'],'design/plan input original bytes changed')
        value=parse(raw);require(value['work_ref']==manifest['work_ref'] and value['authority_effect']=='none','design/plan Work differs')
        require(value['intent_ref']==manifest['intent_ref'] and value['source_sha256']==manifest['original_source_sha256']
                and value['expected_output_sha256']==manifest['output_source_sha256']
                and value['satisfaction_obligations']==list(EXPECTED_CHECKS),'design/plan exact correction differs')
    require(byte_sha(ORIGINAL.read_bytes())==manifest['original_source_sha256'],'original implementation revision changed')
    require(byte_sha(corrected_source(ORIGINAL.read_bytes()))==manifest['output_source_sha256'],'proposed correction bytes differ')
    return manifest,records


class SourceCorrection:
    """Writes one selected candidate file in a host-owned fresh output directory."""
    def __init__(self,root,original_sha,expected_output_sha):
        self.root=Path(root);self.original_sha=original_sha;self.expected_output_sha=expected_output_sha
        require(not self.root.exists(),'engineering Tool destination already exists')
        self.root.mkdir(mode=0o700);self.output=self.root/'registered_evaluator.py';self.journal=self.root/'action.json'
        self.pin=None

    def invoke(self,authority,request,original_input,*,interrupt_after_write=False):
        require(isinstance(authority,HostAuthority),'trusted bounded authority required')
        if self.journal.exists():
            require(authority.check(request)['posture']=='permitted','current source correction authority denied')
            require(byte_sha(self.journal.read_bytes())==self.pin,'engineering action journal changed')
            prior=read(self.journal)
            require(prior['request_sha256']==byte_sha(request),'engineering idempotency conflict')
            require(prior['input_sha256']==byte_sha(original_input),'engineering input binding changed')
            if prior['receipt'] is not None:
                require(self.output.is_file() and not self.output.is_symlink()
                        and byte_sha(self.output.read_bytes())==self.expected_output_sha,'completed engineering output drift')
            return prior['receipt'] or {'posture':'indeterminate','retry_allowed':False,'reconciliation_required':True}
        require(self.pin is None,'engineering action journal missing; reconciliation required')
        evaluation=authority.check(request)
        require(evaluation['posture']=='permitted','source correction authority denied')
        value=parse(original_input);require(set(value)=={'original_sha256','output_sha256','correction_id'},'closed correction input required')
        require(value=={'original_sha256':self.original_sha,'output_sha256':self.expected_output_sha,'correction_id':'host-interface-registry/v1'},'selected correction contract differs')
        require(byte_sha(original_input)==evaluation['request']['input_sha256'],'Tool input binding changed')
        require(len(original_input)<=evaluation['grant'].max_input_bytes,'Tool input budget exceeded')
        require(evaluation['tool_contract']['interface_version']==INTERFACE,'unselected engineering Tool interface')
        require(evaluation['tool_contract']['input_contract_ref']=='protocol:W03-source-correction-input'
                and evaluation['tool_contract']['output_contract_ref']=='protocol:W03-exact-implementation-bytes'
                and evaluation['tool_contract']['evidence_route_ref']=='protocol:W03-engineering-action-journal','selected engineering Tool contract differs')
        require(evaluation['grant'].max_actions>=1,'Tool action budget exhausted')
        require(evaluation['tool_contract']['failure_boundary_refs']==['protocol:W03-no-retry-before-reconciliation'],'unselected Tool failure contract')
        require(byte_sha(Path(__file__).read_bytes())==evaluation['grant'].adapter_sha256,'source correction adapter original bytes changed')
        output=corrected_source(ORIGINAL.read_bytes())
        require(byte_sha(ORIGINAL.read_bytes())==self.original_sha and byte_sha(output)==self.expected_output_sha,'source/output bytes differ from selected correction')
        require(len(output)<=evaluation['grant'].max_output_bytes,'Tool output budget exceeded')
        pending={'authority_effect':'none','posture':'pending','request_sha256':byte_sha(request),
            'input_sha256':byte_sha(original_input),'input_original_b64':base64.b64encode(original_input).decode(),
            'expected_output_sha256':self.expected_output_sha,'receipt':None,'evaluation':public_evaluation(evaluation)}
        atomic(self.journal,pending);self.pin=byte_sha(self.journal.read_bytes())
        immediate=authority.check(request)
        require(immediate['posture']=='permitted','authority changed before correction effect')
        try:
            with self.output.open('xb') as stream:stream.write(output);stream.flush();os.fsync(stream.fileno())
            fsync_directory(self.root)
            if interrupt_after_write:return {'posture':'indeterminate','retry_allowed':False,'reconciliation_required':True}
            require(byte_sha(self.output.read_bytes())==self.expected_output_sha,'observed implementation bytes differ')
            receipt={'authority_effect':'none','posture':'completed','actual_owner_outcome':None,
                'output_sha256':self.expected_output_sha,'original_sha256':self.original_sha,
                'request_sha256':byte_sha(request),'evaluation':public_evaluation(immediate),
                'retry_allowed':False,'reconciliation_required':False}
            pending['posture']='completed';pending['receipt']=receipt;atomic(self.journal,pending);self.pin=byte_sha(self.journal.read_bytes())
            return receipt
        except Exception:return {'posture':'indeterminate','retry_allowed':False,'reconciliation_required':True}


def assess(checks,expected_output_sha,actual_output,*,evidence_root):
    """Independently compare the declared obligations, never a caller success label."""
    require(type(checks) is dict and set(checks)==set(EXPECTED_CHECKS),'incomplete satisfaction evidence')
    require(byte_sha(actual_output)==expected_output_sha,'assessment output revision differs')
    for name,value in checks.items():
        require(type(value) is dict and set(value)=={'result','evidence_sha256','evidence_path'},'unbound satisfaction evidence')
        require(Path(value['evidence_path']).name==value['evidence_path'],'satisfaction evidence outside selected scope')
        path=Path(evidence_root)/value['evidence_path'];require(path.is_file() and not path.is_symlink(),'satisfaction evidence missing')
        raw=path.read_bytes();require(byte_sha(raw)==value['evidence_sha256'],'satisfaction evidence original bytes changed')
        observed=parse(raw)
        require(observed['check']==name and observed['result']==value['result']
                and observed['output_sha256']==expected_output_sha
                and observed['producer']=='W03-independently-executed-behavior-verifier/v1','satisfaction evidence differs')
        require(value['result'] in ['PASS','FLAG'],'unbound satisfaction result')
        if value['result']=='PASS':
            detail=observed['observed']
            if name.endswith('-permitted'):require(detail['posture']=='permitted','fabricated permitted result')
            elif name.endswith('-denied'):require(detail['posture']=='denied','fabricated denied result')
            elif name=='source-bytes-exact':require(detail['observed_sha256']==expected_output_sha,'fabricated source byte result')
            elif name=='default-regression-complete':
                require(detail['result']=='PASS' and detail['tests']==42
                    and detail['evaluator_sha256']==expected_output_sha
                    and len(detail['checks'])==42 and len({r['test'] for r in detail['checks']})==42
                    and all(r['result']=='PASS' for r in detail['checks']),'fabricated default regression result')
                require(detail['log_path']=='default-regression.log','regression log outside evidence scope')
                log=Path(evidence_root)/detail['log_path']
                require(log.is_file() and not log.is_symlink() and byte_sha(log.read_bytes())==detail['log_sha256'],'regression log original bytes differ')
    return {'authority_effect':'none','disposition':'supported' if all(c['result']=='PASS' for c in checks.values()) else 'unsupported',
            'checks':copy.deepcopy(checks),'actual_owner_outcome':None,
            'claim_ceiling':'Exact declared candidate behavior only; no human acceptance, admission or Product benefit.'}


def typed_relation(name,kind,source_ref,target_ref,records,qualifiers):
    require(source_ref in records and target_ref in records,'relation endpoint exact revision unresolved')
    source=records[source_ref];target=records[target_ref]
    matches=[r for r in read(PAIRS)['exact_pairs'] if r['relation_kind_ref']==kind and r['source_kind']==semantic_kind(source) and r['target_kind']==semantic_kind(target)]
    require(len(matches)==1,'relation ordered pair undeclared')
    contract=matches[0]['qualifier_contract'];require(set(qualifiers)==set(contract['required_axes']),'closed qualifier axes differ')
    require(all(type(v) is str and v for v in qualifiers.values()),'qualifier domain differs')
    binding=matches[0]['relation_binding'];require(byte_sha((ROOT/binding['path']).read_bytes())==binding['sha256'],'Relation Kind original bytes changed')
    for ref,record in [(source_ref,source),(target_ref,target)]:
        require(ref.startswith(identity(record)+'@'),'relation endpoint identity differs')
        if 'version' in record:require(ref==identity(record)+'@'+record['version'],'relation endpoint body revision differs')
    payload={'relation_kind_ref':kind,'source':{'ref':identity(source),'version_ref':source_ref,'kind':semantic_kind(source)},
        'target':{'ref':identity(target),'version_ref':target_ref,'kind':semantic_kind(target)},'qualifiers':qualifiers,
        'relation_lifecycle_state':'candidate','relation_evidence_refs':['protocol:W03-exact-candidate-evidence']}
    return artifact('typed-relation',name,payload,[])


class EngineeringWorkflow:
    def __init__(self,inputs,selection_sha,output_root):
        self.inputs=Path(inputs);self.manifest,self.records=resolve_inputs(self.inputs,selection_sha)
        self.output_root=Path(output_root);require(not self.output_root.exists(),'workflow output already exists')
        self.output_root.mkdir(mode=0o700);self.state='prepared';self.events=[]
        self.receipt=None;self.implementation_bytes=None;self.assessment=None
        self.tool=None

    def transition(self,expected,new,detail):
        require(self.state==expected,'invalid engineering transition')
        event={'from':expected,'to':new,'authority_effect':'none','detail':detail,
               'carrier_lifecycle':'candidate','admission':'candidate-unadmitted','commitment':None}
        self.events.append(event);self.state=new

    def design(self):
        # All Define/Design/Plan files were independently pinned before execution.
        pairs=read(PAIRS)['exact_pairs']
        required=[('relation.successor-of','implementation','implementation'),
            ('relation.realizes','implementation','product-capability'),
            ('relation.produces','agent-action','generated-output'),
            ('relation.evaluates','work-outcome-assessment','work'),
            ('relation.member-of','evidence-set','project'),('relation.successor-of','work','work')]
        for kind,source,target in required:
            selected=[p for p in pairs if (p['relation_kind_ref'],p['source_kind'],p['target_kind'])==(kind,source,target)]
            require(len(selected)==1,'engineering design connection undeclared')
            binding=selected[0]['relation_binding']
            require(byte_sha((ROOT/binding['path']).read_bytes())==binding['sha256'],'design Relation Kind changed')
        self.transition('prepared','designed',{'work_ref':self.manifest['work_ref'],
            'source_sha256':self.manifest['original_source_sha256'],
            'proposed_output_sha256':self.manifest['output_source_sha256'],
            'declared_connections':[list(p) for p in required],
            'satisfaction_obligations':list(EXPECTED_CHECKS)})

    def execute(self,authority,request,original_input,*,interrupt_after_write=False):
        require(self.state=='designed','engineering design required before execution')
        self.tool=SourceCorrection(self.output_root/'tool',self.manifest['original_source_sha256'],self.manifest['output_source_sha256'])
        self.receipt=self.tool.invoke(authority,request,original_input,interrupt_after_write=interrupt_after_write)
        if self.receipt['posture']=='indeterminate':
            self.transition('designed','indeterminate',{'receipt':self.receipt});return self.receipt
        require(self.receipt['posture']=='completed','actual implementation output absent')
        self.implementation_bytes=self.tool.output.read_bytes()
        self.transition('designed','implemented',{'output_sha256':byte_sha(self.implementation_bytes),
            'execution_result':'completed','outcome_satisfaction':None})
        return self.receipt

    def assess(self,checks,evidence_root):
        require(self.state=='implemented','implementation completion required before assessment')
        self.assessment=assess(checks,self.manifest['output_source_sha256'],self.implementation_bytes,evidence_root=evidence_root)
        self.transition('implemented','assessed',{'disposition':self.assessment['disposition'],
            'admission':'candidate-unadmitted','actual_owner_outcome':None})
        return self.assessment

    def materialize(self):
        require(self.state=='assessed' and self.assessment is not None,'satisfaction assessment missing')
        manifest=self.manifest;records=copy.deepcopy(self.records);work=records[manifest['work_ref']]
        original_ref=manifest['original_implementation_ref'];original=records[original_ref]
        successor=copy.deepcopy(original)
        successor['name']='Candidate registered-interface actor evaluator'
        successor['payload']['execution_entrypoint_ref']='protocol:W03-registered-evaluator:'+manifest['output_source_sha256']
        successor['successor_refs']=[]
        successor['claim_ceiling']='Candidate registered-interface subset of governed knowledge lifecycle; no broad API/Product conformance or authority grant.'
        successor_ref=identity(successor)+'@registered-candidate.1';records[successor_ref]=successor;validate_record(successor,'implementation')
        generator=artifact('implementation','bounded-source-corrector',{
            'implementation_kind':'bounded-local-source-correction-generator',
            'conforms_to_schema_refs':['protocol:W03-source-correction-input','protocol:W03-exact-implementation-bytes'],
            'realizes_capability_refs':[CAPABILITY+'@foundation.1'],
            'execution_entrypoint_ref':'protocol:W03-SourceCorrection:'+byte_sha(Path(__file__).read_bytes()),
            'environment_contract_ref':'protocol:W03-pinned-Python-environment'},
            [{'relation_kind_ref':'relation.realizes','direction':'source','counterpart_kind':'product-capability','counterpart_ref':CAPABILITY}])
        generator_ref=identity(generator)+'@candidate.1';records[generator_ref]=generator
        evaluation=self.receipt['evaluation'];request=evaluation['request']
        action=artifact('agent-action','source-correction',{'agent_instance_ref':request['instance_record_ref'],
            'session_ref':request['session_record_ref'],'assignment_ref':request['assignment_ref'],
            'action_kind':request['action_kind'],'posture':'completed','input_refs':['protocol:W03-original-source:'+manifest['original_source_sha256']],
            'output_refs':['generated-output:lab-engineering:registered-interface-bytes@candidate.1'],
            'tool_refs':[request['tool_ref']],'implementation_refs':[generator_ref],
            'authority_evidence_refs':[r['ref'] for r in evaluation['evidence_bindings']],
            'receipt_refs':['protocol:W03-source-correction-receipt'],'residue_refs':['protocol:deferred-owner-decision:R08']},
            [{'relation_kind_ref':'relation.uses-tool','direction':'source','counterpart_kind':'tool','counterpart_ref':request['tool_ref']}])
        action['owner_ref']=request['principal_ref'];validate_record(action,'agent-action')
        action_ref=identity(action)+'@candidate.1';records[action_ref]=action
        output=artifact('generated-output','registered-interface-bytes',{'generator_ref':generator_ref,
            'input_refs':[original_ref,manifest['work_ref']],'output_digest':'sha256:'+manifest['output_source_sha256'],
            'reproducibility_receipt_ref':'protocol:W03-source-correction-receipt'},
            [{'relation_kind_ref':'relation.produces','direction':'target','counterpart_kind':'agent-action','counterpart_ref':identity(action)}])
        output_ref=identity(output)+'@candidate.1';records[output_ref]=output
        evidence=artifact('evidence-set','registered-interface-behavior',{'coverage_statement':'All seven declared engineering obligations, actual source bytes and default authority regression.',
            'item_refs':['protocol:W03-'+name for name in EXPECTED_CHECKS],
            'source_refs':[original_ref,successor_ref],'limitations':['Candidate host selections only','No actual owner response','No general API or Product SLA']},
            [{'relation_kind_ref':'relation.member-of','direction':'source','counterpart_kind':'project','counterpart_ref':SCOPE}])
        evidence_ref=identity(evidence)+'@candidate.1';records[evidence_ref]=evidence
        assessment=artifact('work-outcome-assessment','registered-interface-satisfaction',{
            'subject_ref':manifest['work_ref'],'expected_result_ref':'protocol:W03-declared-satisfaction-obligations',
            'observed_result_ref':'protocol:W03-independent-behavior-results','disposition':self.assessment['disposition'],
            'evidence_refs':[evidence_ref],'gap_refs':[] if self.assessment['disposition']=='supported' else ['protocol:W03-failed-satisfaction-checks']},
            [{'relation_kind_ref':'relation.evaluates','direction':'source','counterpart_kind':'work','counterpart_ref':identity(work)}])
        assessment_ref=identity(assessment)+'@candidate.1';records[assessment_ref]=assessment
        capability=read(ROOT/'authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/product-capability.json')
        capability_ref=CAPABILITY+'@foundation.1';records[capability_ref]=capability
        project=read(ROOT/'authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/project.json')
        project_ref=SCOPE+'@'+project['version'];records[project_ref]=project
        work_postimage=copy.deepcopy(work)
        work_postimage['payload']['completion_state']='candidate-assessed'
        work_postimage['payload']['output_refs']=[successor_ref,generator_ref,output_ref,evidence_ref,assessment_ref,action_ref]
        work_postimage['evidence_refs']=[evidence_ref]
        work_postimage_ref=identity(work)+'@assessed-candidate.1'
        validate_record(work_postimage,'work');records[work_postimage_ref]=work_postimage
        relations=[typed_relation('registered-evaluator-succession','relation.successor-of',successor_ref,original_ref,records,{'succession_effect':'candidate-explicit-host-interface-registry-successor'}),
            typed_relation('registered-evaluator-realization','relation.realizes',successor_ref,capability_ref,records,{'realization_role':'candidate-bounded-registered-actor-evaluation','exact_target_version_ref':capability_ref}),
            typed_relation('source-corrector-realization','relation.realizes',generator_ref,capability_ref,records,{'realization_role':'candidate-exact-bounded-source-generation','exact_target_version_ref':capability_ref}),
            typed_relation('source-correction-production','relation.produces',action_ref,output_ref,records,{'action_receipt_ref':'protocol:W03-source-correction-receipt','production_role':'exact-candidate-implementation-bytes','output_posture':'candidate-unadmitted'}),
            typed_relation('engineering-outcome-evaluation','relation.evaluates',assessment_ref,manifest['work_ref'],records,{'evaluation_role':'scoped-machine-satisfaction-assessment','evaluation_purpose':'independent-exact-behavior-versus-declared-engineering-obligations'}),
            typed_relation('engineering-evidence-membership','relation.member-of',evidence_ref,project_ref,records,{'membership_role':'scoped-engineering-verification-evidence'}),
            typed_relation('engineering-work-succession','relation.successor-of',work_postimage_ref,manifest['work_ref'],records,{'succession_effect':'candidate-exact-output-and-assessment-recording'})]
        candidates={'implementation':successor,'source-corrector':generator,'agent-action':action,'generated-output':output,'evidence-set':evidence,'work-outcome-assessment':assessment,'work':work_postimage}
        candidate_refs={'implementation':successor_ref,'agent-action':action_ref,'generated-output':output_ref,
            'evidence-set':evidence_ref,'work-outcome-assessment':assessment_ref,'work':work_postimage_ref}
        candidate_refs[identity(generator)]=generator_ref
        for relation in relations:candidate_refs[identity(relation)]=identity(relation)+'@candidate.1'
        for kind,value in candidates.items():(self.output_root/(kind+'.json')).write_bytes(encoded(value))
        for value in relations:(self.output_root/(value['node_id'].split(':')[-1]+'.json')).write_bytes(encoded(value))
        review={'authority_effect':'none','actual_owner_outcome':None,'source_profile_cut':'decision:0075',
            'requested_effect':'prepare-exact-candidate-review-members','canonical_effects_applied':0,
            'implementation_code_sha256':manifest['output_source_sha256'],
            'member_records':[{'kind':v['kind'],'identity_ref':identity(v),
                'version_ref':candidate_refs.get(identity(v),candidate_refs.get(v['kind'])),
                'record_sha256':byte_sha(encoded(v))} for v in list(candidates.values())+relations],
            'work_effect':{'from_version_ref':manifest['work_ref'],'to_version_ref':work_postimage_ref,
                'proposed_completion_state':'candidate-assessed','actual_owner_outcome':None,'applied':False},
            'assessment_disposition':self.assessment['disposition'],'promotion_eligible':self.assessment['disposition']=='supported',
            'owner_decision_status':'deferred-R08','exclusions':['private Session memory','canonical admission','live activation','unselected records']}
        (self.output_root/'review-effects.json').write_bytes(encoded(review))
        return {'candidates':candidates,'relations':relations,'review':review,'events':self.events,
                'state':self.state,'assessment':self.assessment,'receipt':self.receipt}
