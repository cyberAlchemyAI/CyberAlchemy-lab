"""Explicit original-category targets and actual read-only native Store.review.

No owner authorization, source admission, runtime activation or graph grafting.
Meta descriptors use the native v3 registered_types item, never an instance wrapper.
"""
import argparse
import json
from pathlib import Path
import tempfile
from datetime import datetime, timezone
from jsonschema import Draft202012Validator
import materialize_targets_v2 as M

B = M.B
ROOT = B.ROOT
FIELDS = {'member_ref', 'operation', 'category', 'carrier_ref', 'version_ref',
    'decision_ref', 'record_binding', 'record_origin_binding', 'record_origin_selector',
    'schema_binding', 'descriptor_binding', 'predecessor_binding', 'contract_binding'}

def pointer(view, value, selector):
    return view.handle.common.pointer(value, selector) if selector else value

def body(view, item):
    raw = M.original(item['record_binding'])
    record = json.loads(raw)
    if item['record_origin_binding'] is not None:
        origin = json.loads(M.original(item['record_origin_binding']))
        B.need(item['record_origin_selector'], 'registry origin needs an explicit selector')
        B.need(pointer(view, origin, item['record_origin_selector']) == record,
               'selected registry fragment differs from the exact standalone body')
    else:
        B.need(item['record_origin_selector'] is None, 'selector without bound original registry')
    return raw, record

def preimage(view, item, record_id):
    binding = item['predecessor_binding']
    if item['operation'] == 'admit':
        B.need(binding is None, 'admit cannot select a predecessor')
        return None
    B.need(binding is not None, 'revise/withdraw require an exact original predecessor')
    raw = M.original(binding)
    candidates = [s for s in view.subjects.values() if s['identity'] == record_id
        and s['effective_state'] in ('admitted-current', 'local-admitted-current')]
    B.need(len(candidates) == 1 and json.loads(raw) == candidates[0]['record'],
           'predecessor differs from exact current original source')
    subject = candidates[0]; source = subject['source']; observed = view.source_record(subject)
    sha = (source['sha256'] if source.get('encoding') or not source.get('selector')
           else B.sha(view.handle.common.encoded(subject['record'])))
    B.need(B.sha(raw) == sha and observed['original_file_is_current']
        and observed['parsed_record_matches'], 'original predecessor byte witness differs')
    return subject

