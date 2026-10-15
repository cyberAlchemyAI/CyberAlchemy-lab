"""Exact captured epochs and conservative invalidation over old/new authored uses.

Structural JSON equality only discounts serialization; it is not semantic
 equivalence or source fidelity. Cache eligibility never supplies acceptance.
"""
import base64
import copy
import hashlib
import json
import os
import stat
from pathlib import Path
import contracts as c
import dependencies as d
import resolver as r

ROLES=('interpretation','assumption','coupling','profile','tool','statement')
MAX_ARTIFACTS=2048
MAX_CAPTURE_BYTES=16_000_000
MAX_EPOCH_BYTES=32_000_000
SELECTION_KEYS={'snapshot_ref','roots','packet_refs','cycle_policies','required_edges','bindings'}
EPOCH_KEYS={'schema_version','authority_effect','semantic_ready','selection','captured_artifacts','nodes','graph_projection','global_fingerprints','coverage','engine_bindings','epoch_sha256'}

class InvalidationFault(ValueError):
    def __init__(self,code,path=''):self.code=code;self.path=path

def require(condition,code,path=''):
    if not condition:raise InvalidationFault(code,path)
def exact(value,keys,code):require(type(value) is dict and set(value)==set(keys),code)
def text(value):return type(value) is str and bool(value) and value==value.strip()
def sha(value):return type(value) is str and len(value)==64 and all(x in '0123456789abcdef' for x in value)
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def reference(value):
    exact(value,{'path','sha256'},'malformed-artifact-reference');require(sha(value['sha256']),'malformed-artifact-reference');r.components(value['path']);return value

def engine():
    files=[Path(__file__),Path(d.__file__),Path(r.__file__),Path(c.__file__),Path(d.correspondence.__file__)]
    root=Path(__file__).resolve().parents[4]
    return [{'path':p.relative_to(root).as_posix(),'sha256':r.digest(p.read_bytes())} for p in files]

def selected_artifacts(selection):
    exact(selection,SELECTION_KEYS,'malformed-epoch-selection')
    require(type(selection['roots']) is list and selection['roots'],'nonempty-epoch-roots-required')
    require(type(selection['packet_refs']) is list and type(selection['cycle_policies']) is list and (selection['required_edges'] is None or type(selection['required_edges']) is list),'malformed-graph-selection')
    require(type(selection['bindings']) is list,'malformed-role-bindings')
    refs={}
    def add(ref,format):
        reference(ref);path=ref['path'];record={'ref':ref,'format':format}
        require(path not in refs or r.same_json(refs[path],record),'ambiguous-artifact-binding',path);refs[path]=copy.deepcopy(record)
    add(selection['snapshot_ref'],'json')
    require(len({digest(x) for x in selection['packet_refs']})==len(selection['packet_refs']),'duplicate-packet-reference')
    for ref in selection['packet_refs']:add(ref,'json')
    identities=set()
    for binding in selection['bindings']:
        exact(binding,{'definition_id','artifacts'},'malformed-role-binding');identity=binding['definition_id'];require(text(identity) and identity not in identities,'ambiguous-definition-role-binding');identities.add(identity)
        exact(binding['artifacts'],ROLES,'incomplete-role-denominator')
        for role,items in binding['artifacts'].items():
            require(type(items) is list,'malformed-role-artifacts');seen=set()
            for item in items:
                exact(item,{'ref','format'},'malformed-role-artifact');require(type(item['format']) is str and item['format'] in {'json','opaque'},'unsupported-artifact-format');reference(item['ref']);require(item['ref']['path'] not in seen,'duplicate-role-artifact');seen.add(item['ref']['path']);add(item['ref'],item['format'])
    require(len(refs)<=MAX_ARTIFACTS,'artifact-count-limit')
    for item in [selection['roots'],selection['cycle_policies'],selection['required_edges'],selection['bindings']]:c.bounded_tree(item)
    return refs

