"""Exact Session participation and independently provisioned host permission.

This module performs preflight only. No plan/result creates an Agent, grants an
action, admits a record, restores memory or substitutes for dispatch checks.
"""
from __future__ import annotations
import copy
import base64
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import re
from typing import Callable
from jsonschema import Draft202012Validator


class EligibilityFault(ValueError):
    pass


def require(value, reason):
    if not value: raise EligibilityFault(reason)


def digest(raw): return hashlib.sha256(raw).hexdigest()


def instant(value):
    require(isinstance(value,str),'timestamp must be a string')
    try:
        result=datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError as error:raise EligibilityFault('invalid timestamp') from error
    require(result.tzinfo is not None,'timestamp must name its timezone')
    return result.astimezone(timezone.utc)


def parse(raw):
    def pairs(rows):
        value={}
        for key,item in rows:
            require(key not in value,'duplicate source JSON key');value[key]=item
        return value
    require(type(raw) is bytes and len(raw)<=4*1024*1024,'bounded original source bytes required')
    try:return json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(EligibilityFault('nonfinite source JSON')))
    except (ValueError,UnicodeError) as error:raise EligibilityFault('source JSON cannot be verified') from error


def header(value):
    require(type(value) is dict and set(value)=={'scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256'},'closed artifact reference required')
    require(all(type(v) is str and v for v in value.values()),'artifact reference strings required')
    require(re.fullmatch('[a-f0-9]{64}',value['byte_sha256']) is not None,'original artifact byte hash required')
    require(value['version_ref'].startswith(value['identity_ref']+'@'),'exact artifact identity/version binding required')
    return copy.deepcopy(value)


def no_private_memory(value, *, blank_session_policy=False):
    """Schema-valid Session metadata may declare empty memory and expiry only."""
    permitted={'selected_input_refs':[],'working_record_refs':[],'unresolved_questions':[],'expires_with_session':True}
    def visit(item,path=()):
        if isinstance(item,dict):
            for key,child in item.items():
                if key=='session_memory':
                    require(blank_session_policy and path==('payload',) and type(child) is dict and child==permitted and child.get('expires_with_session') is True,'Session memory is private to its live Session')
                    continue
                if key in ['short_memory','private_key','private_credentials','access_token','refresh_token','password','secret']:
                    require(child in [None,'',[],{}],'private material is not eligible context')
                visit(child,(*path,key))
        elif isinstance(item,list):
            for child in item:visit(child,path)
        elif isinstance(item,str):
            require(re.search(r'-----BEGIN (?:[A-Z0-9 ]* )?PRIVATE KEY-----',item) is None,'private key is not eligible context')
    visit(value)


@dataclass(frozen=True)
class SchemaSpec:
    carrier_ref: str
    semantic_kind: str
    identity_field: str
    original_schema: bytes
    expected_sha256: str
    version_binding_rule: str = 'body-version-equals-reference'

    def validator(self):
        require(self.version_binding_rule in ['body-version-equals-reference','verified-source-revision'],'unknown carrier revision binding rule')
        require(digest(self.original_schema)==self.expected_sha256,'selected schema bytes changed')
        value=parse(self.original_schema)
        def closed(item):
            if isinstance(item,dict):
                require('$dynamicRef' not in item,'dynamic schema reference closure is unsupported')
                if '$ref' in item:
                    ref=item['$ref'];require(type(ref) is str and ref.startswith('#/$defs/') and '%' not in ref,'external schema reference closure must be resolved explicitly')
                    target=value
                    for part in ref[2:].split('/'):
                        part=part.replace('~1','/').replace('~0','~');require(type(target) is dict and part in target,'local schema reference unresolved');target=target[part]
                for child in item.values():closed(child)
            elif isinstance(item,list):
                for child in item:closed(child)
        closed(value);Draft202012Validator.check_schema(value)
        return Draft202012Validator(value)


@dataclass(frozen=True)
class SignedRevisionWitness:
    """Original selected source witness supplied by a verified host reader.

    Parsing this witness proves byte/selector agreement only. The source guard
    must independently verify the signed branch. This is not a signature token.
    """
    source_cut: dict
    artifact_ref: dict
    enclosing_original: bytes
    enclosing_sha256: str
    selector: str
    encoding: str


@dataclass(frozen=True)
class SourceRecord:
    artifact: dict
    original: bytes
    posture: str
    source_ref: str
    revision_witness: SignedRevisionWitness | None = None


