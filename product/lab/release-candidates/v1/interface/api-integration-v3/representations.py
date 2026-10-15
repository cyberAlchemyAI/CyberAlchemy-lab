"""Profile-declared catalog metadata; original signed subjects stay immutable."""
import copy
from .protocol import *

CATALOG=HERE.parent/'api-v93/catalog-representations.json'


def row(view,subject):
    if subject['category']!='artifact-type':return None
    from .source8_catalog import selection
    local=selection(view,subject)
    if local is not None:return local
    value=source.parse(CATALOG.read_bytes())
    rows=[r for r in value['rows'] if r['represented_contract_ref']==subject['version_ref']]
    source.require(len(rows)==1,'declared catalog representation missing or ambiguous')
    result=rows[0];contract=view.data['projection']['contracts'][subject['version_ref']]
    source.require(result['source_binding']=={'path':contract['artifact_path'],'sha256':contract['artifact_sha256']},'catalog source representation drift')
    source.require(view.data['baseline']['materials'][result['source_binding']['path']]==result['source_binding']['sha256'],
        'catalog representation outside original signed material closure')
    source.require(contract['schema_sha256']==result['instance_schema_binding']['sha256'] and contract.get('schema_selector')==result['instance_schema_selector'],
        'catalog instance contract changed')
    return result


def body(view,subject):
    selected=row(view,subject)
    if selected is None:return copy.deepcopy(subject['record'])
    if selected.get('schema_version')=='lab-source8-signed-catalog-declaration/v1-candidate':return copy.deepcopy(selected['body'])
    document=view.data['baseline']['documents'][selected['source_binding']['path']]
    return copy.deepcopy(view.handle.common.pointer(document,selected['selector']))


def header(view,subject):
    selected=row(view,subject)
    if selected is None:return None
    if selected.get('schema_version')=='lab-source8-signed-catalog-declaration/v1-candidate':
        from .source8_catalog import header as local_header
        return local_header(view,subject,selected)
    return {'scope_ref':view.data['config']['scope_ref'],'identity_ref':selected['identity_ref'],'version_ref':subject['version_ref'],
        'carrier_ref':selected['meta_carrier_ref'],'byte_sha256':selected['byte_sha256']}


def bytes_for(view,subject):
    selected=row(view,subject)
    if selected.get('schema_version')=='lab-source8-signed-catalog-declaration/v1-candidate':
        from .source8_catalog import raw
        return raw(view,subject,selected)
    document=source.parse(source.original(selected['source_binding']))
    value=view.handle.common.pointer(document,selected['selector'])
    raw=view.handle.common.encoded(value) if selected['selector'] else source.original(selected['source_binding'])
    source.require(value==body(view,subject) and source.sha(raw)==selected['byte_sha256'] and len(raw)==selected['size_bytes'],
        'exact representation body/bytes differ')
    return raw,selected['source_locator'],('inherited-canonical-json-of-registered-contract-entry' if selected['selector'] else 'original-descriptor-file'),selected['source_binding']['sha256']


def envelope(view,subject,cut,basis):
    selected=row(view,subject)
    if selected.get('schema_version')=='lab-source8-signed-catalog-declaration/v1-candidate':
        from .source8_catalog import envelope as local_envelope
        return local_envelope(view,subject,cut,basis,selected)
    raw,locator,encoding,_=bytes_for(view,subject)
    return {'schema_version':'lab-catalog-representation-envelope/v1-candidate','artifact':header(view,subject),'source_cut':cut,
        'represented_contract_ref':selected['represented_contract_ref'],'representation_kind':selected['representation_kind'],'body':body(view,subject),
        'content':{'content_ref':locator,'byte_sha256':source.sha(raw),'size_bytes':len(raw),'media_type':'application/json'},'source_locator':locator,
        'enclosing_source_binding':{'ref':selected['source_binding']['path'],'sha256':selected['source_binding']['sha256']},
        'representation_profile_binding':binding(str(CATALOG.relative_to(ROOT)),CATALOG.read_bytes()),
        'effective_admission_basis':basis,'claim_ceiling':source.CLAIM+' Exact catalog '+encoding+'; no domain instance inferred.','authority_effect':'none'}
