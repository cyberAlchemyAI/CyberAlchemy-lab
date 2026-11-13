import assert from 'node:assert/strict';import {readFileSync,writeFileSync} from 'node:fs';import path from 'node:path';
import {load,canonical} from '../../../workspaces/products/define/implementation/cli/alchlang/runtime/runtime.mjs';
import {run} from '../../../workspaces/products/define/implementation/cli/alchlang/preparation/cli.mjs';
import {document} from '../../../workspaces/products/define/implementation/cli/alchlang/preparation/journal.mjs';
import {inspectHandoff,responseToHandoff} from '../../../implementation/lab-workflows/records-workflow/handoff.mjs';
const here=import.meta.dirname,work=path.join(here,'.local/define-refinement'),pack=path.join(here,'.local/contract-refinement-package'),actor='person:<vrondelli>',put=(name,x)=>{const file=path.join(here,name);writeFileSync(file,JSON.stringify(x,null,2)+'\n');return file;};
const loaded=await load(work),existing=loaded.events.find(e=>e.preparation?.command==='handoff'&&e.preparation.output.handoff_ref==='handoff:lab-records-refinement');
if(!existing){
 const source=document(Buffer.from(JSON.stringify({workspace_ref:'workspace:define:lab',product_ref:'product:define',scope:'Product-only semantic preparation; no semantic Project or native permission inferred.'}))),snapshot=document(Buffer.from(canonical(loaded.current))),declared=document(Buffer.from('Inspect the exact reused meaning bundle; no new global definition or execution authority.'));
 const context={workspace_selection:source.binding,context_source:source.binding,product:'product:define',project:null,work:null,membership:null,description:source.binding};
 const check={requested_use:'ReviewMeaningBundle',snapshot:snapshot.binding,context_sufficient:true,structural_failures:'0',open_obligations:'0',blocking_obligations:'0',candidate_selected:false,candidate_complete:false,parameter_binding_complete:false,performed_checks:declared.binding,obligations:declared.binding};
 const preview=put('HANDOFF-PREVIEW-INPUT.json',{input:{preparation_context:context,handoff_ref:'handoff:lab-records-refinement',check},documents:[source,snapshot,declared]});
 const input=await run('handoff-input',{'--work':work,'--file':preview,'--package':pack,'--actor':actor});
 await run('handoff',{'--work':work,'--file':put('HANDOFF-INPUT.json',input),'--package':pack,'--actor':actor,'--id':'lab-refinement-handoff'});
}
const request={work,package:pack,handoff_ref:'handoff:lab-records-refinement',consumer:'lab:shared-runtime',intended_use:'inspect-preparation'},verified=await inspectHandoff(request);
await assert.rejects(()=>inspectHandoff({...request,consumer:'foreign-consumer'}),/context-mismatch/);
const selfContained=await inspectHandoff({...request,package:null});assert(selfContained.bytes.equals(verified.bytes));
const response=await responseToHandoff(verified,{responder:'lab:shared-runtime',message:'The exact reusable meaning bundle was inspected. This reported acknowledgement grants no authority.'});assert.equal(response.posture,'reported-acknowledgement');
put('HANDOFF-CONSUMER-VERIFICATION.json',{status:'PASS',handoff:verified.handoff,package_removed_path_supported:true,foreign_consumer_refused:true,response,authority_effect:'none'});
console.log(JSON.stringify({status:'PASS',facts:verified.facts}));
