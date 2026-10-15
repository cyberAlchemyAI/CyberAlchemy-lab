"""Join trusted current source, prospective cores and closed classification rules.

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
RULES=HERE.parent/'classification-rules-v3'
RULE_SOURCE='39db151070cfd1b99578e62dc083078ef9f97412c3358e3bb6e7fca4243d088e'
RULE_PROOF='a0aa676599e80d4bc7992c36e98f557874f88bfd49fdf8f0b51e9b403782fd7b'
CURRENT=('admitted-current','local-admitted-current')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def require(value,reason):
    if not value:raise ValueError(reason)


def evaluator():
    source=RULES/'source-manifest.json';proof=RULES/'receipts/proof-0001.json'
    require(sha(source.read_bytes())==RULE_SOURCE and sha(proof.read_bytes())==RULE_PROOF,
            'independently selected classification evaluator differs')
    document=json.loads(proof.read_bytes())
    require(document['schema_version']=='lab-classification-rule-primitive-proof/v1-candidate'
            and document['result']=='PASS' and document['actual_cases']==35
            and document['actual_terminal_exit_code']==0,'complete actual evaluator proof required')
    for row in json.loads(source.read_bytes())['files']:
        require(sha((ROOT/row['path']).read_bytes())==row['sha256'],'classification evaluator input changed')
    name='_cal_public_classification_preparation_rules_v3'
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,RULES/'__init__.py',submodule_search_locations=[str(RULES)])
        package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    module=importlib.import_module(name+'.engine')
    require(Path(module.__file__).resolve()==RULES/'engine.py','unselected evaluator module')
    return module


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


def record_in_scope(body, header, scope):
    """Select from the verified repository cut without relabeling node scope."""
    require(type(body) is dict and type(header) is dict, 'explicit original body and header required')
    if header['scope_ref'] != scope:
        return False
    if all(key in body for key in ('node_id', 'kind', 'scope_ref')):
        return body['scope_ref'] == scope
    # Other carriers use their declared identity witness during evaluation.
    # A Product domain scope object is never treated as this control selector.
    return True


class RuleFailure(Exception):
    """Known rule outcome after final current source/transport verification."""
    def __init__(self,code,message,evidence):
        super().__init__(message)
        self.code=code;self.message=message;self.evidence=copy.deepcopy(evidence)


class ClassificationPreparation:
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
                    'classification source selection contains a symbolic link')
            selected_inputs.append({'path':str(path.relative_to(ROOT)),
                                    'sha256':sha(path.read_bytes())})
        require(all(row in host_manifest['files'] for row in selected_inputs),
                'classification composition or routing schema is outside the selected host source')
        self.host_source_binding=copy.deepcopy(host_source_binding)
        self.P=importlib.import_module(package+'.protocol')
        self.M=importlib.import_module(package+'.artifact_model')
        self.H=importlib.import_module(package+'.handlers')
        self.vault=host.vault;self.schemas=host.schemas;self.rules=evaluator()
        auth=importlib.import_module(package+'.auth')
        peer=importlib.import_module(package+'.machine_transport')
        require(type(host.channel) in (auth.ReaderChannel,peer.MachinePeer),
                'classification host requires an actual selected authenticated channel')
        self.routing_binding=copy.deepcopy(routing_binding)
        policy=host.channel.policy_guard()
        require(policy.get('classification_control',{}).get('routing_binding')==routing_binding,
                'routing is not independently selected by the signed current host policy')
        self.raw=self.vault.object_read(routing_binding)
        self.routing=self.P.frame_parse(self.raw)
        from jsonschema import Draft202012Validator,FormatChecker
        schema=self.P.frame_parse((HERE/'routing.schema.json').read_bytes())
        require(Draft202012Validator(schema,registry=self.schemas.registry,
                                     format_checker=FormatChecker()).is_valid(self.routing),
                'classification routing schema differs')
        require(set(self.routing)=={'schema_version','scope_ref','source_cut','proposal_binding',
                                   'rule_source_binding','rule_proof_binding','record_basis',
                                   'authority_effect','actual_owner_outcome'},'closed classification routing required')
        require(self.routing['schema_version']=='lab-classification-preparation-routing/v1-candidate'
                and self.routing['authority_effect']=='none' and self.routing['actual_owner_outcome'] is None,
                'classification routing cannot supply authority')
        require(self.routing['record_basis']=='current-plus-exact-prospective-postimage',
                'classification record basis is undeclared')
        require(self.routing['rule_source_binding']=={'ref':str((RULES/'source-manifest.json').relative_to(ROOT)),'sha256':RULE_SOURCE}
                and self.routing['rule_proof_binding']=={'ref':str((RULES/'receipts/proof-0001.json').relative_to(ROOT)),'sha256':RULE_PROOF},
                'classification rule selection differs')

    def preflight(self,message,outer,idempotency_key):
        self.guard_module.verify(self.host_source_binding['sha256'])
        self.schemas.guard();evaluator()
        context=self.host.channel.guard();policy=self.host.channel.policy_guard()
        require('classification.prepare' in policy['allowed_operations'],
                'current independently selected grant does not permit classification preparation')
        require(context['limits']['max_actions']>=1,'classification preparation has no action budget')
        actor={key:context[key] for key in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')}
        actor['role_assignment_refs']=context['role_assignment_bindings']
        require(message['actor']==actor,'classification Actor differs from actual trusted transport')
        require(message['source_cut']==outer==self.routing['source_cut']==self.H.cut(self.host.handlers.view),
                'classification routing and request do not select the exact current cut')
        require(policy.get('classification_control',{}).get('routing_binding')==self.routing_binding
                and self.vault.object_read(self.routing_binding)==self.raw,'classification routing selection or bytes changed')
        proposal_raw=self.vault.object_read(self.routing['proposal_binding'])
        proposal=self.P.frame_parse(proposal_raw)
        require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:change-proposal:v1-candidate',proposal),
                'original ChangeProposal contract required')
        require(proposal['actor']==actor and proposal['idempotency_key']==idempotency_key
                and proposal['base_cut']==outer and proposal['scope_ref']==self.routing['scope_ref'],
                'proposal Actor, key, scope or original source cut differs')
        self.host.candidates.preflight(proposal,outer)
        wanted=message['assignment_candidate_binding']
        matches=[target for target in proposal['targets']
                 if target['operation']!='withdraw' and target['artifact']['carrier_ref']=='cal.artifact-type.classification-assignment/v1'
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
        # Complete exact cores establish a known structural refusal. Let the
        # original calculation exit guards run and commit its failed report
        # before delivering the known error. Incomplete-core failures retain
        # their original uncertain/pending handling.
        if validation['result']=='fail' and len(details['cores'])==len(proposal['targets']):
            raise RuleFailure('invalid-contract',
                'Exact prospective structural validation did not pass; inspect retained evidence.',
                details['evidence'])
        require(validation['result']!='fail' and len(details['cores'])==len(proposal['targets']),
                'classification prospective schema/core closure failed')
        scope=proposal['scope_ref'];records={};headers={};scope_dispositions=[]
        view=self.host.handlers.selected_view
        with self.M.model_read_batch(view):
            for subject in view.subjects.values():
                if subject['effective_state'] not in CURRENT:continue
                header=self.M.artifact_ref(view,subject)
                if header['scope_ref']!=scope:continue
                raw=self.M.record_bytes(view,subject)[0];body=self.P.frame_parse(raw)
                headers[header['version_ref']]=header
                # Every current domain instance is retained. Catalog declarations
                # join when explicitly requested, with their own carrier witness.
                requested={message[key]['version_ref'] for key in ('subject','scheme','value')}
                if subject['category'] not in ('artifact-instance','typed-relation') and header['version_ref'] not in requested:continue
                if all(key in body for key in ('node_id','kind','scope_ref')):
                    if not record_in_scope(body,header,scope):
                        scope_dispositions.append({'artifact':public_artifact_ref(header),
                            'record_scope_ref':body['scope_ref'],
                            'disposition':'outside-requested-record-scope',
                            'record_bytes_rewritten':False})
                        continue
                    records[header['version_ref']]=self.rules.ExactRecord(header['version_ref'],raw,header['byte_sha256'])
                else:
                    records[header['version_ref']]=self.rules.TypedRecord(header['version_ref'],raw,header['byte_sha256'],public_artifact_ref(header))
        for proposed in proposal['targets']:
            previous=proposed['predecessor']
            if previous is not None:
                require(previous['version_ref'] in headers and headers[previous['version_ref']]==previous,
                        'classification transition predecessor is outside the complete selected current set')
                records.pop(previous['version_ref']);headers.pop(previous['version_ref'])
            if proposed['operation']=='withdraw':continue
            header=proposed['artifact'];raw=self.vault.material({'ref':proposed['content']['content_ref'],
                                                               'sha256':proposed['content']['byte_sha256']})
            body=self.P.frame_parse(raw)
            require(header['scope_ref']==scope,'prospective classification header scope differs')
            require(header['version_ref'] not in records,'prospective classification revision duplicates current source')
            if all(key in body for key in ('node_id','kind','scope_ref')):
                require(body['scope_ref']==scope,'prospective classification scope differs')
                records[header['version_ref']]=self.rules.ExactRecord(header['version_ref'],raw,header['byte_sha256'])
            else:
                records[header['version_ref']]=self.rules.TypedRecord(header['version_ref'],raw,header['byte_sha256'],public_artifact_ref(header))
            headers[header['version_ref']]=header
        candidate_raw=self.vault.material(message['assignment_candidate_binding'])
        candidate=self.P.frame_parse(candidate_raw)
        candidate_header=target['artifact']
        require(candidate_header['byte_sha256']==sha(candidate_raw),'assignment original bytes differ')
        records.pop(candidate_header['version_ref'])
        for key in ('subject','scheme','value'):
            require(message[key]['version_ref'] in records,'classification requested revision is unresolved or outside record scope')
            require(public_artifact_ref(headers[message[key]['version_ref']])==message[key],
                    'classification requested exact header differs from selected postimage')
        material_bytes={item['ref']:self.vault.material(item) for item in message['basis_bindings']}
        selected=self.rules.ExactRecords(records.values(),scope)
        existing=sorted(reference for reference,row in records.items()
                        if row.semantic_kind()=='classification-assignment')
        checked=self.rules.evaluate(selected,subject_ref=message['subject']['version_ref'],
                                    scheme_ref=message['scheme']['version_ref'],value_ref=message['value']['version_ref'],
                                    axis_ref=message['axis_ref'],candidate=candidate,basis_bindings=message['basis_bindings'],
                                    material_bytes=material_bytes,existing_assignment_refs=existing)
        checked['complete_postimage_assignment_refs']=existing
        checked['scope_dispositions']=scope_dispositions
        checked['repository_scope_ref']=scope
        checked['record_basis']='current-plus-exact-prospective-postimage'
        checked['original_source_cut']=copy.deepcopy(outer)
        evidence=writer.object(self.P.source.encoded(checked))
        self.preflight(message,outer,idempotency_key)
        require(self.host.handlers.current(),'classification source changed during preparation')
        if checked['result']!='pass':
            raise RuleFailure('closure-missing' if checked['result']=='not-evaluable' else 'conflict',
                              'Exact classification rules did not pass; inspect the recorded evidence.',
                              details['evidence']+[evidence])
        # Return the exact selected original contract. A ProposalReview would be
        # a different domain result and cannot substitute for this ChangeProposal.
        return copy.deepcopy(proposal),details['evidence']+[evidence]
