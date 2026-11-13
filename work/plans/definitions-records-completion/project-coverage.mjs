import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';import path from 'node:path';
import {Snapshots} from '../../../implementation/lab-runtime/alchlang/shared-records/snapshots.mjs';
import {loadTrust} from '../../../implementation/lab-runtime/alchlang/shared-records/implementation.mjs';
import {digest} from '../../../implementation/lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {projectConsumers,projectionMaterials} from '../../../implementation/lab-workflows/records-workflow/coverage.mjs';
import {nativePort} from '../../../implementation/lab-runtime/alchlang/shared-records/ports.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..'),active=JSON.parse(readFileSync(path.join(root,'implementation/lab-runtime/shared-workflow.json'))),trustFile=path.join(root,active.trust),trust=JSON.parse(readFileSync(trustFile)),db=new Snapshots(path.join(root,active.database),{readOnly:true,trust:loadTrust(trustFile)}),selected={...db.current(active.workspace)},sourceMaterial=db.material(selected.digest,'source.json');
db.inspectPublication(active.workspace,sourceMaterial.manifest.operation);
const registry=JSON.parse(db.material(selected.digest,'registry.json').bytes),source=JSON.parse(sourceMaterial.bytes);
const native=process.argv.includes('--audit-cache')?JSON.parse(readFileSync('/tmp/records-native-bounded.json')):nativePort({action:'record-projection',store:path.join(root,active.native_store),require_current:true});
const graph=projectConsumers({registry,source,selected,native,root,workspace:active.workspace,material:b=>db.material(selected.digest,b.ref??b.path).bytes});
const rawMaterials=projectionMaterials(native);rawMaterials.set('registry.json',db.material(selected.digest,'registry.json').bytes);
for(const subject of graph.subjects){
 const b=subject.binding,name=b.ref??b.path;
 let file;
 if(rawMaterials.has(name)){
  file=path.join(here,'operational',name);mkdirSync(path.dirname(file),{recursive:true});writeFileSync(file,rawMaterials.get(name));
 }else if(name.startsWith('authority/')||name.startsWith('workspaces/')||name==='WORKSPACE.json'||name.startsWith('implementation/')||name.startsWith('work/')||name.startsWith('evidence/')||name.startsWith('ontology/')||name.startsWith('docs/')||name.startsWith('dispositions/')){
  file=path.join(root,name);
  try{if(digest(readFileSync(file))!==b.sha256)throw Error('physical material differs');}
  catch{file=path.join(here,'operational/materials',b.sha256);mkdirSync(path.dirname(file),{recursive:true});writeFileSync(file,db.material(selected.digest,name).bytes);}
 }else throw Error('unmapped-consumer-material:'+name);
 trust.materials[name]={path:path.relative(root,file),sha256:b.sha256};
}
const file=path.join(here,'operational/consumer-universe.json');writeFileSync(file,JSON.stringify(graph,null,2)+'\n');
trust.consumer_universe={path:path.relative(root,file),sha256:digest(readFileSync(file))};writeFileSync(trustFile,JSON.stringify(trust,null,2)+'\n');db.close();console.log(JSON.stringify({subjects:graph.subjects.length,edges:graph.edges.length,provenance:graph.provenance.length,unresolved:graph.unresolved,external:graph.external_subjects.length}));