def projection(selection,raws):
    refs=selected_artifacts(selection);require(set(raws)==set(refs),'captured-artifact-denominator-mismatch')
    require(sum(len(x) for x in raws.values())<=MAX_CAPTURE_BYTES,'capture-total-byte-limit')
    parsed={};artifacts=[];meanings={}
    for path,row in sorted(refs.items()):
        raw=raws[path];require(type(raw) is bytes and len(raw)<=4_000_000 and r.digest(raw)==row['ref']['sha256'],'captured-artifact-byte-substitution',path)
        value=r.parse(raw,path) if row['format']=='json' else None
        if row['format']=='json':parsed[path]=value
        meanings[path]=digest(value) if row['format']=='json' else r.digest(raw)
        artifacts.append({**row,'size_bytes':len(raw),'content_base64':base64.b64encode(raw).decode()})
    snapshot=parsed[selection['snapshot_ref']['path']];packets=[parsed[ref['path']] for ref in selection['packet_refs']]
    graph=d.compile_graph(snapshot,selection['roots'],packets,selection['cycle_policies'],selection['required_edges'])
    by_source={row['source']['definition_id']:row for row in graph['nodes']};bindings={row['definition_id']:row['artifacts'] for row in selection['bindings']}
    require(set(bindings)==set(by_source),'role-binding-node-denominator-mismatch')
    packet_map={packet['interpretation']['source']['definition_id']:ref for packet,ref in zip(packets,selection['packet_refs'])}
    versions={row['source']['version_ref']:row['source']['definition_id'] for row in graph['nodes']}
    edge_pairs=sorted({(versions[edge['from']],versions[edge['to']]) for edge in graph['edges']})
    sources={row['path']:row for row in snapshot['captured_files']};nodes=[]
    for identity,row in sorted(by_source.items()):
        source=row['source'];source_raw=base64.b64decode(sources[source['path']]['content_base64'],validate=True)
        parts={'source-content':digest(r.parse(source_raw,source['path'])),'source-identity':digest({k:source[k] for k in ['definition_id','version_ref','path']}),'scope':digest(row['scope'])}
        roles=copy.deepcopy(bindings[identity]);packet=packet_map.get(identity)
        if packet is not None and not any(r.same_json(x['ref'],packet) for x in roles['interpretation']):roles['interpretation'].append({'ref':copy.deepcopy(packet),'format':'json'})
        for role,items in roles.items():
            items.sort(key=lambda x:x['ref']['path']);parts[role]=digest([{'path':x['ref']['path'],'format':x['format'],'content':meanings[x['ref']['path']]} for x in items])
        parts['dependencies']=digest([edge for edge in edge_pairs if edge[0]==identity])
        parts['cycle-policy']=digest([x for x in selection['cycle_policies'] if x['from_source']['definition_id']==identity or x['to_source']['definition_id']==identity])
        representation=digest({'source':source,'roles':roles})
        nodes.append({'definition_id':identity,'source':source,'artifacts':roles,'content_parts':parts,'content_fingerprint':digest(parts),'representation_fingerprint':representation,'interpretation_status':row['interpretation_status']})
    projection={'edges':[list(x) for x in edge_pairs],'strongly_connected_components':sorted([sorted(versions[x] for x in group) for group in graph['strongly_connected_components']]),'execution_order':[[versions[x] for x in group] for group in graph['execution_order']]}
    global_data={'current_source_denominator':digest([{k:row[k] for k in ['definition_id','version_ref','path']} for row in snapshot['current_entries']]),'selected_node_denominator':digest(sorted(by_source)),'source_capture':digest([{k:row[k] for k in ['path','sha256']} for row in snapshot['captured_files']]),'graph_selection':digest({key:selection[key] for key in ['roots','packet_refs','cycle_policies','required_edges']}),'edge_denominator':digest(graph['edge_denominator'])}
    coverage={'edge_denominator':graph['edge_denominator'],'missing_or_quarantined_interpretations':graph['missing_or_quarantined_interpretations'],'pending_correspondence_or_fidelity':graph['pending_correspondence_or_fidelity'],'cycle_reviews':graph['cycle_reviews'],'semantic_closure':'not-established','meaning_equivalence':'not-established'}
    value={'schema_version':'definition-assurance-invalidation-epoch/v1-candidate','authority_effect':'none','semantic_ready':False,'selection':copy.deepcopy(selection),'captured_artifacts':artifacts,'nodes':nodes,'graph_projection':projection,'global_fingerprints':global_data,'coverage':coverage,'engine_bindings':engine()};value['epoch_sha256']=digest(value)
    require(len(json.dumps(value,allow_nan=False).encode())<=MAX_EPOCH_BYTES,'epoch-byte-limit');return value

