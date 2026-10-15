"""Exact connection schema from the actual signed native source.

Domain ExactSources deliberately excludes connection carriers. This reader
does not extend it, reconstruct a Store, admit endpoints or supply permission.
"""
import copy,re
from .protocol import source

def original_schema(selected,carrier,*,expected_binding=None):
    source.require(carrier=='cal.artifact-type.typed-relation/v4','unselected native connection carrier')
    view=selected.view;delivery=getattr(view,'source8_context_producer',None)
    source.require(delivery is not None and type(selected) is delivery.reader.adapter.SignedSources
                   and type(view) is delivery.reader.Inspection and view.custody_signed_sources is selected
                   and view.integrated_reader is delivery.reader,'actual selected signed Source8 reader required')
    delivery.FACT_SCOPE.parent_guard(selected)
    data=view.data;projection=data['projection'];head=data['head']
    source.require(selected.source_cut==delivery.reader.adapter.source.cut(view)
                   and head['sequence']==len(data['transactions'])-1
                   and head['transaction_digest']==data['transactions'][-1]['digest'],
                   'native schema head differs from selected signed source')
    contract=projection['contracts'].get(carrier)
    source.require(type(contract) is dict and contract['semantic_kind']=='typed-relation'
                   and contract['lifecycle_state'] in ('admitted-current','local-admitted-current')
                   and contract['schema_selector'] is None,'current native connection contract unavailable')
    path=contract['schema_path'];documents=projection['documents']
    source.require(path in documents,'native schema document absent')
    binding=projection.get('schema_content_bindings',{}).get(path)
    if binding is not None:
        source.require(set(binding)=={'store_id','path','proposal_id','selector','encoding','content_ref','byte_sha256'},
                       'closed native original schema binding required')
        source.require(binding['store_id']==data['config']['store_id'],'native schema source store differs')
        locator=binding['path'];match=re.fullmatch(r'transactions/([0-9]{10})\.json',locator)
        source.require(match is not None and 0<int(match[1])<len(data['transactions']),'native schema source transaction absent')
        sequence=int(match[1]);original=view.originals.get(locator)
        source.require(type(original) is bytes and source.sha(original)==selected.original_bindings[locator],
                       'native signed original transaction differs')
        tx=view.handle.common.parse(original) if hasattr(view.handle.common,'parse') else source.parse(original)
        source.require(tx==data['transactions'][sequence],'native schema transaction differs from signed replay')
        proposal=tx['proposal'];custody=view.handle.custody
        source.require(proposal['schema_version'] in custody.EXACT_SCHEMA_PROPOSAL_VERSIONS
                       and proposal['proposal_id']==binding['proposal_id'],'native schema source proposal differs')
        selector='/proposal/schema_contents/'+path.replace('~','~0').replace('/','~1')+'/data'
        source.require(binding['selector']==selector and binding['encoding']==custody.ENCODING,
                       'native schema selector or encoding differs')
        entry=proposal['schema_contents'][path]
        source.require(entry['byte_sha256']==binding['byte_sha256']
                       and entry['content_ref']==binding['content_ref'],'native schema original content binding differs')
        raw=custody.decode_content(entry)
    elif path in data['baseline']['materials']:
        raw=source.original({'path':path,'sha256':data['baseline']['materials'][path]})
    else:
        # Preserve the original declared encoding for historical schema entries.
        matches=[(i,t) for i,t in enumerate(data['transactions'][1:],1) if path in t['proposal']['schemas']]
        source.require(bool(matches),'native schema content source absent')
        sequence,tx=matches[0];locator='transactions/'+str(sequence).zfill(10)+'.json'
        original=view.originals.get(locator)
        source.require(type(original) is bytes and source.sha(original)==selected.original_bindings[locator]
                       and source.parse(original)==tx,'native historical schema original transaction differs')
        proposal=tx['proposal'];custody=view.handle.custody
        raw=(custody.decode_content(proposal['schema_contents'][path])
             if proposal['schema_version'] in custody.ORIGINAL_PROPOSAL_VERSIONS else view.handle.common.encoded(proposal['schemas'][path]))
    source.require(type(raw) is bytes and source.sha(raw)==contract['schema_sha256']
                   and source.parse(raw)==documents[path],'native schema bytes or replayed document differ')
    actual={'carrier_ref':carrier,'source_cut':copy.deepcopy(selected.source_cut),
            'schema_path':path,'schema_sha256':contract['schema_sha256'],
            'original_content_binding':copy.deepcopy(binding)}
    if expected_binding is not None:source.require(expected_binding==actual,'independent native schema binding differs')
    delivery.FACT_SCOPE.parent_guard(selected)
    return raw,actual
