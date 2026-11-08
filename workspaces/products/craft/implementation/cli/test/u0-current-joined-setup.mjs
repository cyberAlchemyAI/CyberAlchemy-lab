import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
// Qualification driver only: all business/semantic/generation work is actual
// built Alch/Core API work. No business evaluator callback or JSON-made handle.
// Open Questions: U09 current candidate contract epoch, U10 CLI prefix repair and later installed replay.
export const coreRoot=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
export const repositoryRoot=path.resolve(coreRoot,'../../../../..');
export const alchRoot=path.join(repositoryRoot,'language/capabilities/alchlang/plans/general-compiler-v1/implementation');
export async function prepareJoinedU0(outputParent){
 process.env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT=coreRoot;
 const front=await import(pathToFileURL(path.join(alchRoot,'dist/index.js')).href),preparation=await import(pathToFileURL(path.join(alchRoot,'dist/business-authoring-prepare.js')).href),executable=await import(pathToFileURL(path.join(alchRoot,'dist/application-executable.js')).href),api=(await import(pathToFileURL(path.join(coreRoot,'dist/index.js')).href)).profileEngine;
 const sourceRoot=path.join(repositoryRoot,'implementation/craft-alchlang-commerce-2026-10-16/evidence/J02/selected-project'),decisionFile=path.join(outputParent,'qualification-accepted.json');
 const p=await front.prepareDirectBusinessAuthoringProjectV2(sourceRoot,'business.alch',{profile:'node-http-entry-u0-v4',output:'code'});
 // Explicit fixed qualification fixture choice; no inferred human/product approval.
 if(p.review.review.subject.owner!=='dispatch-team')throw Error('U09 fixture owner changed');
 front.recordDirectBusinessReviewDecisionV2(p.review,{decision_id:'u09-current-schema-qualification',owner:'dispatch-team',outcome:'accepted',reviewed_digest:p.review.review.review_sha256},decisionFile);
 const decision=front.captureDirectBusinessReviewDecisionV2(p.review,decisionFile),accepted=front.requireAcceptedDirectBusinessReviewV2(p.review,decision),input=p.runtime.inputs.form(p.selection,'dispatching',accepted.accepted,p.early),surface=Object.freeze({input:p.runtime.inputs,application:p.runtime.applications}),prepared=preparation.prepareDirectBusinessAuthoringApplicationV2(p.lowered.business,input,surface);
 const sourceProject=path.join(outputParent,'source');api.publishBusinessAuthoringDirectory(sourceProject,Object.entries(prepared.bindings.formation.projectFiles).map(([relative_path,content])=>({relative_path,content})),'.domainspec-direct-source-',()=>p.runtime.inputs.assertCurrent(input));
 p.runtime.registerProject(input,sourceProject);const compiled=executable.compileDirectApplicationExecutableV2(prepared.executable),application=compiled.checked,generated=p.runtime.generation.generate(application),callableRoot=path.join(outputParent,'callable');
 const writeCallable=directory=>api.publishBusinessAuthoringDirectory(directory,generated.files.map(file=>({relative_path:file.path,content:file.content})),'.domainspec-direct-callable-',()=>p.runtime.applications.assertCurrent(application));
 writeCallable(callableRoot);const callable=await p.runtime.generation.importGenerated(generated,path.join(callableRoot,'invoke.mjs'));
 return Object.freeze({front,api,p,decision,accepted,input,prepared,compiled,application,generated,callable,sourceProject,callableRoot,writeCallable,dispose(){front.disposeDirectBusinessAuthoringProjectV2(p);}});
}
