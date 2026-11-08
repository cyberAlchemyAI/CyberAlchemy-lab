"""Pure selected Mapper byte validators. No IO, execution, or host authority.

Native struct order follows the independently pinned runtime lib.rs. Native
floating Value codecs are deliberately unsupported until qualified, never
silently normalized. Historical fixture success is not fresh-source evidence.
"""
from __future__ import annotations

import copy
import functools
import hashlib
import json
import math
import re

MAX = 4 * 1024 * 1024
ZERO = '0' * 64
NATIVE_SHA = 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'


class Refusal(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise Refusal(code)


def boundary(function):
    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Refusal as error:
            raise Refusal(error.args[0]) from None
        except Exception:
            raise Refusal('INVALID_VALIDATOR_INPUT') from None
    return wrapped


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def hexhash(x):
    return type(x) is str and re.fullmatch('[0-9a-f]{64}', x) is not None


def fields(value, keys):
    need(type(value) is dict and set(value) == set(keys), 'CLOSED_FIELDS')


def integer(x, low=0, high=2**64-1):
    return type(x) is int and low <= x <= high


def _domain(value, depth=0):
    need(depth <= 64, 'JSON_DEPTH')
    if type(value) is dict:
        need(len(value) <= 65536, 'JSON_COUNT')
        for key, item in value.items():
            need(type(key) is str, 'JSON_KEY')
            _domain(key, depth+1); _domain(item, depth+1)
    elif type(value) is list:
        need(len(value) <= 65536, 'JSON_COUNT')
        for item in value: _domain(item, depth+1)
    elif type(value) is str:
        need(len(value) <= MAX and not any(0xD800 <= ord(c) <= 0xDFFF for c in value), 'JSON_STRING')
    elif type(value) is float:
        need(math.isfinite(value), 'JSON_FINITE')
    elif type(value) is int:
        need(-2**63 <= value <= 2**64-1, 'JSON_INTEGER')
    else:
        need(value is None or type(value) is bool, 'JSON_TYPE')


def parse(raw, *, maximum=MAX):
    need(type(raw) is bytes and integer(maximum, 1, 32*MAX) and 0 < len(raw) <= maximum, 'JSON_BOUND')
    depth, quoted, escape = 0, False, False
    for c in raw:
        if quoted:
            if escape: escape = False
            elif c == 92: escape = True
            elif c == 34: quoted = False
        elif c == 34: quoted = True
        elif c in (91,123):
            depth += 1; need(depth <= 64, 'JSON_DEPTH')
        elif c in (93,125):
            depth -= 1; need(depth >= 0, 'JSON_SYNTAX')
    def pairs(rows):
        d = {}
        for k,v in rows:
            need(k not in d, 'JSON_DUPLICATE');d[k]=v
        return d
    def invalid(_): raise Refusal('JSON_FINITE')
    try:
        value = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)
        _domain(value)
        return value
    except (ValueError, UnicodeError, RecursionError):
        raise Refusal('JSON_INVALID') from None


def selected(raw, expected_sha256):
    need(hexhash(expected_sha256) and type(raw) is bytes and len(raw) <= MAX
         and sha(raw) == expected_sha256, 'SELECTION_DRIFT')
    return parse(raw)


def encoded(value):
    """Exact historical base.encoded, separate from native struct serializer."""
    _domain(value)
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)+'\n').encode()


# Tuple schemas retain Rust declaration order; ('list',...), ('opt',...),
# ('enum',...) are type constructors. 'value' is serde_json::Value/BTreeMap.
IDENTITY = (('subject_id','str'),('ontology_id','str'),('subject_kind',('enum','node','relation')),('type_ref','str'))
DEFINITION = (('definition_id','str'),('selector_sha256','hash'))
COMPONENT = (('component_id','str'),('type_ref','str'),('definition_ref',DEFINITION))
PROPERTY = (('profile_ref','str'),('values','map'))
OBLIGATION = (('obligation_id','str'),('requirement','str'),('applies_to_use','str'))
COLLAPSE = (('left_ref','str'),('right_ref','str'),('context','str'),('intended_use','str'))
NODE = (('identity',IDENTITY),('lifecycle',('enum','active','retired','removed')),('label','str'),
        ('definition_or_claim','str'),('scope','str'),('semantic_components',('list',COMPONENT)),
        ('semantic_definition_refs',('list',DEFINITION)),('typed_properties',PROPERTY),
        ('use_obligations',('list',OBLIGATION)),('forbidden_collapse',('list',COLLAPSE)),('profile_ref','str'))
