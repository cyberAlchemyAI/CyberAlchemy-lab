"""Join current source, prospective cores and independent failure assessment axes.

The adapter stages a candidate ChangeProposal. Its host must select this exact
module and the qualified evaluator before using it in a public dispatcher.
"""
import copy
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
RULES=HERE.parent/'failure-assessment-rules-v9'
RULE_SOURCE='f05cd62d53dbde6a68534ba921c6e4573df51fe2e9eae9c62e1c22a20420f710'
RULE_PROOF='4cc372baeb697b20ae8974cfeaaa5a97f5ce50a8d948656518ddbc871a1eaf6e'
CURRENT=('admitted-current','local-admitted-current')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def require(value,reason):
    if not value:raise ValueError(reason)


def evaluator():
    source=RULES/'source-manifest.json';proof=RULES/'receipts/proof-0001.json'
    require(sha(source.read_bytes())==RULE_SOURCE and sha(proof.read_bytes())==RULE_PROOF,
            'independently selected failure assessment evaluator differs')
    document=json.loads(proof.read_bytes())
    require(document['schema_version']=='lab-failure-assessment-primitive-proof/v1-candidate'
            and document['result']=='PASS' and document['actual_cases']==75
            and document['actual_terminal_exit_code']==0,'complete actual evaluator proof required')
    for row in json.loads(source.read_bytes())['files']:
        require(sha((ROOT/row['path']).read_bytes())==row['sha256'],'failure assessment evaluator input changed')
    name='_cal_public_failure_preparation_rules_v9'
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,RULES/'__init__.py',submodule_search_locations=[str(RULES)])
        package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    module=importlib.import_module(name+'.engine')
    require(Path(module.__file__).resolve()==RULES/'engine.py','unselected evaluator module')
    return module, module.AssessmentRules(RULE_SOURCE)


PUBLIC_REF_FIELDS=('scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256')


def public_artifact_ref(header):
    """Project a validated candidate header into the original public reference.

    Contract-selection metadata stays on its independently validated proposal
    target. It is not a sixth public reference axis. Unknown fields are refused.
    """
    require(type(header) is dict and set(header) in
            (set(PUBLIC_REF_FIELDS),set(PUBLIC_REF_FIELDS)|{'candidate_contract_binding'}),
            'undeclared artifact reference field or missing public field')
    if 'candidate_contract_binding' in header:
        binding=header['candidate_contract_binding']
        require(type(binding) is dict and set(binding)=={'ref','sha256'},
                'candidate contract binding shape differs')
    return {key:copy.deepcopy(header[key]) for key in PUBLIC_REF_FIELDS}


class RuleFailure(Exception):
    """Known rule outcome after final current source/transport verification."""
    def __init__(self,code,message,evidence):
        super().__init__(message)
        self.code=code;self.message=message;self.evidence=copy.deepcopy(evidence)


