import {readFileSync,existsSync} from 'node:fs';
import {isDeepStrictEqual} from 'node:util';
import {loadTrust,verifyImplementation,repository} from './implementation.mjs';
import {Snapshots} from './snapshots.mjs';
import {Journal} from './journal.mjs';
import {nativePort} from './ports.mjs';
import {digest} from './verified-projection.mjs';
import {evaluate} from './kernel.mjs';
export async function verifyOperationalReadiness(active,providedTrust){
 if(!active)throw Error('shared-workflow-not-selected');
 const trust=providedTrust??loadTrust(active.trust,active.root??repository);
 verifyImplementation(trust.implementation);
 for(const name of ['database','journal','native_store'])if(!existsSync(active[name]))throw Error('shared-resource-missing:'+name);
 const snapshots=new Snapshots(active.database,{readOnly:true,trust});
 try{
  const selected=snapshots.current(active.workspace);
  if(!selected||!isDeepStrictEqual({...selected},active.selector))throw Error('shared-selector-not-reconciled');
  const publication=snapshots.inspectPublication(active.workspace,snapshots.material(selected.digest,'source.json').manifest.operation);
  if(!publication||!isDeepStrictEqual(publication.selected,{...selected}))throw Error('shared-publication-not-verified');
  const native=nativePort({action:'summary',store:active.native_store,require_current:true});
  const journal=new Journal(active.journal,{readOnly:true,trust});
  try{
   for(const row of journal.db.prepare('SELECT workspace,run FROM runs').all())await journal.verifyHistory(row.workspace,row.run);
  }finally{journal.close();}
  for(const group of ['materials','executors']){
   const values=Object.values(trust[group]??{});
   if(values.length===0)throw Error('shared-qualification-missing:'+group);
   for(const selected of values)if(digest(readFileSync(selected.path))!==selected.sha256)throw Error('shared-qualification-drift:'+group);
  }
  if(!trust.consumer_universe||digest(readFileSync(trust.consumer_universe.path))!==trust.consumer_universe.sha256)throw Error('consumer-universe-unqualified');
  const universe=JSON.parse(readFileSync(trust.consumer_universe.path));
  if(universe.scope!==active.workspace||universe.cursor!=='snapshot:'+selected.revision+':'+selected.digest
    ||universe.source_cut!==native.baseline.snapshot_digest)throw Error('consumer-universe-stale');
  await evaluate('EnforceRuntimeReadiness',{value:{selected:true,implementation_current:true,snapshot_verified:true,native_verified:true,journal_verified:true,qualifications_verified:true,source_current:native.freshness.status==='current'}});
  return {status:'ready',implementation:trust.implementation.digest,selector:{...selected},native_source_cut:native.baseline.snapshot_digest,native_head:native.head};
 }finally{snapshots.close();}
}
