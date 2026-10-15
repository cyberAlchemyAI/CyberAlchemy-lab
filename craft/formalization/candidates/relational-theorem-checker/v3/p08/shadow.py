"""Fresh proposal plus independent successor registration before local commit."""
from pathlib import Path
import copy
import hashlib
import json
import threading
import time
import uuid
from ..p03.context import BASE,ROOT,C,check,binding,require
from ..p07.api import OwnedQualifier
from .metadata import HERE,Store,validate,immutable,Cancelled,Exhausted,Reconciliation
from .mapped import MappedQualifier

def outcome(status,reason='',**extra):
    return validate('application',{'schema':'relational.shadow-application/v3','status':status,'reason':str(reason),
            'application_authorized':False,'authority_effect':'none',**extra})

class DeadlineCancel:
    def __init__(self,deadline,external):self.deadline=deadline;self.external=external
    def is_set(self):return time.monotonic()>self.deadline or bool(self.external is not None and self.external.is_set())
    def check(self):
        if time.monotonic()>self.deadline:raise Exhausted('Whole publication deadline.')
        if self.external is not None and self.external.is_set():raise Cancelled('Explicit publication cancellation.')

class ShadowContext:
    """Opaque preparation handles live only in this mediated context instance."""
    def __init__(self,policy,run_root=None):
        self.policy=copy.deepcopy(policy);C.validate('resource-policy',self.policy)
        self.api=OwnedQualifier(run_root or BASE/'p07/consumer-runs/P08',self.policy)
        self._permits={};self._consumed=set();self._lock=threading.Lock()
        self._sources=[]
        for name in ['P04','P07']:
            receipt=C.decode((BASE/(name.lower()+'/task-acceptance.json')).read_bytes())
            require(receipt['result']=='accepted','unaccepted shadow prerequisite '+name)
            # Gate the current trusted runtime source against accepted expected
            # bytes. Heavy request/proof processing remains inside supervision.
            for ref in receipt['artifacts']+receipt['inputs']:
                path=Path(ref['path'])
                if path.suffix in ['.py','.lean'] or path.name.endswith('.schema.json'):
                    check(ref);self._sources.append(ref)
        self._sources += [binding(HERE/'shadow.py'),binding(HERE/'metadata.py')]
        self._sources += [binding(p) for p in HERE.glob('*.schema.json')]
        self._sources += [binding(HERE/'mapped.py'),binding(HERE/'mapped_worker.py')]
        self.mapped=MappedQualifier(self.policy,self._sources)

    def assert_current(self):
        for ref in self._sources:check(ref)

    def _checked_request(self,answer):
        q=answer['qualified_result'];payload=check(q['payload'])
        path=payload.parent/'request.json';require(path.is_relative_to(self.api.supervisor.run_root),'checked request outside owned qualification')
        raw=path.read_bytes();require(len(raw)<=self.policy['work_limits']['input_bytes'],'checked request byte ceiling')
        request=C.decode(raw);C.validate('request',request)
        require(C.identity(request)==q['request_identity'],'checked source request identity differs')
        return request,binding(path)

    def _identity_request(self,template,baseline):
        request=copy.deepcopy(template)
        request['operation']='qualify'
        request['proposal']={'schema':'relational.recursive-proposal/v2','proposal_id':'shadow-independent-registration-'+C.identity(baseline)[:24],
                             'baseline_identity':C.identity(baseline),'before':copy.deepcopy(baseline),'after':copy.deepcopy(baseline)}
        return request

    def _evidence(self,answer,request_ref):
        q=answer['qualified_result'];completion=C.decode(check(answer['completion']).read_bytes())
        return {'proof_mode':'fresh-independent-successor-registration','request':request_ref,
                'qualification':completion['result'],'completion':answer['completion'],'owned_run':answer['owned_run'],
                'required_inventory':[o['id'] for o in C.required_inventory('register')],'fresh_at_creation':True}

    def _qualify(self,raw,cancel):
        cancel.check();self.assert_current()
        answer=self.api.qualify(raw,cancel=cancel)
        if answer['status']!='qualified-candidate':
            if time.monotonic()>cancel.deadline:raise Exhausted('Whole publication deadline during fresh checking.')
            if cancel.external is not None and cancel.external.is_set():raise Cancelled('Cancelled during fresh checking.')
            return answer
        cancel.check();require(self.api.live_event(answer['qualified_result']),'fresh owned completion missing')
        return answer

    def bootstrap(self,root,identity_request,*,cancel=None):
        """Register genesis independently; no unqualified baseline is admitted."""
        started=time.monotonic();bounded=DeadlineCancel(started+self.policy['run_seconds'],cancel)
        try:
            root=Path(root).resolve();require(root.is_relative_to(HERE/'stores') and not root.exists(),'bootstrap requires a new owned P08 store')
            request=copy.deepcopy(identity_request)
            require(request['resource_policy']==self.policy,'bootstrap resource policy mismatch')
            require(request['proposal']['before']==request['proposal']['after'],'bootstrap requires an identity-extension request')
            answer=self._qualify(json.dumps(request,ensure_ascii=False,allow_nan=False).encode(),bounded)
            if answer['status']!='qualified-candidate':return outcome(answer['status'],answer.get('reason','bootstrap qualification refused'))
            checked,request_ref=self._checked_request(answer);evidence=self._evidence(answer,request_ref)
            def gate():
                bounded.check();self.assert_current()
                require(self.api.live_event(answer['qualified_result']),'genesis fresh event unavailable')
                require(C.identity(checked['proposal']['before'])==answer['qualified_result']['manifest']['identity']['baseline'],'genesis baseline mismatch')
            store=Store.initialize(root,checked['proposal']['after'],seed_evidence=evidence,seed_gate=gate)
            return outcome('initialized-candidate-shadow',store=str(store.root.relative_to(ROOT)),head=store.head(),qualification=answer['completion'],seconds=time.monotonic()-started)
        except Cancelled as e:return outcome('cancelled',e)
        except Exhausted as e:return outcome('unknown-resource',e)
        except Exception as e:return outcome('invalid',str(e).splitlines()[0])

    def prepare(self,review_ref,raw,store,*,mappings=(),cancel=None):
        started=time.monotonic();bounded=DeadlineCancel(started+self.policy['run_seconds'],cancel)
        try:
            require(isinstance(raw,bytes) and len(raw)<=self.policy['work_limits']['input_bytes'],'raw request byte ceiling')
            require(store.kind=='fixture-shadow','IO probe cannot authorize theorem-qualified publication')
            review_path=check(review_ref);require(review_path.parent==store.root/'reviews','review from another store')
            review=validate('review',C.decode(review_path.read_bytes()))
            require(review['store_id']==store.id and review['assessment']=='reviewed-candidate','candidate review not accepted')
            require(hashlib.sha256(raw).hexdigest()==review['request_bytes_sha256'],'reviewed request/condition/context bytes changed')
            current=store.recover(deadline=bounded.deadline,cancel=bounded)
            if current['status']!='head-current':return outcome('reconciliation-required',current.get('reason','store requires reconciliation'))
            if current['head']!=review['expected_head']:return outcome('stale-head','Reviewed generation is no longer current.')
            require(len(mappings)<=self.policy['work_limits']['stress_candidates'],'mapped context work ceiling')
            mappings=copy.deepcopy(list(mappings))
            require(C.identity(mappings)==review['mappings_identity'],'reviewed condition/interpretation/mapping bytes changed')
            require([C.identity(m['baseline']['context']) for m in mappings]==review['mapped_contexts'],'reviewed mapped contexts changed')
            proposal=self._qualify(raw,bounded)
            if proposal['status']!='qualified-candidate':return outcome(proposal['status'],proposal.get('reason','proposal refused'))
            request,request_ref=self._checked_request(proposal)
            require(C.identity(request)==review['request_identity'] and C.identity(request['proposal'])==review['proposal_identity'],'reviewed proposal identity changed')
            require(C.identity(request['proposal']['before'])==review['expected_head']['baseline_identity'],'before baseline differs from reviewed head')
            require(C.identity(request['proposal']['after'])==review['successor_identity'],'reviewed successor changed')
            require(C.identity(request['proposal']['before']['context'])==review['context_identity'],'reviewed condition/context identity changed')
            mapped_checks=[]
            for mapped_request in mappings:
                bounded.check();answer=self.mapped.qualify(mapped_request,cancel=bounded)
                if answer['status']!='fresh-mapped-candidate':return outcome(answer['status'],answer.get('reason','mapped qualification refused'))
                inspection=answer['value']['inspection']
                require(inspection['verdict']=='yes','required mapped relation did not check yes')
                if inspection['variant']=='inheritance':
                    require(inspection['condition_status']=='yes','required condition is unknown, false or conflicting')
                    require(not inspection['active_conflicts'],'required active norm context has a conflict')
                mapped_checks.append(answer)
            registration_request=self._identity_request(request,request['proposal']['after'])
            registration=self._qualify(json.dumps(registration_request,ensure_ascii=False,allow_nan=False).encode(),bounded)
            if registration['status']!='qualified-candidate':return outcome(registration['status'],registration.get('reason','successor independent registration refused'))
            reg_checked,reg_request_ref=self._checked_request(registration)
            require(reg_checked['proposal']['before']==reg_checked['proposal']['after']==request['proposal']['after'],'successor independently checked a different baseline')
            handle=uuid.uuid4().hex
            permit={'store_id':store.id,'review_ref':copy.deepcopy(review_ref),'review':copy.deepcopy(review),
                    'request':request,'request_ref':request_ref,'proposal':proposal,'registration':registration,
                    'registration_request':reg_request_ref,'started':started,'cancel':bounded,'handle':handle}
            permit.update(mappings=mappings,mapped_checks=mapped_checks)
            with self._lock:self._permits[handle]=permit
            return outcome('prepared-candidate-shadow',handle=handle,expected_head=review['expected_head'],
                           proposal_qualification=proposal['completion'],successor_registration=registration['completion'],
                           mapped_checks=[a['completion'] for a in mapped_checks],contexts={'horn':review['context_identity'],'mapped':review['mapped_contexts']},
                           seconds=time.monotonic()-started)
        except Cancelled as e:return outcome('cancelled',e)
        except Exhausted as e:return outcome('unknown-resource',e)
        except Exception as e:return outcome('invalid',str(e).splitlines()[0])

    def _guard(self,permit,store):
        permit['cancel'].check();self.assert_current();check(permit['review_ref'])
        require(permit['store_id']==store.id,'prepared application belongs to another store')
        for key in ['proposal','registration']:
            require(self.api.live_event(permit[key]['qualified_result']),'live '+key+' qualification unavailable')
        proposal=permit['proposal']['qualified_result'];reg=permit['registration']['qualified_result']
        request=permit['request'];review=permit['review']
        require(C.identity(permit['mappings'])==review['mappings_identity'],'prepared mappings changed')
        for request_map,answer in zip(permit['mappings'],permit['mapped_checks']):
            require(self.mapped.live_event(answer),'fresh mapped event unavailable')
            require(answer['value']['request_identity']==C.identity(request_map),'prepared mapped request changed')
        require(proposal['request_identity']==C.identity(request)==review['request_identity'],'prepared proposal changed')
        require(C.identity(request['proposal']['after'])==reg['manifest']['identity']['baseline']==review['successor_identity'],'exact successor registration mismatch')
        for q in [proposal,reg]:
            require(q['manifest']['obligations']==[o['id'] for o in C.required_inventory('rule-only')],'fixed complete proof inventory changed')
            require(q['application_authorized'] is False,'qualification escalated authority')

    def commit(self,handle,store):
        with self._lock:permit=self._permits.pop(handle,None)
        if permit is None:return outcome('invalid','No unconsumed live preparation in this context; saved receipts cannot authorize apply.')
        try:
            self._guard(permit,store)
            q=permit['proposal']['qualified_result'];reg_answer=permit['registration']
            with self._lock:
                ids=(q['run_id'],reg_answer['qualified_result']['run_id'])
                require(not any(id in self._consumed for id in ids),'fresh application already consumed')
                self._consumed.update(ids)
            completion=C.decode(check(permit['proposal']['completion']).read_bytes())
            result=store._publish(before=permit['review']['expected_head'],after_baseline=permit['request']['proposal']['after'],
                                  registration_evidence=self._evidence(reg_answer,permit['registration_request']),
                                  review=permit['review_ref'],proposal_qualification=completion['result'],fresh_run_id=q['run_id'],
                                  mapped_checks=[a['completion'] for a in permit['mapped_checks']],
                                  gate=lambda:self._guard(permit,store),deadline=permit['cancel'].deadline,cancel=permit['cancel'])
            return outcome(result['status'],before=result.get('before'),after=result.get('after'),head=result.get('head'),
                           transaction=result.get('transaction'),seconds=time.monotonic()-permit['started'])
        except Exception as e:
            recovered=store.recover()
            if recovered['status']=='reconciliation-required':return outcome('reconciliation-required',str(e).splitlines()[0])
            committed=store.committed_run(permit['proposal']['qualified_result']['run_id'])
            if committed:
                return outcome('applied-candidate-shadow','Recovered a durable commit after a postcommit exception.',before=committed['before_head'],after=committed['after_head'],transaction=committed,head=recovered['head'],seconds=time.monotonic()-permit['started'])
            status='cancelled' if isinstance(e,Cancelled) else 'unknown-resource' if isinstance(e,Exhausted) else 'invalid'
            return outcome(status,str(e).splitlines()[0])

    def apply(self,review_ref,raw,store,*,mappings=(),cancel=None):
        prepared=self.prepare(review_ref,raw,store,mappings=mappings,cancel=cancel)
        return self.commit(prepared['handle'],store) if prepared['status']=='prepared-candidate-shadow' else prepared

def apply(review,request,store,context,**kwargs):return context.apply(review,request,store,**kwargs)
