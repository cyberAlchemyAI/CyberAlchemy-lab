"""Exact read metadata, original body encodings and declared connection adapter."""
import copy
from .protocol import *
from . import representations
from .guarded_reads import selected_model,model_read_batch
def carrier(view,subject):
    if subject['category']=='artifact-type':return representations.header(view,subject)['carrier_ref']
    result=subject['carrier_ref'] or subject['record'].get('classification',{}).get('artifact_type_ref')
    if result is None and subject['category']=='relation-kind':
        # Independently selected catalog discriminator, not an inferred wildcard.
        matches=[ref for ref,c in view.data['projection']['contracts'].items()
            if c['semantic_kind']=='relation-kind' and c['instance_discriminator']['value']==subject['record']['schema_version']]
        source.require(len(matches)==1,'relation-kind carrier missing or ambiguous');result=matches[0]
    source.require(result in view.data['projection']['contracts'],'exact captured carrier unavailable')
    return result


def artifact_ref(view,subject):
    if subject['category']=='artifact-type':return representations.header(view,subject)
    # Catalog Definition and Relation Kind declarations have no instance
    # carrier_ref. Retain their explicit classification/discriminator adapter.
    if view.selected['name']=='custody-participation' and subject['category'] not in ('relation-kind','definition'):
        return selected_model(view).artifact_ref(view,subject)
    source.require(not subject['source'].get('encoding'),'catalog declaration encoding must use its explicit selected representation')
    binding=subject['source']
    # An embedded value has its inherited explicit JSON encoding; a whole-file
    # subject retains the original file byte hash. Neither is a semantic digest.
    digest=source.sha(view.handle.common.encoded(subject['record'])) if binding.get('selector') else binding['sha256']
    return {'scope_ref':view.data['config']['scope_ref'],'identity_ref':subject['identity'],
        'version_ref':subject['version_ref'],'carrier_ref':carrier(view,subject),'byte_sha256':digest}


def references(view):
    with model_read_batch(view):
        return [artifact_ref(view,s) for _,s in sorted(view.subjects.items())
            if s['effective_state'] in ('admitted-current','admitted-historical','local-admitted-current','local-admitted-historical')]


def record_bytes(view,subject):
    if subject['category']=='artifact-type':return representations.bytes_for(view,subject)
    # Catalog Definition and Relation Kind declarations have no instance
    # carrier_ref. Retain their explicit classification/discriminator adapter.
    if view.selected['name']=='custody-participation' and subject['category'] not in ('relation-kind','definition'):
        return selected_model(view).record_bytes(view,subject)
    source.require(not subject['source'].get('encoding'),'catalog declaration encoding must use its explicit selected representation')
    report=view.source_record(subject);b=subject['source']
    source.require(report['original_file_is_current'] and report['parsed_record_matches'],'exact original body bytes unavailable')
    if b.get('selector'):
        raw=view.handle.common.encoded(subject['record'])
        locator=('store:'+b['store_id']+':'+b['path'] if 'store_id' in b else b['path'])+'#'+b['selector']
        encoding='inherited-canonical-json-of-selected-original-value'
    else:
        raw=source.original({'path':b['path'],'sha256':b['sha256']});locator=b['path'];encoding='original-file-bytes'
    source.require(source.sha(raw)==artifact_ref(view,subject)['byte_sha256'],'artifact encoded byte identity differs')
    return raw,locator,encoding,report['original_file_sha256']


def signature(view,ref):
    record=view.data['projection']['relation_contracts'][ref]
    paths=[p for p,doc in view.data['baseline']['documents'].items() if doc==record]
    source.require(len(paths)==1,'closed signature missing or ambiguous')
    path=paths[0]
    return record,{'ref':path,'sha256':view.data['baseline']['materials'][path]}


def connections(view,schemas):
    with model_read_batch(view):
        return _connections(view,schemas)


