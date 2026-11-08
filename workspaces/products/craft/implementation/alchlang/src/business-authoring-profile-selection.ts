import type {BusinessRecipeModelInput,BusinessRecipeRequirements} from './business-authoring-normalization-protocol.js';
import {assertBusinessBehaviorCurrent,type BusinessBehavior} from './business-authoring-behavior.js';
import {businessCanonical,businessHash,businessReject} from './business-authoring-model.js';

/** Trusted public Core SDK surface, never a profile-supplied interpreter or input callback.
 * Open questions: B06 must keep this producer correspondence through accepted materialization. */
export interface BusinessRecipeSelectionSurface {
 readonly kind:'business-recipe-selection';readonly models:readonly BusinessRecipeModelInput[];readonly authority_effect:'none';
}
export interface BusinessRecipeEngine<Snapshot,Selection extends BusinessRecipeSelectionSurface> {
 selectBusinessAuthoringRecipe(snapshot:Snapshot,models:readonly BusinessRecipeModelInput[],requirements?:BusinessRecipeRequirements):Selection;
 assertBusinessRecipeSelectionCurrent(selection:Selection):void;
}
export interface PreparedBusinessRecipeSelection<Selection extends BusinessRecipeSelectionSurface> {
 readonly kind:'prepared-business-recipe-selection';readonly behaviors:readonly BusinessBehavior[];readonly selection:Selection;
}
type Owner={behaviors:readonly BusinessBehavior[];selection:BusinessRecipeSelectionSurface;assertSelection:(value:BusinessRecipeSelectionSurface)=>void;fingerprint:string};
const owners=new WeakMap<object,Owner>();
function inputs(behaviors:readonly BusinessBehavior[]):readonly BusinessRecipeModelInput[] {
 return behaviors.map(behavior=>{
  assertBusinessBehaviorCurrent(behavior);
  const {path,sha256,bytes}=behavior.business.source;
  return {model_id:behavior.data.model_id,source:{path,sha256,bytes},spec:behavior.business.data,formal:behavior.formal.data,behavior:behavior.data};
 });
}
export function prepareBusinessRecipeSelection<Snapshot,Selection extends BusinessRecipeSelectionSurface>(snapshot:Snapshot,behaviors:readonly BusinessBehavior[],engine:BusinessRecipeEngine<Snapshot,Selection>,requirements?:BusinessRecipeRequirements):PreparedBusinessRecipeSelection<Selection> {
 if(!Array.isArray(behaviors)||!behaviors.length)businessReject('BUSINESS_REQUIRED','business.alch',1,1,'current normalized business behaviors required');
 // Check custody before inspecting any supplied handle fields.
 for(const behavior of behaviors)assertBusinessBehaviorCurrent(behavior);
 const ordered=Object.freeze([...behaviors].sort((a,b)=>a.data.model_id<b.data.model_id?-1:a.data.model_id>b.data.model_id?1:0));
 if(new Set(ordered.map(b=>b.data.model_id)).size!==ordered.length)businessReject('BUSINESS_AMBIGUOUS','business.alch',1,1,'one behavior per selected model identity');
 const originalInputs=inputs(ordered),select=engine.selectBusinessAuthoringRecipe.bind(engine),assertSelection=engine.assertBusinessRecipeSelectionCurrent.bind(engine);
 const selection=select(snapshot,originalInputs,requirements);assertSelection(selection);
 for(const behavior of ordered)assertBusinessBehaviorCurrent(behavior);
 if(selection.kind!=='business-recipe-selection'||selection.authority_effect!=='none'||businessCanonical(selection.models)!==businessCanonical(originalInputs))
  businessReject('BUSINESS_SOURCE_DRIFT','business.alch',1,1,'Core recipe selection must retain the exact genuine producer DTOs');
 const value=Object.freeze({kind:'prepared-business-recipe-selection' as const,behaviors:ordered,selection});
 owners.set(value,{behaviors:ordered,selection,assertSelection:assertSelection as Owner['assertSelection'],fingerprint:businessHash(businessCanonical(value))});
 assertPreparedBusinessRecipeSelectionCurrent(value);return value;
}
export function assertPreparedBusinessRecipeSelectionCurrent<Selection extends BusinessRecipeSelectionSurface>(value:PreparedBusinessRecipeSelection<Selection>):void {
 const state=value&&typeof value==='object'?owners.get(value):undefined;
 if(!state)businessReject('BUSINESS_HANDLE','business.alch',1,1,'registered original prepared recipe selection required');
 for(const behavior of state.behaviors)assertBusinessBehaviorCurrent(behavior);
 state.assertSelection(state.selection);
 if(value.behaviors!==state.behaviors||value.selection!==state.selection||businessHash(businessCanonical(value))!==state.fingerprint)
  businessReject('BUSINESS_SOURCE_DRIFT','business.alch',1,1,'prepared producer/profile correspondence changed');
 if(businessCanonical(state.selection.models)!==businessCanonical(inputs(state.behaviors)))
  businessReject('BUSINESS_SOURCE_DRIFT','business.alch',1,1,'selected business DTOs differ from genuine normalized producers');
}