RELATION = (('identity',IDENTITY),('lifecycle',('enum','active','retired','removed')),
            ('source_node_id','str'),('target_node_id','str'),('direction',('enum','directed','symmetric')),
            ('typed_properties',PROPERTY),('forbidden_collapse',('list',COLLAPSE)))
SEMANTIC = (('source_kind',('enum','canonical_event')),('event_family',('enum','semantic')),
            ('event_id','str'),('event_digest','hash'),('stream_id','str'),('subject_identity',IDENTITY),
            ('previous_event_digest',('opt','hash')),('semantic_cursor','u64'),
            ('complete_resulting_semantic_state','state'))
SEMREF = (('semantic_event_id','str'),('semantic_event_digest','hash'),('semantic_cursor','u64'))
PROVENANCE = (('source_ref','str'),('relation','str'),('operation','str'),('owner_route','str'),('posture','str'))
AUTHORITY = (('kind','str'),('posture','str'))
CONFIDENCE = (('scheme_ref','str'),('level','str'))
EDGE = (('kind',('enum','relation_id','selector')),('ref','str'))
CHALLENGE = (('challenge_response','str'),('valid_challenge_modes',('list',('enum','evidence','contradiction','owner_review'))),
             ('contradiction_edges',('list',EDGE)),('validation_edges',('list',EDGE)),('owner_route','str'),
             ('resolution_gate','str'),('blocking_questions',('list','str')),('challenge_residue_route','str'))
RESIDUE = tuple((n,'str') for n in ('source_operation','expected_condition','observed_remainder','residue_type','evidence_ref','owner_route','treatment'))
CONFLICT = tuple((n,'str') for n in ('conflict_id','conflict_type','statement','owner_route'))
GOVSTATE = (('semantic_ref',SEMREF),('provenance',('list',PROVENANCE)),('owner_route','str'),
            ('candidate_or_maturity_status','str'),('promotion_state_or_handle','str'),('authority_kind_and_posture',AUTHORITY),
            ('authority_effect',('enum','none')),('evidence_confidence',CONFIDENCE),('commitment_confidence',CONFIDENCE),
            ('challenge_contract',CHALLENGE),('residue',('list',RESIDUE)),('conflicts',('list',CONFLICT)),
            ('drift_owner','str'),('invalidation_route','str'))
GOVERNANCE = (('source_kind',('enum','canonical_event')),('event_family',('enum','governance')),('event_id','str'),
              ('event_digest','hash'),('stream_id','str'),('semantic_ref',SEMREF),('governance_cursor','u64'),
              ('previous_event_digest',('opt','hash')),('complete_resulting_governance_state',GOVSTATE))
FIXTURE = (('semantic',('list',SEMANTIC)),('governance',('list',GOVERNANCE)))
REFERENCE = (('identity',IDENTITY),('source_event_id','str'),('source_event_digest','hash'),('source_cursor','u64'))
PROJECTED = REFERENCE + (('semantic_state','state'),)
CUT = (('schema_version',('enum','cal-consistent-ontology-cut/v2-candidate')),('authority_effect',('enum','none')),
       ('semantic_cursor','u64'),('source_event_count','u64'),('source_event_set_digest','hash'),('subjects',('list',PROJECTED)))
SELECTOR = (('semantic_cursor','u64'),('required_subject_set',('list',IDENTITY)),
            ('governance_join_policy',('enum','require-exact')),('intended_use','str'),
            ('projection_profile',('enum','test-complete-profile/v1')))
REQUEST = (('selector_ref','str'),('selector',SELECTOR),('governance_cursor','u64'))
CONTEXT = (('context_selector_ref','str'),('source_cursor','u64'),('source_event_set_digest','hash'),
           ('selected_node_ids',('list','str')),('selected_relation_ids',('list','str')),('allowed_readings',('list','str')),
           ('forbidden_authority_moves',('list','str')),('projection_body',(('subjects',('list',REFERENCE)),)))
