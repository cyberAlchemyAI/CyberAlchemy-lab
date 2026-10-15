#!/usr/bin/env python3
"""Stage an immutable exact generator manifest; never admits its Implementation."""
import argparse
import json
from context import *
from lab_runtime.profiles import select
from lab_runtime.sources import capture


def build(executable):
    paths = [PACKAGE/'context.py',PACKAGE/'native_reader.py',PACKAGE/'native/Cargo.toml',PACKAGE/'native/Cargo.lock',PACKAGE/'native/src/main.rs',ROOT/'ontology-lifecycle/runtime/Cargo.toml',ROOT/'ontology-lifecycle/runtime/Cargo.lock',ROOT/'ontology-lifecycle/runtime/src/lib.rs']
    paths += list((RUNTIME/'lab_runtime').rglob('*.py'))
    row=next(r for r in load(RUNTIME/'profiles/selections.json')['selections'] if r['name']=='d75')
    snapshot=capture(select(ROOT,**{k:v for k,v in row.items() if k not in ['name','source_materials','source_bytes']}))
    manifest = {'schema_version':'lab-context-generator-manifest/v1-candidate','authority_effect':'none','package_version':'0.1.0-candidate.1','implementation_version_ref':IMPLEMENTATION_VERSION,
                'files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':byte_digest(regular(p))} for p in sorted(paths)],
                'native_executable_sha256':byte_digest(regular(executable)), 'environment':environment()}
    directory = PACKAGE/'packages'; directory.mkdir(exist_ok=True)
    index=1
    while (directory/f'{index:04d}').exists(): index+=1
    destination=directory/f'{index:04d}';destination.mkdir()
    owner=required_reference(snapshot['subjects'],'principal:repository-owner@candidate.1','principal')
    scope=required_reference(snapshot['subjects'],'project:cyberalchemy-v2-to-lab-migration','project')
    capability=required_reference(snapshot['subjects'],'product-capability:cyberalchemy-lab:governed-knowledge-lifecycle','product-capability')
    impl,relation=generator_records(snapshot,manifest,owner,scope,capability)
    validate(impl,'implementation',snapshot);validate(relation,'typed-relation',snapshot)
    for key,record in [('implementation_record',impl),('realization_record',relation)]:
        file=destination/(key+'.json');file.write_bytes(encoded(record));manifest[key]={'path':file.relative_to(ROOT).as_posix(),'sha256':byte_digest(file.read_bytes())}
    manifest.update(source_profile_sha256=snapshot['source_profile_sha256'],source_snapshot_digest=snapshot['snapshot_digest'])
    path=destination/'generator-manifest.json';path.write_bytes(encoded(manifest))
    pins=GeneratorPins(byte_digest(path.read_bytes()),IMPLEMENTATION_VERSION)
    verify_generator(path,pins)
    (destination/'selection.json').write_bytes(encoded({'schema_version':'lab-context-generator-selection/v1-candidate','authority_effect':'none','manifest_path':path.relative_to(ROOT).as_posix(),**vars(pins),'native_executable_sha256':manifest['native_executable_sha256']}))
    print(json.dumps({'package':destination.relative_to(ROOT).as_posix(),'manifest_sha256':pins.manifest_sha256}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('executable');args=parser.parse_args();build(args.executable)
