/** A source-owned multi-service topology for later generic composition.
 * It carries checked identities and contracts, but grants no executable
 * admission, profile selection, native binding, or event delivery.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from '../commerce/commerce-core-source-owner.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from '../commerce/commerce-core-semantic-owner.js';

export interface CoreServiceTopologyV1 {
 readonly schema_version:'craft.core-service-topology/v1-candidate';
 readonly application:string;
 readonly source_capture_sha256:string;
 readonly executable_sha256:string;
 readonly services:readonly {readonly id:string;readonly module:string}[];
 readonly entries:readonly {
  readonly id:string;readonly service:string;readonly interaction:'request-response'|'event';
  readonly target:string;readonly target_role:'Operation'|'Query'|'Workflow';readonly target_service:string|null;
  readonly principal_kind:'customer'|'service';readonly permission:string;readonly auth_route_id:string;
  readonly contract_sha256:string;readonly source_site:string;
 }[];
 readonly events:readonly {readonly id:string;readonly source_site:string}[];
 readonly workflows:readonly {readonly id:string;readonly source_site:string;readonly contract_sha256:string}[];
 readonly qualification:'checked-core-topology-only;generic-profile-native-and-application-admission-not-established';
 readonly authority_effect:'none';
}

const site=(node:{readonly path:string;readonly start:number;readonly end:number})=>`${node.path}:${node.start}:${node.end}`;
const selector=(row:{readonly module:string;readonly name:string})=>`${row.module}.${row.name}`;

export function projectCoreServiceTopologyV1(
 sources:CoreCommerceSourceOwner,source:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
):CoreServiceTopologyV1 {
 assertCoreCommerceSourceOwner(sources);
 assertCoreCommerceSemanticOwner(semantics);
 semantics.assertSource(semantic,source);
 const capture=sources.inspect(source),checked=semantics.inspect(semantic),model=capture.reconstruction;
 const at=model.modules[0]?.syntax??{path:capture.application_path,start:0,end:0};
 if(checked.source_capture_sha256!==capture.capture_sha256)fail('StaleOwner',at,'semantic source identity differs from current Core capture');
 const declarations=model.modules.flatMap(m=>m.declarations),byId=new Map(declarations.map(d=>[d.id,d]));
 const sourceEntries=declarations.filter(d=>d.surface==='Entry');
 if(sourceEntries.length!==checked.entries.length)fail('MissingMapping',at,'checked Entry contracts must cover every original Entry exactly');
 const entryContracts=new Map(checked.entries.map(e=>[e.id,e]));
 if(entryContracts.size!==checked.entries.length)fail('DuplicateSymbol',at,'duplicate checked Entry identity');
 const serviceIds=new Set(model.services.map(s=>s.service));
 const entries=sourceEntries.map(d=>{
  const entry=entryContracts.get(d.id);
  if(!entry||!serviceIds.has(entry.service))fail('MissingMapping',d.syntax,'Entry requires exact checked service and contract');
  const target=selector(entry.invokes),targetDecl=byId.get(target);
  if(!targetDecl||targetDecl.id!==d.invokes||!['Operation','Query','Workflow'].includes(targetDecl.surface))fail('MissingMapping',d.syntax,'checked Entry target must match original source declaration');
  const targetService=model.ownership.find(o=>o.declaration===target)?.service??null;
  return {id:d.id,service:entry.service,interaction:entry.interaction,target,target_role:targetDecl.surface as 'Operation'|'Query'|'Workflow',target_service:targetService,principal_kind:entry.access.principal_kind,permission:entry.access.permission,auth_route_id:entry.access.auth_route_id,contract_sha256:dataDigest(entry),source_site:site(d.syntax)};
 });
 const checkedWorkflows=new Map(checked.workflows.map(w=>[selector(w.workflow),w]));
 const sourceWorkflows=declarations.filter(d=>d.surface==='Workflow');
 if(sourceWorkflows.length!==checked.workflows.length||checkedWorkflows.size!==checked.workflows.length)fail('MissingMapping',at,'checked Workflow contracts must cover every original Workflow exactly');
 const workflows=sourceWorkflows.map(d=>{
  const contract=checkedWorkflows.get(d.id);
  if(!contract)fail('MissingMapping',d.syntax,'Workflow requires exact checked contract');
  return {id:d.id,source_site:site(d.syntax),contract_sha256:dataDigest(contract)};
 });
 const events=declarations.filter(d=>d.surface==='Event').map(d=>({id:d.id,source_site:site(d.syntax)}));
 sources.assertCurrent(source);
 semantics.assertCurrent(semantic);
 return coreFreeze({schema_version:'craft.core-service-topology/v1-candidate',application:checked.application,source_capture_sha256:capture.capture_sha256,executable_sha256:checked.executable_sha256,services:model.services.map(s=>({id:s.service,module:s.module})),entries,events,workflows,qualification:'checked-core-topology-only;generic-profile-native-and-application-admission-not-established',authority_effect:'none'});
}