VIEW = (('identity',IDENTITY),('semantic_state',NODE),('governance_state',GOVSTATE),('semantic_event_id','str'),
        ('semantic_event_digest','hash'),('semantic_cursor','u64'),('governance_event_refs',('list','str')),
        ('calculated_view_digest','hash'),('context_selector_ref',('opt','str')))
OUTPUT = (('schema_version',('enum','lab-native-context-read/v1-candidate')),('authority_effect',('enum','none')),
          ('cut',CUT),('context',CONTEXT),('governance_cursor','u64'),('governance_event_refs',('list','str')),
          ('governed_nodes',('list',VIEW)))


def ordered(value, schema, depth=0):
    need(depth <= 64, 'NATIVE_DEPTH')
    if type(schema) is str:
        if schema == 'map':
            need(type(value) is dict, 'NATIVE_MAP')
            return ordered(value,'value',depth+1)
        if schema == 'state':
            need(type(value) is dict and type(value.get('identity')) is dict, 'STATE_SHAPE')
            return ordered(value, NODE if value['identity'].get('subject_kind') == 'node' else RELATION, depth+1)
        if schema == 'value':
            if type(value) is float: raise Refusal('UNQUALIFIED_NATIVE_FLOAT_CODEC')
            if type(value) is dict:
                need(all(type(k) is str for k in value), 'VALUE_KEY')
                return {k:ordered(value[k],'value',depth+1) for k in sorted(value)}
            if type(value) is list: return [ordered(x,'value',depth+1) for x in value]
            _domain(value, depth)
            return value
        need((schema == 'str' and type(value) is str and len(value) > 0)
             or (schema == 'hash' and hexhash(value)) or (schema == 'u64' and integer(value)), 'NATIVE_TYPE')
        return value
    if schema[0] == 'list':
        need(type(value) is list and len(value) <= 65536, 'NATIVE_LIST')
        return [ordered(v,schema[1],depth+1) for v in value]
    if schema[0] == 'opt':
        return None if value is None else ordered(value,schema[1],depth+1)
    if schema[0] == 'enum':
        need(type(value) is str and value in schema[1:], 'NATIVE_ENUM');return value
    fields(value,[key for key,_ in schema])
    return {key:ordered(value[key],spec,depth+1) for key,spec in schema}


def native_bytes(value, schema, *, pretty=False):
    _domain(value)
    value = ordered(value, schema)
    return (json.dumps(value, ensure_ascii=False, allow_nan=False,
                       **({'indent':2} if pretty else {'separators':(',',':')}))+'\n').encode()


def zero_root_digest(raw, field):
    """Replace only selected root string token; retain exact remaining UTF-8 bytes."""
    need(type(raw) is bytes and 0 < len(raw) <= MAX and field in ('event_digest','calculated_view_digest'), 'DIGEST_INPUT')
    text = raw.decode('utf-8'); decoder = json.JSONDecoder();i=1;found=[]
    need(text.startswith('{') and text.endswith('}\n'), 'DIGEST_CANONICAL')
    while i < len(text) and text[i] != '}':
        key,end=decoder.raw_decode(text,i);need(text[end]==':','DIGEST_CANONICAL')
        start=end+1;value,end=decoder.raw_decode(text,start)
        if key == field:
            need(hexhash(value), 'DIGEST_TOKEN');found.append((start,end))
        i=end
        if text[i] == ',':i+=1
        elif text[i] != '}':raise Refusal('DIGEST_CANONICAL')
    need(len(found)==1,'DIGEST_MEMBER')
    start,end=found[0]
    return (text[:start]+'"'+ZERO+'"'+text[end:]).encode()


@boundary
def exact_event(raw, family):
    need(family in ('semantic','governance'), 'EVENT_FAMILY')
    schema = SEMANTIC if family == 'semantic' else GOVERNANCE
    v = ordered(parse(raw,maximum=256*1024),schema)
    need(raw == native_bytes(v,schema), 'EVENT_NONCANONICAL')
    need(v['event_digest'] == sha(zero_root_digest(raw,'event_digest')), 'EVENT_DIGEST')
    return v


