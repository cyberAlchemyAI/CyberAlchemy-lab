"""Signed source posture maps only to exact native governance, never lifecycle."""
from source import *
from native_store import NativeCandidateStore


def joined_effect(spec, cut):
    require(type(cut) is VerifiedSourceCut, 'actual independently replayed source cut required')
    effect=cut.effect();subject=spec['subject'];view=spec['source_view']
    require(subject['kind']==effect['source_kind'] and subject['identity']==effect['source_identity_ref']
        and subject['version_ref']==effect['source_version_ref']
        and subject['carrier_bytes_sha256']==effect['record_sha256']
        and view['carrier']['source_binding']==effect['record_binding']
        and view['carrier']['ref']==effect['carrier_ref'], 'native represented source tuple differs from signed effect')
    require(view['record']==cut.data['projection']['subjects'][effect['source_version_ref']]['record'],
        'represented record differs from original signed source')
    return effect


def governance_state(previous, effect):
    state=copy.deepcopy(previous)
    operation=effect['source_effect']
    state['provenance'].append({'source_ref':'source-store:'+effect['source_store_id']
        +'/transactions/'+str(effect['source_sequence'])+'#sha256='+effect['effect_transaction_sha256'],
        'relation':'source-eligibility-of-exact-represented-revision','operation':'map-verified-source-'+operation,
        'owner_route':effect['source_operator_ref'],
        'posture':effect['source_posture']+'; local-fixture-only; repository-admission:none'})
    if operation=='withdraw':
        state['candidate_or_maturity_status']='candidate-representation-with-source-withdrawn'
        state['residue'].append({'source_operation':'map-verified-source-withdraw',
            'expected_condition':'Current-source use requires a current eligible signed source revision.',
            'observed_remainder':'The exact source revision is locally withdrawn; its historical representation remains active.',
            'residue_type':'source-withdrawal-use-constraint','evidence_ref':effect['record_binding']['path'],
            'owner_route':'protocol:O02-source-currentness','treatment':'reject current-source use; retain inspectable history'})
    return state


class SourceEligibilityMapping:
    def __init__(self, native):
        require(type(native) is NativeCandidateStore, 'exact owned native store required')
        self.native=native;self.effects={};self.seen={};self.witnesses=[];self.uncertain=set()

    def apply(self, node, cut):
        self.native.guard()
        require(node in self.native.specs, 'native represented revision unavailable')
        effect=joined_effect(self.native.specs[node],cut)
        key=effect['effect_transaction_digest']
        require(node not in self.uncertain, 'uncertain native effect requires observational reconciliation')
        if (node,key) in self.seen:
            require(effect==self.seen[(node,key)]['effect'], 'replayed source effect changed')
            return {**copy.deepcopy(self.seen[(node,key)]),'idempotent':True}
        if effect['source_effect']=='admit':
            require(node not in self.effects, 'source admission cannot overwrite current mapped posture')
        else:
            require(node in self.effects and self.effects[node]['source_effect']=='admit', 'withdrawal requires exact prior source admission mapping')
            prior=self.effects[node]
            for field in ('source_store_id','source_scope_ref','source_operator_ref','source_version_ref','source_identity_ref',
                          'record_sha256','carrier_ref','config_sha256','baseline_snapshot_digest','record_transaction_sha256'):
                require(effect[field]==prior[field], 'source withdrawal predecessor/configuration/record mismatch')
            require(cut.data['transactions'][2]['previous_digest']==prior['source_head'], 'withdrawal signed chain is not the mapped predecessor')
        semantic=self.native.latest_semantic(node)
        previous=self.native.latest_governance(semantic)['complete_resulting_governance_state']
        before={k:v for k,v in self.native.files().items() if k.startswith('semantic/')}
        state=governance_state(previous,effect)
        event=self.native.seal(governance=[self.native.governance_draft(semantic,state)])['governance'][0]
        witness={'effect':copy.deepcopy(effect),'native_semantic_ref':self.native.reference(semantic),
            'native_governance_event_id':event['event_id'],'native_governance_event_digest':event['event_digest'],
            'source_eligible':effect['source_eligible'],'representation_lifecycle':semantic['complete_resulting_semantic_state']['lifecycle'],
            'semantic_bytes_unchanged':True,'idempotent':False,'authority_effect':'none','actual_owner_outcome':None}
        # Record intent before append. An uncertain native write cannot be
        # automatically redispatched; cold original-byte reconciliation is needed.
        self.uncertain.add(node)
        self.native.append([],[event],witness)
        require(before=={k:v for k,v in self.native.files().items() if k.startswith('semantic/')}, 'source mapping changed native semantic bytes')
        self.effects[node]=copy.deepcopy(effect);self.seen[(node,key)]=copy.deepcopy(witness);self.witnesses.append(witness)
        self.uncertain.remove(node)
        return copy.deepcopy(witness)

    def current_source(self, node, cut):
        self.native.guard()
        require(node not in self.uncertain and node in self.effects, 'source eligibility has no certain mapped effect')
        effect=joined_effect(self.native.specs[node],cut)
        require(effect==self.effects[node], 'source cut is not the latest mapped source posture')
        require(effect['source_eligible'] is True, 'withdrawn source is ineligible for current-source use')
        return copy.deepcopy(cut.data['projection']['subjects'][effect['source_version_ref']]['record'])

    def historical_representation(self, node):
        self.native.guard()
        require(node in self.native.specs, 'historical represented revision unavailable')
        event=self.native.latest_semantic(node)
        return {'semantic_ref':self.native.reference(event),
            'state':copy.deepcopy(event['complete_resulting_semantic_state']),
            'source_effect':copy.deepcopy(self.effects.get(node)),
            'authority_effect':'none','actual_owner_outcome':None}
