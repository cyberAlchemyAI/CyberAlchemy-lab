#!/usr/bin/env python3
"""Inspect the immutable import and selected Lab runtime closure. Never admits."""
import argparse, collections, hashlib, json, re
from pathlib import Path
PACKAGE=Path(__file__).resolve().parent
REPO=PACKAGE.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def relative(p): return p.relative_to(REPO).as_posix()
def closure():
    entries=[PACKAGE/'bin/define.mjs',PACKAGE/'index.mjs',PACKAGE/'compiler.mjs']
    seen=set(); missing=[]; external=set(); todo=entries[:]
    pattern=re.compile(r'''(?:from\s*|import\s*\(\s*|import\s+)["']([^"']+)["']''')
    while todo:
        path=todo.pop().resolve()
        if path in seen: continue
        if not path.is_file(): missing.append(str(path)); continue
        seen.add(path)
        for spec in pattern.findall(path.read_text()):
            if spec.startswith('.'):
                target=(path.parent/spec).resolve()
                if target.suffix in ('.mjs','.js','.json'): todo.append(target)
                elif target.is_file(): seen.add(target)
                else: missing.append(relative(path)+':'+spec)
            elif not spec.startswith('node:'): external.add(spec)
    # Python and selected compiler data are dynamic providers, listed explicitly.
    for base,glob in [(PACKAGE/'schemas','**/*.json'),(PACKAGE/'generated/define-service','**/*'),
                      (PACKAGE/'alch','**/*'),(PACKAGE/'vendor','**/*'),
                      (REPO/'implementation/lab-runtime/v2/lab_runtime','*.py'),
                      (REPO/'craft/impl/cli/dist','**/*'),(REPO/'craft/impl/cli/contracts','**/*.json')]:
        seen.update(p.resolve() for p in base.glob(glob) if p.is_file() and '__pycache__' not in p.parts)
    seen.update((PACKAGE/p).resolve() for p in ['lab_bridge.py','lab_session.py','publish_directory.py','package.json'])
    seen.update([REPO/'implementation/lab-runtime/v2/profile.json',REPO/'craft/impl/cli/package.json',REPO/'define/define'])
    return sorted(seen),missing,sorted(external)
def main():
    args=argparse.ArgumentParser(); args.add_argument('--write-manifest',action='store_true'); args=args.parse_args()
    selected,missing,external=closure()
    rows=[{'path':relative(p),'sha256':sha(p),'size_bytes':p.stat().st_size} for p in selected]
    inventory=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    manifest={'schema_version':'cal.define-runtime-binding/v1','standing':'Lab-owned-candidate-realization','authority_effect':'none',
      'entrypoint':'define/define','files':rows,'inventory_sha256':inventory,'unresolved_relative_imports':missing,
      'external_module_imports':external,'dynamic_providers':['Lab runtime v2 source profile and source currentness','built Craft public API','installed Codex app-server for chat'],
      'claim_ceiling':'Selected runtime bytes and dependency closure; not package admission, live model conformance or general Alch compiler parity.'}
    if args.write_manifest:
        if missing or external: raise SystemExit('Cannot bind unresolved active imports: '+str((missing,external)))
        (PACKAGE/'runtime-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    imported=json.loads((REPO/'evidence/migrations/cyberalchemy-v2-to-lab/executions/0080-define-package-import/manifest.json').read_text())
    bad=[r['destination'] for r in imported['files'] if sha(REPO/r['destination'])!=r['sha256']]
    bound=json.loads((PACKAGE/'runtime-manifest.json').read_text()) if (PACKAGE/'runtime-manifest.json').exists() else {'files':[]}
    drift=[r['path'] for r in bound['files'] if not (REPO/r['path']).is_file() or sha(REPO/r['path'])!=r['sha256']]
    model={}; all_nodes=set(); graphs=[]
    source=REPO/'define/source/cyberAlchemy-v2/define'
    for label,base in [('business',source/'business-ontology'),('system',source/'system-ontology'),('bridge',source)]:
        node_path=base/('nodes.json' if label=='bridge' else 'NODES.json'); edge_path=base/('relations.json' if label=='bridge' else 'RELATIONS.json')
        nodes=json.loads(node_path.read_text())['nodes']; edges=json.loads(edge_path.read_text())['relations']
        ids=[n.get('id',n.get('node_id')) for n in nodes]; all_nodes.update(ids); all_nodes.update(label+'::'+i for i in ids if label!='bridge'); graphs.append((label,edges))
        model[label]={'nodes':len(nodes),'relations':len(edges),'duplicate_node_ids':len(ids)-len(set(ids)),
           'duplicate_relation_ids':len(edges)-len({r.get('id',r.get('relation_id')) for r in edges})}
    for label,edges in graphs:
        model[label]['missing_endpoints']=[r.get('id',r.get('relation_id')) for r in edges if r.get('source',r.get('from_node_id')) not in all_nodes or r.get('target',r.get('to_node_id')) not in all_nodes]
    vendor=json.loads((PACKAGE/'vendor/manifest.json').read_text())
    vendor_drift=[r['destination'] for r in vendor['files'] if sha(REPO/r['destination'])!=r['selected_sha256']]
    origins=[]
    original=REPO/'define/source/cyberAlchemy-v2/implementation/define-cli'
    for path in selected:
        if path.is_relative_to(PACKAGE):
            predecessor=original/path.relative_to(PACKAGE)
            if predecessor.is_file(): origins.append({'selected':relative(path),'source':relative(predecessor),'source_sha256':sha(predecessor),'selected_sha256':sha(path),'adapted':sha(path)!=sha(predecessor)})
    if args.write_manifest: (PACKAGE/'source-selection.json').write_text(json.dumps({'authority_effect':'none','selection':'compiled Define core and explicitly adapted Lab interfaces','source_files':origins},indent=2)+'\n')
    upstream=json.loads((PACKAGE/'evidence/upstream-validation.stdout.json').read_text())
    result={'schema_version':'cal.define-integration-audit/v1','authority_effect':'none',
      'import':{'files':len(imported['files']),'drift':bad,'classification_counts':imported['classification_counts']},
      'active_runtime':{'files':len(rows),'inventory_sha256':inventory,'drift':drift,'missing_imports':missing,'external_modules':external},
      'models':model,'selected_source_files':len(origins),'adapted_source_files':sum(r['adapted'] for r in origins),'vendor_digest_drift':vendor_drift,'upstream_package_validation':{'overall':upstream['overall'],'summary':upstream['summary'],'blockers':upstream['blockers'],'child_runs':upstream['child_runs']},
      'status':'PASS' if not(bad or drift or missing or external or vendor_drift or any(m['missing_endpoints'] or m['duplicate_node_ids'] or m['duplicate_relation_ids'] for m in model.values())) else 'BLOCK',
      'validation_scope':'immutable import, selected successor dependency closure and graph endpoint structure',
      'upstream_validation_is_separate':True}
    print(json.dumps(result,indent=2)); return 0 if result['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