def validate_epoch(value):
    exact(value,EPOCH_KEYS,'malformed-invalidation-epoch');require(value['schema_version']=='definition-assurance-invalidation-epoch/v1-candidate' and value['authority_effect']=='none' and value['semantic_ready'] is False,'invalid-epoch-claim-boundary')
    require(type(value['captured_artifacts']) is list and len(value['captured_artifacts'])<=MAX_ARTIFACTS,'malformed-captured-artifacts');raws={}
    for row in value['captured_artifacts']:
        exact(row,{'ref','format','size_bytes','content_base64'},'malformed-captured-artifact');reference(row['ref']);require(type(row['size_bytes']) is int and 0<=row['size_bytes']<=4_000_000,'malformed-captured-artifact');path=row['ref']['path'];require(path not in raws,'duplicate-captured-artifact')
        require(type(row['content_base64']) is str and len(row['content_base64'])<=5_333_336,'capture-byte-limit')
        try:raw=base64.b64decode(row['content_base64'],validate=True)
        except (ValueError,TypeError) as error:raise InvalidationFault('malformed-captured-bytes') from error
        require(len(raw)==row['size_bytes'],'captured-size-mismatch');raws[path]=raw
    expected=projection(value['selection'],raws);require(r.same_json(value,expected),'epoch-integrity-or-build-substitution');return expected

def live_recheck(epoch,root):
    for row in epoch['captured_artifacts']:
        reference(row['ref']);require(r.digest(r.read_bytes(root,row['ref']['path']))==row['ref']['sha256'],'stale-live-epoch-artifact',row['ref']['path'])
    snapshot=next(row for row in epoch['captured_artifacts'] if row['ref']==epoch['selection']['snapshot_ref']);snapshot=r.parse(base64.b64decode(snapshot['content_base64']),'snapshot');r.verify(snapshot,root)
    require(r.same_json(epoch['engine_bindings'],engine()),'active-invalidation-build-drift')
    return {'result':'PASS','authority_effect':'none','semantic_ready':False,'source_files':len(snapshot['captured_files'])}

def capture_epoch(root,selection,before_final_check=None):
    root=r.resolve_root(root);refs=selected_artifacts(selection);raws={path:r.read_bytes(root,path) for path in refs};value=projection(selection,raws)
    if before_final_check:before_final_check()
    live_recheck(value,root);return value

def read_epoch(root,ref):
    return validate_epoch(r.parse(_epoch_raw(root,ref),ref['path']))


def compare_epochs(old,new):
    old=validate_epoch(old);new=validate_epoch(new);before={n['definition_id']:n for n in old['nodes']};after={n['definition_id']:n for n in new['nodes']};identities=set(before)|set(after);direct=[];seeds=set()
    for identity in sorted(identities):
        a,b=before.get(identity),after.get(identity)
        if a is None:kind='new-selected-definition';parts=['selected-node-denominator']
        elif b is None:kind='removed-selected-definition';parts=['selected-node-denominator']
        else:
            parts=[key for key in sorted(a['content_parts']) if a['content_parts'][key]!=b['content_parts'][key]]
            kind='conservative-content-change' if parts else 'representation-change' if a['representation_fingerprint']!=b['representation_fingerprint'] else 'unchanged'
        if kind!='unchanged':seeds.add(identity);direct.append({'definition_id':identity,'delta':kind,'changed_content_parts':parts,'requires_new_byte_binding':True})
    pairs=set(tuple(x) for x in old['graph_projection']['edges'])|set(tuple(x) for x in new['graph_projection']['edges']);reverse={x:set() for x in identities}
    for consumer,dependency in pairs:reverse[dependency].add(consumer)
    affected=d.closure(seeds,reverse);groups=d.components(sorted(identities),{x:{b for a,b in pairs if a==x} for x in identities})
    global_changes=[key for key in sorted(old['global_fingerprints']) if old['global_fingerprints'][key]!=new['global_fingerprints'][key]]
    value={'schema_version':'definition-assurance-invalidation-plan/v1-candidate','authority_effect':'none','semantic_ready':False,'old_epoch_sha256':old['epoch_sha256'],'new_epoch_sha256':new['epoch_sha256'],'direct_deltas':direct,'invalidated_current_definitions':sorted(set(affected)&set(after)),'affected_prior_only_definitions':sorted(set(affected)-set(after)),'unaffected_cache_candidates':sorted(set(after)-set(affected)),'propagation_edges':[list(x) for x in sorted(pairs)],'propagation_components':groups,'global_changes':global_changes,'global_denominator_changed':any(x in global_changes for x in ['current_source_denominator','selected_node_denominator']),'global_regression_required':bool(seeds or global_changes),'semantic_closure':'not-established','owner_fidelity':'pending','claim_ceiling':'Conservative exact-input change propagation on union of validated old/new declared edges. Parsed JSON equality is not semantic equivalence; unaffected cache candidates require fresh checks.'};value['plan_sha256']=digest(value);return value

