"""Executable full C07/T33/T32 composition over a single outer visibility record.

Native generations are already committed owned provisional representations.
Only the held-inode outer descriptor adopts all exact targets/consequences.
Uncertainty never redispatches either original producer or owner message.
"""
import base64,copy,fcntl,os
from dataclasses import asdict
from datetime import datetime,timezone
from pathlib import Path
from .contracts import Refusal,Uncertain,need,closed,sha,compact,parse,relative,flat,pin,verify_files,typed_records,validate_descriptor,validate_native_selection
from .materializer import render_bundle
from .owner_history import verify_committed_response
from .receipt_store import ReceiptStore
from .origins import require_original

class NativeMixedPublisher:
    def __init__(self,*,store,replay_store,boundary,original,promotion,ingress,parent,source_selection,
                 selections,identity_path,identity_sha256,authority,owner_selection,trust,
                 response_raw,native_store,native_factory,native_selection,output_roles,extension_packages,mirrors,expected_review_sha256):
        # All objects/config are private independently captured Root inputs.
        # A public message cannot construct or replace any producer/resolver.
        need(type(store)is ReceiptStore and store.boundary is boundary,'actual selected private receipt store required')
        need(type(replay_store)is ReceiptStore and replay_store.boundary is boundary and replay_store.root!=store.root
            and not replay_store.root.is_relative_to(store.root)and not store.root.is_relative_to(replay_store.root),'independently selected persistent replay custody must be separate')
        need(trust.usage=='actual-owner','actual independently installed owner context required')
        self.store=store;self.replay_store=replay_store;self.boundary=boundary;self.original=original;self.promotion=promotion;self.ingress=ingress
        self.parent=parent;self.source_selection=source_selection;self.selections=copy.deepcopy(selections)
        self.identity_path=identity_path;self.identity_sha256=identity_sha256;self.authority=authority
        self.owner_selection=owner_selection;self.trust=trust;self.response_raw=response_raw;self.response=ingress.parse(response_raw)
        self.native_store=native_store;self.native_factory=native_factory;self.native_selection=copy.deepcopy(native_selection)
        need(type(output_roles)is tuple and output_roles and len(set(output_roles))==len(output_roles),'independent exact typed output roles required')
        self.output_roles=output_roles;self.extensions=copy.deepcopy(extension_packages);self.mirrors=copy.deepcopy(mirrors)
        self.expected_review_sha256=expected_review_sha256;self.pending=False;self.completed=False
        self.original_inputs=compact({'selections':self.selections,'mirrors':self.mirrors,'identity_sha256':identity_sha256,
            'expected_review_sha256':expected_review_sha256,'authority':authority.core(),'owner_selection':asdict(owner_selection),
            'response_sha256':sha(response_raw),'native_selection':self.native_selection,'output_roles':output_roles,'extensions':self.extensions})
        boundary.guard()
    def guard(self):
        self.boundary.require_held();self.store.check();self.replay_store.check()
        require_original(self.boundary.software,self.original,'repository-publisher')
        require_original(self.boundary.software,self.promotion,'repository-promotion')
        require_original(self.boundary.software,self.ingress,'owner-ingress')
        native_module=__import__('sys').modules[type(self.native_factory).__module__]
        require_original(self.boundary.software,native_module,'native-factory')
        need(self.original.SCHEMA==Path(self.original.__file__).parents[1]/'schemas/promotion.schema.json','original materializer schema origin differs')
        need(self.original_inputs==compact({'selections':self.selections,'mirrors':self.mirrors,'identity_sha256':self.identity_sha256,
            'expected_review_sha256':self.expected_review_sha256,'authority':self.authority.core(),'owner_selection':asdict(self.owner_selection),
            'response_sha256':sha(self.response_raw),'native_selection':self.native_selection,'output_roles':self.output_roles,'extensions':self.extensions}),'private selected publisher inputs changed')
        need(self.response==self.ingress.parse(self.response_raw),'owner response object changed')
        self.boundary.software.function(self.ingress.verify_for_publication)
        self.boundary.software.function(self.promotion.prepare_promotion)
        self.boundary.software.function(self.original.verify_generator)
        if self.native_store is not None:self.boundary.software.function(self.native_store.snapshot_original_outcome)
    def _prepare(self):
        self.guard();need(self.native_store is not None,'cold-only reader cannot prepare new native publication')
        prepared=self.promotion.prepare_promotion(self.parent,self.source_selection,self.selections,self.identity_path,
            self.identity_sha256,self.authority,extension_packages=self.extensions,mirrors=self.mirrors)
        need(sha(compact(prepared['review']))==self.expected_review_sha256,'independently selected exact review differs')
        selected_owner=getattr(self.boundary.owner_guard,'__self__',None)
        from .boundary import OwnerPublicationGuard
        need(type(selected_owner)is OwnerPublicationGuard and selected_owner.review==prepared['review'] and selected_owner.response==self.response
            and selected_owner.ingress is self.ingress and selected_owner.selection==self.owner_selection and selected_owner.trust==self.trust,'boundary owner guard must cover exact actual inputs')
        verified=self.ingress.verify_for_publication(self.response,prepared['review'],self.owner_selection,self.trust)
        need(verified['usage']=='actual-owner' and verified['selected_outcome']==self.ingress.ADMIT,'actual positive owner disposition absent')
        files,manifest=render_bundle(prepared,self.response,self.authority,original=self.original,ingress=self.ingress,
            owner_selection=self.owner_selection,trust=self.trust)
        native=self.native_store.snapshot_original_outcome()
        closed(native,('schema_version','head_binding','head_raw','generation','event_files','projection_raw','projection_sha256','semantic_events','governance_events','causal_witnesses','commit_receipts','typed_Artifacts_constructed','Project_history_committed','authority_effect'))
        need(native['schema_version']=='lab-selected-native-original-outcome/v1-candidate' and native['authority_effect']=='none'
            and native['typed_Artifacts_constructed']is False and native['Project_history_committed']is False,'actual native originals required, no inferred typed projection')
        need(sha(native['head_raw'])==native['head_binding']['sha256'] and sha(native['projection_raw'])==native['projection_sha256'],'actual original native byte correspondence differs')
        validate_native_selection(self.native_selection,native,prepared['review'],self.boundary.control)
        head=parse(native['head_raw']);need(head['generation']==native['generation'] and head['files']=={p:r['sha256'] for p,r in native['event_files'].items()},'actual native head/member correspondence differs')
        record_set=typed_records(files,manifest,prepared['review'],self.original)
        coupled={'repository/'+relative(p):raw for p,raw in files.items()}
        coupled['native/HEAD.original.json']=native['head_raw'];coupled['native/projection.original.json']=native['projection_raw']
        for path,row in native['event_files'].items():
            closed(row,('raw','sha256'));need(sha(row['raw'])==row['sha256'],'original native event changed');coupled['native/events/'+relative(path)]=row['raw']
        coupled['private-owner-response.original.json']=self.response_raw
        coupled['native/recovery.original.json']=compact({'causal_witnesses':native['causal_witnesses'],'commit_receipts':native['commit_receipts']})
        coupled['typed-record-set.json']=compact(record_set)
        descriptor={'schema_version':'lab-coupled-native-original-publication/v1-candidate','bundle_id':flat(prepared['review']['bundle_id']),
            'repository_bundle_binding':{'ref':'repository/bundle.json','sha256':sha(files['bundle.json'])},
            'review_sha256':self.expected_review_sha256,'owner_response_sha256':sha(self.response_raw),'owner_verification':verified,
            'owner_verified_at':datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'native_store_root':str(self.native_store.store_root),'native_store_identity':list(self.native_store.committed.identity),
            'source_binding':self.boundary.control['source_binding'],'profile_binding':self.boundary.control['profile_binding'],
            'source_cut':self.boundary.control['source_cut'],'principal_ref':self.boundary.control['principal_ref'],'work_ref':self.boundary.control['work_ref'],
            'native_store_ref':self.boundary.control['native_store_ref'],'native_branch_ref':self.boundary.control['native_branch_ref'],
            'native_head_binding':native['head_binding'],'native_generation':native['generation'],'native_event_files':head['files'],
            'native_projection_sha256':native['projection_sha256'],'files':{p:sha(raw)for p,raw in sorted(coupled.items())},
            'commit_point':'descriptor-bound-coupled-original-byte-record','inner_native_commit_is_outer_visibility':False,
            'automatic_retry':False,'runtime_activations':0,'external_effect_refs':[],'authority_effect':'none'}
        validate_descriptor(descriptor);verify_files(coupled,descriptor['files']);self.guard()
        return prepared,coupled,descriptor
    def publish(self):
        need(not self.pending and not self.completed,'attempt pending/completed; cold inspect instead of redispatch')
        with self.boundary.hold():
            lock=self.store.lock();replay_lock=None;parent_lock=None
            try:
                replay_lock=self.replay_store.lock()
                # Parent read locks preserve original source selection through
                # preparation, owner replay reservation and outer commit.
                parent_lock=os.open(self.parent.path/'.writer.lock',os.O_RDONLY|os.O_NOFOLLOW)
                fcntl.flock(parent_lock,fcntl.LOCK_SH|fcntl.LOCK_NB)
                prepared,files,descriptor=self._prepare();name=descriptor['bundle_id'];raw=compact(descriptor)
                descriptor_pin=sha(raw);stage='stage-'+descriptor_pin;commit=name+'.coupled.json'
                # Any existing final record is a recovery request, never a new
                # reservation. Caller must supply the independent descriptor pin.
                need(commit not in os.listdir(self.store.fd),'coupled record exists; independently selected cold inspection required')
                event=self.ingress.digest({k:descriptor['owner_verification'][k]for k in ('host_issuer','mechanism_ref','conversation_id','message_id')})
                reservation=event+'.json'
                need(reservation not in os.listdir(self.replay_store.fd),'host message previously reserved; preserve/reconcile')
                self.pending=True
                need(stage not in os.listdir(self.store.fd),'unknown stage preserved; no adoption')
                os.mkdir(stage,0o700,dir_fd=self.store.fd);os.fsync(self.store.fd);base=self.store.directory(self.store.fd,stage)
                for path,body in sorted(files.items()):self.store.write(base,path,body)
                os.fsync(base);os.fsync(self.store.fd)
                # Exact complete plan is durable before either reservation or visibility effect.
                self.store.write(self.store.fd,'plan-'+descriptor_pin+'.json',raw)
                verify_files(self.store.snapshot(base,files),descriptor['files']);self.guard()
                current=self.promotion.prepare_promotion(self.parent,self.source_selection,self.selections,self.identity_path,
                    self.identity_sha256,self.authority,extension_packages=self.extensions,mirrors=self.mirrors)
                need(current['review']==prepared['review']and current['materials']==prepared['materials'],'original source/native/core preimages changed')
                self.ingress.verify_for_publication(self.response,prepared['review'],self.owner_selection,self.trust)
                # Exact old generation is replayed now; a later mutable inner
                # HEAD is never a replacement for this pinned generation.
                self._cold_native(descriptor,files);self.guard()
                # Same T33 event identity and verification result, retained with
                # exact commit plan. O_TMPFILE+linkat binds the reserved inode.
                self.replay_store._commit_record(compact({'schema_version':'lab-coupled-owner-replay-reservation/v1-candidate',
                    'owner_verification':descriptor['owner_verification'],'descriptor_sha256':descriptor_pin,
                    'coupled_record_ref':str(self.store.root/commit),'authority_effect':'none'}),reservation)
                self.guard()
                self.store._commit_record(raw,commit)
                verify_files(self.store.snapshot(base,files),descriptor['files']);self.guard()
                self.completed=True
                return self._outcome(descriptor,files,raw)
            except BaseException as exc:
                if self.pending:raise Uncertain('owned plan/reservation/generation preserved; independently inspect exact coupled record; no automatic retry')from exc
                raise
            finally:
                if parent_lock is not None:os.close(parent_lock)
                if replay_lock is not None:fcntl.flock(replay_lock,fcntl.LOCK_UN);os.close(replay_lock)
                fcntl.flock(lock,fcntl.LOCK_UN);os.close(lock)
    def _cold_native(self,descriptor,files):
        self.boundary.software.function(self.native_factory.cold_snapshot_original_outcome)
        observed=self.native_factory.cold_snapshot_original_outcome(store_root=descriptor['native_store_root'],
            store_identity=tuple(descriptor['native_store_identity']),
            expected_head_binding={'path':str(self.store.root/('stage-'+sha(compact(descriptor)))/'native/HEAD.original.json'),'sha256':descriptor['native_head_binding']['sha256']},
            expected_generation=descriptor['native_generation'],expected_event_files=descriptor['native_event_files'],
            expected_projection_sha256=descriptor['native_projection_sha256'])
        need(observed['schema_version']=='lab-selected-native-immutable-snapshot/v1-candidate' and observed['mutable_inner_HEAD_followed']is False and observed['write_or_retry_performed']is False,'actual immutable generation cold consumer required')
        need(observed['head_raw']==files['native/HEAD.original.json']and observed['projection_raw']==files['native/projection.original.json'],'selected immutable native cold replay differs')
        need(observed['event_files']=={p:{'raw':files['native/events/'+p],'sha256':pin}for p,pin in descriptor['native_event_files'].items()},'selected immutable native original files differ')
        return observed

    def _reservation(self,descriptor,descriptor_sha256):
        event=self.ingress.digest({k:descriptor['owner_verification'][k]for k in ('host_issuer','mechanism_ref','conversation_id','message_id')})
        return event+'.json',compact({'schema_version':'lab-coupled-owner-replay-reservation/v1-candidate',
            'owner_verification':descriptor['owner_verification'],'descriptor_sha256':descriptor_sha256,
            'coupled_record_ref':str(self.store.root/(descriptor['bundle_id']+'.coupled.json')),'authority_effect':'none'})

    def _load_recovery_plan(self,bundle_id,descriptor_sha256):
        """Recognize only an independently pinned complete owned plan/stage."""
        flat(bundle_id);pin(descriptor_sha256);self.guard()
        plan='plan-'+descriptor_sha256+'.json';stage='stage-'+descriptor_sha256;commit=bundle_id+'.coupled.json'
        names=set(os.listdir(self.store.fd))
        need({plan,stage,'publisher.lock'}<=names and names<={plan,stage,commit,'publisher.lock'},
            'missing/foreign/orphan selected publication residue preserved')
        raw=self.store.read(self.store.fd,plan);need(sha(raw)==descriptor_sha256,'independent durable plan pin differs')
        descriptor=parse(raw);validate_descriptor(descriptor)
        need(compact(descriptor)==raw and descriptor['bundle_id']==bundle_id,'exact canonical durable plan/bundle required')
        for field in ('source_binding','profile_binding','source_cut','principal_ref','work_ref','native_store_ref','native_branch_ref'):
            need(descriptor[field]==self.boundary.control[field],'fresh recovery Source/permission scope differs')
        need(descriptor['review_sha256']==self.expected_review_sha256,'fresh selected review differs from plan')
        base=self.store.directory(self.store.fd,stage)
        files=self.store.snapshot(base,descriptor['files']);verify_files(files,descriptor['files'])
        reservation,expected=self._reservation(descriptor,descriptor_sha256)
        reserved=reservation in os.listdir(self.replay_store.fd)
        if reserved:need(self.replay_store.read(self.replay_store.fd,reservation)==expected,'foreign/partial replay reservation preserved')
        committed=commit in names
        need(not committed or reserved,'outer without exact reservation is not recognized recovery')
        if committed:need(self.store.read(self.store.fd,commit)==raw,'competing outer record preserved')
        self.guard()
        return descriptor,files,raw,reservation,expected,reserved,committed

    def _fresh_recovery_write_gate(self,descriptor,files):
        """Actual current positive owner check; historical verification grants no write."""
        from .boundary import OwnerPublicationGuard
        need(self.boundary.control['operation']=='reconcile-coupled-publication','separate explicit recovery-write selection required')
        owner=getattr(self.boundary.owner_guard,'__self__',None)
        need(type(owner)is OwnerPublicationGuard and owner.ingress is self.ingress
            and owner.selection==self.owner_selection and owner.trust==self.trust,'fresh actual owner publication guard required')
        need(files['private-owner-response.original.json']==self.response_raw,'recovery cannot replace original owner response or extend its period')
        prepared=self.promotion.prepare_promotion(self.parent,self.source_selection,self.selections,self.identity_path,
            self.identity_sha256,self.authority,extension_packages=self.extensions,mirrors=self.mirrors)
        need(owner.review==prepared['review']and owner.response==self.response
            and sha(compact(prepared['review']))==descriptor['review_sha256'],'fresh actual owner review differs')
        verified=self.ingress.verify_for_publication(self.response,prepared['review'],self.owner_selection,self.trust)
        need(verified==descriptor['owner_verification']and verified['usage']=='actual-owner'
            and verified['selected_outcome']==self.ingress.ADMIT,'current positive original owner disposition absent')
        rendered,_=render_bundle(prepared,self.response,self.authority,original=self.original,ingress=self.ingress,
            owner_selection=self.owner_selection,trust=self.trust)
        need(rendered=={p.removeprefix('repository/'):body for p,body in files.items()if p.startswith('repository/')},
            'fresh full original source/core/postimage material differs')
        self.guard()

    def reconcile(self,*,bundle_id,descriptor_sha256):
        """Explicit exact-plan recovery. No native append, producer or automatic retry.

        Missing reservation -> reserve once then link; exact reservation -> link
        only; exact outer -> read-only cold inspection. Unknown residue refuses.
        """
        attempted=False
        try:
            with self.boundary.hold():
                lock=self.store.lock();replay_lock=None;parent_lock=None
                try:
                    replay_lock=self.replay_store.lock()
                    parent_lock=os.open(self.parent.path/'.writer.lock',os.O_RDONLY|os.O_NOFOLLOW)
                    fcntl.flock(parent_lock,fcntl.LOCK_SH|fcntl.LOCK_NB)
                    descriptor,files,raw,reservation,expected,reserved,committed=self._load_recovery_plan(bundle_id,descriptor_sha256)
                    self._cold_native(descriptor,files);self._verify_repository(descriptor,files);self.guard()
                    if committed:
                        # Existing visibility never needs another owner reservation
                        # or write. A fresh read-only reader may use this path too.
                        return self._outcome(descriptor,files,raw)
                    self._fresh_recovery_write_gate(descriptor,files)
                    self.pending=True
                    if not reserved:
                        self.guard();attempted=True
                        self.replay_store._commit_record(expected,reservation)
                    # Recheck exact reservation and complete original stage after
                    # the possible syscall; never reserve a second owner event.
                    need(self.replay_store.read(self.replay_store.fd,reservation)==expected,'exact reservation changed before recovered visibility')
                    base=self.store.directory(self.store.fd,'stage-'+descriptor_sha256)
                    verify_files(self.store.snapshot(base,descriptor['files']),descriptor['files'])
                    self.guard();attempted=True
                    self.store._commit_record(raw,bundle_id+'.coupled.json')
                    self.guard();self.completed=True
                    return self._outcome(descriptor,files,raw)
                finally:
                    if parent_lock is not None:os.close(parent_lock)
                    if replay_lock is not None:fcntl.flock(replay_lock,fcntl.LOCK_UN);os.close(replay_lock)
                    fcntl.flock(lock,fcntl.LOCK_UN);os.close(lock)
        except BaseException as exc:
            if attempted:raise Uncertain('explicit recovery outcome uncertain; retain exact plan/reservation/generation and independently inspect; no redispatch')from exc
            raise
    def inspect_committed(self,*,bundle_id,descriptor_sha256):
        # Fresh current authorization; no host message reservation or producer
        # dispatch. Historical owner expiry does not erase an existing commit.
        with self.boundary.hold():
            lock=self.store.lock();replay_lock=None
            try:
                replay_lock=self.replay_store.lock()
                self.guard();raw=self.store.read(self.store.fd,flat(bundle_id)+'.coupled.json');need(sha(raw)==descriptor_sha256,'independent coupled commit pin differs')
                descriptor=parse(raw);validate_descriptor(descriptor);need(descriptor['schema_version']=='lab-coupled-native-original-publication/v1-candidate'and descriptor['bundle_id']==bundle_id,'selected coupled record differs')
                for field in ('source_binding','profile_binding','source_cut','principal_ref','work_ref','native_store_ref','native_branch_ref'):
                    need(descriptor[field]==self.boundary.control[field],'current cold permission/source scope differs')
                need(self.store.read(self.store.fd,'plan-'+descriptor_sha256+'.json')==raw,'preserved complete plan differs')
                event=self.ingress.digest({k:descriptor['owner_verification'][k]for k in ('host_issuer','mechanism_ref','conversation_id','message_id')})
                reservation=parse(self.replay_store.read(self.replay_store.fd,event+'.json'))
                need(reservation=={'schema_version':'lab-coupled-owner-replay-reservation/v1-candidate','owner_verification':descriptor['owner_verification'],
                    'descriptor_sha256':descriptor_sha256,'coupled_record_ref':str(self.store.root/(flat(bundle_id)+'.coupled.json')),'authority_effect':'none'},'actual replay reservation differs')
                base=self.store.directory(self.store.fd,'stage-'+descriptor_sha256);files=self.store.snapshot(base,descriptor['files']);verify_files(files,descriptor['files'])
                self._cold_native(descriptor,files)
                # Exact deterministic recomputation uses recorded response and
                # original material inputs; current code/source guard remains.
                self._verify_repository(descriptor,files)
                self.guard();return self._outcome(descriptor,files,raw)
            finally:
                if replay_lock is not None:fcntl.flock(replay_lock,fcntl.LOCK_UN);os.close(replay_lock)
                fcntl.flock(lock,fcntl.LOCK_UN);os.close(lock)
    def _verify_repository(self,descriptor,files):
        repository={p.removeprefix('repository/'):raw for p,raw in files.items()if p.startswith('repository/')}
        manifest=parse(repository['bundle.json']);need(sha(repository['bundle.json'])==descriptor['repository_bundle_binding']['sha256'],'original repository manifest differs')
        verify_files({p:raw for p,raw in repository.items()if p!='bundle.json'},manifest['files'])
        review=self.original.loads(repository['review.json']);need(sha(compact(review))==descriptor['review_sha256'],'original reviewed core binding differs')
        response=self.ingress.parse(files['private-owner-response.original.json'])
        need(sha(files['private-owner-response.original.json'])==descriptor['owner_response_sha256'], 'actual original owner evidence differs')
        verified=verify_committed_response(response,review,self.owner_selection,self.trust,ingress=self.ingress,publication_time=descriptor['owner_verified_at'])
        need(verified==descriptor['owner_verification'] and verified['usage']=='actual-owner' and verified['selected_outcome']==self.ingress.ADMIT,'historical actual owner evidence differs')
        # Replay the entire original deterministic materializer with a narrowly
        # selected historical verifier object; no production callback/module is
        # replaced. This adapter cannot reserve or commit new effects.
        from .historical_materializer import render_committed_bundle
        expected,_=render_committed_bundle({'review':review,'materials':{p:repository[p]for p in review['material_sha256s']}},response,self.authority,
            original=self.original,ingress=self.ingress,owner_selection=self.owner_selection,trust=self.trust,publication_time=descriptor['owner_verified_at'])
        need(expected==repository,'full original Core/State/history/index cold recomputation differs')
        need(review['authority']==self.authority.core(),'selected cold repository authority differs')
        records=typed_records(repository,manifest,review,self.original)
        need(compact(records)==files['typed-record-set.json'],'actual original typed record correspondence differs')
        recovery=parse(files['native/recovery.original.json']);closed(recovery,('causal_witnesses','commit_receipts'))
        validate_native_selection(self.native_selection,{'head_binding':descriptor['native_head_binding'],
            'generation':descriptor['native_generation'],'event_files':{p:{'raw':files['native/events/'+p],'sha256':digest}for p,digest in descriptor['native_event_files'].items()},
            'projection_sha256':descriptor['native_projection_sha256'],'causal_witnesses':recovery['causal_witnesses']},review,self.boundary.control)
        return repository
    def _outcome(self,descriptor,files,raw):
        repository=self._verify_repository(descriptor,files);rows=parse(files['typed-record-set.json']);record_set=[];selectors=[]
        review=self.original.loads(repository['review.json'])
        producer=self.boundary.software.function(self.capture_selected)
        function=getattr(producer,'__func__',producer)
        captured=[r for r in self.boundary.software.expected if function.__globals__ is r[0].__dict__]
        need(len(captured)==1,'independently captured actual gateway scope-proof producer required')
        producer_binding=copy.deepcopy(captured[0][1])
        for index,row in enumerate(rows):
            body=self.original.loads(base64.b64decode(row['base64_original'],validate=True))
            need(type(body.get('scope_ref'))is str and body['scope_ref'],'explicit original body scope required for typed native output')
            need(row['artifact']['scope_ref']==review['authority']['scope_ref'],'original interchange container/review authority correspondence differs')
            scope={'schema_version':'lab-original-native-record-scope/v1-candidate','artifact':copy.deepcopy(row['artifact']),
                'container_scope_ref':row['artifact']['scope_ref'],'body_scope_ref':body['scope_ref'],
                'authority_scope_ref':review['authority']['scope_ref'],'review_sha256':descriptor['review_sha256'],
                'source_binding':descriptor['source_binding'],'source_cut':descriptor['source_cut'],
                'principal_ref':descriptor['principal_ref'],'work_ref':descriptor['work_ref'],
                'producer_binding':producer_binding,'producer_entrypoint':'NativeMixedPublisher.capture_selected','authority_effect':'none'}
            record_set.append({'role':row['role'],'artifact':row['artifact'],'base64_original':row['base64_original'],'scope_correspondence':scope})
            selectors.append({'role':row['role'],'causal_source':'replay','header_pointer':'/record_set/'+str(index)+'/artifact',
                'original_pointer':'/record_set/'+str(index)+'/base64_original','scope_pointer':'/record_set/'+str(index)+'/scope_correspondence',
                'original_encoding':'base64-original','original_bytes':base64.b64decode(row['base64_original'],validate=True)})
        transaction_raw=repository['bundle.json'];transaction_binding={'ref':str(self.store.root/('stage-'+sha(raw))/'repository/bundle.json'),'sha256':sha(transaction_raw)}
        replay={'schema_version':'lab-native-cold-typed-observation/v2-candidate','native_domain':'repository-bundle-manifest','head_value':parse(transaction_raw)['current_project_state_sha256'],
            'store_ref':descriptor['native_store_ref'],'branch_ref':descriptor['native_branch_ref'],'original_transaction_sha256':sha(transaction_raw),
            'committed':True,'cold_replayed':True,'record_set':record_set,'authority_effect':'none'}
        replay_raw=compact(replay)
        return {'schema_version':'lab-original-native-typed-outcome/v2-candidate','native_domain':'repository-bundle-manifest','operation':self.boundary.control['operation'],
            'principal_ref':descriptor['principal_ref'],'work_ref':descriptor['work_ref'],'source_cut':descriptor['source_cut'],
            'native_store_ref':descriptor['native_store_ref'],'native_branch_ref':descriptor['native_branch_ref'],'transaction_binding':transaction_binding,'transaction_original':transaction_raw,
            'replay_binding':{'ref':'owned-cold-observation:'+sha(replay_raw),'sha256':sha(replay_raw)},'replay_original':replay_raw,
            'records':selectors,'authority_effect':'none'}

    def capture_selected(self):
        """Registered no-argument T31 producer capability; one fresh dispatch."""
        result=self.publish()
        selected=[row for row in result['records']if row['role']in self.output_roles]
        need(set(row['role']for row in selected)==set(self.output_roles),'all independently selected actual output roles required')
        result['records']=selected
        return result

    def close(self):
        self.replay_store.close();self.store.close()
