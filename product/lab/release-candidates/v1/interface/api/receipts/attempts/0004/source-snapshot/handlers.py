"""Real discovery/catalog handlers over verified original signed candidate cuts."""
import copy
import secrets
from auth import now,instant
from protocol import *


class ApplicationError(Exception):
    def __init__(self,code,message):self.code=code;self.message=message;super().__init__(message)


def gap(subject,reason,blocking='full-product-readiness'):
    return {'gap_ref':'gap:R03-api:'+source.sha(reason.encode())[:16], 'subject_ref':subject,
        'reason':reason,'owner_route':'R03/S02/R08','blocking_use':blocking}


def cut(view):
    data=view.data
    return {'store_ref':data['config']['store_id'],'branch_ref':'branch:'+data['config']['store_id'],
        'commit_sequence':data['head']['sequence'],'commit_sha256':data['head']['transaction_digest'],
        'source_profile_sha256':source.PINS.profile_sha256,
        'streams':[{'stream_ref':name,'cursor':len(record['payload']['events']),
            'head_sha256':view.handle.common.digest(record)} for name,record in sorted(data['projection']['histories'].items())]}


class ReadHandlers:
    def __init__(self,view,channel):
        self.view=view;self.channel=channel;self.cursors={}
        source.require(channel.policy['scope_refs']==[view.data['config']['scope_ref']], 'provisioned scope differs from selected store')
        self.available_views=[]
        projection=view.handle.store_module.Store.initial_projection(view.data['baseline'])
        for index,transaction in enumerate(view.data['transactions']):
            if index:
                projection,_=view.handle.operations.prepare(projection,transaction['proposal'],transaction['previous_digest'],view.data['config'])
            source.require(view.handle.common.digest(projection)==transaction['projection_digest'],'historical signed prefix projection differs')
            data={**view.data,'head':{'sequence':index,'transaction_digest':transaction['digest']},
                'projection':copy.deepcopy(projection),'transactions':view.data['transactions'][:index+1]}
            self.available_views.append(source.Inspection(data,view.selected,view.originals,view.handle))
        self.selected_view=view
    def current(self):
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
                '32 declared API operations remain unimplemented in this handler package; SQLite/query and complete Agent/session journeys remain required.'),
                gap(self.view.data['config']['scope_ref'],'Independent fixture reader authentication grants no canonical admission, human pilot outcome or live runtime authority.')]
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
    def close(self):self.cursors.clear()
