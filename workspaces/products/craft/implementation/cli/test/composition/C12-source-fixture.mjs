import {cpSync, mkdtempSync, mkdirSync, readFileSync, writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {GENERIC_EVENT_CAPABILITIES} from '../../src/generic/composition-capabilities.ts';

const repo=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const authoring=path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C12/event-handoff-contract-003/authoring');
const support=fileURLToPath(new URL('fixtures/C12/',import.meta.url));

/** Expand the frozen C12 business input into one physical source closure. */
export function buildEventSourceFixture(kind='request') {
 if(kind!=='request'&&kind!=='permit')throw new Error('request or permit required');
 const producer=kind==='request'?'RequestService':'PermitService',receiver=kind==='request'?'AuditService':'LedgerService';
 const names=[kind+'-service.alch',(kind==='request'?'audit':'ledger')+'-service.alch'];
 const root=path.join(mkdtempSync(path.join(tmpdir(),'craft-c12-event-source-')),'model');
 mkdirSync(root);
 for(const name of names)cpSync(path.join(authoring,name),path.join(root,name));
 cpSync(path.join(support,'contracts'),path.join(root,'contracts'),{recursive:true});
 cpSync(path.join(support,'generated'),path.join(root,'generated'),{recursive:true});
 writeFileSync(path.join(root,'application.alch'),`module CraftGenerated.Root version 1\ninterface Application:\n  kind application-composition\n  source ${names[0]}\n  source ${names[1]}\n  source generated/auth-context.alch\n  service ${producer} module ${producer}\n  service ${receiver} module ${receiver}\n  computation-bounds contracts/bounds.json\n  parameters contracts/selected-profile.json\n`);
 const limits=JSON.parse(readFileSync(path.join(root,'contracts/bounds.json'),'utf8')).computation.limits;
 const transaction_bounds=JSON.parse(readFileSync(path.join(root,'contracts/transactions.json'),'utf8'));
 const profile={schema_version:'craft.generic-event-profile/v1-candidate',id:'node-sqlite-event-candidate',target:'node-esm',capabilities:[...GENERIC_EVENT_CAPABILITIES],limits,services:[{id:producer,module:producer},{id:receiver,module:receiver}],entry_context:'customer-ready-scalars/v1-candidate',auth_abi:'craft.commerce-auth-ready-bridge/v1-candidate',auth_route_template:'commerce:{logical_entry_id}',storage:'sqlite-fenced-event-handoff/v1-candidate',application_namespace:'Craft.Event.Fixture',transaction_bounds,string_policy:{max_utf8_bytes:256,max_scalars:256},event_handoff:{transport:'process-local-checked-envelope/v1-candidate',delivery:'durable-at-least-once/v1-candidate'}};
 writeFileSync(path.join(root,'contracts/selected-profile.json'),JSON.stringify(profile,null,2)+'\n');
 return root;
}