class FailurePreparation:
    def __init__(self,host,routing_binding,host_source_binding):
        self.host=host
        require(type(host_source_binding) is dict and set(host_source_binding)=={'path','sha256'},
                'independently selected host source binding required')
        service_module=sys.modules.get(type(host).__module__)
        require(service_module is not None and getattr(service_module,'Service',None) is type(host),
                'actual selected Service instance required')
        service_path=Path(service_module.__file__).resolve()
        require(service_path.parent.parent==HERE.parent and service_path.name=='service.py',
                'foreign Service source refused')
        host_source=service_path.parent/'source-manifest.json'
        require(host_source_binding=={'path':str(host_source.relative_to(ROOT)),
                                      'sha256':sha(host_source.read_bytes())},'host source selection differs')
        package=type(host).__module__.rsplit('.',1)[0]
        self.guard_module=importlib.import_module(package+'.guard')
        host_manifest=self.guard_module.verify(host_source_binding['sha256'])
        selected_inputs=[]
        for path in (Path(__file__).resolve(),HERE/'routing.schema.json'):
            require(not path.is_symlink() and not any(parent.is_symlink() for parent in path.parents),
                    'failure assessment source selection contains a symbolic link')
            selected_inputs.append({'path':str(path.relative_to(ROOT)),
                                    'sha256':sha(path.read_bytes())})
        require(all(row in host_manifest['files'] for row in selected_inputs),
                'failure assessment composition or routing schema is outside the selected host source')
        self.host_source_binding=copy.deepcopy(host_source_binding)
        self.P=importlib.import_module(package+'.protocol')
        self.M=importlib.import_module(package+'.artifact_model')
        self.H=importlib.import_module(package+'.handlers')
        self.vault=host.vault;self.schemas=host.schemas;self.rule_module,self.rules=evaluator()
        auth=importlib.import_module(package+'.auth')
        peer=importlib.import_module(package+'.machine_transport')
        require(type(host.channel) in (auth.ReaderChannel,peer.MachinePeer),
                'failure assessment host requires an actual selected authenticated channel')
        self.routing_binding=copy.deepcopy(routing_binding)
        policy=host.channel.policy_guard()
        require(policy.get('failure_control',{}).get('routing_binding')==routing_binding,
                'routing is not independently selected by the signed current host policy')
        self.raw=self.vault.object_read(routing_binding)
        self.routing=self.P.frame_parse(self.raw)
        from jsonschema import Draft202012Validator,FormatChecker
        schema=self.P.frame_parse((HERE/'routing.schema.json').read_bytes())
        require(Draft202012Validator(schema,registry=self.schemas.registry,
                                     format_checker=FormatChecker()).is_valid(self.routing),
                'failure assessment routing schema differs')
        require(set(self.routing)=={'schema_version','scope_ref','source_cut','proposal_binding',
                                   'rule_source_binding','rule_proof_binding','axis_basis_binding','incident_threshold_binding','record_basis',
                                   'authority_effect','actual_owner_outcome'},'closed failure assessment routing required')
        require(self.routing['schema_version']=='lab-failure-preparation-routing/v1-candidate'
                and self.routing['authority_effect']=='none' and self.routing['actual_owner_outcome'] is None,
                'failure assessment routing cannot supply authority')
        require(self.routing['record_basis']=='current-plus-exact-prospective-postimage',
                'failure assessment record basis is undeclared')
        require(self.routing['rule_source_binding']=={'ref':str((RULES/'source-manifest.json').relative_to(ROOT)),'sha256':RULE_SOURCE}
                and self.routing['rule_proof_binding']=={'ref':str((RULES/'receipts/proof-0001.json').relative_to(ROOT)),'sha256':RULE_PROOF},
                'failure assessment rule selection differs')

    def preflight(self,message,outer,idempotency_key):
        self.guard_module.verify(self.host_source_binding['sha256'])
        self.schemas.guard();evaluator()
        context=self.host.channel.guard();policy=self.host.channel.policy_guard()
        require('failure.assess' in policy['allowed_operations'],
                'current independently selected grant does not permit failure assessment preparation')
        require(context['limits']['max_actions']>=1,'failure assessment preparation has no action budget')
        actor={key:context[key] for key in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')}
        actor['role_assignment_refs']=context['role_assignment_bindings']
        require(message['actor']==actor,'failure assessment Actor differs from actual trusted transport')
        require(message['source_cut']==outer==self.routing['source_cut']==self.H.cut(self.host.handlers.view),
                'failure assessment routing and request do not select the exact current cut')
        require(policy.get('failure_control',{}).get('routing_binding')==self.routing_binding
                and self.vault.object_read(self.routing_binding)==self.raw,'failure assessment routing selection or bytes changed')
        proposal_raw=self.vault.object_read(self.routing['proposal_binding'])
        proposal=self.P.frame_parse(proposal_raw)
        require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:change-proposal:v1-candidate',proposal),
                'original ChangeProposal contract required')
        require(proposal['actor']==actor and proposal['idempotency_key']==idempotency_key
                and proposal['base_cut']==outer and proposal['scope_ref']==self.routing['scope_ref'],
                'proposal Actor, key, scope or original source cut differs')
        self.host.candidates.preflight(proposal,outer)
        require(message['incident_threshold_binding']==self.routing['incident_threshold_binding'],
                'request threshold differs from independently selected routing')
        basis_raw=self.vault.material(self.routing['axis_basis_binding'])
        basis=self.P.frame_parse(basis_raw)
        self.rules.valid('urn:cyberalchemy-lab:failure-assessment-basis:v1-candidate',basis)
        require(basis['scope_ref']==proposal['scope_ref'] and basis['source_cut']==outer
                and basis['assessment_binding']==message['assessment_candidate_binding'],
                'axis basis does not select this exact scope, cut and candidate')
        for item in message['evidence_bindings']:
            self.vault.material(item)
        wanted=message['assessment_candidate_binding']
        matches=[target for target in proposal['targets']
                 if target['operation']!='withdraw' and target['artifact']['carrier_ref']=='cal.artifact-type.failure-assessment/v1'
                 and {'ref':target['content']['content_ref'],'sha256':target['content']['byte_sha256']}==wanted]
        require(len(matches)==1,'exact independently selected assignment target missing or duplicated')
        return proposal_raw,proposal,matches[0]

    def prepare(self,message,request,outer,idempotency_key):
        guarded=importlib.import_module(type(self.host).__module__.rsplit('.',1)[0]+'.guarded_candidate')
        pending=None
        with guarded.calculation(self.host) as writer:
            try:
                result=self._prepare(message,request,outer,idempotency_key,writer)
            except RuleFailure as error:
                # Publish a known rule outcome only after full source exit checks.
                pending=error
        if pending is not None:raise pending
        return result

    def _prepare(self,message,request,outer,idempotency_key,writer):
        proposal_raw,proposal,target=self.preflight(message,outer,idempotency_key)
        # The original validator independently compares every prospective schema,
        # original body/header and stable Decision core before rule evaluation.
        validation,details=self.host.candidates.validate(proposal,request,outer,proposal_raw,evidence_writer=writer)
        require(validation['result']!='fail' and len(details['cores'])==len(proposal['targets']),
                'failure assessment prospective schema/core closure failed')
        scope=proposal['scope_ref'];records={};headers={};scope_dispositions=[]
        view=self.host.handlers.selected_view
        # Candidate validation has compared every exact current predecessor.
        # Superseded/withdrawn preimages cannot remain active in the postimage.
        removed={entry['predecessor']['version_ref'] for entry in proposal['targets']
                 if entry['operation'] in ('revise','withdraw')}
        with self.M.model_read_batch(view):
            for subject in view.subjects.values():
                if subject['effective_state'] not in CURRENT or subject['version_ref'] in removed:continue
                header=self.M.artifact_ref(view,subject)
                if header['scope_ref']!=scope:continue
                headers[header['version_ref']]=header
                if subject['category'] not in ('artifact-instance','typed-relation'):continue
                raw=self.M.record_bytes(view,subject)[0];body=self.P.frame_parse(raw)
                if all(key in body for key in ('node_id','kind','scope_ref')) and body['scope_ref']!=scope:
                    scope_dispositions.append({'artifact':public_artifact_ref(header),
                        'record_scope_ref':body['scope_ref'],
                        'disposition':'outside-requested-record-scope','record_bytes_rewritten':False})
                    continue
                records[header['version_ref']]=self.rule_module.Record(public_artifact_ref(header),raw)
        for prospective in proposal['targets']:
            if prospective['operation']=='withdraw':continue
            header=prospective['artifact']
            require(header['scope_ref']==scope,'prospective failure header scope differs')
            require(header['version_ref'] not in records,'duplicate prospective failure revision')
            raw=self.vault.material({'ref':prospective['content']['content_ref'],
                                     'sha256':prospective['content']['byte_sha256']})
            records[header['version_ref']]=self.rule_module.Record(public_artifact_ref(header),raw)
            headers[header['version_ref']]=header
        raw=self.vault.material(message['assessment_candidate_binding'])
        candidate=self.rule_module.Record(public_artifact_ref(target['artifact']),raw)
        require(candidate.header['byte_sha256']==sha(raw),'assessment candidate bytes differ')
        records.pop(candidate.header['version_ref'])
        for header in [message['occurrence'],message['mode_assignment'],*message['cause_hypothesis_refs']]:
            require(header['version_ref'] in records and records[header['version_ref']].header==header,
                    'failure request exact current/prospective header unresolved or differs')
        threshold=self.routing['incident_threshold_binding']
        require(message['incident_threshold_binding']==threshold,'threshold differs from current independently selected routing')
        basis_binding=self.routing['axis_basis_binding']
        basis_raw=self.vault.material(basis_binding)
        material_bytes={item['ref']:self.vault.material(item) for item in message['evidence_bindings']}
        if threshold is not None:material_bytes[threshold['ref']]=self.vault.material(threshold)
        checked=self.rules.evaluate(list(records.values()),message,candidate,
                    basis_binding=basis_binding,basis_raw=basis_raw,
                    material_bytes=material_bytes,selected_threshold_binding=threshold)
        checked['record_basis']='current-plus-exact-prospective-postimage'
        checked['complete_postimage_record_refs']=sorted(records)
        checked['scope_dispositions']=scope_dispositions
        checked['repository_scope_ref']=scope
        checked['removed_current_preimage_refs']=sorted(removed)
        checked['original_source_cut']=copy.deepcopy(outer)
        evidence=writer.object(self.P.source.encoded(checked))
        self.preflight(message,outer,idempotency_key)
        require(self.host.handlers.current(),'failure assessment source changed during preparation')
        if checked['result']!='pass':
            raise RuleFailure('closure-missing' if checked['result']=='not-evaluable' else 'conflict',
                              'Exact failure assessment rules did not pass; inspect the recorded evidence.',
                              details['evidence']+[evidence])
        # Return the exact selected original contract. A ProposalReview would be
        # a different domain result and cannot substitute for this ChangeProposal.
        return copy.deepcopy(proposal),details['evidence']+[evidence]
