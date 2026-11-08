"""Independent frozen fixture expectations; no runtime-derived identities."""
PUBLIC_SOURCE_NAME='completion-legacy:legacy-live-20261015093410-31d1bbb85b71'
EXPECTED_NOT_BEFORE='2026-10-15T09:34:10.677832+00:00'
EXPECTED_EXPIRES_AT='2026-10-16T09:34:10.677832+00:00'
EXPECTED_PRINCIPAL='principal:completion-legacy-live-20261015093410-31d1bbb85b71'
EXPECTED_RELATION_PREFIX='typed-relation:completion-legacy-live-20261015093410-31d1bbb85b71:'
EXPECTED_PRODUCT_VERSION='product:cyberalchemy-lab@current-episode-0004.candidate.1'
EXPECTED_READER_ROOT='/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/fresh-legacy-current-runtime-preparation-0006/instances/legacy-live-20261015093410-31d1bbb85b71/reader'
EXPECTED_ENTRYPOINT='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/fresh-legacy-current-runtime-preparation-0006/instances/legacy-live-20261015093410-31d1bbb85b71/reader/reader.py#SelectedReader.open_signed'
EXPECTED_READER_SHA='5c85be9aef9e0afc6ee3bf49cf7140872c99cf648775fcb5805107f268ac1a53'
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

EXPECTED_RELATION_VERSIONS=frozenset(['typed-relation:completion-legacy-live-20261015093410-31d1bbb85b71:reference-principal@1.0.0-candidate.1', 'typed-relation:completion-legacy-live-20261015093410-31d1bbb85b71:work-project@1.0.0-candidate.1', 'typed-relation:completion-legacy-live-20261015093410-31d1bbb85b71:assignment-project@1.0.0-candidate.1', 'typed-relation:completion-legacy-live-20261015093410-31d1bbb85b71:goal-project@1.0.0-candidate.1', 'typed-relation:completion-legacy-live-20261015093410-31d1bbb85b71:context-project@1.0.0-candidate.1', 'typed-relation:completion-legacy-live-20261015093410-31d1bbb85b71:assignment-intent@1.0.0-candidate.1', 'typed-relation:completion-legacy-live-20261015093410-31d1bbb85b71:goal-intent@1.0.0-candidate.1', 'typed-relation:completion-legacy-live-20261015093410-31d1bbb85b71:profile-capability@1.0.0-candidate.1', 'typed-relation:completion-legacy-live-20261015093410-31d1bbb85b71:implementation-product-capability@1.0.0-candidate.1', 'typed-relation:completion-legacy-live-20261015093410-31d1bbb85b71:context-goal@1.0.0-candidate.1'])
