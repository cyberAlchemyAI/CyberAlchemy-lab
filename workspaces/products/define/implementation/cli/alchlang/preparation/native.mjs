/** Execute only original, checked AlchLang selections. This adapter owns no semantic rules. */
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,existsSync} from 'node:fs';
import path from 'node:path';
import {build,root,craftRoot,sha} from './build.mjs';
import {build as authorBuild} from '../runtime/build.mjs';
import {createSourceOperationCompiler} from '../../../../../../../implementation/artifact-runtime/compile-source-operation.mjs';
import {evaluateArtifact} from '../../../../../../../implementation/artifact-runtime/pure-operation.mjs';
const compiler=await createSourceOperationCompiler(path.join(craftRoot,'cli'));
export const selectors=Object.freeze({carry:'Define.Design.PlanSelectiveCarry',view:'Define.Design.ValidateCurrentView',search:'Define.Design.SearchCatalog',kind:'Define.Design.NoteKindForCommand',contribute:'Define.Design.RecordContribution',assessment:'Define.Design.RecordCandidateAssessment',candidate:'Define.Design.RecordCandidateDraft',scopedContext:'Define.Design.ValidateScopedContext',context:'Define.Design.ValidateContext',lookup:'Define.Design.ObserveLookup',revise:'Define.Design.ValidateRevision','inspect-fields':'Define.Design.InspectAttributableFields',fields:'Define.Design.InspectCandidateFields',assess:'Define.Design.AssessObservedPreparation',handoff:'Define.Design.PrepareHandoff',ack:'Define.Design.ObserveAcknowledgement',note:'Define.Design.PrepareJournalNote',next:'Define.Design.NextObservedAction'});
function checked(b){const m=JSON.parse(readFileSync(path.join(b.output,'manifest.json')));if(sha(readFileSync(path.join(b.output,'manifest.json')))!==b.manifest_sha256)throw Error('preparation-manifest-drift');for(const row of m.files){const raw=readFileSync(path.join(b.output,row.path));if(raw.length!==row.bytes||sha(raw)!==row.sha256)throw Error('preparation-member-drift');}return b;}
function selection(selector){
 if(!Object.values(selectors).includes(selector))throw Error('unselected-preparation-operation');
 const app=checked(build()),base=path.join(root,'.local/roles');mkdirSync(base,{recursive:true});const key=sha(app.source+selector+readFileSync(import.meta.filename)),index=path.join(base,key+'.json');
 if(existsSync(index)){const saved=JSON.parse(readFileSync(index));return saved;}
 const output=path.join(mkdtempSync(path.join(base,'role-')),'generated');compiler.compile({modelRoot:path.join(app.output,'model'),selector,outputDirectory:output});const result={output,manifest_sha256:sha(readFileSync(path.join(output,'manifest.json')))};try{writeFileSync(index,JSON.stringify(result),{flag:'wx'});}catch(error){if(error.code!=='EEXIST')throw error;return JSON.parse(readFileSync(index));}return result;
}
export async function evaluate(selector,input){const b=selection(selector),r=await evaluateArtifact(b.output,'operation.mjs',input,{manifest_sha256:b.manifest_sha256});return returned(r,JSON.parse(readFileSync(path.join(b.output,'manifest.json'))).role==='Operation');}
function returned(r,operation=true){if(!r.ok)throw Error('preparation-evaluation-'+r.error.code);const w=JSON.parse(new TextDecoder().decode(r.wire));if(!operation)return w;if(w.tag!=='Returned')throw Error('preparation-'+w.tag.toLowerCase()+'-'+w.fields.code);return w.fields.value;}
export async function authorValue(selector,current){const b=authorBuild(),m=JSON.parse(readFileSync(path.join(b.output,'manifest.json'))),directory=path.join(b.output,m.selections[selector]);return returned(await evaluateArtifact(directory,'operation.mjs',{session:current},{manifest_sha256:b.files[m.selections[selector]+'/manifest.json']}),false);}
export const facts=current=>authorValue('Define.Work.SemanticPreparationFacts',current);
export function model(){return checked(build()).source;}