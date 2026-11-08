"""Current-family metadata grants retain live period and producer boundaries."""
import json
from pathlib import Path
from . import runtime_selection as PORTABLE
from .guard import _capture_exact
from .protocol import source

def validate(channel,value,producer,check_source,clock,instant):
    PORTABLE.guard()
    selected=PORTABLE.binding('family.period')
    raw=_capture_exact(PORTABLE.ROOT,selected)
    period=source.parse(raw)
    expected={'period_binding':selected,'principal_ref':period['principal_ref'],
              'source_name':PORTABLE.value('identity.source_name')}
    if check_source:
        source.require(producer is not None
            and producer.HERE==PORTABLE.ROOT/Path(PORTABLE.binding('family.context_source')['path']).parent
            and producer.reader.HERE==PORTABLE.ROOT/Path(PORTABLE.binding('family.reader_source')['path']).parent
            and producer.records.PRINCIPAL==period['principal_ref'],
            'current metadata producer or period principal differs')
        channel.current_metadata_basis=expected
    else:
        source.require(channel.current_metadata_basis==expected,
            'current metadata retained period basis differs')
    source.require(value['source_name']==expected['source_name']
        and value['principal_ref'] not in (expected['principal_ref'],'principal:R03-fresh-reader'),
        'current metadata principal cannot borrow original Agent participation')
    source.require(instant(period['not_before'])<=clock()<instant(value['expires_at'])<=instant(period['expires_at']),
        'current metadata grant exceeds actual signed source period')
    return expected['principal_ref']
