#!/usr/bin/env python3
"""Freeze a new exact committed-context generator without changing C08."""
import sys
from pathlib import Path
from local_context import *
from lab_runtime.profiles import select
from lab_runtime.sources import capture

if __name__ == '__main__':
    row = next(r for r in load(RUNTIME/'profiles/selections.json')['selections'] if r['name']=='d75')
    snapshot = capture(select(ROOT, **{k:v for k,v in row.items() if k not in ['name','source_materials','source_bytes']}))
    old = load(SOURCE_CONTEXT/'packages/0004/generator-manifest.json')
    paths = [PACKAGE/'local_context.py', SOURCE_CONTEXT/'native_reader.py', SOURCE_CONTEXT/'native/Cargo.toml',SOURCE_CONTEXT/'native/Cargo.lock',SOURCE_CONTEXT/'native/src/main.rs', ROOT/'ontology-lifecycle/runtime/Cargo.toml',ROOT/'ontology-lifecycle/runtime/Cargo.lock',ROOT/'ontology-lifecycle/runtime/src/lib.rs']
    paths += list((RUNTIME/'lab_runtime').rglob('*.py'))
    packages=PACKAGE/'packages';packages.mkdir(exist_ok=True);index=1
    while (packages/f'{index:04d}').exists(): index+=1
    destination=packages/f'{index:04d}';destination.mkdir()
    manifest={'schema_version':'lab-context-generator-manifest/v1-candidate','authority_effect':'none',
        'package_version':'0.1.0-candidate.1','implementation_version_ref':IMPLEMENTATION_VERSION,
        'files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':byte_digest(regular(p))} for p in sorted(set(paths))],
        'native_executable_sha256':old['native_executable_sha256'],'environment':environment(),
        'source_profile_sha256':snapshot['source_profile_sha256'],'source_snapshot_digest':snapshot['snapshot_digest']}
    refs=[required_reference(snapshot['subjects'],ref,kind) for ref,kind in [('principal:repository-owner','principal'),('project:cyberalchemy-v2-to-lab-migration','project'),('product-capability:cyberalchemy-lab:governed-knowledge-lifecycle','product-capability')]]
    implementation,relation=generator_records(snapshot,manifest,*refs)
    for key,name,record,kind in [('implementation_record','implementation.json',implementation,'implementation'),('realization_record','realization.json',relation,'typed-relation')]:
        validate(record,kind,snapshot); path=destination/name;path.write_bytes(encoded(record))
        manifest[key]={'path':path.relative_to(ROOT).as_posix(),'sha256':byte_digest(regular(path))}
    path=destination/'generator-manifest.json';path.write_bytes(encoded(manifest))
    pins=GeneratorPins(byte_digest(regular(path)),IMPLEMENTATION_VERSION);verify_generator(path,pins)
    print(__import__('json').dumps({'path':path.relative_to(ROOT).as_posix(),'sha256':pins.manifest_sha256,'implementation_version_ref':IMPLEMENTATION_VERSION}),flush=True)
