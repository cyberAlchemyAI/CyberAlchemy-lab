import {verifyRecordReviews} from '../../../lab-workflows/records-workflow/record-review.mjs';
import {resolveHost} from '../../../lab-workflows/records-workflow/host.mjs';
import { readFileSync, writeFileSync } from 'node:fs';
import { isDeepStrictEqual } from 'node:util';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { issue, execute } from './service.mjs';
import { transition, publish, projected, initializeJoin } from './runtime.mjs';
import { Snapshots } from './snapshots.mjs';
import { Journal } from './journal.mjs';
import { nativePort, impactClosure, independentAssessment } from './ports.mjs';
import { signPacket, authenticatePacket } from './security.mjs';
import { digest } from './verified-projection.mjs';
import { validateSchema } from './schema.mjs';
import { readPublishedCatalog } from './catalog.mjs';
import {loadTrust,verifyImplementation} from './implementation.mjs';
import {deriveCarryForward,verifyCurrentDefinitionReviews} from './carry-forward.mjs';
import {verifyOperationalReadiness} from './readiness.mjs';
import {restoreRecovery} from './recovery.mjs';
import {enforceManagedContext} from './managed-context.mjs';
import { activation } from './activation.mjs';

function options(args) {
  const values = {};
  for (let index = 0; index < args.length; index += 2) {
    const name = args[index];
    if (!name.startsWith('--') || index + 1 === args.length || Object.hasOwn(values, name.slice(2))) {
      throw Error('expected-unique-option-and-value');
    }
    values[name.slice(2)] = args[index + 1];
  }
  return values;
}
const load = filename => JSON.parse(readFileSync(filename));
const requiredDestination=value=>{if(!value)throw Error('recovery-destination-required');return path.resolve(value);};

