"""Owned candidate ontology events over the inherited native EventStore."""
import copy
from pathlib import Path
import subprocess
import tempfile
import time

from translation import *


class NativeCandidateStore:
    def __init__(self, translator, executable, executable_sha256):
        self.translator = translator
        self.executable = Path(executable).resolve()
        self.executable_sha256 = executable_sha256
        require(sha(self.executable.read_bytes())==executable_sha256,'independent native executable pin differs')
        self.owned = tempfile.TemporaryDirectory(prefix='cal-O02-owned-ontology-')
        self.root = Path(self.owned.name)
        require(not self.root.is_relative_to(ROOT),'owned ontology store must be outside repository')
        self.semantic = self.root/'semantic';self.semantic.mkdir()
        self.governance = self.root/'governance';self.governance.mkdir()
        self.semantic_events = [];self.governance_events = []
        self.expected_files = {};self.closed = False;self.expires = time.monotonic()+900
        self.specs = {};self.witnesses = []
        self.sources = {}

    def files(self):
        files = {}
        for directory in [self.semantic,self.governance]:
            for path in directory.iterdir():
                require(path.is_file() and not path.is_symlink(),'unexpected native store entry')
                files[path.relative_to(self.root).as_posix()] = sha(path.read_bytes())
        return files

    def guard(self):
        require(not self.closed and self.root.is_dir() and time.monotonic()<self.expires,'owned candidate store closed or expired')
        self.translator.guard()
        require(not self.executable.is_symlink() and sha(self.executable.read_bytes())==self.executable_sha256,'native executable changed')
        require(self.files()==self.expected_files,'native original event closure changed')
        for source in self.sources.values():original(source)

    def call(self, mode, args, value=None):
        self.guard()
        if value is not None:
            path = self.root/('request-'+sha(canonical(value))+'.json')
            if not path.exists():path.write_bytes(canonical(value))
            args = [*args,str(path)]
        child = subprocess.run([str(self.executable),mode,*map(str,args)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
        require(child.returncode==0,'native '+mode+' rejected: '+child.stderr.decode(errors='replace'))
        return parse(child.stdout)

    def seal(self, semantic=None, governance=None):
        return self.call('seal',[],{'semantic':semantic or [],'governance':governance or []})

    def identity(self, state):return state['identity']
    def stream(self, identity, family):
        return family+':'+identity['ontology_id']+':'+identity['subject_kind']+':'+identity['subject_id']

    def semantic_draft(self,state):
        identity = self.identity(state);stream = self.stream(identity,'semantic')
        previous = next((e['event_digest'] for e in reversed(self.semantic_events) if e['stream_id']==stream),None)
        cursor = len(self.semantic_events)+1
        return {'source_kind':'canonical_event','event_family':'semantic','event_id':'ontology-semantic:O02:'+str(cursor),
            'event_digest':'0'*64,'stream_id':stream,'subject_identity':identity,'previous_event_digest':previous,
            'semantic_cursor':cursor,'complete_resulting_semantic_state':copy.deepcopy(state)}

    def reference(self,event):
        return {'semantic_event_id':event['event_id'],'semantic_event_digest':event['event_digest'],'semantic_cursor':event['semantic_cursor']}

    def governance_draft(self,semantic,state):
        stream = self.stream(semantic['subject_identity'],'governance')
        previous = next((e['event_digest'] for e in reversed(self.governance_events) if e['stream_id']==stream),None)
        cursor = len(self.governance_events)+1
        reference = self.reference(semantic)
        require(state['semantic_ref']==reference,'governance must join exact current semantic tuple')
        return {'source_kind':'canonical_event','event_family':'governance','event_id':'ontology-governance:O02:'+str(cursor),
            'event_digest':'0'*64,'stream_id':stream,'semantic_ref':reference,'governance_cursor':cursor,
            'previous_event_digest':previous,'complete_resulting_governance_state':copy.deepcopy(state)}

    def basic_governance(self,semantic,source,operation):
        profile = self.translator.profile;reference = self.reference(semantic)
        confidence = {'scheme_ref':profile['confidence']['scheme_ref'],'level':'not-assessed'}
        return {'semantic_ref':reference,'provenance':[{'source_ref':source,'relation':'represents-exact-selected-revision',
                'operation':operation,'owner_route':'protocol:O02-candidate-review','posture':'candidate-representation-only'}],
            'owner_route':'protocol:O02-candidate-review','candidate_or_maturity_status':'candidate-unadmitted',
            'promotion_state_or_handle':'not-promoted','authority_kind_and_posture':{'kind':'candidate-representation','posture':'no-source-admission-authority'},
            'authority_effect':'none','evidence_confidence':copy.deepcopy(confidence),'commitment_confidence':copy.deepcopy(confidence),
            'challenge_contract':{'challenge_response':'Inspect exact represented revision, source witnesses and native event joins.',
                'valid_challenge_modes':['evidence','contradiction','owner_review'],'contradiction_edges':[],'validation_edges':[],
                'owner_route':'protocol:O02-candidate-review','resolution_gate':'protocol:O02-final-exact-owner-review',
                'blocking_questions':[],'challenge_residue_route':'protocol:O02-candidate-review'},
            'residue':[],'conflicts':[],'drift_owner':'protocol:O02-source-currentness',
            'invalidation_route':'protocol:O02-original-source-byte-drift'}

    def append(self,semantic,governance,witness):
        self.guard()
        # A successful library append is still only an explicitly owned test
        # store operation. It has no ontology adoption or source admission.
        self.call('append',[self.semantic,self.governance],{'semantic':semantic,'governance':governance})
        self.semantic_events.extend(copy.deepcopy(semantic));self.governance_events.extend(copy.deepcopy(governance))
        self.expected_files = self.files()
        self.witnesses.append(copy.deepcopy(witness))
        actual = self.read()
        require(actual['semantic_events']==self.semantic_events and actual['governance_events']==self.governance_events,
            'native replay differs from exact appended original events')
        return actual

    def map_node(self,view):
        spec = self.translator.node_spec(view)
        require(spec['node_id'] not in self.specs,'same exact source node already mapped')
        draft_ref = {'semantic_event_id':'ontology-semantic:O02:'+str(len(self.semantic_events)+1),
            'semantic_event_digest':'0'*64,'semantic_cursor':len(self.semantic_events)+1}
        draft_record = self.translator.rich_record(spec,draft_ref,[])
        state,_ = self.translator.translate_node(draft_record,spec)
        semantic = self.seal([self.semantic_draft(state)])['semantic'][0]
        gs = self.basic_governance(semantic,view['carrier']['source_binding']['path'],'map-selected-source-revision')
        governance = self.seal(governance=[self.governance_draft(semantic,gs)])['governance'][0]
        record = self.translator.rich_record(spec,self.reference(semantic),[governance['event_id']])
        actual_state,witness = self.translator.translate_node(record,spec)
        require(actual_state==state,'final Node/v2 translation differs from sealed native state')
        witness['rich_record']=record;witness['source_view']=copy.deepcopy(view)
        for binding in [view['carrier']['source_binding'],view['carrier']['schema_binding']]+[d['source_binding'] for d in witness['definition_witnesses']]:
            self.sources[binding['path']]=copy.deepcopy(binding)
        self.append([semantic],[governance],witness);self.specs[spec['node_id']]=spec
        return spec['node_id'],witness

    def latest_semantic(self, subject_id):
        return next(e for e in reversed(self.semantic_events) if e['subject_identity']['subject_id']==subject_id)

    def latest_governance(self,semantic):
        return next(e for e in reversed(self.governance_events) if e['semantic_ref']==self.reference(semantic))

    def map_relation(self,view,cut_view,endpoint_nodes):
        self.translator.adapter.validate_candidate_relations(cut_view)
        record = view['record'];p = record['payload']
        require(view==cut_view['views'].get(view['represented_subject']['version_ref']),'relation view is outside the validated exact cut')
        require(view['carrier']['kind']=='typed-relation','not a typed source relation')
        for endpoint in [p['source'],p['target']]:
            require(endpoint['version_ref'] in endpoint_nodes,'exact native endpoint revision unresolved')
            node = endpoint_nodes[endpoint['version_ref']]
            spec = self.specs[node]
            require(spec['subject']['version_ref']==endpoint['version_ref'] and spec['subject']['identity']==endpoint['ref']
                and spec['subject']['kind']==endpoint['kind'],'native endpoint represented tuple differs')
        properties = {'relation_kind_ref':p['relation_kind_ref'],'relation_version_ref':view['represented_subject']['version_ref'],
            'source_version_ref':p['source']['version_ref'],'target_version_ref':p['target']['version_ref'],
            'record_sha256':view['carrier']['source_binding']['sha256'],'qualifiers_sha256':sha(canonical(p['qualifiers'])),
            'mapping_sha256':view['mapping_binding']['sha256']}
        check_schema(properties,self.translator.profile['property_schema_bindings']['relation'])
        identity = {'subject_id':'ontology-relation:'+sha(canonical(properties)),
            'ontology_id':self.translator.profile['ontology_ref'],'subject_kind':'relation','type_ref':p['relation_kind_ref']}
        state = {'identity':identity,'lifecycle':'active','source_node_id':endpoint_nodes[p['source']['version_ref']],
            'target_node_id':endpoint_nodes[p['target']['version_ref']],'direction':'directed',
            'typed_properties':{'profile_ref':self.translator.profile['relation_profile_ref'],'values':properties},
            'forbidden_collapse':[{'left_ref':identity['subject_id'],'right_ref':'semantic-axis:source-typed-relation',
                'context':identity['ontology_id'],'intended_use':'candidate exact relation representation'}]}
        semantic = self.seal([self.semantic_draft(state)])['semantic'][0]
        gs = self.basic_governance(semantic,view['carrier']['source_binding']['path'],'map-selected-typed-connection')
        governance = self.seal(governance=[self.governance_draft(semantic,gs)])['governance'][0]
        witness = {'source_typed_relation':copy.deepcopy(view),'exact_source_revision':p['source']['version_ref'],
            'exact_target_revision':p['target']['version_ref'],'qualifiers':copy.deepcopy(p['qualifiers']),
            'native_semantic_ref':self.reference(semantic),'confirmed_global_edge_eligible':False,
            'authority_effect':'none','actual_owner_outcome':None}
        for binding in [view['carrier']['source_binding'],view['carrier']['schema_binding']]:self.sources[binding['path']]=copy.deepcopy(binding)
        self.append([semantic],[governance],witness)
        return identity['subject_id'],witness

    def map_challenge(self,node_id,event_row,contract_row,decision_row=None):
        self.guard()
        event = parse(original({k:event_row[k] for k in ['path','sha256']}))
        contract = parse(original({k:contract_row[k] for k in ['path','sha256']}))
        adapter = self.translator.adapter
        adapter.represent({k:event_row[k] for k in ['path','sha256','kind','version_ref']})
        adapter.represent({k:contract_row[k] for k in ['path','sha256','kind','version_ref']})
        spec = self.specs[node_id];p = event['payload'];cp = contract['payload']
        require(p['subject_ref']==spec['subject']['identity'] and p['subject_version_ref']==spec['subject']['version_ref'],
            'challenge subject identity/revision mismatch')
        require(p['challenge_contract_ref']==contract_row['version_ref'] and p['ground'] in cp['grounds']
            and spec['source_view']['carrier']['kind'] in cp['challengeable_subject_kinds'],'challenge contract/ground/subject mismatch')
        decision_binding = None
        if p['response_state']=='resolved-for-revision':
            require(decision_row is not None and decision_row['kind']=='decision'
                and decision_row['version_ref']==p['resolution_decision_ref'],'exact source resolution Decision missing')
            decision_binding = {k:decision_row[k] for k in ['path','sha256']}
            decision = parse(original(decision_binding))
            adapter.represent({k:decision_row[k] for k in ['path','sha256','kind','version_ref']})
            require(decision['payload']['subject_refs'] and all(r.startswith(event['node_id']+'@') for r in decision['payload']['subject_refs']),
                'source Decision targets a different contest identity')
            require(decision['payload']['selected_outcome']=='fixture-accept-contest-for-revision',
                'candidate source Decision does not select the declared local contest disposition')
        else:
            require(p['resolution_decision_ref']=='none','unresolved source contest invents a Decision')
        semantic = self.latest_semantic(node_id);current = self.latest_governance(semantic)
        before = {k:v for k,v in self.files().items() if k.startswith('semantic/')}
        state = copy.deepcopy(current['complete_resulting_governance_state'])
        state['provenance'].append({'source_ref':event_row['path']+'#sha256='+event_row['sha256'],
            'relation':'challenges-exact-represented-revision','operation':'map-challenge-'+p['response_state'],
            'owner_route':cp['owner_route'],'posture':'candidate-source-event; no owner outcome inferred'})
        modes = {'evidence':'evidence','contradiction':'contradiction','owner-review':'owner_review'}
        require(all(m in modes for m in cp['response_modes']),'undeclared native challenge mode')
        state['challenge_contract']={'challenge_response':'Inspect the exact source Challenge Event and its bound Contract.',
            'valid_challenge_modes':[modes[m] for m in cp['response_modes']],
            'contradiction_edges':[],'validation_edges':[],'owner_route':cp['owner_route'],
            'resolution_gate':'source-gate:'+sha(cp['resolution_gate_ref'].encode()),
            'blocking_questions':[] if p['response_state']=='resolved-for-revision' else [p['ground']],
            'challenge_residue_route':cp['unresolved_residue_route']}
        state['conflicts']=[] if p['response_state']=='resolved-for-revision' else [{'conflict_id':'challenge:'+sha(event_row['version_ref'].encode()),
            'conflict_type':p['ground'],'statement':'Exact source contest state: '+p['response_state'],'owner_route':cp['owner_route']}]
        if decision_binding:
            state['residue'].append({'source_operation':'map-candidate-fixture-contest-disposition',
                'expected_condition':'Actual owner authority and canonical contest disposition remain separate review obligations.',
                'observed_remainder':'The source Decision is a scoped candidate fixture disposition only.',
                'residue_type':'actual-owner-authority-unverified','evidence_ref':decision_binding['path'],
                'owner_route':'protocol:deferred-owner-decision:R08','treatment':'retain exact source and review boundary'})
        governance = self.seal(governance=[self.governance_draft(semantic,state)])['governance'][0]
        witness = {'challenge_event_binding':{k:event_row[k] for k in ['path','sha256']},
            'challenge_contract_binding':{k:contract_row[k] for k in ['path','sha256']},
            'source_event_revision':event_row['version_ref'],'source_contract_revision':contract_row['version_ref'],
            'source_resolution_decision_ref':p['resolution_decision_ref'],'source_resolution_gate_ref':cp['resolution_gate_ref'],
            'native_gate_identifier':state['challenge_contract']['resolution_gate'],'native_semantic_ref':self.reference(semantic),
            'source_response_state':p['response_state'],'actual_owner_outcome':None,'authority_effect':'none'}
        witness['source_resolution_decision_binding']=decision_binding
        for binding in [witness['challenge_event_binding'],witness['challenge_contract_binding']]:self.sources[binding['path']]=copy.deepcopy(binding)
        if decision_binding:self.sources[decision_binding['path']]=copy.deepcopy(decision_binding)
        self.append([],[governance],witness)
        after = {k:v for k,v in self.files().items() if k.startswith('semantic/')}
        require(before==after,'governance-only challenge mutated semantic original bytes')
        return {**witness,'semantic_bytes_unchanged':True}

    def change_lifecycle(self,subject_id,next_state):
        self.guard();require(next_state in ('active','retired','removed'),'undeclared ontology lifecycle')
        current = self.latest_semantic(subject_id)
        state = copy.deepcopy(current['complete_resulting_semantic_state']);state['lifecycle']=next_state
        semantic = self.seal([self.semantic_draft(state)])['semantic'][0]
        old = self.latest_governance(current)['complete_resulting_governance_state']
        gs = copy.deepcopy(old);gs['semantic_ref']=self.reference(semantic)
        gs['provenance'].append({'source_ref':subject_id,'relation':'representation-lifecycle-only',
            'operation':'candidate-'+next_state,'owner_route':'protocol:O02-candidate-review','posture':'no source withdrawal or source admission'})
        governance = self.seal(governance=[self.governance_draft(semantic,gs)])['governance'][0]
        # Retire/remove an edge before its node; live endpoints are enforced by
        # the inherited reducer and each intermediate cut remains inspectable.
        return self.append([semantic],[governance],{'subject_id':subject_id,'ontology_lifecycle':next_state,
            'source_effects_applied':0,'authority_effect':'none','actual_owner_outcome':None})

    def read(self):
        require(self.semantic_events,'empty ontology has no cut')
        return self.call('read',[self.semantic,self.governance,len(self.semantic_events)])

    def export(self):
        self.guard()
        import base64
        return {'schema_version':'lab-O02-public-native-archive/v1-candidate','authority_effect':'none','actual_owner_outcome':None,
            'files':{str(path.relative_to(self.root)):{'sha256':sha(path.read_bytes()),
                'base64_original_bytes':base64.b64encode(path.read_bytes()).decode()}
                for directory in [self.semantic,self.governance] for path in directory.iterdir()},
            'native_executable_sha256':self.executable_sha256,'semantic_cursor':len(self.semantic_events),
            'governance_cursor':len(self.governance_events),'private_key_included':False,'Session_memory_included':False,
            'ontology_admission':False,'source_effects_applied':0}

    def close(self):
        self.closed = True;self.owned.cleanup()