def _identity_key(i):
    return (i['subject_id'],i['ontology_id'],0 if i['subject_kind']=='node' else 1,i['type_ref'])


@boundary
def validate_events(semantic_raw, governance_raw):
    need(type(semantic_raw) is list and type(governance_raw) is list
         and len(semantic_raw)==len(governance_raw)==25, 'EVENT_COUNTS')
    sem=[exact_event(x,'semantic') for x in semantic_raw];gov=[exact_event(x,'governance') for x in governance_raw]
    ids=set(); node_ids=set(); versions=set()
    for index,(s,g) in enumerate(zip(sem,gov),1):
        i=s['subject_identity'];state=s['complete_resulting_semantic_state']
        key=_identity_key(i)
        need(key not in ids and s['semantic_cursor']==g['governance_cursor']==index
             and i['subject_kind']==('node' if index<=15 else 'relation'), 'EVENT_ORDER_IDENTITY')
        ids.add(key)
        need(state['identity']==i and state['lifecycle']=='active' and s['previous_event_digest'] is None
             and g['previous_event_digest'] is None, 'EVENT_STATE')
        need(s['event_id']=='semantic:'+i['subject_id'] and g['event_id']=='governance:'+i['subject_id']
             and s['stream_id']=='semantic:'+i['ontology_id']+':'+i['subject_kind']+':'+i['subject_id']
             and g['stream_id']==s['stream_id'].replace('semantic:','governance:',1), 'EVENT_STREAM')
        ref={'semantic_event_id':s['event_id'],'semantic_event_digest':s['event_digest'],'semantic_cursor':index}
        need(g['semantic_ref']==ref and g['complete_resulting_governance_state']['semantic_ref']==ref, 'GOVERNANCE_JOIN')
        if index<=15:node_ids.add(i['subject_id'])
        else:need(state['source_node_id'] in node_ids and state['target_node_id'] in node_ids
                  and state['direction']=='directed','RELATION_ENDPOINT')
    return sem,gov


@boundary
def validate_seal(input_raw, output_raw, *, expected_input_sha256, family, semantic_raw=None):
    inp=ordered(selected(input_raw,expected_input_sha256),FIXTURE)
    need(family in ('semantic','governance'), 'SEAL_FAMILY')
    other='governance' if family=='semantic' else 'semantic'
    need(len(inp[family])==25 and inp[other]==[], 'SEAL_COUNTS')
    out=ordered(parse(output_raw),FIXTURE)
    need(output_raw==native_bytes(out,FIXTURE) and len(out[family])==25 and out[other]==[], 'SEAL_CANONICAL')
    for old,new in zip(inp[family],out[family]):
        need(old['event_digest']==ZERO, 'SEAL_INPUT_DIGEST')
        copied=copy.deepcopy(new);copied['event_digest']=ZERO
        need(copied==old,'SEAL_MUTATED_CONTENT')
        exact_event(native_bytes(new,SEMANTIC if family=='semantic' else GOVERNANCE),family)
    if family=='governance':
        need(type(semantic_raw) is list,'SEMANTIC_SELECTION')
        validate_events(semantic_raw,[native_bytes(e,GOVERNANCE) for e in out[family]])
    return out[family]


@boundary
def validate_request(raw, sem):
    req=ordered(parse(raw),REQUEST)
    need(req['selector_ref']=='protocol:R03-exact-same-cut-domain-context'
         and req['governance_cursor']==req['selector']['semantic_cursor']==25
         and req['selector']['required_subject_set']==[s['subject_identity'] for s in sem]
         and req['selector']['intended_use']=='protocol:R03-read-current-scoped-project-state', 'REQUEST_JOIN')
    need(raw==encoded(req), 'REQUEST_ENCODING')
    return req