class ExactSources:
    """Host selected source cut and original byte closure, outside request JSON."""
    def __init__(self, scope_ref, source_cut, records, schemas, current_guard):
        self.scope_ref=scope_ref;self.source_cut=copy.deepcopy(source_cut)
        self.schemas={s.carrier_ref:s for s in schemas};self.validators={k:s.validator() for k,s in self.schemas.items()}
        require(len(self.schemas)==len(schemas),'duplicate source carrier selection')
        require(0<len(records)<=512,'source record count budget exceeded')
        self.records={};self.current_guard=current_guard
        for record in records:
            require(isinstance(record,SourceRecord),'trusted selected original record required')
            ref=header(record.artifact);require(ref['version_ref'] not in self.records,'duplicate source revision')
            self.records[ref['version_ref']]=SourceRecord(ref,record.original,record.posture,record.source_ref,copy.deepcopy(record.revision_witness))
        self.guard()

    def guard(self):
        require(self.current_guard() is True,'source cut or byte closure is no longer current')

    def get(self,ref,carrier=None):
        self.guard();wanted=header(ref)
        require(wanted['scope_ref']==self.scope_ref,'source scope differs')
        record=self.records.get(wanted['version_ref'])
        require(record is not None and record.artifact==wanted,'exact original source reference unresolved')
        require(record.posture in ['admitted-current','local-admitted-current','isolated-candidate-current'],'source revision is not current')
        require(carrier is None or wanted['carrier_ref']==carrier,'source carrier differs')
        spec=self.schemas.get(wanted['carrier_ref']);require(spec is not None,'selected carrier contract unavailable')
        require(digest(record.original)==wanted['byte_sha256'],'selected original source bytes changed')
        body=parse(record.original)
        require(self.validators[wanted['carrier_ref']].is_valid(body),'selected body violates exact carrier schema')
        require(body.get(spec.identity_field)==wanted['identity_ref'],'source body identity differs')
        body_kind=body.get('kind',body.get('classification',{}).get('semantic_kind'))
        require(body_kind is None or body_kind==spec.semantic_kind,'source semantic kind differs')
        if spec.version_binding_rule=='verified-source-revision':
            witness=record.revision_witness
            require(isinstance(witness,SignedRevisionWitness),'verified source revision witness required')
            require(witness.source_cut==self.source_cut and header(witness.artifact_ref)==wanted,'signed revision witness cut or reference differs')
            require(type(witness.enclosing_original) is bytes and len(witness.enclosing_original)<=4*1024*1024 and digest(witness.enclosing_original)==witness.enclosing_sha256,'enclosing original source bytes differ')
            if witness.encoding=='original-file-bytes':
                require(witness.selector=='' and witness.enclosing_original==record.original,'whole-file revision witness differs')
            elif witness.encoding=='inherited-canonical-json-of-selected-original-value':
                require(type(witness.selector) is str and witness.selector.startswith('/') and '%' not in witness.selector,'explicit inherited JSON pointer required')
                selected=parse(witness.enclosing_original)
                for part in witness.selector[1:].split('/'):
                    require(re.search('~(?![01])',part) is None,'invalid inherited pointer escape')
                    part=part.replace('~1','/').replace('~0','~')
                    if type(selected) is list:
                        require(re.fullmatch('0|[1-9][0-9]*',part) is not None and int(part)<len(selected),'inherited pointer index unavailable');selected=selected[int(part)]
                    else:
                        require(type(selected) is dict and part in selected,'inherited pointer member unavailable');selected=selected[part]
                raw=(json.dumps(selected,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
                require(raw==record.original,'inherited selected value bytes differ')
            elif witness.encoding=='base64-original-json/v1-candidate':
                match=re.fullmatch(r'/proposal/targets/(0|[1-9][0-9]*)/content/data',witness.selector)
                require(match is not None,'explicit original-content revision pointer required')
                tx=parse(witness.enclosing_original)
                families={'lab-runtime-original-json-proposal/v1-candidate':'lab-runtime-original-json-transaction/v1-candidate',
                    'lab-runtime-reviewed-original-json-proposal/v1-candidate':'lab-runtime-reviewed-original-json-transaction/v1-candidate',
                    'lab-runtime-original-json-proposal/v2-candidate':'lab-runtime-original-json-transaction/v2-candidate',
                    'lab-runtime-reviewed-original-json-proposal/v2-candidate':'lab-runtime-reviewed-original-json-transaction/v2-candidate'}
                proposal=tx.get('proposal',{})
                require(proposal.get('schema_version') in families and tx.get('schema_version')==families[proposal['schema_version']],
                    'explicit original-content transaction family required')
                index=int(match.group(1));targets=proposal.get('targets',[])
                require(index<len(targets),'original-content revision target absent');target=targets[index]
                require(target.get('version_ref')==wanted['version_ref'] and target.get('carrier_ref')==wanted['carrier_ref']
                    and proposal.get('scope_ref')==wanted['scope_ref'],'original-content revision target differs')
                entry=target.get('content');require(type(entry) is dict and set(entry)==set('schema_version content_ref media_type byte_sha256 size_bytes encoding data semantic_binding'.split()),
                    'closed original-content revision entry required')
                require(entry['schema_version']=='lab-artifact-content-entry/v1-candidate' and entry['encoding']=='base64'
                    and entry['media_type']=='application/json' and entry['semantic_binding'] is None,'original-content revision profile differs')
                try:raw=base64.b64decode(entry['data'],validate=True)
                except (ValueError,TypeError) as error:raise EligibilityFault('invalid original-content revision bytes') from error
                require(base64.b64encode(raw).decode()==entry['data'] and type(entry['size_bytes']) is int
                    and entry['size_bytes']==len(raw)<=1048576,'original-content revision encoding or size differs')
                require(raw==record.original and digest(raw)==entry['byte_sha256']==wanted['byte_sha256']
                    and entry['content_ref']=='runtime-content:sha256:'+wanted['byte_sha256'],'original-content revision bytes differ')
                structural=lambda value:json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
                require(structural(parse(raw))==structural(target.get('record')),'original-content parsed revision differs')
            else:require(False,'unknown signed revision witness encoding')
        elif 'version' in body:require(wanted['version_ref']==wanted['identity_ref']+'@'+body['version'],'source body version differs')
        no_private_memory(body,blank_session_policy=spec.semantic_kind=='agent-session')
        return record,body

    def resolve(self,ref,carrier=None):
        require(type(ref) is str and ref,'exact reference string required')
        matches=[r for r in self.records.values() if (r.artifact['version_ref']==ref or r.artifact['identity_ref']==ref)
            and r.posture in ['admitted-current','local-admitted-current','isolated-candidate-current']]
        require(len(matches)==1,'source reference missing or ambiguous')
        return self.get(matches[0].artifact,carrier)


@dataclass(frozen=True)
class SessionPermission:
    """Current host permission; never instantiate this from a public message."""
    principal_ref: str
    scope_ref: str
    operations: frozenset[str]
    not_before: str
    expires_at: str
    periods: dict
    active_policy_refs: frozenset[str]
    reached_stop_conditions: frozenset[str]
    revoked_refs: frozenset[str]
    evidence_bindings: tuple
    max_actions: int
    max_input_bytes: int
    max_output_bytes: int
    max_session_seconds: int
    implementation_bindings: dict
    protocol_bindings: dict


class SessionEligibility:
    def __init__(self,sources,permission_reader,permission_guard,*,clock=lambda:datetime.now(timezone.utc)):
        require(isinstance(sources,ExactSources),'exact host source resolver required')
        self.sources=sources;self.permission_reader=permission_reader;self.permission_guard=permission_guard;self.clock=clock

    def _start(self,message,verified_actor,operation):
        require(message['actor']==verified_actor,'public Actor claims differ from authenticated transport')
        require(message['source_cut']==self.sources.source_cut,'Session request cut differs from selected source')
        self.sources.guard();p=copy.deepcopy(self.permission_reader())
        require(isinstance(p,SessionPermission),'independently provisioned host Session permission absent')
        require(self.permission_guard(p) is True and 0<len(p.evidence_bindings)<=32,'host permission evidence cannot be verified')
        for b in p.evidence_bindings:
            require(type(b) is dict and set(b)=={'ref','sha256'} and type(b['ref']) is str and b['ref'] and type(b['sha256']) is str and re.fullmatch('[a-f0-9]{64}',b['sha256']), 'exact host permission evidence binding required')
        require(p.principal_ref==verified_actor['principal_ref'] and p.scope_ref==self.sources.scope_ref,'host principal or scope differs')
        require(operation in p.operations,'host does not permit this Session operation')
        now=self.clock();require(now.tzinfo is not None,'host clock must name timezone')
        require(instant(p.not_before)<=now<instant(p.expires_at),'host Session permission expired or not yet effective')
        require(type(p.max_session_seconds) is int and 1<=p.max_session_seconds<=86400,'host Session lifetime budget invalid')
        budget=message['budget'];require(set(budget)=={'max_actions','max_input_bytes','max_output_bytes','deadline'},'closed Session request budget required')
        for key in ['max_actions','max_input_bytes','max_output_bytes']:
            require(type(budget[key]) is int and budget[key]>=0,'Session budget must contain nonnegative integers')
            require(type(getattr(p,key)) is int and getattr(p,key)>=0 and budget[key]<=getattr(p,key),'Session budget exceeds current host limits')
        require(operation!='context.get' or budget['max_actions']==0,'context read action budget must be zero')
        require(operation!='session.open' or budget['max_actions']>=1,'Session creation needs a positive independently provisioned action budget')
        expires=min(instant(p.expires_at),instant(budget['deadline']),now+timedelta(seconds=p.max_session_seconds))
        require(now<expires,'strictest request deadline expired')
        principal,body=self.sources.resolve(verified_actor['principal_ref'],'cal.artifact-type.principal/v1')
        require(body['payload']['status']=='active','recognized principal is inactive')
        require(not {principal.artifact['identity_ref'],principal.artifact['version_ref']} & p.revoked_refs,'principal is revoked')
        return p,now,expires,[principal]

    def _fact(self,ref,carrier,p,selected):
        record,body=self.sources.get(ref,carrier)
        require(not {record.artifact['identity_ref'],record.artifact['version_ref']} & p.revoked_refs,'selected participation source is revoked')
        selected.append(record);return record,body

    def _period(self,ref,p,now):
        require(ref in p.periods,'Assignment period has no explicit host resolution')
        period=p.periods[ref]
        require(type(period) in [list,tuple] and len(period)==2,'closed absolute Assignment period required')
        start,end=map(instant,period);require(start<end and start<=now<end,'Assignment period expired or not yet effective')
        return end

    def participation(self,assignment,profile,work,coordination,verified_actor,p,now,selected,*,fresh_instance_ref=None):
        a,assignment_body=self._fact(assignment,'cal.artifact-type.agent-assignment/v1',p,selected)
        pr,profile_body=self._fact(profile,'cal.artifact-type.agent-profile/v1',p,selected)
        w,work_body=self._fact(work,'cal.artifact-type.work/v1',p,selected)
        c,coord=self._fact(coordination,'cal.artifact-type.coordination-context/v2',p,selected)
        ap=assignment_body['payload'];wp=work_body['payload'];pp=profile_body['payload']
        principal,principal_body=self.sources.resolve(verified_actor['principal_ref'],'cal.artifact-type.principal/v1')
        require(ap['owner_ref'] in [principal.artifact['identity_ref'],principal.artifact['version_ref']],'Assignment owner differs from authenticated principal')
        require(ap['eligible_agent_ref'] in [pr.artifact['identity_ref'],pr.artifact['version_ref'],fresh_instance_ref] and ap['eligible_agent_ref'] is not None,'Assignment is for another Profile or ephemeral instance')
        require(ap['work_ref'] in [w.artifact['identity_ref'],w.artifact['version_ref']],'Assignment Work differs')
        require(ap['project_ref']==wp['project_ref']==self.sources.scope_ref,'Assignment and Work Project differ')
        project,_=self.sources.resolve(self.sources.scope_ref,'cal.artifact-type.project-identity/v1');selected.append(project)
        intent,intent_body=self.sources.resolve(ap['intent_ref'],'cal.artifact-type.intent/v1');selected.append(intent)
        for relation in work_body['relation_refs']:
            require(relation=={'relation_kind_ref':'relation.member-of','direction':'source','counterpart_kind':'project','counterpart_ref':wp['project_ref']},'Work membership declaration differs from its Project binding')
        for relation in assignment_body['relation_refs']:
            if relation['relation_kind_ref'] in ['relation.member-of','relation.addresses-intent']:
                expected_kind='project' if relation['relation_kind_ref']=='relation.member-of' else 'intent'
                target=project if expected_kind=='project' else intent
                require(relation['direction']=='source' and relation['counterpart_kind']==expected_kind and relation['counterpart_ref'] in [target.artifact['identity_ref'],target.artifact['version_ref']],'Assignment declared relationship differs from participation binding')
        require(coord['project_ref']==self.sources.scope_ref and coord['lifecycle_state']=='active','Coordination Context is inactive or for another Project')
        consumers={verified_actor['principal_ref'],pr.artifact['identity_ref'],pr.artifact['version_ref'],verified_actor.get('agent_instance_ref')}
        require(consumers & set(coord['consumer_refs']),'Coordination Context does not select this consumer')
        require(set(ap['expected_output_refs'])==set(wp['output_refs']),'Assignment expected outputs differ from declared Work outputs')
        for input_ref in wp['input_refs']:
            if input_ref.startswith('protocol:'):self._protocol(input_ref,p,'input')
            else:
                record,_=self.sources.resolve(input_ref);selected.append(record)
        product,_=self.sources.resolve(coord['product_ref'],'cal.artifact-type.product-identity/v2');selected.append(product)
        require(coord['goal_ref'] is not None and coord['goal_ref'] in wp['goal_refs'],'Coordination Context must select one explicit Work Goal')
        goal,_=self.sources.resolve(coord['goal_ref'],'cal.artifact-type.goal/v1');selected.append(goal)
        for ref in wp['goal_refs']:
            row,_=self.sources.resolve(ref,'cal.artifact-type.goal/v1');selected.append(row)
        require(set(coord['source_policy_refs'])<=p.active_policy_refs and set(pp['policy_refs'])<=p.active_policy_refs,'Profile or Coordination source Policy unresolved')
        for policy_ref in set(coord['source_policy_refs'])|set(pp['policy_refs']):
            if policy_ref.startswith('protocol:'):self._protocol(policy_ref,p,'policy')
            else:
                record,_=self.sources.resolve(policy_ref);require(record.artifact['carrier_ref'] in ['cal.artifact-type.policy/v1','cal.artifact-type.policy/v2'],'source Policy carrier differs');selected.append(record)
        require(not (set(ap['stop_conditions'])|set(pp['stop_conditions'])) & p.reached_stop_conditions,'Assignment or Profile stop condition reached')
        require({'context-view','ontology-view'}<=set(pp['allowed_input_kinds']),'Profile does not accept delivered Context and Ontology Views')
        expiry=self._period(ap['period'],p,now)
        return {'assignment':a,'profile':pr,'work':w,'coordination_context':c,'goal':goal,'product':product,'project':project,'expires':expiry,'profile_body':profile_body}

    def _protocol(self,ref,p,kind):
        selected=p.protocol_bindings.get(ref)
        require(ref.startswith('protocol:') and type(selected) is dict and set(selected)=={'kind','binding'} and selected['kind']==kind,'protocol reference has no exact declared kind/byte binding')
        b=selected['binding'];require(type(b) is dict and set(b)=={'ref','sha256'} and b['ref'] and type(b['sha256']) is str and re.fullmatch('[a-f0-9]{64}',b['sha256']), 'protocol original byte binding invalid')
        return selected

    def _finish(self,p,now,expires,selected,plan):
        self.sources.guard();later=self.permission_reader()
        require(not any({r.artifact['identity_ref'],r.artifact['version_ref']} & p.revoked_refs for r in selected),'participation source is revoked')
        require(later==p and self.permission_guard(later) is True,'host permission changed during preflight')
        require(self.clock()<expires,'eligibility expired during source/permission checks')
        return {**plan,'expires_at':expires.isoformat(),'source_cut':copy.deepcopy(self.sources.source_cut),
            'selected_original_bindings':[{'ref':r.source_ref,'sha256':digest(r.original)} for r in {r.artifact['version_ref']:r for r in selected}.values()],
            'authority_effect':'none','permission_result_is_dispatch_token':False,'Agent_created':False,'Session_created':False,
            'durable_continuity_source':'project-state-via-context-and-ontology-views','memory_persistence_allowed':False}

    def context_plan(self,message,verified_actor,profile):
        p,now,expires,selected=self._start(message,verified_actor,'context.get')
        plan=self.participation(message['assignment'],profile,message['work'],message['coordination_context'],verified_actor,p,now,selected)
        require(message['freshness_requirement']=='current','historical context cannot authorize a fresh operational Session')
        coord_body=parse(plan['coordination_context'].original)
        require(message['intended_use'] in coord_body['intended_uses'],'intended use is outside Coordination Context')
        require(not set(message['exclusions']) & {v for r in selected for v in [r.artifact['identity_ref'],r.artifact['version_ref']]},'request excludes required participation closure')
        for ref in message['selectors']:
            row,body=self.sources.get(ref)
            require(ref['identity_ref'] not in message['exclusions'] and ref['version_ref'] not in message['exclusions'],'requested selector is excluded')
            selected.append(row)
        return self._finish(p,now,min(expires,plan['expires']),selected,plan)

    def open_plan(self,message,verified_actor,delivery_reader,*,fresh_instance_ref=None):
        p,now,expires,selected=self._start(message,verified_actor,'session.open')
        memory_policy=message['memory_policy']
        require(type(memory_policy) is dict and set(memory_policy)=={'persistence_allowed','expires_with_session'} and memory_policy['persistence_allowed'] is False and memory_policy['expires_with_session'] is True,'Machine Agent memory must expire with its Session')
        delivery=delivery_reader(message['context_delivery_binding'])
        require(type(delivery) is dict and delivery['verified_original_binding']==message['context_delivery_binding'],'exact delivered context binding unresolved')
        require(delivery['posture']=='ready' and delivery['scope_enforced'] is True and delivery['freshness']=='current' and delivery['source_cut']==self.sources.source_cut,'delivered Context/Ontology Views are not current and scope enforced')
        require(delivery['assignment']==message['assignment'],'delivered context Assignment differs')
        require(delivery['authenticated_principal_ref']==verified_actor['principal_ref'],'delivered context belongs to another principal')
        require(delivery['authority_envelope_binding']==message['authority_envelope_binding'],'current independently provisioned authority envelope differs')
        expires=min(expires,instant(delivery['expires_at']))
        plan=self.participation(message['assignment'],message['profile'],delivery['work'],delivery['coordination_context'],verified_actor,p,now,selected,fresh_instance_ref=fresh_instance_ref)
        implementation,ib=self._fact(message['implementation'],'cal.artifact-type.implementation/v1',p,selected)
        selected_impl=p.implementation_bindings.get(implementation.artifact['version_ref'])
        require(type(selected_impl) is dict and set(selected_impl)=={'entrypoint_ref','environment_contract_ref','evidence_binding'},'selected Implementation has no independent code/environment binding')
        require(ib['payload']['execution_entrypoint_ref']==selected_impl['entrypoint_ref'] and ib['payload']['environment_contract_ref']==selected_impl['environment_contract_ref'],'Implementation source or environment differs from host selection')
        b=selected_impl['evidence_binding'];require(type(b) is dict and set(b)=={'ref','sha256'} and type(b['sha256']) is str and re.fullmatch('[a-f0-9]{64}',b['sha256']), 'Implementation evidence byte binding invalid')
        declared=[r['counterpart_ref'] for r in plan['profile_body']['relation_refs'] if r['relation_kind_ref']=='relation.has-capability' and r['direction']=='source' and r['counterpart_kind']=='agent-capability']
        declared_caps={self.sources.resolve(ref,'cal.artifact-type.agent-capability/v1')[0].artifact['version_ref'] for ref in declared}
        supplied=[]
        for ref in message['capabilities']:
            cap,cb=self._fact(ref,'cal.artifact-type.agent-capability/v1',p,selected)
            require(cap.artifact['version_ref'] in declared_caps,'Agent Capability is not declared by selected Profile')
            require(implementation.artifact['version_ref'] in cb['payload']['implementation_refs'],'Agent Capability has no exact selected Implementation binding')
            for field,kind in [('input_contract_refs','input-contract'),('output_contract_refs','output-contract'),('evidence_contract_refs','evidence-contract'),('failure_mode_refs','failure-boundary')]:
                for target in cb['payload'][field]:
                    if target.startswith('protocol:'):self._protocol(target,p,kind)
                    else:
                        resolved,_=self.sources.resolve(target)
                        allowed=['cal.artifact-type.failure-mode/v1'] if field=='failure_mode_refs' else ['cal.artifact-type.contract/v1','cal.artifact-type.schema/v1']
                        require(resolved.artifact['carrier_ref'] in allowed,'Agent Capability contract/failure reference kind differs');selected.append(resolved)
            supplied.append(cap.artifact['version_ref'])
        require(len(supplied)==len(set(supplied)),'duplicate Agent Capability selection')
        require(now<expires,'delivered context expired')
        return self._finish(p,now,min(expires,plan['expires']),selected,{**plan,'implementation':implementation,'agent_capability_refs':supplied})
