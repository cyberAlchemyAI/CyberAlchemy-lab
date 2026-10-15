"""Original content bridge over independently pinned replayed source files."""
import hashlib
import json

def _unique_pairs(rows):
    result={}
    for key,value in rows:
        if key in result:raise ValueError('duplicate captured transaction key')
        result[key]=value
    return result

def _nonfinite(value):raise ValueError('nonfinite captured transaction')

def source_record(view,subject):
    binding=subject['source'];handle=view.handle;require=handle.common.require
    require(binding.get('encoding')==handle.custody.ENCODING,'explicit original content encoding required')
    require(binding.get('store_id')==view.data['config']['store_id'] and binding['path'] in view.originals,
        'original signed transaction unavailable in captured source')
    raw_file=view.originals[binding['path']];tx=json.loads(raw_file,object_pairs_hook=_unique_pairs,parse_constant=_nonfinite)
    handle.common.verify_seal(tx)
    selector=binding['selector'];prefix=selector.removesuffix('/data');require(prefix+'/data'==selector,'content selector mismatch')
    entry=handle.common.pointer(tx,prefix);raw=handle.custody.decode_content(entry)
    require(hashlib.sha256(raw).hexdigest()==binding['sha256'] and entry['content_ref']==binding['content_ref'],
        'captured original content binding differs')
    record=handle.common.pointer(tx,binding['record_selector']);handle.custody.equivalent(raw,record)
    require(handle.common.digest(record)==handle.common.digest(subject['record']),'captured original parsed record differs')
    return {'encoding':handle.custody.ENCODING,'record_binding':binding,'original_file_sha256':hashlib.sha256(raw_file).hexdigest(),
        'original_file_is_current':True,'parsed_record_matches':True},raw
