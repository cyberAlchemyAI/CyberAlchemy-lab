import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {compileProject} from '../compilation/certificate.js';
import {assertCompiledProjectSnapshot} from '../input/project-model.js';
import type {CompiledProjectGraph} from '../input/project-model.js';
import {captureJson,reject} from './contracts.js';
import {loadBusinessU0ProfileV4,assertLoadedU0ProfileV4Current,loadedU0RuntimeFilesV4,disposeLoadedU0ProfileV4,captureU0FileV4,type U0ProfileLoadOptionsV4} from './loader-v4.js';
import {captureBusinessIdentityV2} from './business-authoring-identity-v2.js';
import {createBusinessCoreRecipeOwnerV2} from './business-authoring-recipes.js';
import {createBusinessReviewOwnerV2} from './business-decision.js';
import {createBusinessRequestStagesOwnerV2,type U0RequestNativeAssetsOwnerV2} from './business-authoring-request.js';
import {createAuthoringBusinessInputOwnerV2} from './business-authoring-input.js';
import {createBusinessDirectApplicationOwnerV2} from './business-authoring-application.js';
import {createBusinessPureGenerationOwnerV2} from './application-adapter.js';
import {createBusinessDirectCoverageOwnerV2} from './business-authoring-coverage.js';
import {createBusinessCoverageViewsOwnerV2} from './business-authoring-views.js';
import {createBusinessOutputWriterOwnerV2} from './business-authoring-output.js';
import type {BusinessSourceCapture} from './business-authoring-protocol.js';
import type {BusinessCaptureIdentityV2,AuthoringBusinessInputV2} from './business-authoring-identity-protocol-v2.js';
import type {BusinessPureGenerationOwnerV2} from './business-authoring-stages-v2.js';
/** Trusted built SDK assembly. No business evaluator or mutable public init port.
 * Open Questions: J02/Q02/K02/U04/G01/U08/U09 qualify original joined witnesses. */
function fail(at:string,message:string):never{return reject('BUSINESS_U0_BOOTSTRAP',at,message);}
const implementation=captureU0FileV4(fileURLToPath(import.meta.url));
export async function createBusinessU0RuntimeV4(options:U0ProfileLoadOptionsV4={}){
 const loaded=await loadBusinessU0ProfileV4(options),basis=loaded.basis;
 const models=new Map<string,Readonly<{source:BusinessSourceCapture;capture:BusinessCaptureIdentityV2;assertCurrent:()=>void}>>();
 const assertCurrent=()=>{implementation.assertCurrent();assertLoadedU0ProfileV4Current(loaded);for(const model of models.values())model.assertCurrent();};
 const assertBasis=(candidate:typeof basis)=>{if(candidate!==basis)fail('/basis','exact original loaded basis required');assertCurrent();};
 const captureOwner=Object.freeze({assertCurrent:assertBasis,capture(modelId:string,candidate:typeof basis){assertBasis(candidate);const model=models.get(modelId);if(!model)fail('/model','source has not been independently captured');model.assertCurrent();return Object.freeze({source:model.source,capture:model.capture});}});
 const recipes=createBusinessCoreRecipeOwnerV2(captureOwner),reviews=createBusinessReviewOwnerV2(recipes);
 const native=Object.freeze<U0RequestNativeAssetsOwnerV2>({assertCurrent:assertBasis,assertSelectionBasis(selection,candidate){assertBasis(candidate);recipes.assertCurrent(selection);if(selection.native_basis.basis_sha256!==basis.basis_sha256)fail('/selection','selection must belong to this original SDK/basis owner');},assets(candidate){assertBasis(candidate);return loadedU0RuntimeFilesV4(loaded);}});
 let actualGeneration:BusinessPureGenerationOwnerV2|undefined;
 function generationOwner(){if(!actualGeneration)fail('/generation','private owner assembly is not initialized');return actualGeneration;}
 const generationPort=Object.freeze<BusinessPureGenerationOwnerV2>({generate(application){return generationOwner().generate(application);},importGenerated(source,file){return generationOwner().importGenerated(source,file);},assertCurrent(callable){generationOwner().assertCurrent(callable);}});
 const requests=createBusinessRequestStagesOwnerV2(recipes,generationPort,native),inputs=createAuthoringBusinessInputOwnerV2(recipes,reviews,requests);
 const graphRegistry=new WeakMap<object,CompiledProjectGraph>();
 const graphs=Object.freeze({capture(input:AuthoringBusinessInputV2){inputs.assertCurrent(input);const graph=graphRegistry.get(input);if(!graph)fail('/graph','actual compiled source project has not been registered');assertCompiledProjectSnapshot(graph);return graph;},assertCurrent(input:AuthoringBusinessInputV2,graph:CompiledProjectGraph){inputs.assertCurrent(input);if(graphRegistry.get(input)!==graph)fail('/graph','exact original input/compiled graph required');assertCompiledProjectSnapshot(graph);}});
 const applications=createBusinessDirectApplicationOwnerV2(inputs,graphs);actualGeneration=createBusinessPureGenerationOwnerV2(applications);
 const coverage=createBusinessDirectCoverageOwnerV2(inputs,applications,requests,actualGeneration),views=createBusinessCoverageViewsOwnerV2(coverage),output=createBusinessOutputWriterOwnerV2(applications,requests,actualGeneration,views,native);
 assertCurrent();
 return Object.freeze({kind:'business-u0-runtime-v4' as const,loaded,basis,recipes,reviews,requests,inputs,applications,generation:actualGeneration,coverage,views,output,native,assertCurrent,
  captureSource(modelId:string,root:string,relative:string){assertCurrent();if(typeof modelId!=='string'||!modelId||modelId.length>128||models.has(modelId))fail('/model','unique bounded model ID required');if(typeof relative!=='string'||path.isAbsolute(relative)||relative.split('/').some(part=>!part||part==='.'||part==='..')||relative.includes('\\'))fail('/source','relative source path required');
   const file=captureU0FileV4(path.join(path.resolve(root),relative));
   const source=captureJson({path:relative,text:file.text,sha256:file.sha256,bytes:file.bytes}) as unknown as BusinessSourceCapture;
   const capture=captureBusinessIdentityV2({schema_version:'craft.business-capture/v2-candidate',recipe_ref:'direct-entity-bool-operation/v2-candidate',source:{path:relative,sha256:file.sha256,bytes:file.bytes},profiles:[{id:loaded.profile.id,version:loaded.profile.version,sha256:loaded.manifest.sha256}],tools:[{id:'node',sha256:loaded.node.sha256},{id:'public-sdk',sha256:basis.sdk_sha256}],authority_effect:'none'});
   models.set(modelId,Object.freeze({source,capture,assertCurrent:file.assertCurrent}));assertCurrent();return Object.freeze({source,capture});
  },
  registerProject(input:AuthoringBusinessInputV2,root:string){assertCurrent();inputs.assertCurrent(input);if(graphRegistry.has(input))fail('/graph','input already owns a project');const graph=compileProject(path.resolve(root)).graph;assertCompiledProjectSnapshot(graph);graphRegistry.set(input,graph);return graph;},
  dispose(){assertCurrent();disposeLoadedU0ProfileV4(loaded);},
 });
}
export type BusinessU0RuntimeV4=Awaited<ReturnType<typeof createBusinessU0RuntimeV4>>;