def expected_cold(sem,gov,req):
    sorted_sem=sorted(sem,key=lambda s:_identity_key(s['subject_identity']))
    def ref(s):return {'identity':s['subject_identity'],'source_event_id':s['event_id'],
                       'source_event_digest':s['event_digest'],'source_cursor':s['semantic_cursor']}
    refs=[ref(s) for s in sorted_sem];refs_digest=sha(native_bytes(refs,('list',REFERENCE)))
    cut={'schema_version':'cal-consistent-ontology-cut/v2-candidate','authority_effect':'none','semantic_cursor':25,
         'source_event_count':25,'source_event_set_digest':refs_digest,
         'subjects':[dict(ref(s),semantic_state=s['complete_resulting_semantic_state']) for s in sorted_sem]}
    context={'context_selector_ref':req['selector_ref'],'source_cursor':25,'source_event_set_digest':refs_digest,
             'selected_node_ids':sorted(s['subject_identity']['subject_id'] for s in sem[:15]),
             'selected_relation_ids':sorted(s['subject_identity']['subject_id'] for s in sem[15:]),
             'allowed_readings':['calculated-view-for-'+req['selector']['intended_use']],
             'forbidden_authority_moves':['admission-from-projection','acceptance-from-projection','publication-from-projection'],
             'projection_body':{'subjects':refs}}
    nodes=[]
    for s,g in zip(sem[:15],gov[:15]):
        view={'identity':s['subject_identity'],'semantic_state':s['complete_resulting_semantic_state'],
              'governance_state':g['complete_resulting_governance_state'],'semantic_event_id':s['event_id'],
              'semantic_event_digest':s['event_digest'],'semantic_cursor':s['semantic_cursor'],
              'governance_event_refs':[g['event_id']],'calculated_view_digest':ZERO,'context_selector_ref':req['selector_ref']}
        view['calculated_view_digest']=sha(native_bytes(view,VIEW));nodes.append(view)
    return {'schema_version':'lab-native-context-read/v1-candidate','authority_effect':'none','cut':cut,'context':context,
            'governance_cursor':25,'governance_event_refs':[g['event_id'] for g in gov],'governed_nodes':nodes}


@boundary
def validate_cold(first_raw, second_raw, *, semantic_raw, governance_raw, request_raw):
    sem,gov=validate_events(semantic_raw,governance_raw);req=validate_request(request_raw,sem)
    output=ordered(parse(first_raw),OUTPUT);expected=expected_cold(sem,gov,req)
    need(type(second_raw) is bytes and first_raw==second_raw, 'COLD_PARITY')
    need(output==expected, 'COLD_FULL_PROJECTION')
    need(first_raw==native_bytes(expected,OUTPUT,pretty=True), 'COLD_ENCODING')
    return {'authority_effect':'none','semantic_events':25,'governance_events':25,'nodes':15,'relations':10,
            'stdout_sha256':sha(first_raw),'fresh_runtime_qualified':False}


MAPPING_BASIS_FIELDS=('source_cut','source_name','source_closure','source_package_binding',
                      'source_assignment_interval_binding','policy_binding','projection_dispositions','rows')
MAPPING_FIXED={'schema_version':'lab-same-signed-cut-native-domain-mapping/v1-candidate',
               'semantic_cursor':25,'governance_cursor':25,'authority_effect':'none','actual_owner_outcome':None,
               'native_seal_processes':2,'actual_cold_native_read_processes':2,'native_domain_mapping_supplied':True,
               'context_or_ontology_view_carriers_generated':False,'public_API_operations_added':0,'active_Agents_created':0,
               'projection_is_host_permission':False,'native_representation_is_artifact_instance':False}


def _binding(value):
    fields(value,('path','sha256'));need(type(value['path']) is str and len(value['path'])>0
                                      and hexhash(value['sha256']), 'BINDING')


