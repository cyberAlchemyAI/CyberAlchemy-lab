import {loadCompiledProjectGraph,type CompiledProjectGraph} from '../input/project-model.js';
import {decodeReconciledCompilationSelection,planCompiledReconciledProject} from '../generation/reconciled-project.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {sha256} from '../input/source-manifest.js';
import {executeReconciledVerification,validateReconciledVerificationTools,type ReconciledVerificationTools} from './reconciled-execution.js';
import {decodeReconciledPythonSelection} from '../generation/reconciled-python-selection.js';
import {planCompiledReconciledPythonProject} from '../generation/reconciled-python-project.js';
import {executeReconciledPythonVerification,validatePythonVerificationOptions,type PythonVerificationOptions} from './reconciled-python-native.js';
import {decodeReconciledRustSelection} from '../generation/reconciled-rust-selection.js';
import {planCompiledReconciledRustProject} from '../generation/reconciled-rust-project.js';
import {executeReconciledRustVerification,validateRustVerificationOptions,type RustVerificationOptions} from './reconciled-rust-native.js';

export const VERIFICATION_ENTRYPOINTS_DEFINITION_SHA256='dc29a6a22b60a3bce1b9fb3471ff6ee3e1312377d93cac24e12f143ad9b70f40';
function inputs(selection:unknown,tools:ReconciledVerificationTools){
 const selected=decodeReconciledCompilationSelection(selection),options=validateReconciledVerificationTools(tools);
 if(sha256(getReconciledSource('verification_entrypoints'))!==VERIFICATION_ENTRYPOINTS_DEFINITION_SHA256)throw new TypeError('DS_RECONCILED_VERIFICATION_ENTRYPOINTS: definition drift');
 return {selected,options};
}
/** Source verification loads once; currentness is independently rechecked by the executor. */
export function verifyReconciledSourceProject(sourceRoot:string,selection:unknown,tools:ReconciledVerificationTools){
 const {selected,options}=inputs(selection,tools),graph=loadCompiledProjectGraph(sourceRoot);
 return executeReconciledVerification(graph,planCompiledReconciledProject(graph,selected),options);
}
/** Planning uses the registered snapshot, never a silently refreshed replacement graph. */
export function verifyCompiledReconciledProject(graph:CompiledProjectGraph,selection:unknown,tools:ReconciledVerificationTools){
 const {selected,options}=inputs(selection,tools);
 return executeReconciledVerification(graph,planCompiledReconciledProject(graph,selected),options);
}
/** Python source verification loads once and joins native, semantic and finite
 * structural verification in the same owned temporary workspace. */
export function verifyReconciledPythonSourceProject(sourceRoot:string,selection:unknown,tools:PythonVerificationOptions){
 const selected=decodeReconciledPythonSelection(selection),options=validatePythonVerificationOptions(tools),graph=loadCompiledProjectGraph(sourceRoot);
 return executeReconciledPythonVerification(graph,planCompiledReconciledPythonProject(graph,selected),options);
}
export function verifyCompiledReconciledPythonProject(graph:CompiledProjectGraph,selection:unknown,tools:PythonVerificationOptions){
 const selected=decodeReconciledPythonSelection(selection),options=validatePythonVerificationOptions(tools);
 return executeReconciledPythonVerification(graph,planCompiledReconciledPythonProject(graph,selected),options);
}
/** Rust source verification loads once and runs exact native Cargo validation. */
export function verifyReconciledRustSourceProject(sourceRoot:string,selection:unknown,tools:RustVerificationOptions){
 const selected=decodeReconciledRustSelection(selection),options=validateRustVerificationOptions(tools),graph=loadCompiledProjectGraph(sourceRoot);
 return executeReconciledRustVerification(graph,planCompiledReconciledRustProject(graph,selected),options);
}
export function verifyCompiledReconciledRustProject(graph:CompiledProjectGraph,selection:unknown,tools:RustVerificationOptions){
 const selected=decodeReconciledRustSelection(selection),options=validateRustVerificationOptions(tools);
 return executeReconciledRustVerification(graph,planCompiledReconciledRustProject(graph,selected),options);
}
