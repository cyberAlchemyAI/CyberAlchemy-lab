"""Explicit v2 package builder, actual carrier validators, no admission/native run."""
import argparse,json,os
from pathlib import Path
from . import context_selected as C
from . import selected_runtime as SR

def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--snapshot',required=True);parser.add_argument('--snapshot-sha256',required=True)
    parser.add_argument('--destination',required=True)
    for key in ['owner-ref','scope-ref','capability-ref']:parser.add_argument('--'+key,required=True)
    args=parser.parse_args(argv)
    snapshot=C.loads(SR.exact({'path':args.snapshot,'sha256':args.snapshot_sha256}))
    selection_path=C.PACKAGE/'generator-source-selection.json'
    selection=C.load(selection_path);binding={'path':selection_path.relative_to(C.ROOT).as_posix(),'sha256':C.byte_digest(C.regular(selection_path))}
    m={'schema_version':'lab-context-generator-manifest/v2-candidate','authority_effect':'none','package_version':'0.1.0-selected-native-candidate.1',
       'implementation_version_ref':C.IMPLEMENTATION_VERSION,'files':selection['files']+[binding],
       'source_closure_binding':binding,'predecessor_generator_binding':selection['predecessor_generator_binding'],
       'runtime_bindings':selection['runtime_bindings'],'environment':C.environment(),
       'source_profile_sha256':snapshot['source_profile_sha256'],'source_snapshot_digest':snapshot['snapshot_digest']}
    dependencies=C.loads(SR.exact(selection['runtime_bindings']['dependency_selection']))
    native=[r for r in dependencies['inputs'] if r['kind']=='native-executable'];SR.need(len(native)==1,'exact selected native required')
    m['native_executable_sha256']=native[0]['sha256']
    runtime=SR.SelectedRuntime(C.copy.deepcopy(m));runtime.guard()
    owner=C.required_reference(snapshot['subjects'],args.owner_ref,'principal');scope=C.required_reference(snapshot['subjects'],args.scope_ref,'project')
    capability=C.required_reference(snapshot['subjects'],args.capability_ref,'product-capability')
    impl,relation=C.generator_records(snapshot,m,owner,scope,capability)
    C.validate(impl,'implementation',snapshot);C.validate(relation,'typed-relation',snapshot)
    destination=C.ROOT/args.destination
    SR.need(destination.is_relative_to(C.PACKAGE/'packages') and '..' not in destination.parts and not destination.exists(),
            'fresh explicit own candidate package required')
    SR.need(not any(p.is_symlink() for p in (destination,*destination.parents)),'candidate output origin alias')
    destination.mkdir(parents=True,mode=0o700)
    for key,record in [('implementation_record',impl),('realization_record',relation)]:
        path=destination/(key+'.json');raw=C.encoded(record)
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
        m[key]={'path':path.relative_to(C.ROOT).as_posix(),'sha256':C.byte_digest(raw)}
    path=destination/'generator-manifest.json';raw=C.encoded(m)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    pins=C.SelectedGeneratorPins(C.byte_digest(raw),C.IMPLEMENTATION_VERSION)
    C.verify_generator(path,pins);runtime.guard()
    print(json.dumps({'result':'STAGED-candidate-generator-v2','manifest_binding':{'path':path.relative_to(C.ROOT).as_posix(),'sha256':pins.manifest_sha256},
                      'authority_effect':'none','admitted':False,'runtime_or_owner_qualified':False},sort_keys=True));return 0
