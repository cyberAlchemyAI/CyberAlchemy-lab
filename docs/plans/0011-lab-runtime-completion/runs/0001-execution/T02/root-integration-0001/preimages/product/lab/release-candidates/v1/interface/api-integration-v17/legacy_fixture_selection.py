"""Independent frozen fixture expectations; no runtime-derived identities."""
PUBLIC_SOURCE_NAME='legacy-session-fixture'
EXPECTED_NOT_BEFORE='2026-10-13T04:44:35.714260+00:00'
EXPECTED_EXPIRES_AT='2026-10-14T04:44:35.714260+00:00'
EXPECTED_PRINCIPAL='principal:R03-legacy-session-fixture-0257'
EXPECTED_RELATION_PREFIX='typed-relation:R03-legacy-session-fixture-0257:'
EXPECTED_PRODUCT_VERSION='product:cyberalchemy-lab@current-episode-0004.candidate.1'
EXPECTED_READER_ROOT='legacy-session-fixture-reader-v1-action-0148'
EXPECTED_ENTRYPOINT='product/lab/release-candidates/v1/interface/legacy-session-fixture-reader-v1-action-0148/reader.py#SelectedReader.open_signed'
EXPECTED_READER_SHA='f93a1f218238c05b18a7c355f9bc1363bbf42d2b1d442d03e191e121f8e9c9b9'
EXPECTED_PREVIOUS_EXPIRES_AT='2026-10-13T01:28:58.791379+00:00'
EXPECTED_ORIGINAL5_PERIOD={'path':'product/lab/release-candidates/v1/interface/current-participation-v5/packages/0001/period.json','sha256':'5d2184e3491509b6c8d15939d97c6f95609d5277c61bb8f3f0bbd911ff3f35e3'}
EXPECTED_ORIGINAL5_PRIOR={'path':'product/lab/release-candidates/v1/interface/custody-participation-v1/packages/0001/period.json','sha256':'6367fe047f84f0a4a90c5882e79b8441669b814c857c233c81d1e6828febcdce'}
def verify_retained_original_period_chain(source):
    old=source.parse(source.original(EXPECTED_ORIGINAL5_PERIOD))
    assert old['not_before']=='2026-10-12T01:28:58.791379+00:00' and old['expires_at']==EXPECTED_PREVIOUS_EXPIRES_AT
    assert old['original_expired_period_binding']==EXPECTED_ORIGINAL5_PRIOR
    earlier=source.parse(source.original(EXPECTED_ORIGINAL5_PRIOR))
    assert earlier['expires_at']=='2026-10-10T02:45:14.443492+00:00'
    return True

EXPECTED_RELATION_VERSIONS=frozenset(['typed-relation:R03-legacy-session-fixture-0257:assignment-intent@1.0.0-candidate.1', 'typed-relation:R03-legacy-session-fixture-0257:assignment-project@1.0.0-candidate.1', 'typed-relation:R03-legacy-session-fixture-0257:context-goal@1.0.0-candidate.1', 'typed-relation:R03-legacy-session-fixture-0257:context-project@1.0.0-candidate.1', 'typed-relation:R03-legacy-session-fixture-0257:goal-intent@1.0.0-candidate.1', 'typed-relation:R03-legacy-session-fixture-0257:goal-project@1.0.0-candidate.1', 'typed-relation:R03-legacy-session-fixture-0257:implementation-product-capability@1.0.0-candidate.1', 'typed-relation:R03-legacy-session-fixture-0257:profile-capability@1.0.0-candidate.1', 'typed-relation:R03-legacy-session-fixture-0257:reference-principal@1.0.0-candidate.1', 'typed-relation:R03-legacy-session-fixture-0257:work-project@1.0.0-candidate.1'])