def target(view, schemas, members, item):
    B.need(set(item) == FIELDS and item['member_ref'] in members, 'closed known member selection required')
    member=members[item['member_ref']]
    chosen=item['predecessor_binding'] if item['operation']=='withdraw' else item['record_binding']
    B.need(chosen in member.get('targets', []) or chosen==member.get('postimage_binding'),
           'typed body/preimage not selected by exact review member')
    B.need(item['operation'] in ('admit', 'revise', 'withdraw'), 'unsupported native operation')
    carrier = view.data['projection']['contracts'].get(item['carrier_ref'])
    B.need(carrier and carrier['lifecycle_state'] in ('admitted-current', 'local-admitted-current'),
           'exact current original carrier required')
    B.need(item['schema_binding'] == {'path': carrier['schema_path'], 'sha256': carrier['schema_sha256']}
        and item['descriptor_binding'] == {'path': carrier['artifact_path'], 'sha256': carrier['artifact_sha256']},
        'carrier schema/descriptor origin differs')
    schema = json.loads(M.original(item['schema_binding']))
    descriptor = json.loads(M.original(item['descriptor_binding']))
    category = {'definition':'definition','artifact-type':'artifact-type',
        'relation-kind':'relation-kind','typed-relation':'typed-relation'}.get(carrier['semantic_kind'], 'artifact-instance')
    B.need(item['category'] == category, 'original category/carrier mismatch')
    if item['operation'] == 'withdraw':
        B.need(all(item[k] is None for k in ('record_binding','record_origin_binding',
            'record_origin_selector','contract_binding')), 'withdrawal cannot replace original content')
        existing = view.subjects.get(item['version_ref'])
        B.need(existing and existing['carrier_ref'] == item['carrier_ref'], 'withdrawal must select exact existing revision/carrier')
        prior = preimage(view, item, existing['identity'])
        B.need(prior['version_ref'] == item['version_ref'], 'withdrawal version/predecessor differs')
        record = None; content = None; contract = None
    else:
        raw, record = body(view, item)
        B.need(isinstance(record, dict), 'native body must be an object')
        if category == 'artifact-type':
            B.need(item['carrier_ref'] == 'cal.artifact-type.artifact-type/v3', 'native meta route requires original v3 descriptor slot')
            selector = '#/properties/registered_types/items'
            record_id = record['artifact_type_ref'].rsplit('/', 1)[0]
            B.need(item['version_ref'] == record['artifact_type_ref'], 'exact native descriptor version required')
            contract = json.loads(M.original(item['contract_binding']))
            required = {'semantic_kind','schema_path','schema_sha256','schema_selector',
                'instance_discriminator','identity_field','allowed_relation_kinds','relation_roles'}
            B.need(set(contract) == required and all(record[k] == contract[k] for k in
                ('semantic_kind','schema_path','schema_sha256','schema_selector')), 'exact closed native schema contract required')
        else:
            B.need(item['contract_binding'] is None, 'contract only belongs to native artifact-type registration')
            selector = carrier.get('schema_selector')
            field = descriptor.get('instance_contract', {}).get('identity_field')
            B.need(field == carrier['artifact'].get('instance_contract', {}).get('identity_field') and field,
                   'original declared identity selector differs')
            record_id = view.handle.common.identity(record, field)
            B.need(item['version_ref'].startswith(record_id + '@') and len(item['version_ref']) > len(record_id) + 1,
                   'exact qualified native identity required')
            contract = None
        schemas.guard()
        # Original native resolver keeps fragment/root and dependency identities.
        view.handle.sources.validate_schema(record, carrier['schema_path'], selector,
            view.data['projection']['documents'])
        prior = preimage(view, item, record_id)
        content = view.handle.custody.content_entry(raw)
    return {'category':category, 'operation':item['operation'], 'carrier_ref':item['carrier_ref'],
        'version_ref':item['version_ref'], 'decision_ref':item['decision_ref'],
        'predecessor_ref':prior['version_ref'] if prior else None,
        'record':record, 'content':content, 'contract':contract}

