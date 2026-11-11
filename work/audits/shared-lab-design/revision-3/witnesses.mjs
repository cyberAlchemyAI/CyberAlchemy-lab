import assert from 'node:assert/strict';import{readFileSync,writeFileSync,mkdirSync,mkdtempSync}from'node:fs';import path from'node:path';import{build,root,craftRoot,sha}from'/home/vlad_/projects/CyberAlchemy-lab/work/plans/shared-definitions-records-r3/alchlang/build.mjs';import{createSourceOperationCompiler}from'/home/vlad_/projects/CyberAlchemy-lab/implementation/artifact-runtime/compile-source-operation.mjs';import{evaluateArtifact}from'/home/vlad_/projects/CyberAlchemy-lab/implementation/artifact-runtime/pure-operation.mjs';
const b=build(),compiler=await createSourceOperationCompiler(path.join(craftRoot,'cli')),base=path.join(root,'.local/fixtures');mkdirSync(base,{recursive:true});const directory=mkdtempSync(path.join(base,'run-')),compiled=new Map(),checks=[];
async function call(name,input){let value=compiled.get(name);if(!value){const out=path.join(directory,name);compiler.compile({modelRoot:path.join(b.output,'model'),selector:'Lab.SharedDesign.'+name,outputDirectory:out});value={out,sha:sha(readFileSync(path.join(out,'manifest.json')))};compiled.set(name,value);}const r=await evaluateArtifact(value.out,'operation.mjs',input,{manifest_sha256:value.sha});assert.equal(r.ok,true,JSON.stringify(r));const output=JSON.parse(new TextDecoder().decode(r.wire));if(output.tag!=='Returned')throw Error(output.fields.code);return output.fields.value;}
const check=async(name,fn)=>{await fn();checks.push(name);console.log('PASS '+name);},hash='a'.repeat(64),other='b'.repeat(64),B=(ref='fixture:body',digest=hash)=>({ref,sha256:digest,bytes:'10'});
const review=(ref='fixture:definition')=>({target:B(ref),expected_owner:'role:definition-owner',scope:'scope:fixture',source_cut:hash,source_current:true,fields_receipt:B('fixture:schema-proof'),consumer_bindings_current:true,disposition:null});
function accept(value){return {...value,disposition:{target:value.target,previous:null,owner:value.expected_owner,scope:value.scope,source_cut:value.source_cut,outcome:'Accepted',role_assignment:B('fixture:role'),verification_receipt:B('fixture:owner-proof')}};}
const V=(subject,scope,cut,predicate,issuer="fixture:verifier")=>({subject,scope,cut,predicate,issuer,policy:B("fixture:policy"),proof:B("fixture:proof")});
const five=Array.from({length:5},(_,i)=>review('fixture:definition:'+i)),fiveArgs={expected:five.map(x=>x.target),reviews:five};
const join={run_ref:'join:fixture',workspace:'workspace:fixture',phase:'NativeUnknown',source_cut:hash,current_source_cut:other,original_operation:'operation:fixture',native_outcome:'Unknown',publication_outcome:'Unobserved'};
const transition={observed_operation:join.original_operation,observed_run:join.run_ref,observed_phase:'NativeUnknown',observed_signal:'ObserveRefusal',observed_outcome:'Refused',join_key:{id:'1',operation_key:'2',run_ref:join.run_ref,workspace:join.workspace,operation:join.original_operation,evidence:V(B(join.run_ref),join.workspace,hash,'stable-join-identity')},phase:'NativeUnknown',signal:'ObserveRefusal',revision:'2',observed_revision:'2',cut:hash,past_fact:B('fixture:refusal'),evidence:V(B('fixture:refusal'),join.workspace,hash,'join-transition')};

const {projectVerified,digest}=await import('/home/vlad_/projects/CyberAlchemy-lab/work/plans/shared-definitions-records-r3/alchlang/verified-projection.mjs');
const operation='AssessJoinTransition',scope='workspace:fixture',cut=hash;
const artifactBytes=Buffer.from(JSON.stringify({operation,scope,cut,input:{value:transition}}));
const receiptBytes=Buffer.from(JSON.stringify({version:1,predicate:'verified-planning-input',operation,scope,cut,artifact:{sha256:digest(artifactBytes),bytes:artifactBytes.length}}));
const pin=digest(receiptBytes);
const projected=await projectVerified({operation,scope,cut,artifactBytes,receiptBytes,authenticate:async bytes=>digest(bytes)===pin?pin:null});
assert.deepEqual(projected.value,transition);
const results=[{name:'envelope-projection-uses-no-original-receipt-bytes',observed:'Accepted pinned envelope; original receipts are issuer obligations'}];
async function observe(name,operation,input,expected){
 const observed=await call(operation,input);
 assert.equal(observed,expected);
 results.push({name,observed});
}
await observe('direct-publication-refusal-continuation','PlanJoinContinuation',{value:{...join,phase:'PublicationPrepared',native_outcome:'Committed',publication_outcome:'Refused',current_source_cut:hash}},'PreserveRefusal');
await assert.rejects(()=>call('ValidateJoinTransition',{phase:'PublicationPrepared',signal:'ObserveRefusal'}),/invalid-join-transition/);
results.push({name:'direct-publication-refusal-transition',observed:'invalid-join-transition'});
await observe('published-old-cut-continuation','PlanJoinContinuation',{value:{...join,phase:'CanonicalPublished',native_outcome:'Committed',publication_outcome:'Committed',current_source_cut:other}},'Stale');
await observe('terminal-phase-with-unresolved-effects','PlanJoinContinuation',{value:{...join,phase:'Completed',native_outcome:'Unknown',publication_outcome:'Unknown'}},'PreserveCompleted');
writeFileSync(new URL('./WITNESSES.json',import.meta.url),JSON.stringify({source:b.source,manifest_sha256:b.manifest_sha256,results},null,2)+'\n');
