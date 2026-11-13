#!/usr/bin/env node
import {readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {activation} from '../../lab-runtime/alchlang/shared-records/activation.mjs';
import {loadTrust} from '../../lab-runtime/alchlang/shared-records/implementation.mjs';
import {inspectViews,reconcileViews} from './views.mjs';
import {prepareDirectoryView,publishDirectoryView} from './publication.mjs';
import {runLifecycle} from './lifecycle.mjs';
import {readPublishedRecords} from './catalog.mjs';
export async function main(args=process.argv.slice(2)){
 const [command,...rest]=args,flags={};
 for(let i=0;i<rest.length;i+=2){if(!['--file','--output'].includes(rest[i])||!rest[i+1]||Object.hasOwn(flags,rest[i]))throw Error('invalid-record-workflow-option');flags[rest[i]]=rest[i+1];}
 if(!command||command==='help')return {commands:['views-inspect','views-reconcile','prepare-directory-view','publish-directory-view','lifecycle','record-catalog']};
 const active=activation({required:true}),trust=loadTrust(active.trust),request=flags['--file']?JSON.parse(readFileSync(flags['--file'])):null;
 let result;
 if(command==='views-inspect')result=await inspectViews(active,trust);
 else if(command==='views-reconcile')result=await reconcileViews(active,trust);
 else if(command==='prepare-directory-view')result=await prepareDirectoryView(active,trust,request);
 else if(command==='publish-directory-view')result=await publishDirectoryView(request,trust,active);
 else if(command==='lifecycle')result=await runLifecycle(request,active,trust);
 else if(command==='record-catalog')result=readPublishedRecords(active,trust);
 else throw Error('unsupported-records-workflow-command');
 if(flags['--output'])writeFileSync(path.resolve(flags['--output']),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
 return result;
}
if(process.argv[1]===import.meta.filename){try{console.log(JSON.stringify(await main()));}catch(e){console.error(JSON.stringify({outcome:'Refused',reason:e.message}));process.exitCode=2;}}
