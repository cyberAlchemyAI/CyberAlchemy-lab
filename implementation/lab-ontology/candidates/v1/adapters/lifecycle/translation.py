"""Rich Node/v2 translation with exact Definition and source witnesses."""
import copy
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from represented_subjects import *

LIFECYCLE = Path(__file__).resolve().parent
PROFILE = LIFECYCLE/'profiles/translation-profile.json'
NODE_SCHEMA = ROOT/'authority/artifact-types/ontology-node/v2/schema.json'


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()


def check_schema(record,binding):
    schema = parse(original(binding))
    errors = list(Draft202012Validator(schema).iter_errors(record))
    require(not errors,'selected schema violation: '+('; '.join(e.message for e in errors[:2])))


def node_id(subject, profile):
    fields = [profile['ontology_ref'],profile['namespace'],subject['kind'],subject['identity'],
        subject['version_ref'],subject['carrier_bytes_sha256']]
    raw = b''.join(len(f.encode()).to_bytes(8,'big')+f.encode() for f in fields)
    return 'ontology-node:'+sha(raw)


class RichTranslation:
    def __init__(self, adapter, profile_binding):
        self.adapter = adapter
        self.profile_binding = copy.deepcopy(profile_binding)
        self.profile = parse(original(profile_binding))
        require(profile_binding['path']==PROFILE.relative_to(ROOT).as_posix(),'unselected native translation profile')
        require(self.profile['authority_effect']=='none' and self.profile['actual_owner_outcome'] is None,'profile claims authority')
        self.node_schema_binding = bind(NODE_SCHEMA)
        self.profile_sha = object_sha(self.profile)

    def guard(self):
        self.adapter.guard()
        require(object_sha(self.profile)==self.profile_sha and parse(original(self.profile_binding))==self.profile,'translation profile changed')
        original(self.node_schema_binding)
        for binding in self.profile['property_schema_bindings'].values():original(binding)

    def definition(self, exact_ref):
        subjects = self.adapter.catalog['subjects']
        require(exact_ref in subjects,'exact Definition revision unresolved')
        row = subjects[exact_ref]
        require(row['kind']=='definition' and row['effective_state'] in ('admitted-current','local-admitted-current'),'Definition revision ineligible')
        record = parse(original(row['source']))
        require(record==row['record'] and exact_ref==record['definition_id']+'@'+record['version'],'Definition original/revision mismatch')
        selected = pointer(record,self.profile['definition_selector'])
        require(type(selected) is dict and selected.get('normative_statement'),'selected Definition voice unresolved')
        digest = sha(canonical(selected))
        return {'reference':{'definition_id':record['definition_id'],'selector_sha256':digest},
            'witness':{'version_ref':exact_ref,'source_binding':copy.deepcopy(row['source']),
                'selector':self.profile['definition_selector'],'selector_sha256':digest},'term':record['term']}

    def node_spec(self, view):
        self.guard()
        source = view['carrier']['source_binding'];ref = view['represented_subject']['version_ref']
        require(self.adapter.represent({**source,'kind':view['carrier']['kind'],'version_ref':ref})==view,'source view changed')
        carrier = view['carrier']['ref']
        require(carrier in self.adapter.catalog['contracts'],'rich source carrier is not in selected signed catalog')
        source_defs = self.adapter.catalog['contracts'][carrier]['semantic_definition_refs']
        require(source_defs,'rich source carrier has no selected Definition')
        refs = ['cal.definition.ontology-node@1.0.0-candidate.1']+source_defs
        refs = list(dict.fromkeys(refs))
        definitions = {r:self.definition(r) for r in refs}
        subject = view['represented_subject'];ident = node_id(subject,self.profile)
        components = [{'name':'ontology-representation','type_ref':'cal.artifact-type.ontology-node/v2',
            'definition_ref':refs[0]}]+[{'name':'represented-'+definitions[r]['reference']['definition_id'],
            'type_ref':carrier,'definition_ref':r} for r in source_defs]
        properties = {'carrier_ref':carrier,'carrier_kind':view['carrier']['kind'],'represented_kind':subject['kind'],
            'identity_ref':subject['identity'],'version_ref':ref,'record_sha256':source['sha256'],
            'schema_sha256':view['carrier']['schema_binding']['sha256'],'mapping_sha256':view['mapping_binding']['sha256']}
        check_schema(properties,self.profile['property_schema_bindings']['node'])
        label = view['record'].get('name',subject['identity'])
        return {'node_id':ident,'subject':copy.deepcopy(subject),'source_view':copy.deepcopy(view),
            'definitions':definitions,'components':components,'properties':properties,'label':label,
            'proposition':'Represents the exact '+view['carrier']['kind']+' revision '+ref+'; source admission and action authority remain separate.',
            'scope_ref':view['record'].get('scope_ref','scope:lab-candidate-representation')}

    def signed_source_effect(self,view):
        """Resolve actual source transaction bytes, not an Artifact record label."""
        self.guard()
        import base64
        source = view['signed_catalog_subject_binding']
        require(source is not None and 'selector' in source and 'store_id' in source,'source is not a selected signed local transaction')
        archive = parse(original(bind(ARCHIVE)))
        require(sha(ARCHIVE.read_bytes())==ARCHIVE_SHA and source['path'] in archive['files'],'signed source transaction absent')
        selected = archive['files'][source['path']]
        raw = base64.b64decode(selected['base64_original_bytes'],validate=True)
        require(sha(raw)==selected['sha256'],'original source transaction bytes changed')
        tx = parse(raw);value = tx
        for part in source['selector'].strip('/').split('/'):
            value = value[int(part)] if isinstance(value,list) else value[part]
        require(value==view['record'],'signed transaction selector differs from represented record')
        require(source['sha256']==sha((json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()),
            'signed source record digest differs')
        targets = [t for t in tx['proposal']['targets'] if t['version_ref']==view['represented_subject']['version_ref']]
        require(len(targets)==1 and targets[0]['record']==value and targets[0]['operation']=='admit','signed source effect mismatch')
        histories = self.adapter.catalog['histories']
        return {'archive_binding':bind(ARCHIVE),'original_transaction_binding':{'archive_path':source['path'],'sha256':selected['sha256']},
            'record_selector':source['selector'],'record_sha256':source['sha256'],'transaction_digest':tx['digest'],
            'source_store_id':source['store_id'],'source_scope_ref':tx['proposal']['scope_ref'],
            'source_operator_ref':tx['approval']['owner_ref'],'source_effect':'admit',
            'source_version_ref':targets[0]['version_ref'],'source_posture':view['source_admission'],
            'project_histories':{k:{'identity_ref':v['node_id'],'cursor':len(v['payload']['events']),
                'chain_digest':v['payload']['chain_digest']} for k,v in histories.items()},
            'source_admission_is_repository_admission':False,'actual_owner_outcome':None,'authority_effect':'none'}

    def rich_record(self,spec,semantic_ref,governance_refs):
        record = {'schema_version':'cyberalchemy-lab-ontology-node/v2','kind':'ontology-node','node_id':spec['node_id'],
            'name':spec['label'],'record_state':'candidate','authority_effect':'none','owner_ref':'protocol:O02-candidate-representation-owner',
            'scope_ref':spec['scope_ref'],'evidence_refs':[spec['source_view']['carrier']['source_binding']['path']],
            'challenge_route':'protocol:O02-exact-representation-review','successor_refs':[],
            'claim_ceiling':self.profile['claim_ceiling'],'payload':{
                'ontology_ref':self.profile['ontology_ref'],'ontology_manifest_ref':'protocol:O02-owned-event-archive',
                'node_type_ref':self.profile['node_type_ref'],'profile_ref':self.profile['node_profile_ref'],'branch':'mixed',
                'represented_subject':{'kind':spec['subject']['kind'],'ref':spec['subject']['identity'],
                    'version_ref':spec['subject']['version_ref'],'digest':spec['subject']['carrier_bytes_sha256']},
                'semantic_state':{'lifecycle':'active','label':spec['label'],'proposition':spec['proposition'],
                    'semantic_components':[c['name'] for c in spec['components']],
                    'semantic_definition_refs':list(spec['definitions']),'typed_properties':copy.deepcopy(spec['properties']),
                    'use_obligations':copy.deepcopy(self.profile['use_obligations']),
                    'forbidden_collapse':copy.deepcopy(self.profile['forbidden_collapse'])},
                'governance_binding':{'semantic_event_ref':copy.deepcopy(semantic_ref),'governance_event_refs':list(governance_refs),
                    'evidence_confidence_ref':self.profile['confidence']['scheme_ref']+'#evidence:not-assessed',
                    'commitment_confidence_ref':self.profile['confidence']['scheme_ref']+'#commitment:not-assessed',
                    'challenge_contract_ref':'protocol:O02-exact-representation-review','authority_effect':'none'},
                'provenance_refs':[spec['source_view']['carrier']['source_binding']['path']],'replay_source':False}}
        check_schema(record,self.node_schema_binding)
        return record

    def translate_node(self,record,spec):
        self.guard();check_schema(record,self.node_schema_binding)
        require(self.node_spec(spec['source_view'])==spec,'rich source specification was altered')
        p = record['payload'];s = p['semantic_state']
        require(p['profile_ref']==self.profile['node_profile_ref'],'undeclared native Node profile')
        require(record['node_id']==spec['node_id'] and p['ontology_ref']==self.profile['ontology_ref']
            and p['node_type_ref']==self.profile['node_type_ref'],'ontology identity/profile mismatch')
        expected = {'kind':spec['subject']['kind'],'ref':spec['subject']['identity'],
            'version_ref':spec['subject']['version_ref'],'digest':spec['subject']['carrier_bytes_sha256']}
        require(p['represented_subject']==expected,'represented source identity/revision/digest mismatch')
        require(s['semantic_definition_refs']==list(spec['definitions']),'Definition selection differs')
        resolved = {r:self.definition(r) for r in s['semantic_definition_refs']}
        require(resolved==spec['definitions'],'Definition witness changed')
        require(s['semantic_components']==[c['name'] for c in spec['components']],'component binding incomplete')
        require(s['typed_properties']==spec['properties'],'rich properties changed or dropped')
        check_schema(s['typed_properties'],self.profile['property_schema_bindings']['node'])
        require(s['use_obligations']==self.profile['use_obligations'] and s['forbidden_collapse']==self.profile['forbidden_collapse'],
            'use or no-collapse declarations lost')
        require(s['label']==spec['label'] and s['proposition']==spec['proposition'] and record['scope_ref']==spec['scope_ref'],
            'rich semantic assertion/scope changed')
        state = {'identity':{'subject_id':record['node_id'],'ontology_id':p['ontology_ref'],'subject_kind':'node','type_ref':p['node_type_ref']},
            'lifecycle':s['lifecycle'],'label':s['label'],'definition_or_claim':s['proposition'],'scope':record['scope_ref'],
            'semantic_components':[{'component_id':c['name'],'type_ref':c['type_ref'],
                'definition_ref':resolved[c['definition_ref']]['reference']} for c in spec['components']],
            'semantic_definition_refs':[r['reference'] for r in resolved.values()],
            'typed_properties':{'profile_ref':p['profile_ref'],'values':copy.deepcopy(s['typed_properties'])},
            'use_obligations':[{'obligation_id':'use-obligation:'+sha(v.encode()),'requirement':v,'applies_to_use':p['profile_ref']} for v in s['use_obligations']],
            'forbidden_collapse':[{'left_ref':record['node_id'],'right_ref':'semantic-axis:'+v,
                'context':p['ontology_ref'],'intended_use':p['profile_ref']} for v in s['forbidden_collapse']],
            'profile_ref':p['profile_ref']}
        witness = {'source_node_sha256':sha(canonical(record)),'source_node_schema_binding':copy.deepcopy(self.node_schema_binding),
            'translation_profile_binding':copy.deepcopy(self.profile_binding),
            'definition_witnesses':[r['witness'] for r in resolved.values()],
            'component_bindings':copy.deepcopy(spec['components']),'source_governance_binding':copy.deepcopy(p['governance_binding']),
            'authority_effect':'none','actual_owner_outcome':None}
        return state,witness
