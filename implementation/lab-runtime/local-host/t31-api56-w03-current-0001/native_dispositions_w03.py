"""Exact current-family native artifact representability boundary."""
from pathlib import Path
from .protocol import source, ROOT
from .guarded_reads import _active

SOURCE_PACKAGE = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-ce4d53a6479188a5/source/packages/0001/manifest.json'
SOURCE_PACKAGE_SHA = '7006fd4fac3327b76f4ffcc03d93ffb070bb25288ca7bab7e7e5b20470baf22c'
MAPPED_PACKAGE = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-ce4d53a6479188a5/mapped/packages/0001/manifest.json'
MAPPED_PACKAGE_SHA = '2d40300776f1416f156afdfde53aa82009c71e71d4f318a78ce1c162b072087a'
MAPPING = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-ce4d53a6479188a5/mapped/packages/0001/mapping.json'
MAPPING_SHA = '070f0cbf746294221347e520bc6dcd4fddb5c8be172b5834025b35e3dd5a587c'
W03_CONTEXT = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-8d0312c813444f57/context-w03-0005'
W03_SOURCE_PACKAGE = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-8d0312c813444f57/source/packages/0001/manifest.json'
W03_SOURCE_PACKAGE_SHA = 'b78fe83c69e40457b891550540873c62a53294d671d7622807d2129600766d27'
W03_MAPPED_PACKAGE = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-8d0312c813444f57/mapped-w03-0004/packages/0001/manifest.json'
W03_MAPPED_PACKAGE_SHA = '06860ad635e2bce7c3e302f97e4d977330df4f72a2e0b5d363965a51cdcb0414'
W03_MAPPING = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-8d0312c813444f57/mapped-w03-0004/packages/0001/mapping.json'
W03_MAPPING_SHA = 'f38aa25daede03cccfac0e8b64a5ad49fa2e7017df343a4cd5aadd180eb5348d'
EXCLUDED = frozenset(('role-assignment:lab-repository-owner-bootstrap-0005@sha256.08afbee78d4fc8b3c478001941bfd494de4014384113852cffbf3bb8fedf6c60', 'role-assignment:lab-specialist-artifact-type-owner-bootstrap-0003@sha256.708e1da320083a0044db32ffe05373f14be6efa74d2cf086074dbb2b3223e911', 'role-assignment:lab-specialist-definition-owner-bootstrap-0003@sha256.65e6e307b5a451a684831b7317069a98508c62672d036eb224b5cd646dd391ec', 'role-assignment:lab-specialist-identity-graph-owner-bootstrap-0003@sha256.9e05beddb520ce49fbaba9e47d892f492ad8da99397c767eb889d04225e73c4b', 'role:artifact-type-owner@sha256.3c6878874484210908e895c3ead966f63c3408dcf8b50f361d82616e27ac1a5b', 'role:definition-owner@sha256.bbd3a83be40588d8a162f57edb593a4621a5e8b7cf9ed00c8fe8d351632bf6ba', 'role:identity-graph-owner@sha256.2c6b57c7039ebfc39237cdf32b8ae3419bfaec55831c5e568b5d1a6bf4ee9dce', 'role:repository-owner@sha256.18c11c56a8ef8ef17079525ae98b55b655f8ffadbfca8c2ed3e5f82f966605cf'))
REASON = ('Selected signed source retains this T12 Role or RoleAssignment outside the declared native Context selection; '
          'it has no native artifact carrier, so this bounded API read cannot present an artifact reference. '
          'Mapping SHA-256: ' + MAPPING_SHA + '.')
W03_REASON = ('Selected signed source retains this T12 Role or RoleAssignment outside the declared native Context selection; '
              'it has no native artifact carrier, so this bounded API read cannot present an artifact reference. '
              'Mapping SHA-256: ' + W03_MAPPING_SHA + '.')

def _exact(path, expected):
    source.require(path.is_file() and not path.is_symlink(), 'native disposition path missing or linked')
    raw = path.read_bytes()
    source.require(source.sha(raw) == expected, 'native disposition bytes differ')
    return raw

