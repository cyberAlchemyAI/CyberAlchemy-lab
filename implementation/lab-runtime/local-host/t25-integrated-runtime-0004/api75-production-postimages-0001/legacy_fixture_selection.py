"""Independent frozen fixture expectations; no runtime-derived identities."""
from . import runtime_selection as PORTABLE
from pathlib import Path
PUBLIC_SOURCE_NAME = PORTABLE.value('identity.source_name')
EXPECTED_NOT_BEFORE = PORTABLE.value('period.not_before')
EXPECTED_EXPIRES_AT = PORTABLE.value('period.expires_at')
EXPECTED_PRINCIPAL='principal:'+PORTABLE.value('identity.store')
EXPECTED_RELATION_PREFIX='typed-relation:'+PORTABLE.value('identity.store')+':'
EXPECTED_PRODUCT_VERSION='product:cyberalchemy-lab@current-episode-0004.candidate.1'
EXPECTED_READER_ROOT = str(PORTABLE.ROOT/Path(PORTABLE.binding('family.reader_source')['path']).parent)
EXPECTED_ENTRYPOINT = str(Path(PORTABLE.binding('family.reader_source')['path']).parent/'reader.py')+'#SelectedReader.open_signed'
EXPECTED_READER_SHA = PORTABLE.member_pin('family.reader_source',str(Path(PORTABLE.binding('family.reader_source')['path']).parent/'reader.py'))
EXPECTED_PREVIOUS_EXPIRES_AT='2026-10-13T01:28:58.791379+00:00'
EXPECTED_ORIGINAL5_PERIOD={'path':'product/lab/release-candidates/v1/interface/current-participation-v5/packages/0001/period.json','sha256':'5d2184e3491509b6c8d15939d97c6f95609d5277c61bb8f3f0bbd911ff3f35e3'}
EXPECTED_ORIGINAL5_PRIOR={'path':'product/lab/release-candidates/v1/interface/custody-participation-v1/packages/0001/period.json','sha256':'6367fe047f84f0a4a90c5882e79b8441669b814c857c233c81d1e6828febcdce'}
def verify_retained_original_period_chain(source):
    old=source.parse(source.original(EXPECTED_ORIGINAL5_PERIOD))
    if not (old['not_before']=='2026-10-12T01:28:58.791379+00:00' and old['expires_at']==EXPECTED_PREVIOUS_EXPIRES_AT):
        raise ValueError("retained expired source predicate 1 differs")
    if not (old['original_expired_period_binding']==EXPECTED_ORIGINAL5_PRIOR):
        raise ValueError("retained expired source predicate 2 differs")
    earlier=source.parse(source.original(EXPECTED_ORIGINAL5_PRIOR))
    if not (earlier['expires_at']=='2026-10-10T02:45:14.443492+00:00'):
        raise ValueError("retained expired source predicate 3 differs")
    return True

EXPECTED_RELATION_VERSIONS=frozenset([EXPECTED_RELATION_PREFIX+'reference-principal@1.0.0-candidate.1', EXPECTED_RELATION_PREFIX+'work-project@1.0.0-candidate.1', EXPECTED_RELATION_PREFIX+'assignment-project@1.0.0-candidate.1', EXPECTED_RELATION_PREFIX+'goal-project@1.0.0-candidate.1', EXPECTED_RELATION_PREFIX+'context-project@1.0.0-candidate.1', EXPECTED_RELATION_PREFIX+'assignment-intent@1.0.0-candidate.1', EXPECTED_RELATION_PREFIX+'goal-intent@1.0.0-candidate.1', EXPECTED_RELATION_PREFIX+'profile-capability@1.0.0-candidate.1', EXPECTED_RELATION_PREFIX+'implementation-product-capability@1.0.0-candidate.1', EXPECTED_RELATION_PREFIX+'context-goal@1.0.0-candidate.1'])