@boundary
def validate_mapping(raw, *, basis_raw, expected_basis_sha256, semantic_raw, governance_raw):
    basis=selected(basis_raw,expected_basis_sha256);fields(basis,MAPPING_BASIS_FIELDS)
    value=parse(raw);fields(value,(*MAPPING_BASIS_FIELDS,*MAPPING_FIXED))
    need(value==dict(basis,**MAPPING_FIXED) and raw==encoded(value), 'MAPPING_SELECTED_BASIS')
    for key in ('source_package_binding','source_assignment_interval_binding','policy_binding'):_binding(value[key])
    sem,gov=validate_events(semantic_raw,governance_raw)
    need(type(value['rows']) is list and len(value['rows'])==25,'MAPPING_ROWS')
    by_version={}
    for index,(row,s,g) in enumerate(zip(value['rows'],sem,gov)):
        common=('subject_identity','artifact','origin')
        fields(row,common+(('semantic_kind','definition_witnesses','schema_binding') if index<15 else
                           ('signature_binding','axis_ref','closed_signature','source','target','qualifiers')))
        a=row['artifact'];fields(a,('identity_ref','version_ref','carrier_ref','scope_ref','byte_sha256'))
        need(all(type(x) is str and len(x)>0 for x in a.values()) and hexhash(a['byte_sha256']), 'ARTIFACT')
        i=s['subject_identity'];state=s['complete_resulting_semantic_state'];props=state['typed_properties']['values']
        need(row['subject_identity']==i and i['subject_id']==i['subject_kind']+':'+sha(encoded(a))
             and props['record_sha256']==a['byte_sha256'] and props['mapping_sha256']==value['policy_binding']['sha256'], 'MAPPING_EVENT_JOIN')
        fields(row['origin'],('source_locator','encoding','enclosing_source_sha256'))
        need(g['complete_resulting_governance_state']['provenance'][0]['source_ref']==row['origin']['source_locator'], 'ORIGIN_JOIN')
        if index<15:
            need(a['version_ref'] not in by_version,'VERSION_DUPLICATE');by_version[a['version_ref']]=row
            need(props['carrier_ref']==a['carrier_ref'] and props['identity_ref']==a['identity_ref']
                 and props['version_ref']==a['version_ref'] and props['represented_kind']==row['semantic_kind']
                 and props['schema_sha256']==row['schema_binding']['sha256'], 'NODE_MAPPING_JOIN')
            refs=[{'definition_id':w['identity_ref'],'selector_sha256':w['selected_original_sha256']} for w in row['definition_witnesses']]
            need(refs==state['semantic_definition_refs'], 'DEFINITION_JOIN')
        else:
            need(props['relation_version_ref']==a['version_ref'] and props['qualifiers_sha256']==sha(encoded(row['qualifiers']))
                 and row['axis_ref']==row['closed_signature']['axis_id']
                 and props['relation_kind_ref']==row['closed_signature']['relation_kind_id'], 'RELATION_MAPPING_JOIN')
            for side in ('source','target'):
                endpoint=row[side];fields(endpoint,('ref','version_ref','kind'));target=by_version.get(endpoint['version_ref'])
                need(target is not None and endpoint['ref']==target['artifact']['identity_ref']
                     and endpoint['kind']==target['semantic_kind'] and props[side+'_version_ref']==endpoint['version_ref']
                     and state[side+'_node_id']==target['subject_identity']['subject_id'], 'ENDPOINT_MAPPING_JOIN')
    return {'rows':25,'dispositions':len(value['projection_dispositions']),'authority_effect':'none',
            'source_custody_verified':False,'mapping_sha256':sha(raw)}


