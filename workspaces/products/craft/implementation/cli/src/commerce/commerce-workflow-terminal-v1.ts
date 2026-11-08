/** A selected finish is admitted only when the checked terminal guard holds
 * over fresh original rows owned by the Workflow service. No effect occurs.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture}
 from './commerce-core-source-owner.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture}
 from './commerce-core-semantic-owner.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1}
 from './commerce-workflow-coordination-binding-v1.js';
import {assertCommerceComputationDomainOwner,type CommerceComputationDomainOwner,
 type CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1}
 from './commerce-service-storage-v1.js';
import {assertCommerceWorkflowSnapshotOwnerV1,type CommerceWorkflowSnapshotOwnerV1,
 type CommerceWorkflowSnapshotHandleV1} from './commerce-workflow-snapshot-v1.js';
import {assertCommerceWorkflowResumeSelectorV1,type CommerceWorkflowResumeSelectorV1,
 type CommerceWorkflowResumeSelectionV1} from './commerce-workflow-resume-v1.js';
import {createCommerceWorkflowExpressionOwnerV1} from './commerce-workflow-expression-v1.js';

export type CommerceWorkflowTerminalResultV1=
 Readonly<{kind:'finished';terminal:string;order_id:string;source_capture_sha256:string;
  qualification:'checked-terminal-guard-on-current-original-owned-rows';authority_effect:'none'}>|
 Readonly<{kind:'terminal-suspended';terminal:string;reason:'guard-false'|'row-missing';
  authority_effect:'none'}>;

/** The resume decision supplies only the terminal name. The guard, persisted
 * row selectors and source identity are selected again from original owners. */
export function inspectCommerceWorkflowTerminalV1(input:Readonly<{
 sources:CoreCommerceSourceOwner;capture:CoreCommerceSourceCapture;
 semantics:CoreCommerceSemanticOwner;semantic:CoreCommerceSemanticCapture;
 binding:CommerceWorkflowCoordinationBindingV1;
 domain:CommerceComputationDomainOwner;baseline:CommerceComputationDomainHandle;
 storage:CommerceServiceStorageOwnerV1;
 snapshots:CommerceWorkflowSnapshotOwnerV1;snapshot:CommerceWorkflowSnapshotHandleV1;
 resumes:CommerceWorkflowResumeSelectorV1;selection:CommerceWorkflowResumeSelectionV1;
}>):CommerceWorkflowTerminalResultV1 {
 const {sources,capture,semantics,semantic,binding,domain,baseline,storage,
  snapshots,snapshot,resumes,selection}=input;
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceSemanticOwner(semantics);
 assertCommerceWorkflowCoordinationBindingV1(binding);
 assertCommerceComputationDomainOwner(domain);assertCommerceServiceStorageOwnerV1(storage);
 assertCommerceWorkflowSnapshotOwnerV1(snapshots);assertCommerceWorkflowResumeSelectorV1(resumes);
 resumes.assertSelectionCurrent(selection);
 const selected=resumes.inspectSelection(selection),action=selected.action,source=binding.inspect(),
  captured=sources.inspect(capture),store=storage.inspect(),witness=snapshots.recheck(snapshot);
 if(selected.outcome!=='selected'||action?.kind!=='finish'||
  selected.source_capture_sha256!==source.source_capture_sha256||
  captured.capture_sha256!==source.source_capture_sha256||
  store.source_capture_sha256!==source.source_capture_sha256||
  store.service!==source.owner_service||witness.source_capture_sha256!==source.source_capture_sha256||
  witness.store_id!==store.store_id||witness.order_id!==selected.order_id||
  witness.worker_id!==selected.worker_id||witness.worker_epoch!==selected.worker_epoch||
  witness.progress_version!==selected.progress_version)
  throw new Error('selected terminal requires the current original Workflow snapshot and store');
 const terminalIndex=source.workflow.terminals.findIndex(row=>row.name===action.target),
  terminal=source.workflow.terminals[terminalIndex];
 if(terminalIndex<0||!terminal||terminal.effects!=='none'||
  terminal.persisted_sources.length<1||terminal.persisted_sources.length>16)
  throw new Error('one checked source terminal with bounded persisted rows required');
 const records:Record<string,Record<string,unknown>>=Object.create(null);
 for(const entity of terminal.persisted_sources){
  const declarations=captured.reconstruction.modules.flatMap(module=>module.declarations)
   .filter(row=>row.id===entity&&row.surface==='Entity');
  if(declarations.length!==1||declarations[0]!.identity.length!==1||
   captured.reconstruction.ownership.filter(row=>row.declaration===entity&&
    row.service===source.owner_service).length!==1)
   throw new Error('terminal persisted source needs one original owned Entity identity');
  const key=Object.freeze({[declarations[0]!.identity[0]!]:selected.order_id});
  const value=storage.inspectStoredRecord(entity,0,key);
  if(value===null)return Object.freeze({kind:'terminal-suspended' as const,terminal:terminal.name,
   reason:'row-missing' as const,authority_effect:'none' as const});
  const [namespace,name]=entity.split('.');
  if(!namespace||!name||entity.split('.').length!==2)
   throw new Error('terminal persisted source requires a checked module and Entity name');
  (records[namespace]??=Object.create(null))[name]=value as Record<string,unknown>;
 }
 const expression=createCommerceWorkflowExpressionOwnerV1(binding,semantics,semantic,domain,baseline);
 try{
  const guard=expression.bind(`$.terminals[${terminalIndex}].guard`),allowed=expression.evaluate(guard,records);
  if(typeof allowed!=='boolean')throw new Error('checked terminal guard must return Bool');
  resumes.assertSelectionCurrent(selection);snapshots.recheck(snapshot);storage.assertCurrent();
  return allowed?Object.freeze({kind:'finished' as const,terminal:terminal.name,
   order_id:selected.order_id,source_capture_sha256:source.source_capture_sha256,
   qualification:'checked-terminal-guard-on-current-original-owned-rows' as const,
   authority_effect:'none' as const}):
   Object.freeze({kind:'terminal-suspended' as const,terminal:terminal.name,
    reason:'guard-false' as const,authority_effect:'none' as const});
 }finally{expression.dispose();}
}
