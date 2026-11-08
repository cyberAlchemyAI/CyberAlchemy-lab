"""Exact current-family native artifact representability boundary."""
from . import runtime_selection as PORTABLE
from pathlib import Path
from .protocol import source, ROOT
from .guarded_reads import _active

SOURCE_PACKAGE = ROOT / PORTABLE.binding('family.source_package')['path']
SOURCE_PACKAGE_SHA = PORTABLE.binding('family.source_package')['sha256']
MAPPED_PACKAGE = ROOT / PORTABLE.binding('family.mapper_package')['path']
MAPPED_PACKAGE_SHA = PORTABLE.binding('family.mapper_package')['sha256']
MAPPING = ROOT / PORTABLE.binding('family.mapping')['path']
MAPPING_SHA = PORTABLE.binding('family.mapping')['sha256']
EXCLUDED = frozenset(('role-assignment:lab-repository-owner-bootstrap-0005@sha256.08afbee78d4fc8b3c478001941bfd494de4014384113852cffbf3bb8fedf6c60', 'role-assignment:lab-specialist-artifact-type-owner-bootstrap-0003@sha256.708e1da320083a0044db32ffe05373f14be6efa74d2cf086074dbb2b3223e911', 'role-assignment:lab-specialist-definition-owner-bootstrap-0003@sha256.65e6e307b5a451a684831b7317069a98508c62672d036eb224b5cd646dd391ec', 'role-assignment:lab-specialist-identity-graph-owner-bootstrap-0003@sha256.9e05beddb520ce49fbaba9e47d892f492ad8da99397c767eb889d04225e73c4b', 'role:artifact-type-owner@sha256.3c6878874484210908e895c3ead966f63c3408dcf8b50f361d82616e27ac1a5b', 'role:definition-owner@sha256.bbd3a83be40588d8a162f57edb593a4621a5e8b7cf9ed00c8fe8d351632bf6ba', 'role:identity-graph-owner@sha256.2c6b57c7039ebfc39237cdf32b8ae3419bfaec55831c5e568b5d1a6bf4ee9dce', 'role:repository-owner@sha256.18c11c56a8ef8ef17079525ae98b55b655f8ffadbfca8c2ed3e5f82f966605cf'))
REASON = ('Selected signed source retains this T12 Role or RoleAssignment outside the declared native Context selection; '
          'it has no native artifact carrier, so this bounded API read cannot present an artifact reference. '
          'Mapping SHA-256: ' + MAPPING_SHA + '.')

def _exact(path, expected):
    source.require(path.is_file() and not path.is_symlink(), 'native disposition path missing or linked')
    raw = path.read_bytes()
    source.require(source.sha(raw) == expected, 'native disposition bytes differ')
    return raw

def _current(view):
    legacy = getattr(view, 'legacy_context_producer', None)
    modern = getattr(view, 'source8_context_producer', None)
    return ((legacy is not None and legacy.HERE == ROOT / source.CURRENT_LEGACY_CONTEXT) or
            (modern is not None and modern.HERE == ROOT / source.CURRENT_LEGACY_CONTEXT))

def selected(view):
    if not _current(view):
        return frozenset()
    active = getattr(_active, 'value', None)
    source.require(active is not None and active['view'] is view,
                   'native disposition outside verified original model read batch')
    cached = active.get('native_role_exclusions')
    if cached is not None:
        return cached
    _exact(SOURCE_PACKAGE, SOURCE_PACKAGE_SHA)
    package = source.parse(_exact(MAPPED_PACKAGE, MAPPED_PACKAGE_SHA))
    source.require(package['schema_version'] == 'lab-mapped-context-package/v1-candidate' and
                   [row for row in package['files'] if row['path'] == str(MAPPING.relative_to(ROOT))] ==
                   [{'path': str(MAPPING.relative_to(ROOT)), 'sha256': MAPPING_SHA}],
                   'selected native mapping package does not bind mapping bytes')
    data = source.parse(_exact(MAPPING, MAPPING_SHA))
    from .handlers import cut
    origin = getattr(view, 'legacy_original_view', getattr(view, 'source8_original_view', view))
    source.require(data['source_name'] == 'custody-participation' and
                   data['source_package_binding'] ==
                   {'path': str(SOURCE_PACKAGE.relative_to(ROOT)), 'sha256': SOURCE_PACKAGE_SHA} and
                   data['source_cut'] == cut(origin),
                   'native disposition source package or cut differs')
    rows = data['projection_dispositions']
    source.require(type(rows) is list and len(rows) == 619 and
                   len({row['version_ref'] for row in rows}) == 619 and
                   data['source_closure']['accounted_subjects'] == 619,
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
        _exact(SOURCE_PACKAGE, SOURCE_PACKAGE_SHA)
        _exact(MAPPED_PACKAGE, MAPPED_PACKAGE_SHA)
        _exact(MAPPING, MAPPING_SHA)
