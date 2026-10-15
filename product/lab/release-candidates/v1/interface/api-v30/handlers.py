"""Real discovery/catalog handlers over verified original signed candidate cuts."""
import copy
import secrets
from .auth import now,instant
from .protocol import *
from . import artifact_model as model
from .projection import Generation


class ApplicationError(Exception):
    def __init__(self,code,message):self.code=code;self.message=message;super().__init__(message)


def gap(subject,reason,blocking='full-product-readiness'):
    return {'gap_ref':'gap:R03-api:'+source.sha(reason.encode())[:16], 'subject_ref':subject,
        'reason':reason,'owner_route':'R03/S02/R08','blocking_use':blocking}


def cut(view):
    data=view.data
    return {'store_ref':data['config']['store_id'],'branch_ref':'branch:'+data['config']['store_id'],
        'commit_sequence':data['head']['sequence'],'commit_sha256':data['head']['transaction_digest'],
        'source_profile_sha256':source.selected_profile_sha(view),
        'streams':[{'stream_ref':name,'cursor':len(record['payload']['events']),
            'head_sha256':view.handle.common.digest(record)} for name,record in sorted(data['projection']['histories'].items())]}


class ReadHandlers:
    def __init__(self,view,channel,schemas):
        self.view=view;self.channel=channel;self.schemas=schemas;self.cursors={};self.generations={}
        source.require(channel.policy['scope_refs']==[view.data['config']['scope_ref']], 'provisioned scope differs from selected store')
        self.available_views=[]
        projection=view.handle.store_module.Store.initial_projection(view.data['baseline'])
        for index,transaction in enumerate(view.data['transactions']):
            if index==len(view.data['transactions'])-1:
                # Source opening already verified the complete signed chain,
                # signatures, cores, consequences and externally pinned digest.
                # Reuse that final original projection; no cache grants authority.
                projection=copy.deepcopy(view.data['projection'])
            elif index:
                projection,cores=view.handle.operations.prepare(projection,transaction['proposal'],transaction['previous_digest'],view.data['config'])
                consequences=view.handle.store_module.consequences(projection,transaction['proposal'],cores,
                    transaction['approval'],index,view.data['config']['store_id'])
                source.require(cores==transaction['decision_cores'] and consequences==transaction['consequences'],
                    'historical signed prefix Decision cores/consequences differ')
            source.require(view.handle.common.digest(projection)==transaction['projection_digest'],'historical signed prefix projection differs')
            data={**view.data,'head':{'sequence':index,'transaction_digest':transaction['digest']},
                'projection':copy.deepcopy(projection),'transactions':view.data['transactions'][:index+1]}
            self.available_views.append(source.inspection(data,view.selected,view.originals,view.handle))
        self.selected_view=view
    def current(self):
        if hasattr(self.view,'custody_signed_sources'):self.view.custody_signed_sources.guard()
        if hasattr(self.view,'fresh_signed_sources'):self.view.fresh_signed_sources.guard()
        self.view.handle.guard()
        self.view.data['freshness']=self.view.handle.sources.freshness(ROOT,self.view.data['baseline'])
        return self.view.data['freshness']['status']=='current'
    def selected_cut(self,message,outer):
        selected=message['source_cut']
        if selected!=outer:raise ApplicationError('invalid-contract','Outer and message source cuts disagree.')
        self.selected_view=self.view
        if selected is not None:
            matches=[view for view in self.available_views if cut(view)==selected]
            if len(matches)!=1:raise ApplicationError('stale-cut','Requested cut is not an exact verified prefix of this independently selected original signed chain.')
            self.selected_view=matches[0]
        observed=cut(self.selected_view)
        if not self.current():raise ApplicationError('stale-cut','Original source cut is no longer current; changed bytes do not replace captured material.')
        return observed
    def status(self,message,request_binding,outer):
        observed=self.selected_cut(message,outer)
        if not set(message['scope_refs'])<=set(self.channel.policy['scope_refs']):raise ApplicationError('unauthorized','Requested scope is not authorized.')
        catalog=ROOT/'docs/proposals/0008-lab-api-contracts/api-contracts.json'
        gaps=[gap(self.view.data['config']['scope_ref'],
                '21 declared API operations remain unimplemented in this handler package; complete transaction journeys, final owner review and broader ontology/workflow integration remain required.'),
                gap(self.view.data['config']['scope_ref'],'Independent fixture reader authentication grants no canonical admission, human pilot outcome or live runtime authority.')]
        if self.channel.policy['schema_version']=='lab-local-metadata-candidate-policy/v1-candidate':
            gaps.append(gap(observed['branch_ref'],'This fresh metadata grant permits eight inspection/preparation operations; it grants no live Agent context or Session participation, and does not renew the original expired Assignment.','live-Agent-participation'))
        if self.channel.policy['schema_version']=='lab-local-export-candidate-policy/v1-candidate':
            gaps.append(gap(observed['branch_ref'],'This fresh export grant permits eight metadata operations and files.materialize in its independently owned output root; it grants no Agent or Session participation.','live-Agent-participation'))
        if self.selected_view.selected['name']=='reference-corrected':
            coverage=model.connection_coverage(self.selected_view,self.schemas)
            gaps.append(gap(observed['branch_ref'],f"Connection coverage: {coverage['current']['closed']} current closed, {coverage['current']['unclosed']} current unclosed; {coverage['historical']['closed']} historical closed, {coverage['historical']['unclosed']} historical unresolved. Original historical residue remains inspectable.",'historical-corrective-closure'))
        if observed!=cut(self.view):gaps.append(gap(observed['branch_ref'],'Exact historical prefix read from original signed chain; it does not change the selected branch HEAD.','current-operation-from-historical-read'))
        return {'schema_version':'lab-lab-status-result/v1-candidate','request_binding':request_binding,
            'source_cut':observed,'source_profile_binding':{'ref':self.view.handle.manifest['profile_binding']['path'],
                'sha256':self.view.handle.manifest['profile_binding']['sha256']},
            'catalog_binding':binding(str(catalog.relative_to(ROOT)),catalog.read_bytes()),
            'supported_operations':list(SUPPORTED),'implementation_posture':'implemented-local',
            'projection_status_binding':None,'gaps':gaps,
            'claim_ceiling':source.CLAIM,'authority_effect':'none'}
    def cursor_fingerprint(self,message):
        selectors={k:message[k] for k in ('source_cut','carrier_refs','include_relations','limit')}
        return source.sha(compact({'operation':'catalog.get','selectors':selectors,
            'principal_ref':self.channel.context['principal_ref'],'authority_scope':self.channel.context['authority_scope'],
            'scope_refs':self.channel.context['scope_refs'],'context_ref':self.channel.context['context_ref']}))
    def catalog(self,message,request_binding,outer):
        observed=self.selected_cut(message,outer);limit=message['limit']
        if type(limit) is not int or not 1<=limit<=1000:raise ApplicationError('budget-exceeded','Catalog page exceeds the host item budget.')
        fingerprint=self.cursor_fingerprint(message);cursor=message['page_cursor'];offset=0
        if cursor is not None:
            row=self.cursors.get(cursor)
            if row is None or row['fingerprint']!=fingerprint or row['cut']!=observed:
                raise ApplicationError('invalid-cursor','Cursor is not bound to this authenticated principal, request and cut.')
            offset=row['offset']
        contracts=self.selected_view.data['projection']['contracts']
        selected=set(message['carrier_refs'])
        if selected and not selected<=contracts.keys():raise ApplicationError('not-found','Selected carrier is not in the eligible captured catalog.')
        entries=[]
        for ref,contract in sorted(contracts.items()):
            if selected and ref not in selected:continue
            state=contract['lifecycle_state']
            if state not in ('admitted-current','local-admitted-current','admitted-historical','local-admitted-historical'):continue
            entries.append({'carrier_ref':ref,'schema_binding':{'ref':contract['schema_path'],'sha256':contract['schema_sha256']},
                'descriptor_binding':{'ref':contract['artifact_path'],'sha256':contract['artifact_sha256']},
                'schema_selector':contract.get('schema_selector') or None,'semantic_kind':contract['semantic_kind'],
                'write_posture':'current' if state in ('admitted-current','local-admitted-current') else 'historical-read-only',
                'admission_decision_ref':contract['admission_decision_ref']})
        next_cursor=None
        if offset+limit<len(entries):
            if len(self.cursors)>=256:raise ApplicationError('budget-exceeded','Cursor budget exhausted for this authenticated connection.')
            next_cursor='cursor:R03-api:'+secrets.token_hex(24)
            self.cursors[next_cursor]={'offset':offset+limit,'fingerprint':fingerprint,'cut':copy.deepcopy(observed)}
        relations=[]
        if message['include_relations']:
            for ref,record in sorted(self.selected_view.data['projection']['relation_contracts'].items()):
                matches=[p for p,doc in self.selected_view.data['baseline']['documents'].items() if doc==record]
                if len(matches)!=1:raise ApplicationError('closure-missing','Exact captured eligible relation signature is missing or ambiguous.')
                path=matches[0]
                relations.append({'relation_kind_ref':ref,'axis_ref':record['payload']['axis_id'],
                    'signature_binding':{'ref':path,'sha256':self.selected_view.data['baseline']['materials'][path]}})
        registry='authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'
        return {'schema_version':'lab-catalog-result/v1-candidate','request_binding':request_binding,
            'source_cut':observed,'domain_catalog_binding':{'ref':registry,'sha256':self.view.data['baseline']['materials'][registry]},
            'contract_entries':entries[offset:offset+limit],'relation_signatures':relations,'next_page_cursor':next_cursor,
            'gaps':[gap(self.view.data['config']['scope_ref'],'Only exact catalog versions selected by this signed source profile; external unadmitted candidate queues are not indexed.')],
            'claim_ceiling':source.CLAIM,'authority_effect':'none'}
    def resolve_exact(self,header):
        if header['scope_ref']!=self.channel.policy['scope_refs'][0]:raise ApplicationError('unauthorized','Artifact read namespace is outside the authenticated scope.')
        subject=self.selected_view.subjects.get(header['version_ref'])
        if subject is None:raise ApplicationError('not-found','Exact artifact revision is not in this selected signed cut.')
        if model.artifact_ref(self.selected_view,subject)!=header:raise ApplicationError('invalid-contract','Artifact identity/carrier/encoded bytes disagree with the exact selected revision.')
        return subject
    def inspect(self,message,request_binding,outer):
        observed=self.selected_cut(message,outer);view=self.selected_view;subject=self.resolve_exact(message['artifact'])
        included=list(message['include']);contract=view.data['projection']['contracts'][model.carrier(view,subject)]
        selected=set(included);provenance=[];authority=[];evidence=[];gaps=[];envelope=None;relations=[]
        if 'authority' in selected:
            # The verified source archive binds captured eligibility overlay and
            # signed local transactions. It does not substitute for missing owner
            # Decision bodies or imply a new canonical owner response.
            b=view.selected['archive_binding'];authority=[{'ref':b['path'],'sha256':b['sha256']}]
        catalog_row=model.representations.row(view,subject)
        if 'body' in selected:
            from .workspace import privacy
            try:privacy(subject['record'])
            except Exception:raise ApplicationError('unauthorized','The exact original body contains protected Session memory or credential material. Use metadata inspection; original bytes remain in protected source custody.')
            if catalog_row is not None:
                envelope=model.representations.envelope(view,subject,observed,authority)
            else:
                decoded={'carrier_ref':model.carrier(view,subject),'body':copy.deepcopy(subject['record'])}
                if not self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:domain-artifact:v1-candidate',decoded):
                    raise ApplicationError('invalid-contract','Captured body does not conform to this exact generic carrier envelope; descriptor/root schema mismatch remains a declared R03 gap.')
                raw,locator,encoding,file_sha=model.record_bytes(view,subject)
                envelope={'schema_version':'lab-artifact-envelope/v1-candidate','artifact':message['artifact'],'source_cut':observed,
                    'content':{'content_ref':locator,'byte_sha256':source.sha(raw),'size_bytes':len(raw),'media_type':'application/json'},
                    'decoded_artifact':decoded,'effective_admission_basis':authority,'source_locator':locator,
                    'claim_ceiling':source.CLAIM+' Encoded content basis: '+encoding+'.','authority_effect':'none'}
        if 'provenance' in selected:
            report=view.source_record(subject);b=subject['source']
            locator=('store:'+b['store_id']+':'+b['path']) if 'store_id' in b else b['path']
            provenance=[{'ref':locator,'sha256':report['original_file_sha256']}]
        if 'evidence' in selected:
            for ref in subject['record'].get('evidence_refs',[]):
                if ref in view.data['baseline']['materials']:
                    evidence.append({'ref':ref,'sha256':view.data['baseline']['materials'][ref]})
        if 'relations' in selected:
            rows,missing=model.connections(view,self.schemas)
            relations=[r['connection'] for r in rows if any(r['connection'][end]['artifact']['version_ref']==subject['version_ref'] for end in ('source','target'))]
        if 'gaps' in selected:
            gaps=[gap(subject['version_ref'],'Captured eligibility overlay is verified, but not every referenced canonical Decision body/evidence is in this selected source cut.')]
            if catalog_row is not None:
                gaps.append(gap(subject['version_ref'],'Catalog representation validates an exact captured declaration; instance schema, independent future instances and owner admission remain separate.'))
        if 'gaps' in selected and subject['kind']=='typed-relation':
            try:view.handle.operations.validate_relation(subject['record'],view.data['projection'],allow_historical=True)
            except Exception:
                family='Historical' if subject['effective_state'] in ('admitted-historical','local-admitted-historical') else 'Current'
                gaps.append(gap(subject['version_ref'],family+' exact relation retains unresolved endpoints; admission/body conformance does not establish connection closure.','use-needing-connection-closure'))
        if 'evidence' in selected and subject.get('reference_correction_proof'):
            correction=subject['reference_correction_proof']
            for key in ['reference_correction_binding','correction_profile_binding','carrier_schema_binding','carrier_descriptor_binding']:
                b=correction[key]
                if view.data['baseline']['materials'].get(b['path'])!=b['sha256']:
                    raise ApplicationError('integrity-failed','Correction evidence is outside the independently signed baseline.')
                evidence.append({'ref':b['path'],'sha256':b['sha256']})
        facets=source.facets(subject)
        return {'schema_version':'lab-artifact-inspect-result/v2-candidate','request_binding':request_binding,'artifact':message['artifact'],
            'source_cut':observed,'included_sections':included,'envelope':envelope,
            'status_facets':{k:facets[k] for k in ('admission','domain','implementation','runtime_observation','outcome')},
            'contract_binding':(binding(str((HERE/'schemas/catalog-envelope.schema.json').relative_to(ROOT)),(HERE/'schemas/catalog-envelope.schema.json').read_bytes())
                if catalog_row is not None else {'ref':contract['schema_path'],'sha256':contract['schema_sha256']}) if 'contract' in selected else None,
            'authority_bindings':authority if 'authority' in selected else [],'provenance_bindings':provenance,'evidence_bindings':evidence,
            'connections':relations,'gaps':gaps,'claim_ceiling':source.CLAIM,'authority_effect':'none'}
    def query_cut(self,message,outer):
        selected=message['source_cut']
        if selected!=outer:raise ApplicationError('invalid-contract','Outer and message source cuts disagree.')
        matches=[v for v in self.available_views if cut(v)==selected]
        if len(matches)!=1:raise ApplicationError('stale-cut','Requested cut is not an exact verified prefix of this independently selected signed archive.')
        self.selected_view=matches[0];current=self.current();historical=selected!=cut(self.view)
        requirement=message['freshness_requirement']
        if requirement=='current' and (not current or historical):raise ApplicationError('stale-cut','Current query requires the current independently selected HEAD and unchanged captured source material.')
        if not current and requirement!='allow-stale':raise ApplicationError('stale-cut','Changed or missing original material requires explicit stale read permission; no changed bytes are substituted.')
        if requirement=='exact-historical' and not historical:raise ApplicationError('invalid-contract','Exact historical query requires an earlier verified prefix.')
        return 'stale' if not current else 'historical' if historical else 'current'
    def query(self,message,request_binding,outer):
        if message['scope_refs']!=self.channel.policy['scope_refs']:raise ApplicationError('unauthorized','Query namespace is outside the authenticated selected archive scope.')
        if message['limit']>1000 or message['max_depth']>4 or len(message['identity_refs'])>100 or len(message['carrier_refs'])>143:
            raise ApplicationError('budget-exceeded','Query item/depth/selector budget exceeds the host ceiling.')
        freshness=self.query_cut(message,outer);view=self.selected_view;observed=cut(view)
        canonical=model.references(view);relations,missing=model.connections(view,self.schemas)
        canonical_items,canonical_edges=model.select(canonical,relations,message)
        canonical_edges=sorted(canonical_edges,key=lambda r:r['version_ref'])
        items=canonical_items;edges=canonical_edges;basis='canonical';generation=None;gaps=[]
        if message['query_basis']!='canonical':
            key=source.sha(compact(observed));projector=self.generations.get(key)
            try:
                if projector is None:
                    projector=Generation(view,observed,self.schemas);self.generations[key]=projector
                items,edges=projector.query(message)
                if items!=canonical_items or edges!=canonical_edges:raise ValueError('canonical/SQL parity differs')
                generation=projector.binding;basis='projection'
            except Exception:
                if message['query_basis']=='projection':raise ApplicationError('integrity-failed','Complete selected SQL generation is missing, corrupted or differs from independently replayed canonical inputs.')
                items=canonical_items;edges=canonical_edges
                gaps.append(gap(observed['branch_ref'],'Requested projection failed verification; prefer-projection explicitly fell back to the independently verified canonical cut.'))
        if len(items)>1000 or len(edges)>1000:raise ApplicationError('budget-exceeded','Query expansion exceeds the host result/edge ceiling.')
        fingerprint=source.sha(compact({'operation':'artifact.query','selectors':{k:v for k,v in message.items()
            if k not in ('request_ref','actor','budget','page_cursor')},'context':self.channel.context,'cut':observed,'generation':generation,'basis':basis,'freshness':freshness}))
        cursor=message['page_cursor'];offset=0
        if cursor is not None:
            saved=self.cursors.get(cursor)
            if saved is None or saved.get('query_fingerprint')!=fingerprint:raise ApplicationError('invalid-cursor','Cursor does not match this exact query/cut/generation/principal/context/scope.')
            offset=saved['offset']
        next_cursor=None
        if offset+message['limit']<len(items):
            if len(self.cursors)>=256:raise ApplicationError('budget-exceeded','Connection cursor budget exhausted.')
            next_cursor='cursor:R03-query:'+secrets.token_hex(24);self.cursors[next_cursor]={'query_fingerprint':fingerprint,'offset':offset+message['limit']}
        page=items[offset:offset+message['limit']];versions={r['version_ref'] for r in page}
        returned_edges=[r['connection'] for r in edges if any(r['connection'][end]['artifact']['version_ref'] in versions for end in ('source','target'))]
        gaps.extend(gap(r['subject_ref'],r['reason'],'use-needing-connection-closure') for r in missing)
        heads={}
        for subject in view.subjects.values():
            if subject['effective_state'] in ('admitted-current','local-admitted-current'):
                heads.setdefault(model.artifact_ref(view,subject)['identity_ref'],[]).append(subject['version_ref'])
        gaps.extend(gap(identity,'Multiple independently captured eligible current revisions; no unique artifact head selected from admission posture.',
            'use-needing-unique-head') for identity,versions in sorted(heads.items()) if len(versions)>1)
        gaps.append(gap(observed['branch_ref'],'Only captured eligible source-profile revisions are indexed; external candidate queues, complete owner evidence and ontology joins remain separate obligations.'))
        return {'schema_version':'lab-artifact-query-result/v1-candidate','request_binding':request_binding,'source_cut':observed,
            'requested_source_cut':message['source_cut'],'projection_generation':generation,'query_basis':basis,'freshness':freshness,
            'results':page,'connections':returned_edges,'next_page_cursor':next_cursor,'gaps':gaps,'claim_ceiling':source.CLAIM,'authority_effect':'none'}
    def close(self):
        self.cursors.clear()
        for generation in self.generations.values():generation.close()
        self.generations.clear()