def _connections(view,schemas):
    rows=[];gaps=[]
    for subject in sorted(view.subjects.values(),key=lambda s:s['version_ref']):
        if subject['kind']!='typed-relation':continue
        try:
            view.handle.operations.validate_relation(subject['record'],view.data['projection'],allow_historical=True)
            p=subject['record']['payload'];contract,b=signature(view,p['relation_kind_ref'])
            endpoints=[]
            for end in (p['source'],p['target']):
                resolved=view.subjects[end['version_ref']]
                source.require(resolved['identity']==end['ref'],'connection endpoint identity differs')
                endpoints.append({'artifact':artifact_ref(view,resolved),'semantic_kind':end['kind']})
            value={'relation_kind_ref':p['relation_kind_ref'],'signature_sha256':b['sha256'],
                'axis_ref':contract['payload']['axis_id'],'source':endpoints[0],'target':endpoints[1],
                'qualifiers':copy.deepcopy(p['qualifiers'])}
            source.require(schemas.protocol_valid('urn:cyberalchemy-lab:protocol:typed-connection:v1-candidate',value),
                'connection adapter does not meet original exact endpoint/signature/qualifier contract')
            kinds=[s for s in view.subjects.values() if s['category']=='relation-kind' and s['record']==contract
                and s['source']['sha256']==b['sha256']]
            source.require(len(kinds)==1,'exact relation-kind revision missing or ambiguous')
            rows.append({'version_ref':subject['version_ref'],'kind_version_ref':kinds[0]['version_ref'],'connection':value})
        except Exception:
            gaps.append({'subject_ref':subject['version_ref'],'reason':('Historical relation remains unresolved in this exact cut; its original endpoint/signature/body bytes are preserved; no current traversal or permission inferred.' if subject['effective_state'] in ('admitted-historical','local-admitted-historical') else 'Current relation does not close under the exact selected endpoint/signature/body schema; no traversal or permission inferred.')})
    return rows,gaps


def select(items,relations,message):
    carriers=set(message['carrier_refs']);identities=set(message['identity_refs']);kinds=set(message['relation_kind_refs'])
    by_version={row['version_ref']:row for row in items}
    selected={row['version_ref'] for row in items if row['carrier_ref'] in carriers
        and (not identities or row['identity_ref'] in identities or row['version_ref'] in identities)}
    traversed={};frontier=set(selected)
    # Declared direction: incident-edge breadth-first traversal. Preserve directed
    # source/target tuples in each returned connection; do not invent an inverse.
    for _ in range(message['max_depth']):
        following=set()
        for row in relations:
            c=row['connection'];a=c['source']['artifact']['version_ref'];b=c['target']['artifact']['version_ref']
            if kinds and c['relation_kind_ref'] not in kinds:continue
            if a in frontier or b in frontier:
                traversed[row['version_ref']]=row
                following.update(v for v in (a,b) if v not in selected)
        selected.update(following);frontier=following
        if not frontier:break
    return [by_version[v] for v in sorted(selected)],list(traversed.values())


def connection_coverage(view,schemas):
    rows,gaps=connections(view,schemas);closed={r['version_ref'] for r in rows};missing={g['subject_ref'] for g in gaps}
    result={'current':{'closed':0,'unclosed':0},'historical':{'closed':0,'unclosed':0},'excluded':[],'total':0}
    for subject in sorted(view.subjects.values(),key=lambda s:s['version_ref']):
        if subject['kind']!='typed-relation':continue
        state=subject['effective_state'];result['total']+=1
        family='current' if state in ('admitted-current','local-admitted-current') else 'historical' if state in ('admitted-historical','local-admitted-historical') else None
        if family is None:result['excluded'].append({'version_ref':subject['version_ref'],'admission':state});continue
        source.require(subject['version_ref'] in closed or subject['version_ref'] in missing,'relation omitted from closure coverage')
        result[family]['closed' if subject['version_ref'] in closed else 'unclosed']+=1
    source.require(result['total']==sum(sum(v.values()) for v in [result['current'],result['historical']])+len(result['excluded']),'incomplete relation coverage')
    return result
