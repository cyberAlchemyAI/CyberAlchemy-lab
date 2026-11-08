"""Exact original target bytes and preserved inherited generated-value encoding."""
from . import base as source
def carrier(view,subject):
    ref=subject['carrier_ref'];source.require(ref in view.data['projection']['contracts'],'captured carrier unavailable');return ref
def artifact_ref(view,subject):
    b=subject['source']
    if b.get('encoding'):
        source.require(b['encoding']==view.handle.custody.ENCODING,'unknown source content encoding')
        byte_sha=b['sha256']
    else:byte_sha=source.sha(view.handle.common.encoded(subject['record'])) if b.get('selector') else b['sha256']
    return {'scope_ref':view.data['config']['scope_ref'],'identity_ref':subject['identity'],'version_ref':subject['version_ref'],
        'carrier_ref':carrier(view,subject),'byte_sha256':byte_sha}
def record_bytes(view,subject):
    report=view.source_record(subject);b=subject['source']
    source.require(report['original_file_is_current'] and report['parsed_record_matches'],'exact original bytes unavailable')
    if b.get('encoding'):
        _,raw=source.original_bridge.source_record(view,subject);encoding=b['encoding']
    elif b.get('selector'):
        raw=view.handle.common.encoded(subject['record']);encoding='inherited-canonical-json-of-selected-original-value'
    else:raw=source.original({'path':b['path'],'sha256':b['sha256']});encoding='original-file-bytes'
    locator=('store:'+b['store_id']+':'+b['path'] if b.get('store_id') else b['path'])+('#'+b['selector'] if b.get('selector') else '')
    source.require(source.sha(raw)==artifact_ref(view,subject)['byte_sha256'],'original artifact byte identity differs')
    return raw,locator,encoding,report['original_file_sha256']
def signature(view,ref):
    record=view.data['projection']['relation_contracts'][ref]
    paths=[p for p,doc in view.data['baseline']['documents'].items() if doc==record]
    source.require(len(paths)==1,'closed signature missing or ambiguous');path=paths[0]
    return record,{'ref':path,'sha256':view.data['baseline']['materials'][path]}
