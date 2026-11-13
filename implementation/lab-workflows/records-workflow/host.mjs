import {nativePort} from '../../lab-runtime/alchlang/shared-records/ports.mjs';
import {enforce} from './kernel.mjs';
export async function resolveHost(request){
 const context=nativePort({action:'context',...request});
 await enforce('EnforceHost',{workspace_bound:!!context.workspace_ref,runtime_shared:context.placement==='shared',host_bound:!!context.native_host_project_ref,semantic_project_required:request.work!=null,semantic_project_present:context.project_ref!=null,semantic_project_matches:context.project_ref==null||context.project_ref===context.native_host_project_ref,record_scope_matches:request.work==null||request.work.payload?.project_ref===context.project_ref});
 return context;
}
