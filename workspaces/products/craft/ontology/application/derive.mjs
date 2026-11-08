/** Craft readers over the existing Ontology Lifecycle source consumer.
 * Open questions: README.md (source standing and effective authority).
 */
import {createHash} from 'node:crypto';
import {readFileSync,mkdtempSync,rmSync,realpathSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {labRoot,upstreamRoot} from '../../implementation/source-bindings.mjs';

export const craftRoot=path.resolve(import.meta.dirname,'../..');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const json=file=>JSON.parse(readFileSync(file,'utf8'));
const need=(ok,message)=>{if(!ok)throw Error('CRAFT_ONTOLOGY:'+message);};
const canonical=v=>JSON.stringify(v,(_,x)=>x&&typeof x==='object'&&!Array.isArray(x)
  ?Object.fromEntries(Object.keys(x).sort().map(k=>[k,x[k]])):x);
const pointer=(v,p)=>p.split('/').slice(1).reduce((value,key)=>value[key.replaceAll('~1','/').replaceAll('~0','~')],v);
export const viewNames=Object.freeze(['product','project-work','authority','identity','business','system','bridge','verification-requirements']);

function validateSemanticSources(document,root){
  const lab=labRoot,upstream=upstreamRoot;
  for(const name of ['product-bridge','orodi-bridge']){
    const registry=document('ontology/packages/'+name+'/sources.json').data;
    for(const source of registry.sources){
      let base,relative;
      if(source.path.startsWith('cyberAlchemy-v2/')){base=upstream;relative=source.path.slice('cyberAlchemy-v2/'.length);}
      else {need(source.path.startsWith('craft/'),'undeclared semantic source namespace');base=root;relative=source.path.slice('craft/'.length);}
      const file=inputFile(base,relative);
      need(sha(readFileSync(file))===source.sha256,'semantic source drift: '+source.source_id);
    }
  }
}

function inputFile(root,relative){
  need(typeof relative==='string'&&!path.isAbsolute(relative)&&!relative.includes('\\')&&
    path.posix.normalize(relative)===relative&&!relative.split('/').includes('..'),'unsafe input path');
  const file=path.resolve(root,relative),physical=realpathSync(file);
  need(physical===file&&file.startsWith(realpathSync(root)+path.sep),'input escapes physical Craft root');
  return file;
}

export function validateExport(exported,manifest,{root=craftRoot}={}){
  need(exported.authority_effect==='none'&&Array.isArray(exported.records),'invalid native export');
  const documents=new Map(),nodes=[],relations=[],seen=new Set();
  const packages=new Map(manifest.packages.map(p=>[p.package_key,p]));
  let expected=0;
  for(const pkg of packages.values()){
    expected+=pkg.documents.length;
    for(const registry of [pkg.nodes,pkg.relations])expected+=pointer(json(inputFile(root,registry.source.path)),registry.selector).length;
  }
  need(exported.records.length===expected,'incomplete native export');
  for(const row of exported.records){
    const binding=row.source_binding,pkg=packages.get(binding?.package_key);
    need(pkg&&row.lifecycle==='active'&&['node','relation'].includes(row.identity?.subject_kind),'unknown package or inactive source');
    const key=binding.package_key+':'+binding.path+'#'+binding.selector;
    need(!seen.has(key),'duplicate source selector');seen.add(key);
    const file=inputFile(root,binding.path),bytes=readFileSync(file);
    need(sha(bytes)===binding.sha256,'source changed after native export: '+binding.path);
    const record=row.source_record;
    // The native consumer's canonical JSON digest includes its trailing newline.
    need(sha(canonical(record)+'\n')===binding.record_sha256,'exported record digest mismatch');
    if(row.identity.type_ref==='source-document'){
      need(pkg.documents.some(d=>d.path===binding.path&&d.sha256===binding.sha256),'undeclared supporting document');
      need(binding.selector==='/document'&&record.document_path===binding.path&&
        record.content===bytes.toString('utf8')&&record.content_sha256===binding.sha256,'document binding mismatch');
      need(row.identity.subject_id===binding.package_key+':document-'+sha(binding.path),'document identity mismatch');
      const prior=documents.get(binding.path);
      need(!prior||prior.sha256===binding.sha256,'conflicting source document');
      documents.set(binding.path,{path:binding.path,sha256:binding.sha256,content:record.content});
    }else{
      const registry=row.identity.subject_kind==='relation'?pkg.relations:pkg.nodes;
      need(registry.source.path===binding.path&&registry.source.sha256===binding.sha256&&
        binding.selector.startsWith(registry.selector+'/'),'undeclared registry selector');
      need(canonical(pointer(JSON.parse(bytes),binding.selector))===canonical(record),'native source record mismatch');
      const nativeId=registry.id_field==='$tuple'?'tuple-'+sha(canonical([
        record[registry.type_field],record[registry.source_field],record[registry.target_field]])+'\n'):record[registry.id_field];
      need(row.identity.subject_id===binding.package_key+':'+row.identity.subject_kind+'-'+sha(nativeId),'native subject identity mismatch');
      const carrier={package_key:binding.package_key,subject_id:row.identity.subject_id,
        source_path:binding.path,source_selector:binding.selector,record};
      (row.identity.subject_kind==='relation'?relations:nodes).push(carrier);
    }
  }
  return {documents,nodes,relations,head:exported.head};
}

export function deriveCraftViews(exported,manifest,{root=craftRoot}={}){
  const context=validateExport(exported,manifest,{root});
  const document=relative=>{
    const row=context.documents.get(relative);need(row,'view input absent from native export: '+relative);
    return {path:'craft/'+row.path,sha256:row.sha256,data:JSON.parse(row.content)};
  };
  const index=document('ontology/views/inputs/index.json').data;
  validateSemanticSources(document,root);
  const inputs={};
  for(const ref of index.views){
    need(ref.path.startsWith('craft/'),'view definition outside Craft');
    const definition=document(ref.path.slice(6)).data;
    need(definition.view_id===ref.view_id&&definition.proof_record_files_selected===0,'input-view identity or proof policy changed');
    const name=ref.view_id.replace('craft.input.','');
    need(!Object.hasOwn(inputs,name),'duplicate named input');
    inputs[name]=definition.input_paths.map(p=>{need(p.startsWith('craft/'),'input outside Craft');return document(p.slice(6));});
  }
  need(Object.keys(inputs).sort().join(',')==='authority,business,evidence,identity,product,project,system,traceability,work','input view coverage');
  const catalog=inputs.product.find(r=>r.path.endsWith('/capabilities/catalog.json')).data;
  const capabilities=catalog.families.flatMap(f=>{
    const d=document('product/capabilities/'+f.path).data;
    return f.record_collection?d[f.record_collection]:[d];
  });
  need(capabilities.length===37&&new Set(capabilities.map(c=>c.node_id)).size===37,'Product capability coverage');
  const native=node=>context.nodes.filter(n=>n.record.branch===node);
  const edges=branch=>context.relations.filter(r=>r.record.branch===branch);
  const reconciliation=context.documents.has('ontology/sources/reconciliation.json')
    ?document('ontology/sources/reconciliation.json').data:null;
  const common={schema_version:'craft.derived-view/v1',authority_effect:'none',
    producer:'ontology-lifecycle/source-consumer-v4 + craft/ontology/application/derive.mjs',
    source_manifest_sha256:sha(canonical(manifest)),native_head:context.head,
    source_standing:'current reviewed source declarations; candidate limits retained and no admission inferred',
    source_reconciliation:reconciliation?{status:reconciliation.status,counts:reconciliation.counts}:null};
  const result={
    product:{inputs:inputs.product,capabilities,reference_applications:inputs.product.filter(r=>r.data.schema_version==='craft.reference-application/v1').map(r=>r.data)},
    'project-work':{project:inputs.project,work:inputs.work},
    authority:{inputs:inputs.authority,effective_authority:'source-declared routes only; no new owner decisions'},
    identity:{inputs:inputs.identity},
    business:{nodes:native('business'),relations:edges('business')},
    system:{nodes:native('system'),relations:edges('system'),implementation:inputs.system.filter(r=>r.path.endsWith('/bindings.json'))},
    bridge:{relations:edges('bridge')},
    'verification-requirements':{inputs:inputs.evidence,observed_results_loaded:false}
  };
  const identities=new Set(context.nodes.map(n=>n.package_key+':'+(n.record.node_id??n.record.identity_ref)));
  for(const edge of result.bridge.relations)for(const endpoint of [edge.record.from,edge.record.to])
    need(identities.has(edge.package_key+':'+endpoint),'bridge endpoint closure');
  return Object.fromEntries(viewNames.map(name=>[name,{...common,view_id:'craft.output.'+name,...result[name]}]));
}

function invoke(binary,args,root){
  const result=spawnSync(binary,args,{cwd:root,encoding:'utf8',maxBuffer:32*1024*1024});
  need(result.status===0,String(result.stderr||result.error||'native consumer failed'));
  return JSON.parse(result.stdout);
}

export function loadNativeExport({root=craftRoot,binary=path.resolve(craftRoot,'implementation/.local/ontology-build/release/cal-ontology-source-runtime')}={}){
  const manifestFile=path.join(root,'ontology/application/source-manifest.json');
  const manifest=json(manifestFile);
  need(manifest.schema_version==='cal-source-runtime-manifest/v1'&&manifest.authority_effect==='none'&&
    canonical(manifest.roots)==='{"craft":"."}','consumer manifest contract');
  const temporary=mkdtempSync(path.join(tmpdir(),'craft-ontology-view-'));
  try{
    const store=path.join(temporary,'store');
    invoke(binary,['import',manifestFile,store],root);
    const exported=invoke(binary,['export',store],root);
    validateExport(exported,manifest,{root});
    return {manifest,exported};
  }finally{rmSync(temporary,{recursive:true,force:true});}
}

if(process.argv[1]&&import.meta.url===pathToFileURL(realpathSync(process.argv[1])).href){
  const selected=process.argv[2]??'all';
  need(process.argv.length<=3&&(selected==='all'||viewNames.includes(selected)),'unknown output view');
  const {manifest,exported}=loadNativeExport();
  const views=deriveCraftViews(exported,manifest);
  console.log(JSON.stringify(selected==='all'?views:views[selected],null,2));
}