def compare_selected(root,old_ref,new_ref):
    return compare_epochs(read_epoch(root,old_ref),read_epoch(root,new_ref))

def check_cache(root,old_ref,new_ref,entries,before_final_check=None):
    """Fresh E03 replay; a cache reference never replaces current evidence checks."""
    import verifier as v
    base={'authority_effect':'none','semantic_ready':False,'owner_fidelity':'not-accepted','semantic_closure':'not-established'}
    try:
        root=r.resolve_root(root);old=read_epoch(root,old_ref);new=read_epoch(root,new_ref);plan=compare_epochs(old,new);live_recheck(new,root)
        require(type(entries) is list and len(entries)<=MAX_ARTIFACTS,'cache-entry-list-required');c.bounded_tree(entries);reports=[];seen=set();nodes={x['definition_id']:x for x in new['nodes']};allowed=set(plan['unaffected_cache_candidates']);selected={}
        verifier_files=[Path(v.__file__),Path(v.o.__file__),v.o.RULES]
        verifier_bytes=[x.read_bytes() for x in verifier_files];verifier_contract=v.b.checked_contract();provider_bindings=v.f.current_bindings()
        def capture_refs(refs):
            for ref in refs:
                reference(ref);path=ref['path'];raw=r.read_bytes(root,path);require(r.digest(raw)==ref['sha256'],'stale-cache-input',path)
                if path in selected:require(selected[path]==raw,'cache-read-race',path)
                selected[path]=raw
                require(len(selected)<=MAX_ARTIFACTS and sum(len(x) for x in selected.values())<=MAX_CAPTURE_BYTES,'cache-capture-limit')
        for entry in entries:
            exact(entry,{'cache_id','definition_ids','bundle_manifest_ref','verification_selection_ref'},'malformed-cache-entry');identity=entry['cache_id'];require(text(identity) and identity not in seen,'duplicate-cache-id');seen.add(identity)
            ids=entry['definition_ids'];require(type(ids) is list and ids and all(text(x) for x in ids) and len(set(ids))==len(ids),'malformed-cache-definition-denominator')
            if not set(ids)<=allowed:reports.append({'cache_id':identity,'status':'invalidated-cache','definition_ids':ids,'semantic_ready':False});continue
            for key in ['bundle_manifest_ref','verification_selection_ref']:
                ref=reference(entry[key]);raw=r.read_bytes(root,ref['path']);require(r.digest(raw)==ref['sha256'],'stale-cache-reference',ref['path']);selected[ref['path']]=raw
            manifest_ref=entry['bundle_manifest_ref'];require(manifest_ref['path'].endswith('/manifest.json'),'malformed-cache-manifest-path');bundle_path=manifest_ref['path'].removesuffix('/manifest.json');selection=r.parse(selected[entry['verification_selection_ref']['path']],'cache-selection')
            # E03 independently re-derives the required set and checks every selected byte.
            report=v.verify(root,bundle_path,entry['verification_selection_ref'],root)
            if report['status']!='verified-candidate-accounting':reports.append({'cache_id':identity,'status':'cache-verification-failed','verification':report,'semantic_ready':False});continue
            theory_ref=reference(selection['theory_ref']);theory=r.parse(r.read_bytes(root,theory_ref['path']),'cache-theory');require({x['definition_id'] for x in theory['sources']}==set(ids),'cache-source-denominator-substitution')
            for source in theory['sources']:require(r.same_json(source,nodes[source['definition_id']]['source']),'cache-current-source-substitution')
            envelope_raw=r.read_bytes(root,bundle_path+'/envelope.json');selected[bundle_path+'/envelope.json']=envelope_raw;envelope=r.parse(envelope_raw,'cache-envelope');capture_refs(v.b.e.artifact_refs(envelope)+[entry['verification_selection_ref']]);capture_refs([selection[key] for key in ['theory_ref','relation_requests_ref','populations_ref','endpoint_bindings_ref','snapshot_ref','assumption_set_ref','dependency_graph_ref','finite_requests_ref','expected_provider_bindings_ref']]+selection['coupling_refs'])
            finite_requests=r.parse(selected[selection['finite_requests_ref']['path']],'cache-finite-requests');capture_refs(list(finite_requests.values()))
            for finite_ref in finite_requests.values():
                request=r.parse(selected[finite_ref['path']],'cache-finite-request');capture_refs([request['subject_ref']]+(request['selected_input_refs'] or [])+request['alignment_refs'])
            manifest=r.parse(selected[manifest_ref['path']],'cache-manifest')
            for object_row in manifest['files']:
                object_path=bundle_path+'/'+object_row['object_path'];object_raw=r.read_bytes(root,object_path);require(r.digest(object_raw)==object_row['sha256'],'stale-cached-object');selected[object_path]=object_raw
            bound_refs={digest(x) for x in v.b.e.artifact_refs(envelope)}
            for node_id in ids:
                for items in nodes[node_id]['artifacts'].values():
                    for item in items:require(digest(item['ref']) in bound_refs,'cache-missing-current-role-binding',item['ref']['path'])
            reports.append({'cache_id':identity,'status':'freshly-checked-candidate-cache','definition_ids':sorted(ids),'verification':report,'semantic_ready':False,'authority_effect':'none'})
        if before_final_check:before_final_check()
        live_recheck(new,root)
        require(verifier_bytes==[x.read_bytes() for x in verifier_files] and r.same_json(verifier_contract,v.b.checked_contract()) and r.same_json(provider_bindings,v.f.current_bindings()),'cache-active-verifier-or-runtime-drift')
        for ref in [old_ref,new_ref]:require(r.digest(_epoch_raw(root,ref,verify_hash=False))==ref['sha256'],'epoch-changed-during-cache-check')
        for path,raw in selected.items():require(r.read_bytes(root,path)==raw,'cache-input-changed-during-check',path)
        return {**base,'status':'cache-check-completed','invalidation_plan':plan,'entries':reports,'claim_ceiling':'Fresh candidate accounting and checked evidence only; every missing proof/fidelity/readiness gate is retained.'}
    except (InvalidationFault,r.CaptureFault,d.GraphFault,c.InputError) as error:
        return {**base,'status':'cache-check-unresolved','entries':[],'diagnostics':[{'code':error.code,'path':getattr(error,'path','')}],'claim_ceiling':'No cache support retained after binding failure.'}
    except (OSError,ValueError,TypeError,KeyError,RecursionError) as error:
        return {**base,'status':'cache-check-unresolved','entries':[],'diagnostics':[{'code':type(error).__name__}],'claim_ceiling':'Execution or malformed input; no cached support.'}

def _epoch_raw(root,ref,verify_hash=True):
    # Repeat the bounded no-follow read without reconstructing the graph again.
    reference(ref);parent,name=r.open_parent(root,ref['path'])
    try:
        fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent)
        try:
            require(stat.S_ISREG(os.fstat(fd).st_mode),'unsafe-epoch-kind')
            with os.fdopen(fd,'rb',closefd=False) as stream:raw=stream.read(MAX_EPOCH_BYTES+1)
        finally:os.close(fd)
    finally:os.close(parent)
    require(len(raw)<=MAX_EPOCH_BYTES,'epoch-byte-limit')
    if verify_hash:require(r.digest(raw)==ref['sha256'],'stale-selected-epoch')
    return raw
