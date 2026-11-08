"""Complete exact signed-family and baseline freshness at Session commit."""
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[6]
def require(value,reason):
    if not value:raise ValueError(reason)

def declared_externals(body, selected):
    """Only independently selected manifest file rows may name host inputs."""
    rows=body.get('external_dependency_bindings',[])
    require(type(rows)is list and len(rows)<=4096,'selected external manifest inventory differs')
    for row in rows:
        require(type(row)is dict and set(row)=={'path','sha256'},'closed external file binding required')
        name=row['path'];pin=row['sha256']
        require(type(name)is str and not name.startswith('//') and Path(name).is_absolute() and Path(name).as_posix()==name
                and '..'not in Path(name).parts and '\\'not in name and '\0'not in name,
                'exact absolute external file locator required')
        require(type(pin)is str and len(pin)==64 and all(c in '0123456789abcdef' for c in pin),
                'independent external file digest required')
        require(row in body['files'],'external dependency is not in its own selected file inventory')
        previous=selected.setdefault(name,pin)
        require(previous==pin,'independent external file pins conflict')

def closure_inputs(closure, external):
    rows=[{'path':path,'sha256':digest} for path,digest in sorted(closure.items())]
    for row in rows:
        if Path(row['path']).is_absolute():
            require(external.get(row['path'])==row['sha256'],'absolute family input lacks independently selected external binding')
    return rows,tuple({'path':path,'sha256':digest} for path,digest in sorted(external.items()))

def fresh_selected_source(selected, expected_family=None):
    """Recheck every selected physical source byte without native replay.

    The original producer capture checks no-follow path custody and exact
    digests. Its archive-handle read also rehashes the owner-only archive.
    The full signed source proof is still required at call entry.
    """
    reader = selected.view.integrated_reader
    require(reader is not None and selected.view.custody_signed_sources is selected,
            'selected source/view identity changed')
    producer = reader.adapter.source
    context = selected.view.legacy_context_producer
    from . import source_bridge
    require(context.reader is reader and context.MAPPED.reader is reader,
            'selected Context/Mapper/Reader family changed')
    basis = selected.selected['candidate_selection_basis']
    context_source = context.HERE / 'source-manifest.json'
    context_pin = source_bridge.CURRENT_LEGACY_DELIVERY_PIN
    context_body = producer.parse(producer.original({
        'path': context_source.relative_to(ROOT).as_posix(), 'sha256': context_pin}))
    mapper_source = context.MAPPED.HERE / 'source-manifest.json'
    mapper_package = context.MAPPED.HERE / 'packages/0001/manifest.json'
    mapper_source_pin = context_body['qualified_mapper_source_binding']['sha256']
    mapper_package_pin = context_body['qualified_mapper_package_binding']['sha256']
    require(context_body['qualified_mapper_source_binding']['path'] == mapper_source.relative_to(ROOT).as_posix()
            and context_body['qualified_mapper_package_binding']['path'] == mapper_package.relative_to(ROOT).as_posix(),
            'Context selected Mapper source/package paths differ')
    manifests = (
        (reader.HERE / 'source-manifest.json', basis['source_manifest_sha256']),
        (reader.adapter.HERE / 'source-manifest.json', basis['adapter_source_sha256']),
        (mapper_source, mapper_source_pin),
        (context_source, context_pin),
    )
    closure = {}
    external = {}
    family = {}
    for path, digest in manifests:
        ref = path.relative_to(ROOT).as_posix()
        raw = producer.original({'path': ref, 'sha256': digest})
        family[ref] = digest
        body = producer.parse(raw)
        require(type(body.get('files')) is list and len(body['files']) <= 4096,
                'selected family source manifest inventory differs')
        declared_externals(body,external)
        for row in body['files']:
            previous = closure.setdefault(row['path'], row['sha256'])
            require(previous == row['sha256'], 'signed family member pins conflict')
    packages = (
        (reader.HERE / 'packages/0001/manifest.json', basis['manifest_sha256']),
        (mapper_package, mapper_package_pin),
        (context.HERE / 'packages/0001/manifest.json', None),
    )
    for path, pin in packages:
        ref = path.relative_to(ROOT).as_posix()
        if pin is None:
            raw = path.read_bytes()
            pin = hashlib.sha256(raw).hexdigest()
        raw = producer.original({'path': ref, 'sha256': pin})
        body = producer.parse(raw)
        require(type(body.get('files')) is list and len(body['files']) <= 4096,
                'selected family package inventory differs')
        family[ref] = pin
        if path.parent.parent.parent == context.HERE:
            require(body['source_manifest_binding'] == {'path': (context.HERE / 'source-manifest.json').relative_to(ROOT).as_posix(),
                                                       'sha256': source_bridge.CURRENT_LEGACY_DELIVERY_PIN},
                    'Context package is not bound to selected source manifest')
        for row in body['files']:
            previous = closure.setdefault(row['path'], row['sha256'])
            require(previous == row['sha256'], 'signed family package member pins conflict')
    producer.original(selected.selected['archive_binding'])
    producer.original(selected.selected['expected_replay_binding'])
    materials = selected.view.data['baseline']['materials']
    require(type(materials) is dict and 0 < len(materials) <= 2048,
            'selected baseline material closure differs')
    for path, digest in materials.items():
        previous = closure.setdefault(path, digest)
        require(previous == digest, 'baseline and signed family pins conflict')
    rows,selected_external=closure_inputs(closure,external)
    producer.B.verify_inputs(rows,selected_external=selected_external)
    if expected_family is not None:
        require(family == expected_family, 'selected signed family package bindings changed')
    return family

def captured_source_basis(selected):
    """Cheap integrity of private facts shared across trusted operations.

    This neither authenticates wire fields nor replaces physical freshness.
    Expected file digests remain independently selected by family manifests.
    """
    producer=selected.view.integrated_reader.adapter.source
    require(not selected.closed and not selected.view.handle.closed,
            'selected source or handle closed')
    require(selected.sources.current_guard==selected.guard,
            'selected source callback changed')
    require(selected.view.subjects==selected.view.data['projection']['subjects'],
            'captured projection subject views differ')
    common=selected.view.handle.common
    return {
        'config':common.digest(selected.view.data['config']),
        'baseline':common.digest(selected.view.data['baseline']),
        'projection':common.digest(selected.view.data['projection']),
        'cut':producer.cut(selected.view),
        'source_cut':selected.source_cut,'exact_sources_cut':selected.sources.source_cut,
        'scope':selected.sources.scope_ref,
        'records':producer.sha(selected.record_stamp(selected.records)),
        'exact_records':producer.sha(selected.record_stamp(selected.sources.records.values())),
        'schemas':producer.sha(selected.schema_stamp(selected.schemas)),
        'exact_schemas':producer.sha(selected.schema_stamp(selected.sources.schemas.values())),
        'validators':{k:producer.sha(producer.encoded(v.schema))
                      for k,v in selected.sources.validators.items()},
        'originals':{k:producer.sha(v) for k,v in selected.view.originals.items()},
    }