@boundary
def validate_result(raw, *, source_sha256, observed_duration_seconds, maximum_duration_seconds):
    need(hexhash(source_sha256) and type(observed_duration_seconds) in (int,float)
         and type(maximum_duration_seconds) in (int,float) and math.isfinite(observed_duration_seconds)
         and math.isfinite(maximum_duration_seconds) and 0<=observed_duration_seconds<=maximum_duration_seconds<=180, 'DURATION')
    expected={'result':'PASS','node_count':15,'edge_count':10,'exact_governance_joins':25,
              'cold_native_replay_byte_parity':True,'same_signed_source_cut':True,'source_sha256':source_sha256,
              'duration_seconds':observed_duration_seconds,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    value=parse(raw);need(value==expected and raw==encoded(expected), 'RESULT_JOIN')
    return {'authority_effect':'none','result_sha256':sha(raw),'timing_independently_measured':False}


def package_names():
    return {f'{family}/{i:08d}.json' for family in ('semantic','governance') for i in range(1,26)} | {
        'request.json','native-output.json','mapping.json','build-result.json','manifest.json'}


@boundary
def validate_manifest(raw, *, package_files, package_path, source_manifest_binding):
    _binding(source_manifest_binding)
    need(type(package_files) is dict and set(package_files)==package_names()
         and all(type(x) is bytes and len(x)<=MAX for x in package_files.values())
         and sum(map(len,package_files.values()))<=32*MAX and package_files['manifest.json']==raw, 'PACKAGE_CLOSURE')
    need(type(package_path) is str and len(package_path)>0 and '\\' not in package_path
         and '\x00' not in package_path and all(x not in ('','.','..') for x in package_path.removeprefix('/').split('/')), 'PACKAGE_PATH')
    expected={'schema_version':'lab-mapped-context-package/v1-candidate',
              'files':[{'path':package_path+'/'+name,'sha256':sha(package_files[name])}
                       for name in sorted(package_names()-{'manifest.json'})],
              'source_manifest_binding':source_manifest_binding,'authority_effect':'none','actual_owner_outcome':None}
    value=parse(raw);need(value==expected and raw==encoded(expected), 'MANIFEST_JOIN')
    return {'authority_effect':'none','leaves':55,'manifest_rows':54,'manifest_sha256':sha(raw),'physical_custody_verified':False}


NATIVE_ROLES=('snapshot','native','loader','libgcc','libc','bwrap')
IDENTITY_FIELDS=('device','inode','mount_id','uid','gid','mode','nlink','size_bytes','kind','locator')


@boundary
def validate_native_basis(basis_raw, *, expected_basis_sha256, originals, observed, launch_index, phase):
    """Compare supplied observations only. Never opens or proves an executed image."""
    basis=selected(basis_raw,expected_basis_sha256);fields(basis,('schema_version','files'))
    need(basis['schema_version']=='lab-mapper-native-launch-basis/v1' and integer(launch_index,0,3)
         and phase in ('before','after','finish'), 'NATIVE_BASIS')
    fields(basis['files'],NATIVE_ROLES);fields(observed,NATIVE_ROLES)
    fields(originals,('native','loader','libgcc','libc','bwrap'))
    physical=set()
    for role in NATIVE_ROLES:
        row=basis['files'][role];fields(row,('sha256','size_bytes','origin','identity'));_binding(row['origin'])
        identity=row['identity'];fields(identity,IDENTITY_FIELDS)
        source_role='native' if role=='snapshot' else role
        source=originals[source_role];obs=observed[role];fields(obs,('identity','bytes'))
        need(type(source) is bytes and type(obs['bytes']) is bytes and len(source)<=32*MAX
             and integer(row['size_bytes'],1,32*MAX) and len(source)==len(obs['bytes'])==row['size_bytes']
             and hexhash(row['sha256']) and sha(source)==row['sha256']==row['origin']['sha256']
             and source==obs['bytes'], 'NATIVE_BYTE_DRIFT')
        fields(obs['identity'],IDENTITY_FIELDS)
        need(all(type(obs['identity'][k]) is type(identity[k]) for k in IDENTITY_FIELDS)
             and obs['identity']==identity and identity['kind']=='regular' and identity['nlink']==1
             and identity['size_bytes']==row['size_bytes']
             and all(integer(identity[k]) for k in ('device','inode','mount_id','uid','gid','mode','nlink','size_bytes'))
             and type(identity['locator']) is str and identity['locator'].startswith('/'), 'NATIVE_IDENTITY_DRIFT')
        need(integer(identity['uid'],0,2**32-2) and integer(identity['gid'],0,2**32-2)
             and integer(identity['inode'],1) and integer(identity['mount_id'],1), 'NATIVE_IDENTITY_RANGE')
        key=(identity['device'],identity['inode'],identity['mount_id'])
        need(key not in physical,'NATIVE_COPY_ALIAS');physical.add(key)
        need(identity['mode']==(0o400 if role=='snapshot' else 0o644 if role in ('libgcc','libc') else 0o755), 'NATIVE_MODE')
        if role in ('native','snapshot'):need(row['sha256']==NATIVE_SHA and row['size_bytes']==20243600,'HISTORICAL_NATIVE_JOIN')
    need(observed['snapshot']['bytes']==observed['native']['bytes'], 'SNAPSHOT_NATIVE_JOIN')
    return {'authority_effect':'none','launch_index':launch_index,'phase':phase,'basis_sha256':expected_basis_sha256,
            'observed_bytes_equal':True,'kernel_identity_verified':False,'executed_image_verified':False}