def _family(view):
    legacy = getattr(view, 'legacy_context_producer', None)
    modern = getattr(view, 'source8_context_producer', None)
    if legacy is not None and legacy.HERE == W03_CONTEXT:
        return (W03_SOURCE_PACKAGE, W03_SOURCE_PACKAGE_SHA, W03_MAPPED_PACKAGE,
                W03_MAPPED_PACKAGE_SHA, W03_MAPPING, W03_MAPPING_SHA, 661)
    old_context = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-ce4d53a6479188a5/context'
    if ((legacy is not None and legacy.HERE == old_context) or
            (modern is not None and modern.HERE == old_context)):
        return (SOURCE_PACKAGE, SOURCE_PACKAGE_SHA, MAPPED_PACKAGE,
                MAPPED_PACKAGE_SHA, MAPPING, MAPPING_SHA, 616)
    return None

def reason(view):
    selected_family = _family(view)
    source.require(selected_family is not None, 'native role reason needs selected current family')
    return W03_REASON if selected_family[5] == W03_MAPPING_SHA else REASON

def selected(view):
    selected_family = _family(view)
    if selected_family is None:
        return frozenset()
    active = getattr(_active, 'value', None)
    source.require(active is not None and active['view'] is view,
                   'native disposition outside verified original model read batch')
    cached = active.get('native_role_exclusions')
    if cached is not None:
        source.require(active.get('native_role_family') == selected_family,
                       'cached native role exclusion family differs')
        return cached
    source_package, source_sha, mapped_package, mapped_sha, mapping, mapping_sha, expected_count = selected_family
    _exact(source_package, source_sha)
    package = source.parse(_exact(mapped_package, mapped_sha))
    source.require(package['schema_version'] == 'lab-mapped-context-package/v1-candidate' and
                   [row for row in package['files'] if row['path'] == str(mapping.relative_to(ROOT))] ==
                   [{'path': str(mapping.relative_to(ROOT)), 'sha256': mapping_sha}],
                   'selected native mapping package does not bind mapping bytes')
    data = source.parse(_exact(mapping, mapping_sha))
    from .handlers import cut
    origin = getattr(view, 'legacy_original_view', getattr(view, 'source8_original_view', view))
    source.require(data['source_name'] == 'custody-participation' and
                   data['source_package_binding'] ==
                   {'path': str(source_package.relative_to(ROOT)), 'sha256': source_sha} and
                   data['source_cut'] == cut(origin),
                   'native disposition source package or cut differs')
    rows = data['projection_dispositions']
    source.require(type(rows) is list and len(rows) == expected_count and
                   len({row['version_ref'] for row in rows}) == expected_count and
                   data['source_closure']['accounted_subjects'] == expected_count,
                   'native disposition source closure differs')
    by_ref = {row['version_ref']: row for row in rows}
    source.require(set(origin.subjects) == set(by_ref),
                   'native disposition subjects differ from selected signed source')
    for ref in EXCLUDED:
        subject = origin.subjects[ref]
        source.require(subject['category'] == 'artifact-instance' and
                       subject['effective_state'] == 'admitted-current' and
                       subject['carrier_ref'] is None and
                       by_ref[ref] == {'version_ref': ref, 'carrier_ref': None,
                                        'effective_state': 'admitted-current',
                                        'disposition': 'retained-source-outside-declared-context-selection'},
                       'exact T12 native-unrepresentable role disposition differs')
    active['native_role_family'] = selected_family
    active['native_role_exclusions'] = EXCLUDED
    return EXCLUDED

def unrepresentable(view, subject):
    result = subject['version_ref'] in selected(view)
    if result:
        source.require(subject['category'] == 'artifact-instance' and
                       subject['effective_state'] == 'admitted-current' and
                       subject['carrier_ref'] is None,
                       'role exclusion subject changed in selected prefix')
    return result

def excluded_subjects(view):
    refs = selected(view)
    return [view.subjects[ref] for ref in sorted(refs) if ref in view.subjects]

def verify_end(view):
    active = getattr(_active, 'value', None)
    if active is not None and active.get('view') is view and 'native_role_exclusions' in active:
        selected_family = _family(view)
        source.require(selected_family is not None and selected_family == active.get('native_role_family'),
                       'native disposition family changed during selected read')
        source_package, source_sha, mapped_package, mapped_sha, mapping, mapping_sha, _ = selected_family
        _exact(source_package, source_sha)
        _exact(mapped_package, mapped_sha)
        _exact(mapping, mapping_sha)