def materialize(args):
    selection = B.exact(Path(args.selection), args.selection_sha256)
    B.need(set(selection) == {'schema_version','inventory_binding','additional_member_binding',
        'API_source_binding','API_profile_binding','source_name','source_selection',
        'targets','schema_inputs','proposal_header_binding','helper_bindings',
        'authority_effect','actual_owner_outcome'}, 'closed typed selection required')
    B.need(selection['schema_version'] == 'lab-explicit-final-target-selection/v4-candidate'
        and selection['authority_effect'] == 'none' and selection['actual_owner_outcome'] is None,
        'selection cannot grant owner authority')
    B.need(selection['helper_bindings'] == [B.bind(Path(__file__)), B.bind(B.HERE/'materialize_targets_v2.py'), B.bind(B.HERE/'build_runtime.py')],
           'independent exact materializer/helper pins required')
    M.original(selection['API_source_binding']); M.original(selection['API_profile_binding'])
    api = (ROOT / selection['API_source_binding']['path']).parent
    B.need(selection['API_profile_binding']['path'] == str((api/'contract-profile.json').relative_to(ROOT)), 'foreign profile')
    members = M.inventory(ROOT/selection['inventory_binding']['path'], selection['inventory_binding']['sha256'], selection['additional_member_binding'])
    B.need(Path(M.__file__).resolve()==B.HERE/'materialize_targets_v2.py' and Path(B.__file__).resolve()==B.HERE/'build_runtime.py', 'helper module origin differs')
    guard, bridge, schemas = M.family(api, selection['API_source_binding']['sha256'], selection['API_profile_binding']['sha256'])
    B.need(bridge.source_selection(selection['source_name']) == selection['source_selection'], 'independent exact original source/cut differs')
    output = Path(args.output_directory).resolve()
    B.need(output.parent == B.HERE and not output.exists(), 'exclusive owned materialization directory required')
    output.mkdir(mode=0o700)
    started = datetime.now(timezone.utc).isoformat(); materialized = []; native_failure = None; reviewed = None
    with bridge.replay_source(selection['source_name']) as view:
        before = view.handle.common.digest(view.data['projection'])
        seen = set()
        for i,item in enumerate(selection['targets']):
            B.need(item['member_ref'] not in seen, 'duplicate selected member')
            seen.add(item['member_ref']); value = target(view, schemas, members, item)
            path = output/('target-'+str(i).zfill(4)+'.json'); B.emit(path,value)
            materialized.append({'member_ref':item['member_ref'],'target_binding':B.bind(path)})
        header = json.loads(M.original(selection['proposal_header_binding']))
        B.need(set(header) == {'schema_version','proposal_id','expected_head','source_snapshot_digest','scope_ref','policy_ref','challenge_route'}, 'closed native proposal header required')
        config = view.data['config']
        B.need(header['schema_version'] == view.handle.custody.EXACT_SCHEMA_PROPOSAL_VERSION
            and header['expected_head'] == view.data['head']['transaction_digest']
            and all(header[k] == config[k] for k in ('scope_ref','policy_ref','challenge_route','source_snapshot_digest')),
            'original native proposal context differs')
        documents={}; contents={}
        for row in selection['schema_inputs']:
            B.need(set(row) == {'native_path','binding'}, 'closed exact native schema input required')
            B.need(row['native_path'] not in documents, 'duplicate native schema input')
            raw=M.original(row['binding']); documents[row['native_path']]=json.loads(raw)
            contents[row['native_path']]=view.handle.custody.content_entry(raw)
        proposal={**header,'targets':[B.load(ROOT/r['target_binding']['path']) for r in materialized],
            'schemas':documents,'schema_contents':contents}
        B.emit(output/'native-proposal.json',proposal)
        # Pure native Review: exact cold original bytes, no key, owner callback or admission.
        with tempfile.TemporaryDirectory(prefix='cal-final-target-original-review-0254-') as temporary:
            store=Path(temporary)/'store';store.mkdir(mode=0o700)
            for name,raw in view.originals.items():
                path=store/name;path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
                with path.open('xb') as stream:stream.write(raw)
                path.chmod(0o600)
            try:
                reviewed=view.handle.store_module.Store(store,ROOT).review(proposal)
            except view.handle.common.RuntimeFault as exc:
                native_failure={'type':type(exc).__name__,'message':str(exc)}
            B.need(all((store/name).read_bytes()==raw for name,raw in view.originals.items()), 'native Review modified original bytes')
            B.need({p.relative_to(store).as_posix() for p in store.rglob('*') if p.is_file()} == set(view.originals), 'native Review created source/Session material')
        B.need(view.handle.common.digest(view.data['projection'])==before,'projection was modified or grafted')
        view.handle.guard()
    schemas.guard();guard.verify(selection['API_source_binding']['sha256'])
    for row in selection['helper_bindings']:M.original(row)
    report={'schema_version':'lab-explicit-final-native-target-review/v4-candidate',
        'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),
        'selection_binding':B.bind(Path(args.selection)),'helper_bindings':selection['helper_bindings'],
        'source_selection':selection['source_selection'],'materialized_targets':materialized,
        'native_proposal_binding':B.bind(output/'native-proposal.json'),'actual_original_native_review':reviewed,
        'actual_original_native_refusal':native_failure,'result':'REFUSED' if native_failure else 'REVIEWED-CANDIDATE-ONLY',
        'native_review_executed':True,'full_API_entry_exit_guards':True,'original_reader_exit_guard':True,
        'source_bytes_unchanged':True,'owned_scratch_removed':True,'source_admissions':0,'projection_grafted':False,
        'all_member_targets_materialized':len(seen)==len(members),'unselected_member_refs':sorted(set(members)-seen),
        'actual_owner_outcome':None,'owner_authority_resolved':False,'authority_effect':'none',
        'ready_for_R08':False,'task_complete':False,'goal_complete':False}
    B.emit(output/'materialization.json',report)
    print(json.dumps({'result':report['result'],'targets':len(materialized),'report_binding':B.bind(output/'materialization.json'),
        'native_refusal':native_failure}),flush=True)
    return 2 if native_failure else 0

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--selection',required=True);parser.add_argument('--selection-sha256',required=True)
    parser.add_argument('--output-directory',required=True)
    raise SystemExit(materialize(parser.parse_args()))

if __name__=='__main__':main()
