/** Source-bound generation of the authored pure Pack components. */
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,existsSync,linkSync,unlinkSync} from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {implementationRoot as craftRoot,upstreamRoot} from '../../../../craft/implementation/source-bindings.mjs';
export const root=import.meta.dirname;
export const node=path.join(upstreamRoot,'.runtime/craft-release-2026-10-29/node-v26.12.1-linux-x64/bin/node');
const hash=raw=>createHash('sha256').update(raw).digest('hex');
export function componentGenerator(catalog='pack-engine-sources.json'){
 const catalogRaw=readFileSync(path.join(root,catalog)),catalogHash=hash(catalogRaw),selected=JSON.parse(catalogRaw);
 const inputs=[catalog,...new Set([...(selected.sources??[selected.source]),...Object.values(selected.source_groups??{}).flat()]),selected.profile,'contracts/bounds.json'];
 const fingerprint=()=>{if(hash(readFileSync(path.join(root,catalog)))!==catalogHash)throw Error('component-catalog-changed-after-selection');return hash(JSON.stringify(inputs.map(name=>[name,hash(readFileSync(path.join(root,name)))])));};
 function generate(name){
 const component=selected.components.find(row=>row.name===name);if(!component)throw Error('unselected-component');
 const source=fingerprint(),base=path.join(root,'.local/pack-engine');mkdirSync(base,{recursive:true});
 const index=path.join(base,source+'-'+name+'.json');
 if(existsSync(index)){
  const record=JSON.parse(readFileSync(index));
  for(const item of record.files){const raw=readFileSync(path.join(record.output,item.path));if(hash(raw)!==item.sha256||raw.length!==item.bytes)throw Error('generated-component-drift');}
  if(record.source!==source)throw Error('source-selection-drift');const manifestRaw=readFileSync(path.join(record.output,'manifest.json'));if(JSON.stringify(JSON.parse(manifestRaw).files)!==JSON.stringify(record.files))throw Error('generated-manifest-drift');return {...record,manifest_sha256:hash(manifestRaw)};
 }
 const directory=mkdtempSync(path.join(base,name+'-')),output=path.join(directory,'generated');
 const fragments=component.source_group?selected.source_groups[component.source_group]:selected.sources;
 const authored=fragments?path.join(directory,'source.alch'):path.join(root,selected.source);
 if(fragments){writeFileSync(authored,fragments.map(name=>readFileSync(path.join(root,name),'utf8')).join('\n'));mkdirSync(path.join(directory,'contracts'));writeFileSync(path.join(directory,'contracts/bounds.json'),readFileSync(path.join(root,'contracts/bounds.json')));}
 const args=[path.join(craftRoot,'alchlang/dist/generic-composition-cli.js'),'generate','--source',authored,'--profile',path.join(root,selected.profile),'--'+component.kind,component.selector,'--out',output,'--accept-local-review','define-alchlang-behavior-migration'];
 const result=spawnSync(node,args,{encoding:'utf8',maxBuffer:16*1024*1024,env:{...process.env,ALCHLANG_DOMAINSPEC_PACKAGE_ROOT:path.join(craftRoot,'cli')}});
 writeFileSync(path.join(directory,'stdout.log'),result.stdout??'');writeFileSync(path.join(directory,'stderr.log'),result.stderr??'');
 if(result.status!==0)throw Error('component-generation-failed: '+directory);
 if(fingerprint()!==source)throw Error('source-changed-during-generation');
 const manifest=JSON.parse(readFileSync(path.join(output,'manifest.json')));
 const record={name,source,output,member:component.kind+'.mjs',files:manifest.files};
 const pending=path.join(directory,'index.json');
 writeFileSync(pending,JSON.stringify(record,null,2)+'\n',{flag:'wx'});
 try {linkSync(pending,index);} catch(error) {if(error.code!=='EEXIST')throw error;} finally {unlinkSync(pending);}
 // Publication is no-replace and complete before another process reads it.
 // Reuse the winner only after the ordinary source and artifact checks.
 return generate(name);
}
 return {selected,inputs,fingerprint,generate};
}
export const {selected,inputs,fingerprint,generate}=componentGenerator();
