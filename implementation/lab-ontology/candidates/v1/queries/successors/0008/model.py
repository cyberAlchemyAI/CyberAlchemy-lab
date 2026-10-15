"""Normative bounded Python graph with separate recorded and confirmed paths."""
from collections import Counter, deque
from jsonschema import Draft202012Validator
from common import *
from contract import SCOPES

class Model:
    def __init__(self,scope):
        self.scope=scope;self.data=scope.data;self.p=self.data['projection'];self.profile=profile()
        self.nodes={};self.refs={};self.edges={};self.gaps=[];self.accounting=[]
        self.mappings={v['carrier_ref']:v for v in self.profile['domain_carrier_mappings']}
        self.materials=self.data['baseline']['materials'];self.obligations={}
        for ref,e in sorted(self.p['subjects'].items()):self.subject(ref,e)
        for ref,e in sorted(self.p['subjects'].items()):self.links(ref,e)
        self.history_links();self.implementation_links();self.native_links()
        self.cut=digest({'scope':scope.scope_ref,'snapshot':self.data['baseline'].get('query_source_snapshot_digest',self.data['baseline']['snapshot_digest']),
            'histories':self.histories(),'controls':scope.control_bindings,'native':scope.native})
        self.graph_digest=digest({'nodes':self.nodes,'edges':self.edges,'accounting':self.accounting,'gaps':self.gaps})
    def gap(self,ref,kind,reason,*,binding=None,closing_task='S02',related=None):
        item={'subject':ref,'kind':kind,'reason':str(reason),'binding':binding,'closing_task':closing_task,
            'excluded_from_confirmed_paths':True,'related':related}
        if item not in self.gaps:self.gaps.append(item)
    def add(self,identity,version,kind,namespace,binding,**fields):
        key=node_key(namespace,kind,identity,version,binding['sha256'])
        v={'graph_id':key,'namespace':namespace,'kind':kind,'identity_ref':identity,'version_ref':version,'source_binding':binding,**fields}
        require(key not in self.nodes or self.nodes[key]==v,'six-field node collision');self.nodes[key]=v;return key
    def source(self,b):
        original(b);return self.add(b['path'],'sha256:'+b['sha256'],'source-file','lab.local-evidence',b,
            material_posture='observed-exact-original-bytes',runtime_conformance='not-evaluated')
    def edge(self,s,t,predicate,mode,evidence,qualifiers,*,subject=None,admission='candidate-derived',confirmed=True,endpoint_semantics=None):
        require(s in self.nodes and t in self.nodes,'exact edge endpoint missing')
        if mode=='profile-local':
            pairs=self.profile['local_edges']['signatures'];q=self.profile['local_edges']['allowed_qualifiers']
            require(predicate in pairs and [self.nodes[s]['kind'],self.nodes[t]['kind']] in pairs[predicate],'undeclared ordered local signature')
            require(set(qualifiers)==set(q[predicate]),'local qualifier closure differs')
        core={'source':s,'target':t,'predicate':predicate,'mode':mode,'direction':'directed','qualifiers':qualifiers,
            'evidence':evidence,'relation_subject_ref':subject,'effective_admission':admission,'version_resolution':'exact',
            'confirmed':confirmed,'endpoint_semantics':endpoint_semantics or {'source_node_kind':self.nodes[s]['kind'],'target_node_kind':self.nodes[t]['kind'],'interpretation':'selected representation profile signature'},'profile_posture':'candidate-unadmitted' if mode=='profile-local' else 'source-recorded'}
        ident='query-edge:'+digest(core);self.edges[ident]={'edge_id':ident,**core};return ident
    def subject(self,ref,e):
        r=e['record'];b=e['source'];original(b);carrier=e.get('carrier_ref') or r.get('classification',{}).get('artifact_type_ref');mapping=self.mappings.get(carrier);reasons=[]
        if not mapping:reasons.append('No exact carrier mapping in selected candidate profile.')
        else:
            original(mapping['schema_binding'])
            try:
                require(self.scope.validate_schema is not None,'No frozen schema resolver selected')
                self.scope.validate_schema(r,mapping['schema_binding'],self.p)
            except ValueError as error:reasons.append('Exact schema mismatch: '+str(error))
            if mapping['semantic_kind']!=e['kind'] and (e['kind'],mapping['semantic_kind']) not in [('project','project-identity'),('product','product-identity')]:reasons.append('Descriptor semantic kind and captured raw kind differ; explicit coupling interpretation remains separate.')
        axes={'carrier_contract':{'ref':carrier,'mapping_binding':bind(PROFILE),'schema_binding':mapping['schema_binding'] if mapping else None,
                'posture':self.p['contracts'].get(e['carrier_ref'],{}).get('lifecycle_state','unknown')},
            'instance_admission':e['effective_state'],'domain_state':r.get('lifecycle_posture',{}).get('status',r.get('lifecycle_state',r.get('status',r.get('record_state','unknown')))),
            'ontology_lifecycle':'not-established','confidence':r.get('evidence_confidence','not-evaluated'),
            'commitment':r.get('commitment','not-evaluated'),'challenge_state':r.get('payload',{}).get('response_state','not-evaluated'),
            'runtime_observation':'not-observed','agent_session':e.get('operational_disposition',r.get('payload',{}).get('termination_state','not-applicable'))}
        key=self.add(e['identity'],ref,mapping['semantic_kind'] if mapping else e['kind'],'lab.governed-subject',b,axes=axes,source_projection_kind=e['kind'],
            owner_route=r.get('owner_ref',r.get('semantic_owner_ref',r.get('owner_route','unknown'))),
            recorded_source_state=r.get('lifecycle_state',r.get('record_state',r.get('status','unknown'))),
            decision_ref=e['decision_ref'],semantic_identity_posture='Original source record preserved; carrier representation kind follows the exact O01 mapping. Global endpoint meaning is a separate explicit coupling interpretation.',
            contract_epoch_note=e.get('historical_contract_posture'))
        self.refs[ref]=key
        self.accounting.append({'version_ref':ref,'kind':e['kind'],'source_binding':b,'disposition':'unresolved' if reasons else 'mapped',
            'reasons':reasons,'closing_task':'S02' if reasons else None})
        for reason in reasons:self.gap(ref,'carrier-mapping-gap',reason,binding=b)
    def unresolved(self,ref,reason):
        row=next(v for v in self.accounting if v['version_ref']==ref);row['disposition']='unresolved'
        if reason not in row['reasons']:row['reasons'].append(reason);row['closing_task']='S02'
    def decision(self,ident):
        found=[]
        for path,doc in self.p['documents'].items():
            if isinstance(doc,dict) and doc.get('decision_id')==ident and path.endswith('/decision.json'):
                found.append((path,doc))
        if len(found)!=1:return None
        path,doc=found[0];b={'path':path,'sha256':self.materials[path]};original(b)
        overlays=[{'path':path,'sha256':self.materials[path]} for path,value in sorted(self.p['documents'].items()) if isinstance(value,dict) and value.get('decision_id')==ident and path.endswith(('/artifact-instance-admission.json','/typed-relation-admission.json'))]
        counts={name:sum(len(self.p['documents'][ob['path']]['entries']) for ob in overlays if ob['path'].endswith('/'+name+'-admission.json')) for name in ['artifact-instance','typed-relation']}
        key=self.add(ident,'sha256:'+b['sha256'],'decision','lab.local-evidence',b,
            recorded_status=doc.get('status','unknown'),owner_route=doc.get('owner_ref','unknown'),
            authority_for_new_action='not-evaluated',recorded_overlay_counts=counts,admission_overlay_bindings=overlays,recorded_effects=doc.get('effects',{}),claim_ceiling=doc.get('claim_ceiling','unknown'))
        self.refs['recorded-decision:'+ident]=key
        for ob in overlays:
            target=self.source(ob);self.edge(key,target,'cites-source','profile-local',[b,ob],{'source_binding':ob})
        auth=doc.get('authorization')
        if isinstance(auth,dict) and set(auth)>= {'path','sha256'}:
            ab={k:auth[k] for k in ['path','sha256']}
            if self.materials.get(ab['path'])==ab['sha256']:
                target=self.source(ab);self.edge(key,target,'authorizes-recorded-effect','profile-local',[b,ab],
                    {'authorization_binding':ab,'recorded_scope':doc.get('authority_effect','unknown')})
            else:self.gap(ident,'unresolved-authorization','Exact authorization bytes not in verified source closure.',binding=ab)
        for field in ['admission_bundle','proposal']:
            q=doc.get(field)
            if isinstance(q,dict) and set(q)>={'path','sha256'} and self.materials.get(q['path'])==q['sha256']:
                qb={k:q[k] for k in ['path','sha256']};target=self.source(qb)
                self.edge(key,target,'cites-source','profile-local',[b,qb],{'source_binding':qb})
        return key
    def links(self,ref,e):
        key=self.refs[ref];b=e['source'];r=e['record'];source=self.source(b)
        self.edge(key,source,'cites-source','profile-local',[b],{'source_binding':b})
        carrier=e.get('carrier_ref') or r.get('classification',{}).get('artifact_type_ref');mapping=self.mappings.get(carrier)
        if carrier in self.refs and mapping:
            pair=[self.nodes[key]['kind'],self.nodes[self.refs[carrier]]['kind']]
            if pair in self.profile['local_edges']['signatures']['uses-contract']:
                self.edge(key,self.refs[carrier],'uses-contract','profile-local',[b,mapping['schema_binding']],{'schema_binding':mapping['schema_binding']})
            else:self.gap(ref,'unselected-local-contract-signature','Exact schema facet retained; no local edge is declared for ordered pair '+str(pair),binding=mapping['schema_binding'],closing_task='O06')
        else:self.gap(ref,'contract-node-outside-selection','Exact schema can be inspected; carrier descriptor node is outside this selected query scope.',binding=mapping['schema_binding'] if mapping else None)
        decisions=e['decision_ref'] if isinstance(e['decision_ref'],list) else [e['decision_ref']]
        for ident in decisions:
            if not ident:continue
            dk=self.decision(ident);overlay=e.get('admission_overlay_binding')
            if not overlay:
                matches=[]
                for path,doc in self.p['documents'].items():
                    if isinstance(doc,dict) and doc.get('decision_id')==ident and any(v.get('admitted_instance_path')==b['path'] for v in doc.get('entries',[]) if isinstance(v,dict)):
                        matches.append({'path':path,'sha256':self.materials[path]})
                if len(matches)==1:overlay=matches[0]
            if dk and overlay:
                original(overlay);db=self.nodes[dk]['source_binding']
                self.edge(key,dk,'admitted-by','profile-local',[b,overlay,db],{'decision_binding':db,'admission_overlay_binding':overlay},admission=e['effective_state'])
            else:self.gap(ref,'unresolved-admission-join','Exact Decision or exact overlay unavailable; recorded posture retained.',binding=b)
        if e['category']=='artifact-type':
            for definition in r.get('semantic_definition_refs',[]):
                if definition in self.refs:
                    db=self.p['subjects'][definition]['source'];self.edge(key,self.refs[definition],'defined-by','profile-local',[b,db],{'definition_binding':db})
                else:self.gap(ref,'unresolved-definition',definition,binding=b)
        if e['category']=='typed-relation':
            p=r['payload'];src=p['source']['version_ref'];target=p['target']['version_ref']
            try:
                require(self.scope.validate_relation is not None,'No global semantic validation selected')
                self.scope.validate_relation(r,self.p)
                require(src in self.refs and target in self.refs,'exact endpoint revision missing')
                current=e['effective_state'] in ['admitted-current','local-admitted-current']
                self.edge(self.refs[src],self.refs[target],p['relation_kind_ref'],'global-typed-relation',
                    [b,self.p['subjects'][src]['source'],self.p['subjects'][target]['source']],p['qualifiers'],subject=ref,
                    admission=e['effective_state'],confirmed=current,endpoint_semantics={'recorded_source_endpoint':p['source'],'recorded_target_endpoint':p['target'],
                    'source_mapping':self.scope.endpoint_mapper(self.p['subjects'][src],self.p),'target_mapping':self.scope.endpoint_mapper(self.p['subjects'][target],self.p),'raw_subjects_rewritten':False})
            except ValueError as error:
                self.gap(ref,'unresolved-global-connection',str(error),binding=b,related=[src,target]);self.unresolved(ref,str(error))
        if e['kind']=='ontology-node':
            represented=r.get('payload',{}).get('represented_subject',{});target=represented.get('version_ref');actual=self.p['subjects'].get(target)
            if not actual or actual['identity']!=represented.get('ref') or actual['source']['sha256']!=represented.get('digest'):
                self.gap(ref,'unresolved-represented-revision','Exact ontology represented identity/version/digest does not resolve.',binding=b,related=[target]);self.unresolved(ref,'Exact represented revision unresolved.')
        if e['kind']=='challenge-event':
            p=r.get('payload',{});rev=p.get('subject_version_ref');target=self.p['subjects'].get(rev)
            if not target or target['identity']!=p.get('subject_ref'):
                self.gap(ref,'challenge-revision-gap','Challenge exact subject tuple unresolved.',binding=b)
            else:self.edge(key,self.refs[rev],'challenges-revision','profile-local',[b,target['source']],{'challenge_event_binding':b,'response_state':p.get('response_state','unknown')})
            refs=[v for v,x in self.p['subjects'].items() if x['identity']==p.get('challenge_contract_ref') and x['effective_state']=='admitted-current']
            if len(refs)==1:
                cb=self.p['subjects'][refs[0]]['source'];self.edge(key,self.refs[refs[0]],'uses-challenge-contract','profile-local',[b,cb],{'challenge_contract_binding':cb})
            else:self.gap(ref,'challenge-contract-gap','Challenge Contract exact revision unresolved.',binding=b)
    def history_links(self):
        history=self.p['histories'].get('project-semantic-event-history')
        if not history:return
        states={v['identity']:v for v in self.p['subjects'].values() if v['kind']=='project-state'}
        for event in history['payload']['events']:
            a=states.get(event['resulting_state_ref']);b=states.get(event.get('predecessor_state_ref'))
            if not a or not b:continue
            if a['record']['payload']['state_digest']!=event['resulting_state_digest'] or b['record']['payload']['state_digest']!=event['predecessor_state_digest']:continue
            # Project event identity joins do not repair a malformed Typed Relation revision.
            ev={'history_binding':next(v['source'] for v in self.p['subjects'].values() if v['record']==history),
                'event_id':event['event_id'],'event_digest':event['event_digest'],'cursor':event['cursor']}
            self.edge(self.refs[a['version_ref']],self.refs[b['version_ref']],'transition-from','profile-local',
                [a['source'],b['source'],ev],{'project_semantic_event_binding':ev,
                'state_digest_bindings':[event['resulting_state_digest'],event['predecessor_state_digest']]})
    def implementation_links(self):
        for binding in self.data['baseline']['profile'].get('implementation_bindings',[]):
            b={'path':binding['path'],'sha256':self.materials[binding['path']]};selector=binding['selector'];raw=original(b)
            # Independent source bindings remain observed; declarations cannot self-certify realization.
            identity='implementation-symbol:'+b['path']+'#'+selector
            key=self.add(identity,'sha256:'+b['sha256'],'implementation-symbol','lab.implementation-symbol',b,
                selector=selector,material_posture='observed-source-symbol',declared_assertion=binding.get('assertion'),runtime_conformance='not-evaluated')
            for ref,e in self.p['subjects'].items():
                if e['kind']!=binding['subject_kind'] or binding.get('subject_version_ref') not in [None,ref]:continue
                alignment=binding.get('alignment_evidence_binding')
                if not alignment:
                    self.gap(ref,'unresolved-implementation-bridge','Source symbol present; exact endpoint alignment evidence absent.',binding=b,closing_task='R03');continue
                assertion=parse(original(alignment))
                require(assertion.get('subject_binding')==e['source'] and assertion.get('subject_version_ref')==ref
                    and assertion.get('implementation_binding')==b and assertion.get('selector')==selector
                    and assertion.get('evaluation_status')=='supported','exact alignment assertion/endpoint joins differ')
                self.edge(self.refs[ref],key,'implemented-by','profile-local',[e['source'],b,alignment],
                    {'source_binding':b,'selector':selector,'alignment_evidence_binding':alignment})
    def native_links(self):
        if not self.scope.native:return
        native=self.scope.native
        semantic={v['event_id']:v for v in native['semantic_events']};governance={v['event_id']:v for v in native['governance_events']}
        byid={v['identity']:v for v in self.p['subjects'].values()}
        vocabulary={'legacy-product-local-predicate:'+v+'/v1-candidate' for v in self.data['source_translation_profile']['predicates']}
        for ref,e in sorted(self.p['subjects'].items()):
            if e['kind'] not in ['ontology-node','ontology-edge']:continue
            p=e['record']['payload'];binding=p.get('semantic_event_ref',p.get('governance_binding',{}).get('semantic_event_ref'))
            ev=semantic.get(binding['semantic_event_id']);require(ev and ev['event_digest']==binding['semantic_event_digest'] and ev['semantic_cursor']==binding['semantic_cursor'],'native exact semantic tuple differs')
            joined=[g for g in governance.values() if g['semantic_ref']==binding];require(len(joined)==1,'native exact governance tuple missing/ambiguous')
            node=self.nodes[self.refs[ref]];node['axes']['ontology_lifecycle']=p.get('semantic_state',{}).get('lifecycle',p.get('lifecycle','unknown'))
            node['native_join']={'semantic':binding,'governance_event_id':joined[0]['event_id'],'governance_event_digest':joined[0]['event_digest'],
                'governance_cursor':joined[0]['governance_cursor'],'posture':'candidate-owned-event-history; no source admission'}
            node['axes']['confidence']=joined[0]['complete_resulting_governance_state']['evidence_confidence']
            node['axes']['commitment']=joined[0]['complete_resulting_governance_state']['commitment_confidence']
            if e['kind']=='ontology-edge':
                src=byid.get(p['source_node_ref']);target=byid.get(p['target_node_ref']);require(src and target,'native exact edge endpoints absent')
                require(p['edge_mode']=='local-interpretation' and p['direction']=='directed' and p['global_typed_relation_binding'] is None,'local/source/global collapse')
                require(p['relation_type_ref'] in vocabulary,'undeclared local source predicate');qualifiers=p['closed_qualifiers']
                require(set(qualifiers)==set(self.data['source_translation_profile']['closed_qualifier_keys']),'source-local qualifier closure differs')
                for field,endpoint in [('source_node_version_ref',src),('target_node_version_ref',target)]:
                    require(qualifiers[field]==endpoint['record']['payload']['represented_subject']['version_ref'],'native represented endpoint version differs')
                self.edge(self.refs[src['version_ref']],self.refs[target['version_ref']],p['relation_type_ref'],'source-local-interpretation',
                    [e['source'],src['source'],target['source'],binding],qualifiers,subject=ref,admission='candidate-unadmitted')
        for row in self.scope.reconciliation:
            if row['disposition']=='block':self.gap(row['item_id'],'blocked-original-dependency','Expected exact original revision unavailable; current bytes cannot substitute.',binding={'expected_sha256':row['blocked_expected_sha256']},closing_task='O06')
    def histories(self):
        result={}
        for name in ['project-semantic-event-history','project-governance-event-history']:
            h=self.p['histories'].get(name);e=next((v for v in self.p['subjects'].values() if h and v['record']==h),None)
            result[name]={'identity_ref':h.get('node_id'),'version_ref':e['version_ref'],'cursor':h['payload'].get('latest_cursor',h['payload'].get('latest_governance_cursor')),'source_binding':e['source']} if h and e else None
        n=self.scope.native
        result['ontology-semantic']={'cursor':len(n['semantic_events']),'event_set_digest':digest(n['semantic_events']),'candidate_owned':True} if n else None
        result['ontology-governance']={'cursor':len(n['governance_events']),'event_set_digest':digest(n['governance_events']),'candidate_owned':True} if n else None
        return result
    def evaluate(self,request,selected_edges,selected_nodes):
        q=request['query_id'];claims=[];met={};root=request['root'];node=self.nodes.get(self.refs.get(root,''));edges=[self.edges[e] for e in selected_edges]
        def claim(name,supported,basis):
            met[name]=bool(supported);claims.append({'obligation':name,'status':'source-backed' if supported else 'not-evaluated',
                'scope_ref':request['scope_ref'],'basis':basis,'authority_effect':'none'})
        if q=='lifecycle-slice':
            state=self.p['state'];states=[v for v in self.p['subjects'].values() if v['kind']=='project-state' and v['effective_state']=='admitted-current'];hist=self.histories()
            claim('current-state',bool(state and len(states)==1),{'selected_state_ref':states[0]['version_ref'] if len(states)==1 else None,'content_cursor':state['payload']['cursor'] if state else None,
                'source_binding':states[0]['source'] if len(states)==1 else None,'admission_epoch':self.data['selected_admission_epoch']})
            claim('separate-project-histories',bool(hist['project-semantic-event-history'] and hist['project-governance-event-history']),hist)
            claim('state-admission',any(e['predicate']=='admitted-by' and states and e['source']==self.refs[states[0]['version_ref']] for e in edges),{'recorded_effect_only':True})
            claim('exact-predecessor-path',any(e['predicate']=='relation.successor-of' and states and e['source']==self.refs[states[0]['version_ref']] for e in edges),{'local_history_trace_does_not_repair_global_relation':True})
        elif q=='authority-explanation':
            claim('recorded-admission',bool(node and node.get('recorded_status')=='owner-admitted'),{'decision_binding':node['source_binding'] if node else None,'recorded_status':node.get('recorded_status') if node else None})
            claim('exact-authorization',any(e['predicate']=='authorizes-recorded-effect' and e['source']==node['graph_id'] for e in edges) if node else False,{'owner_route':node.get('owner_route') if node else None})
            claim('effect-scope',bool(node and node.get('recorded_effects') and node['recorded_overlay_counts']['artifact-instance']==node['recorded_effects'].get('artifact_instances_admitted') and node['recorded_overlay_counts']['typed-relation']==node['recorded_effects'].get('typed_relation_instances_admitted')),{ 'recorded_effects':node.get('recorded_effects') if node else None,'actual_original_overlay_counts':node.get('recorded_overlay_counts') if node else None,'overlay_bindings':node.get('admission_overlay_bindings') if node else None,'runtime_observation':'not-observed'})
        else:
            claim('exact-lineage',any(e['predicate']=='relation.derives-from' and node and e['source']==node['graph_id'] for e in edges),{'realization_inferred':False})
        claim('implementation-bridge',any(e['predicate']=='implemented-by' for e in edges),{'file_presence_establishes_realization':False})
        claim('ontology-event-join',any(self.nodes[k].get('native_join') for k in selected_nodes),self.histories())
        claim('effectiveness',False,{'evaluation':'not-evaluated'})
        claim('new-action-permission',False,{'authorization':'not-evaluated'})
        return claims,{o:met.get(o,False) for o in request['obligations']}
    def query(self,request):
        Draft202012Validator(load(HERE/'contracts/request.schema.json')).validate(request)
        require(request['scope_ref']==self.scope.scope_ref and request['admission_as_of']==SCOPES[request['scope_ref']],'scope/epoch mismatch')
        require(not self.data['historical_scope'] or request['view']=='historical','historical D73 cannot answer current-state request')
        status=self.scope.guard();freshness={**status,'state':'historical' if request['view']=='historical' and status['state']=='current' else status['state']}
        active=status['state']=='current';edges=[v for v in self.edges.values() if v['confirmed'] and (not request['edge_selection'] or v['predicate'] in request['edge_selection'])] if active else []
        closed={v['predicate'] for v in self.edges.values()}|set(self.profile['local_edges']['signatures'])|set(self.p['relation_contracts'])
        require(set(request['edge_selection'])<=closed,'unknown edge predicate')
        lens={'Lifecycle':{'project-state','project-semantic-event-history','project-governance-event-history'},'Authority':{'decision'},'Provenance':{'product-capability','product-thesis'}}
        root=request['root'];initial=sorted(k for k,v in self.nodes.items() if v['kind'] in lens[root] and v.get('axes',{}).get('instance_admission','admitted-current')=='admitted-current') if root in lens else [self.refs[root]] if root in self.refs else []
        limits=request['limits'];chosen={v:0 for v in initial[:limits['nodes']]};queue=deque(chosen);paths={v:[] for v in chosen};accepted={};frontier=set(initial[limits['nodes']:]);adj={}
        for e in sorted(edges,key=lambda v:v['edge_id']):
            if request['direction'] in ['outgoing','both']:adj.setdefault(e['source'],[]).append((e,e['target']))
            if request['direction'] in ['incoming','both']:adj.setdefault(e['target'],[]).append((e,e['source']))
        while queue:
            current=queue.popleft()
            for e,other in adj.get(current,[]):
                if e['edge_id'] in accepted:continue
                if chosen[current]>=limits['depth'] or len(accepted)>=limits['edges'] or (other not in chosen and len(chosen)>=limits['nodes']):frontier.add(e['edge_id']);continue
                accepted[e['edge_id']]=e
                if other not in chosen:
                    chosen[other]=chosen[current]+1;paths[other]=paths[current]+[{'edge_id':e['edge_id'],'source':e['source'],'target':e['target'],
                        'navigation':'forward' if current==e['source'] else 'incoming','evidence':e['evidence']}];queue.append(other)
        claims,obligations=self.evaluate(request,accepted,chosen)
        if not active:
            for claim in claims:claim['status']='historical-source-observation';claim['confirmed_current']=False
            obligations={k:False for k in obligations}
        gaps=copy.deepcopy(self.gaps)
        if not initial:gaps.append({'kind':'unresolved-root','subject':root,'reason':'Exact revision absent; no identity/latest alias applied.'})
        if not active:gaps.append({'kind':'source-currentness','subject':root,'reason':status,'excluded_from_confirmed_paths':True})
        for o,fulfilled in obligations.items():
            if not fulfilled:gaps.append({'kind':'unmet-query-obligation','subject':root,'reason':o})
        rows=copy.deepcopy(self.accounting)
        if not active:
            for row in rows:row.update(disposition='unresolved',reasons=row['reasons']+['Selected source/control/HEAD currentness not verified.'])
        counts=Counter(row['disposition'] for row in rows)
        exclusions=[{'area':'repository outside exact declared source envelope','reason':'Not selected; file inventory is not semantic coverage.'},
            {'area':'live runtime, general effectiveness, new-action authorization','reason':'No fresh observation or permission evaluated.'}]
        if self.scope.native:exclusions += [{'area':'original source bodies / original domain conformance / global relation creation','reason':'O05 selects private source-qualified metadata and local interpretations only.'}]
        coverage={'scope_ref':request['scope_ref'],'selected_subjects':len(rows),'partition':{'mapped':counts['mapped'],'unresolved':counts['unresolved'],'excluded':counts['excluded']},
            'subject_rows':rows,'required_obligations':obligations,'selected_nodes':len(chosen),'selected_edges':len(accepted),'truncated':bool(frontier),
            'omitted_frontier':sorted(frontier),'continuation':{'source_cut_digest':self.cut,'frontier_digest':digest(sorted(frontier)),
                'guidance':'Refine predicate/root or increase limits against this same cut; no implicit pagination across changed sources.'},
            'source_item_accounting':self.scope.reconciliation,'excluded_areas':exclusions}
        response={'schema_version':'lab-three-lens-response/v1-candidate','query':request,
            'result_status':'blocked' if not active or not initial else 'partial' if frontier or not all(obligations.values()) else 'complete',
            'source_snapshot':{'manifest_digest':self.data['baseline'].get('query_source_snapshot_digest',self.data['baseline']['snapshot_digest']),'source_cut_digest':self.cut,'graph_digest':self.graph_digest,
                'admission_epoch':self.data['selected_admission_epoch'],'bindings':[{'path':p,'sha256':s} for p,s in sorted(self.materials.items())]+self.scope.control_bindings,
                'histories':self.histories(),'historical_source_relocations':self.data.get('historical_source_relocations',[]),'check_time_rule':'Fresh scope guard executed for this response; wall-clock observation belongs to execution receipt.',
                'canonical_ontology_cut':False if not self.scope.native else 'candidate-owned-native-cut; not canonical Lab admission'},
            'freshness':freshness,'subjects':[self.nodes[k] for k in sorted(chosen)],
            'state_tracks':[{'graph_id':k,**self.nodes[k]['axes']} for k in sorted(chosen) if 'axes' in self.nodes[k]],
            'connections':list(accepted.values()),'explanation_paths':[{'root':root,'target':k,'steps':paths[k]} for k in sorted(paths)],
            'claims':claims,'gaps':gaps,'coverage':coverage,'authority_effect':'none','replay_source':False,
            'claim_ceiling':'Exact selected candidate read interpretation; no new admission, new action permission, realization by presence, general truth or live operation.'}
        Draft202012Validator(load(HERE/'contracts/response.schema.json')).validate(response);return response
