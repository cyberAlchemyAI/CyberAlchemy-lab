#!/usr/bin/env python3
"""Resolve the explicit registry envelope, without choosing authority by time."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'execution'))
import support as s
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'baseline'))
import run_baseline
BASE=Path(__file__).resolve().parent


def resolve():
    baseline=s.read(s.BASE/'baseline/baseline-manifest.json')
    for b in baseline['source_bindings']:s.check_binding(b)
    fresh=run_baseline.capture()
    s.require(fresh==baseline,'selected baseline changed; refresh and replan explicitly')
    registry_root=run_baseline.REGISTRY.parent
    artifact_path=registry_root/'artifact-type-registry.json';endpoint_path=registry_root/'endpoint-inventory.json'
    application=s.read(registry_root.parent/'receipts/application.json')
    for role,path in [('artifact_type_registry',artifact_path),('endpoint_inventory',endpoint_path)]:
        s.require(s.digest(path)==application['outputs'][role]['sha256'],'unresolved carrier registry output')
    artifact=s.read(artifact_path);endpoint=s.read(endpoint_path)
    descriptors={d['artifact_type_ref']:d for d in artifact['descriptors']}
    carriers=[];bindings=[]
    for e in endpoint['entries']:
        s.require(e['carrier_ref'] in descriptors,'missing endpoint descriptor')
        d=descriptors[e['carrier_ref']]
        for pathkey,hashkey in [('descriptor_path','descriptor_sha256'),('schema_path','schema_sha256')]:
            path=s.ROOT/d[pathkey];s.require(s.digest(path)==d[hashkey],'carrier source drift');bindings.append(s.binding(path))
        carriers.append({'endpoint':e,'descriptor':d,'source_posture':s.read(s.ROOT/d['descriptor_path']).get('status',s.read(s.ROOT/d['descriptor_path']).get('lifecycle_state'))})
    typed=descriptors[artifact['current_by_identity']['cal.artifact-type.typed-relation']]
    bindings+=[s.binding(artifact_path),s.binding(endpoint_path)]
    for pathkey,hashkey in [('descriptor_path','descriptor_sha256'),('schema_path','schema_sha256')]:
        path=s.ROOT/typed[pathkey];s.require(s.digest(path)==typed[hashkey],'typed carrier source drift');bindings.append(s.binding(path))
    return {'schema':'relational.effective-snapshot/v1','records':baseline['records'],'counts':baseline['counts'],
        'endpoint_count':len(carriers),'carriers':carriers,'current_typed_relation':typed,
        'source_bindings':baseline['source_bindings']+bindings,'selection_policy':'explicit frozen D74 envelope; D75 context recorded separately',
        'authority_effect':'none'}


def main():
    s.context('C01',[(s.PLAN,'tasks[id=C01]'),(s.BASE/'gates/l0/task-acceptance.json','accepted minimum slice'),
        (s.BASE/'baseline/baseline-manifest.json','explicit selected envelope and source postures'),
        (run_baseline.REGISTRY,'all exact relation entries'),(run_baseline.REGISTRY.parent/'artifact-type-registry.json','descriptor hashes and current_by_identity'),
        (run_baseline.REGISTRY.parent/'endpoint-inventory.json','closed endpoint inventory')],
        [{'classification':'non-blocking','choice':'resolve the explicit D74 envelope only; record D75 separately','basis':'Frozen registry selection is not newest-path discovery.'}])
    snapshot=resolve()
    s.require(snapshot['counts']=={'kinds':41,'ordered_pairs':550} and snapshot['endpoint_count']==109,'coverage changed')
    s.write(BASE/'effective-snapshot.json',snapshot)
    s.write(BASE/'source-resolution-report.json',{'result':'pass','relation_sources_resolved':41,'ordered_pairs':550,'endpoint_carriers_resolved':109,
        'hashed_source_bindings':len(snapshot['source_bindings']),'source_posture_retained':True,'effective_overlay_resolved':True,
        'current_carrier':snapshot['current_typed_relation'],'selection_frozen':True,'authority_effect':'none'})
    s.accept('C01',{n:BASE/n for n in ['effective-snapshot.json','source-resolution-report.json']},
        ['Every relation source, D70/D74 overlay and all 109 endpoint descriptor/schema bindings resolve exactly; source posture is retained.',
         'Measured coverage is recomputed as 41 kinds and 550 pairs with 109 named endpoint kinds and immutable provenance.'],
        ['Baseline and admission-output digests are checked before resolution; unresolved carrier sources fail.',
         'A fresh capture must equal the frozen baseline; no changed live lookup replaces it implicitly.'],
        [Path(__file__),s.BASE/'baseline/run_baseline.py'])
    print(json.dumps({'task':'C01','result':'accepted','counts':snapshot['counts'],'endpoints':snapshot['endpoint_count']}))


if __name__=='__main__':main()