export async function main(args = process.argv.slice(2)) {
  const [command, ...rest] = args;
  if (!command || command === 'help' || command === '--help') {
    return { commands: ['status','activate','restore','carry-forward','attest','observe-native','issue','evaluate','join-init','join-transition','join-inspect','stage','publish',
      'inspect-publication','catalog','read','context','create','native-review','native-apply','native-recover','impact','assess'],
      input: '--file REQUEST.json', trust: '--trust LOCAL-TRUST.json', persistence: '--db DATABASE',
      issuance: '--issuer PRINCIPAL --key PRIVATE-KEY.pem', output: '--out FILE' };
  }
  const flags = options(rest);
  const active = activation();
  if (!flags.db && active) flags.db = command.startsWith('join-') ? active.journal : active.database;
  if (!flags.trust && active) flags.trust = active.trust;
  const request = flags.file ? load(flags.file) : ['catalog','status','activate'].includes(command) && active ? {workspace:active.workspace} : (()=>{throw Error('request-file-required');})();
  const trust = flags.trust ? loadTrust(flags.trust) : null;
  if(active && !request.store && ['create','native-review','native-apply','native-recover'].includes(command)) request.store=active.native_store;
  if(active && command==='publish' && !request.native_store) request.native_store=active.native_store;
  if(trust)verifyImplementation(trust.implementation);
  enforceManagedContext(command,flags,request,active,trust);
  let result;
  const mutation=['join-init','join-transition','stage','publish','native-apply','native-recover'];
  if(active&&mutation.includes(command)){
    const activeTarget=(flags.db===active.database||flags.db===active.journal)
      && (!request.store||request.store===active.native_store);
    if(activeTarget)verifyImplementation(trust.implementation);
  }
  if(command==='restore'){
    if(!active?.recovery)throw Error('qualified-recovery-archive-required');
    const raw=readFileSync(path.resolve(active.root,active.recovery.path));
    result=await restoreRecovery(raw,active.recovery,requiredDestination(request.destination),active,trust);
  }else if(command==='activate'){
    result=await verifyOperationalReadiness(active,trust);
  }else if (command === 'carry-forward') {
    result=await deriveCarryForward(request,trust,flags.db);
  } else if (command === 'status') {
    if (!active) throw Error('shared-workflow-not-activated');
    const readiness=await verifyOperationalReadiness(active,trust);
    const catalog=readPublishedCatalog(flags.db,request.workspace);
    const native=nativePort({action:'summary',store:active.native_store,require_current:true});
    result={status:'active',readiness,native:{freshness:native.freshness.status,source_cut:native.baseline.snapshot_digest,head:native.head},workspace:request.workspace,selector:catalog.selected,
      versions:catalog.entries.length,current:Object.keys(catalog.current_lookup).length,
      registry_contract:'cal.artifact-type.definition-registry/v2',
      activation_decision:active.decision_ref,shared_runtime_copies:0};
  } else if (command === 'attest' || command === 'observe-native') {
    let artifact;
    let predicate = request.predicate;
    if (command === 'observe-native') {
      const observed = nativePort({action:'committed',store:request.store,operation:request.original_operation});
      if (observed.source_cut !== request.cut) throw Error('native-observation-cut-mismatch');
      artifact = Buffer.from(JSON.stringify(observed));
      predicate = 'native-effect';
    } else {
      artifact = readFileSync(request.artifact);
    }
    const schema = trust.schemas[request.schema];
    if (!schema) throw Error('attestation-schema-unqualified');
    const rawSchema = readFileSync(schema.path);
    if (digest(rawSchema) !== schema.sha256) throw Error('attestation-schema-drift');
    validateSchema(JSON.parse(rawSchema),artifact);
    const statement = Buffer.from(JSON.stringify({
      version:1,predicate,operation:request.operation,scope:request.scope,cut:request.cut,
      artifact:{sha256:digest(artifact),bytes:artifact.length}
    }));
    const receipt = signPacket(statement,flags.issuer,readFileSync(flags.key));
    authenticatePacket(receipt,trust);
    result = {artifact:artifact.toString('base64'),receipt};
  } else if (command === 'issue') {
    result = await issue(request, trust, flags.issuer, readFileSync(flags.key));
  } else if (command === 'evaluate') {
    result = await execute(request, trust);
  } else if (command === 'join-init') {
    if (request.operation !== 'InitializeJoin') throw Error('join-initialization-operation-required');
    const { input } = await projected(request, trust);
    result = await initializeJoin(input.value, flags.db,trust);
  } else if (command === 'join-transition') {
    result = await transition(request, trust, flags.db);
  } else if (command === 'publish') {
    result = await publish(request, trust, flags.db);
  } else if (command === 'catalog') {
    const catalog = readPublishedCatalog(flags.db,request.workspace,'lab.catalog-reader',trust);
    result = {selector:catalog.selected,entries:catalog.entries,current_lookup:catalog.current_lookup};
  } else if (command === 'join-inspect') {
    const journal = new Journal(flags.db,{readOnly:true,trust});
    try { result = await journal.verifyHistory(request.workspace, request.run); } finally { journal.close(); }
  } else if (['stage','inspect-publication','read'].includes(command)) {
    const snapshots = new Snapshots(flags.db,{readOnly:command!=='stage',trust});
    try {
      if (command === 'stage') result = snapshots.stage(request.workspace, request.operation, request.cut, request.files);
      if (command === 'inspect-publication') result = snapshots.inspectPublication(request.workspace, request.operation);
      if (command === 'read') {
        const current = snapshots.current(request.workspace);
        if (!current) throw Error('workspace-has-no-published-snapshot');
        const material = snapshots.material(current.digest, request.name);
        result = { selector: current, binding: material.binding, body: material.bytes.toString('base64') };
      }
    } finally { snapshots.close(); }
  } else if (['context','create','native-review','native-apply','native-recover'].includes(command)) {
    if (command === 'native-apply') {
      if (!request.construction || !['AssessConstructionEntry','AssessCarriedConstructionEntry'].includes(request.construction.operation)) throw Error('native-construction-entry-required');
      if (!request.workspace || !request.catalog) throw Error('native-workspace-context-required');
      const context = await resolveHost({workspace:request.workspace,catalog:request.catalog,
        project:Object.hasOwn(request,'semantic_project')?request.semantic_project:request.project,store:request.store,goal:request.goal,work:request.work,
        workspace_revision:request.workspace_revision});
      const contextScope = trust.workspaces?.[context.workspace_ref]?.scope ?? context.workspace_ref;
      if (request.construction.scope !== contextScope) throw Error('native-workspace-scope-mismatch');
      const checkedInput = await projected(request.construction, trust);
      const value = checkedInput.input.value;
      if (!request.approval_artifact) throw Error('native-original-approval-required');
      const approvalBytes = Buffer.from(request.approval_artifact,'base64');
      if (!isDeepStrictEqual(JSON.parse(approvalBytes),request.approval)) throw Error('native-approval-artifact-mismatch');
      const approval = {digest:digest(approvalBytes)};
      const carried=request.construction.operation==='AssessCarriedConstructionEntry';
      if(carried){
        if(!request.carry_forward)throw Error('carry-forward-originals-required');
        const derived=await deriveCarryForward({...request.carry_forward,proposal:request.proposal,approval_artifact:request.approval_artifact},trust,flags.db);
        if(!isDeepStrictEqual(derived,value))throw Error('carry-forward-projection-mismatch');
      }
      if(!carried){
       verifyCurrentDefinitionReviews(value,request,trust,flags.db);
       if(request.proposal.targets.some(t=>t.category==='artifact-instance'))verifyRecordReviews(request,value,trust,nativePort({action:'record-projection',store:request.store,require_current:true}));
      }
      if (!(carried?value.original.effects_requested:value.effects_requested)
          || (carried?value.current_cut:value.source_cut)!==request.proposal.source_snapshot_digest
          || (carried?value.current_permission:value.permission)?.sha256!==approval.digest)
        throw Error('native-construction-effect-binding-mismatch');
      const construction = await execute(request.construction, trust);
      if (construction.result !== 'GenerationEntryPlanReady') throw Error('native-construction-not-ready');
    }
    result = command==='context'&&request.store ? await resolveHost(request) : nativePort({ ...request, action: {
      context:'context', create:'create', 'native-review':'review', 'native-apply':'apply', 'native-recover':'recover'
    }[command] });
  } else if (command === 'impact') {
    verifyImplementation(trust.implementation);
    const universe=trust.consumer_universe;
    if(!universe)throw Error('consumer-universe-unqualified');
    const rawUniverse=readFileSync(universe.path);
    if(digest(rawUniverse)!==universe.sha256)throw Error('consumer-universe-drift');
    const manifest=JSON.parse(rawUniverse);
    if(!manifest.scope)throw Error('consumer-universe-scope-required');
    const snapshots=new Snapshots(flags.db,{readOnly:true,trust});
    try{
      const selected=snapshots.current(manifest.scope);
      if(!selected||manifest.cursor!=='snapshot:'+selected.revision+':'+selected.digest
        ||(manifest.registry_cut??manifest.source_cut)!==snapshots.material(selected.digest,'registry.json').manifest.cut)throw Error('consumer-universe-stale');
    }finally{snapshots.close();}
    if(request.manifest&&!isDeepStrictEqual(request.manifest,manifest))throw Error('consumer-universe-mismatch');
    result = impactClosure(manifest, request.root, binding => {
      const qualified = trust.materials?.[binding.ref];
      if (!qualified || qualified.sha256 !== binding.sha256) throw Error('impact-material-unqualified');
      return readFileSync(qualified.path);
    });
  } else if (command === 'assess') {
    verifyImplementation(trust.implementation);
    result = independentAssessment(request.specifications, request.output, trust.executors,trust.materials);
  } else throw Error('unknown-shared-command');
  if (flags.out) writeFileSync(flags.out, JSON.stringify(result, null, 2) + '\n', { flag: 'wx' });
  return result;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { console.log(JSON.stringify(await main())); }
  catch (error) { console.error(JSON.stringify({ outcome:'Refused', reason:error.message })); process.exitCode = 2; }
}
