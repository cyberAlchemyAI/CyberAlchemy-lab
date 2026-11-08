/** Original checked finite service-SQLite schema/repository generation owner.
 * No DB is opened, no query declaration or JSON projection grants row access.
 * Open Questions: docs/COMMERCE-SQLITE-FAMILY-V1.md#open-questions. */
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {mkdirSync} from 'node:fs';
import {stripTypeScriptTypes} from 'node:module';
import {createHash} from 'node:crypto';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {pinCoreImplementation,pinCorePhysicalCaptures,readCorePhysicalFile,writeCoreExclusiveFile,type CorePhysicalFile} from './commerce-core-physical.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import {assertCoreCommerceStageSourceOwner,type CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import {assertCommerceComputationDomainOwner,type CommerceComputationDomainOwner,type CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import {assertCommerceLocalPlanOwnerV1,type CommerceLocalPlanOwnerV1,type CommerceLocalReadHandleV1} from './commerce-local-plan-owner-v1.js';
import {assertFamilyOwnerV5,type CommerceFamilyOwnerV5} from '../profile-engine/family-v5.js';
import {createCoreValueTypes} from './commerce-core-types.js';
import {createCoreContextCatalog} from './commerce-core-context.js';
import {generateCommerceValueCodecBundle} from './commerce-value-codec-generation.js';
import {adoptCommerceGeneratedRepositoryV1} from './commerce-repository-adoption-v1.js';
import {deriveCommerceSqliteTableV1,deriveCommerceSqliteQueryV1,deriveCommerceSqliteServiceV1,type CommerceSqliteServiceDataV1,type CommerceSqliteQueryV1} from './commerce-sqlite-generation-v1.js';
import type {CommerceSourceHandle,CommerceDerivedFamilyHandle} from './commerce-stages-v1.js';
import type {CommerceRepositoryDataComponentV1} from './commerce-sqlite-repository-runtime-v1.js';
// Keep the authored TypeScript emitter as the byte-identical template in both
// source execution and the installed archive. Compilation removes declarations
// from the adjacent .js module, so that module cannot emit repository source.
const ext=path.extname(fileURLToPath(import.meta.url)),template='commerce-sqlite-repository-runtime-v1.ts';
const pin=pinCoreImplementation(import.meta.url,['commerce-sqlite-generation-v1'+ext,template,'commerce-core-physical'+ext,'commerce-repository-adoption-v1'+ext,'commerce-core-source-owner'+ext,'commerce-core-semantic-owner'+ext,'commerce-core-stage-owner'+ext,'commerce-core-types'+ext,'commerce-core-context'+ext,'commerce-computation-domain'+ext,'commerce-local-plan-owner-v1'+ext,'commerce-value-codec-generation'+ext,'../profile-engine/family-v5'+ext,'../profile-engine/contracts'+ext,'../system-integration/persistence-v2'+ext,'../system-integration/kernel-v2'+ext,'../system-integration/kernel-v2-types'+ext,'../system-integration/persistence-v2-types'+ext,'../input/source-manifest'+ext]);
const where={path:'service-sqlite-family',start:0,end:0},sha=(s:string)=>createHash('sha256').update(s).digest('hex');
export interface CommerceServiceSchemaHandleV1 {readonly kind:'original-commerce-service-sqlite-schema/v1-candidate'}
export interface CommerceRepositoryBundleHandleV1 {readonly kind:'original-generated-commerce-service-repository/v1-candidate'}
export interface CommerceSqliteQueryHandleV1 {readonly kind:'original-commerce-scoped-query-mapping/v1-candidate'}
export interface CommerceSqliteBundleV1 {readonly files:readonly {readonly path:string;readonly text:string}[];readonly manifest:Readonly<Record<string,unknown>>}
export interface CommerceSqliteFamilyOwnerV1 {
 bindService(service:string):CommerceServiceSchemaHandleV1;
 inspectService(handle:CommerceServiceSchemaHandleV1):CommerceSqliteServiceDataV1;
 bindQuery(service:CommerceServiceSchemaHandleV1,read:CommerceLocalReadHandleV1):CommerceSqliteQueryHandleV1;
 inspectQuery(handle:CommerceSqliteQueryHandleV1):CommerceSqliteQueryV1;
 emit(handle:CommerceServiceSchemaHandleV1):CommerceSqliteBundleV1;
 materialize(handle:CommerceServiceSchemaHandleV1,directory:string):CommerceRepositoryBundleHandleV1;
 adoptExisting(handle:CommerceServiceSchemaHandleV1,directory:string):CommerceRepositoryBundleHandleV1;
 inspectBundle(handle:CommerceRepositoryBundleHandleV1):Readonly<{service:string;source_capture_sha256:string;family_sha256:string;schema_sha256:string;directory:string;members:readonly CorePhysicalFile['file'][];qualification:string;authority_effect:'none'}>;
 loadDataComponent(handle:CommerceRepositoryBundleHandleV1):Promise<CommerceRepositoryDataComponentV1>;
 assertServiceCurrent(handle:CommerceServiceSchemaHandleV1):void;assertBundleCurrent(handle:CommerceRepositoryBundleHandleV1):void;
 disposeService(handle:CommerceServiceSchemaHandleV1):void;assertCurrent():void;dispose():void;
}
type Service={data:CommerceSqliteServiceDataV1;disposed:boolean};
type Bundle={service:Service;directory:string;files:readonly CorePhysicalFile[];physical:Readonly<{assertCurrent():void}>;data:CommerceRepositoryDataComponentV1|null};
const owners=new WeakSet<object>();
export function assertCommerceSqliteFamilyOwnerV1(owner:CommerceSqliteFamilyOwnerV1):void {if(!owner||typeof owner!=='object'||!owners.has(owner))fail('ForeignOwner',where,'original SQLite family owner required');owner.assertCurrent();}
export function createCommerceSqliteFamilyOwnerV1(sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,plans:CommerceLocalPlanOwnerV1,families:CommerceFamilyOwnerV5,family:CommerceDerivedFamilyHandle):CommerceSqliteFamilyOwnerV1 {
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceSemanticOwner(semantics);assertCoreCommerceStageSourceOwner(stage);assertCommerceComputationDomainOwner(domain);assertCommerceLocalPlanOwnerV1(plans);assertFamilyOwnerV5(families);semantics.assertSource(semantic,capture);pin.assertCurrent();
 // A matching digest alone does not prove that the plan owns these exact
 // parents. Establish identity once before using its transitive currentness.
 plans.assertParents({sources,capture,semantics,semantic,stage,source,domain,baseline});
 const captured=sources.inspect(capture),checked=semantics.inspect(semantic),staged=stage.inspect(source),values=domain.inspect(baseline),selected=families.inspect(family);
 if([checked.source_capture_sha256,staged.source_sha256,values.source_capture_sha256,selected.source_capture_sha256].some(x=>x!==captured.capture_sha256))fail('ForeignOwner',where,'SQLite source/semantic/domain/family parents must share original capture');
 if(!selected.native_requirements.some(r=>r.primitive_id==='service-sqlite'&&r.abi==='craft.commerce-service-store/v1-candidate'))fail('UnsupportedCapability',where,'actual selected family must require the known SQLite primitive');
 const prefix=selected.descriptor.parameters.tablePrefix;if(!/^[a-z][a-z0-9_]{0,15}$/.test(prefix)||selected.mapping_result.tablePrefix!==prefix)fail('InvalidContract',where,'actual checked profile Mapping must supply valid prefix');
 const types=createCoreValueTypes(captured.reconstruction),catalog=createCoreContextCatalog(types,captured.files.filter(f=>f.path.endsWith('.json'))),root=[...types.declarations.values()].find(d=>d.interface_kind==='application-composition')!;
 const coordination=catalog.asset(root,['coordination-contract'])?.value as any,coord=coordination?.coordination,app=staged.application,modules=stage.moduleContracts(source),recordMap=new Map(values.contract.values.records.map(r=>[r.name,r])),entityOwners=new Map<string,{service:string;suffix:string|undefined}>();
 if(!coord||typeof coord.owner_service!=='string'||!app.services.some(s=>s.id===coord.owner_service)||!coord.schema_selectors||!coord.physical_suffixes)fail('MissingMapping',where,'declared coordination schema owner required');
 const coordSelectors=new Set(Object.values(coord.schema_selectors));
 for(const row of checked.ownership){const record=recordMap.get(row.declaration);if(record?.role!=='Entity')continue;if(row.category==='technical')continue;
  let service=row.service,suffix:string|undefined;
  if(row.category==='coordination'){
   if(!coordSelectors.has(row.declaration))fail('MissingMapping',where,'coordination Entity must have explicit source selector and store owner');service=coord.owner_service;const name=row.declaration.split('.').at(-1)!;suffix=coord.physical_suffixes[name];if(typeof suffix!=='string'||!/^[a-z][a-z0-9_]{0,63}$/.test(suffix))fail('InvalidContract',where,'declared coordination physical suffix required');
  }
  if(!service||!app.services.some(s=>s.id===service)||!record.entity)fail('MissingMapping',where,'business Entity needs explicit original service ownership');entityOwners.set(row.declaration,{service,suffix});
 }
 const allTables=[...entityOwners].map(([name,owner])=>{const module=modules.find(m=>m.declarations.some(d=>d.selector.module+'.'+d.selector.name===name));if(!module)fail('UnknownReference',where,'table source identity absent');return deriveCommerceSqliteTableV1(recordMap.get(name)!,owner.service,prefix,module.source,values.contract.values,owner.suffix);});
 if(new Set(allTables.map(t=>t.physical_name)).size!==allTables.length)fail('DuplicateSymbol',where,'generated physical table names collide');
 const byService=new Map<string,CommerceSqliteServiceDataV1>();for(const service of app.services){const tables=allTables.filter(t=>t.owner===service.id);if(!tables.length)fail('MissingMapping',where,'selected service has no explicit source-owned Entity');const queries=checked.reads.filter(r=>r.service===service.id&&r.kind==='local').map(r=>deriveCommerceSqliteQueryV1(r as Extract<typeof r,{kind:'local'}>,tables,service.id));byService.set(service.id,deriveCommerceSqliteServiceV1(service.id,prefix,tables,queries,values.contract.values,values.contract.limits));}
 const codecs=generateCommerceValueCodecBundle(stage,source,domain,baseline),runtime=readCorePhysicalFile(fileURLToPath(new URL(template,import.meta.url))).text;
 let disposed=false;const services=new WeakMap<object,Service>(),bundles=new WeakMap<object,Bundle>(),queries=new WeakMap<object,{service:Service;read:CommerceLocalReadHandleV1;data:CommerceSqliteQueryV1}>();
 const current=()=>{if(disposed)fail('DisposedOwner',where,'SQLite family disposed');pin.assertCurrent();plans.assertCurrent();families.assertCurrent(family);};
 const service=(h:CommerceServiceSchemaHandleV1)=>{current();const s=h&&typeof h==='object'?services.get(h):undefined;if(!s)fail('ForeignOwner',where,'original service schema required');if(s.disposed)fail('DisposedOwner',where,'service schema disposed');return s;};
 const bundle=(h:CommerceRepositoryBundleHandleV1)=>{current();const s=h&&typeof h==='object'?bundles.get(h):undefined;if(!s)fail('ForeignOwner',where,'original materialized repository bundle required');if(s.service.disposed)fail('DisposedOwner',where,'parent service schema disposed');s.physical.assertCurrent();return s;};
 const emitted=(s:Service):CommerceSqliteBundleV1=>{
  const model=JSON.stringify(s.data),modelLine='declare const commerceRepositoryModel:any;',codecLine='declare const repositoryCodecs:any;';if(!runtime.includes(modelLine)||!runtime.includes(codecLine))fail('InvalidContract',where,'fixed repository emitter declarations changed');
  const text=runtime.replace(modelLine,'const commerceRepositoryModel:any=JSON.parse('+JSON.stringify(model)+');').replace(codecLine,"import {createCommerceValueCodecs} from './values-and-codecs.js';\nconst repositoryCodecs=createCommerceValueCodecs();");
  const files=coreFreeze([...codecs.files,{path:'service-repositories.ts',text},{path:'001-service-schema.sql',text:s.data.migration_sql},{path:'service-persistence.json',text:JSON.stringify(s.data.persistence,null,2)+'\n'}]);
  return coreFreeze({files,manifest:{kind:'actual-generated-service-sqlite-schema-repository/v1-candidate',service:s.data.service,source_capture_sha256:captured.capture_sha256,family_sha256:selected.family_sha256,technical_graph_sha256:selected.graph_sha256,schema_sha256:s.data.schema_sha256,code_epoch_sha256:pin.sha256,codec_manifest:codecs.manifest,members:files.map(f=>({path:f.path,sha256:sha(f.text),bytes:Buffer.byteLength(f.text)})),qualification:'actual-generated-schema-repository-data-only;no-native-store-or-application-custody',authority_effect:'none'}});
 };
 const owner:CommerceSqliteFamilyOwnerV1=Object.freeze({
  bindService(id:string){current();const data=byService.get(id);if(!data)fail('UnknownReference',where,'declared source service required');const h=Object.freeze({kind:'original-commerce-service-sqlite-schema/v1-candidate' as const});services.set(h,{data,disposed:false});return h;},inspectService(h:CommerceServiceSchemaHandleV1){return service(h).data;},
  bindQuery(h:CommerceServiceSchemaHandleV1,read:CommerceLocalReadHandleV1){const s=service(h),r=plans.inspectRead(read);if(r.source_capture_sha256!==captured.capture_sha256||r.plan.service!==s.data.service)fail('ForeignOwner',where,'original Query must belong to the same source/service');const q=s.data.queries.find(q=>q.id===r.query);if(!q||dataDigest(q.plan)!==dataDigest(r.plan))fail('InvalidContract',where,'exact original Query mapping required');const out=Object.freeze({kind:'original-commerce-scoped-query-mapping/v1-candidate' as const});queries.set(out,{service:s,read,data:q});return out;},
  inspectQuery(h:CommerceSqliteQueryHandleV1){current();const q=h&&typeof h==='object'?queries.get(h):undefined;if(!q)fail('ForeignOwner',where,'original scoped Query mapping required');if(q.service.disposed)fail('DisposedOwner',where,'service disposed');plans.assertReadCurrent(q.read);return q.data;},
  emit(h:CommerceServiceSchemaHandleV1){const result=emitted(service(h));current();return result;},
  materialize(h:CommerceServiceSchemaHandleV1,directory:string){const s=service(h);if(typeof directory!=='string'||!path.isAbsolute(directory)||path.normalize(directory)!==directory)fail('InvalidContract',where,'fresh normalized absolute output directory required');mkdirSync(directory,{mode:0o700});const generated=emitted(s),files:CorePhysicalFile[]=[];
   for(const f of generated.files){files.push(writeCoreExclusiveFile(path.join(directory,f.path),f.text));if(f.path.endsWith('.ts'))files.push(writeCoreExclusiveFile(path.join(directory,f.path.replace(/\.ts$/,'.js')),stripTypeScriptTypes(f.text)));}
   files.push(writeCoreExclusiveFile(path.join(directory,'repository-manifest.json'),JSON.stringify(generated.manifest,null,2)+'\n'));const physical=pinCorePhysicalCaptures(files);current();const out=Object.freeze({kind:'original-generated-commerce-service-repository/v1-candidate' as const});bundles.set(out,{service:s,directory,files,physical,data:null});bundle(out);return out;
  },
  adoptExisting(h:CommerceServiceSchemaHandleV1,directory:string){const s=service(h);
   const generated=emitted(s),adopted=adoptCommerceGeneratedRepositoryV1(directory,generated);
   current();const out=Object.freeze({kind:'original-generated-commerce-service-repository/v1-candidate' as const});
   bundles.set(out,{service:s,directory,files:adopted.files,physical:adopted.physical,data:null});bundle(out);return out;
  },
  inspectBundle(h:CommerceRepositoryBundleHandleV1){const s=bundle(h);return coreFreeze({service:s.service.data.service,source_capture_sha256:captured.capture_sha256,family_sha256:selected.family_sha256,schema_sha256:s.service.data.schema_sha256,directory:s.directory,members:s.files.map(f=>f.file),qualification:'actual-generated-repository-data-only;not-native-database-or-row-custody',authority_effect:'none' as const});},
  async loadDataComponent(h:CommerceRepositoryBundleHandleV1){const s=bundle(h);if(!s.data){const loaded=await import(pathToFileURL(path.join(s.directory,'service-repositories.js')).href);bundle(h);if(!loaded.commerceRepositoryData||loaded.commerceRepositoryData.qualification!=='generated-repository-data-only;not-store-query-row-or-authorization-custody')fail('InvalidContract',where,'actual fixed generated data component required');s.data=loaded.commerceRepositoryData;}bundle(h);return s.data!;},
  assertServiceCurrent(h:CommerceServiceSchemaHandleV1){service(h);},assertBundleCurrent(h:CommerceRepositoryBundleHandleV1){bundle(h);},disposeService(h:CommerceServiceSchemaHandleV1){service(h).disposed=true;},assertCurrent:current,dispose(){disposed=true;},
 });owners.add(owner);current();return owner;
}
