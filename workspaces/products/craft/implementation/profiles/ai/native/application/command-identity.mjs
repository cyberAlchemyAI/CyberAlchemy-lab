/** Client-side durable identity allocation; original command/effect owners still
 * own execution/replay. No business payload or tokens are stored here.
 * Open Questions: ../credentials/README.md. */
import {DatabaseSync} from 'node:sqlite';
import {randomUUID} from 'node:crypto';
import {openSync,closeSync,lstatSync} from 'node:fs';
import {assert,canonical,closed,freeze,sha256,text} from '../shared.mjs';

export function childEffectIdentity({parentCommand,callSite,occurrence,provider,account,operation,resource}){
 for(const v of [parentCommand,callSite,occurrence,provider,account,operation,resource])text(v,'stable child effect identity',512);
 return 'child-effect-'+sha256(canonical({parentCommand,callSite,occurrence,provider,account,operation,resource}));
}
export function applicationEffectIdentity({application,selection,source,logicalIdentity,work}){
 const logical=selection.logicalIdentity!==undefined;
 if(selection.identityMode==='stable-command')assert(logical&&logicalIdentity&&typeof logicalIdentity.parentCommand==='string'&&typeof logicalIdentity.callSite==='string'&&typeof logicalIdentity.occurrence==='string','InvalidContract','stable-command identity requires authored parent/call-site/persisted-occurrence projection');
 assert(selection.identityMode===undefined||selection.identityMode==='stable-command','UnsupportedCapability','selected effect identity mode');
 if(logical){const values=Object.values(logicalIdentity??{});assert(values.length>0&&values.length<=16&&Buffer.byteLength(canonical(logicalIdentity))<=4096,'ResourceLimit','bounded owned logical business identity');for(const value of values)text(value,'logical business identity',512);}
 return 'application-effect-'+sha256(canonical({application,...(logical?{tenant:source.principal.tenant,provider:selection.provider,account:selection.account,operation:selection.operation,logicalIdentity}:{sourceId:source.sources.facts.id,objectVersion:source.facts.objectVersion}),resource:selection.resourceId,action:selection.action,recipient:source.target.recipient,...(selection.readCurrent?{read:{run:work.run,ordinal:work.ordinal,...(selection.identityMode==='stable-command'?{}:{attempt:work.attempt})}}:{})}));
}
export function createCommandIdentityStore({path,assertCurrent,now=Date.now,idFactory=randomUUID,maxCommands=100000}){
 text(path,'durable identity path',4096);assert(path!==':memory:'&&typeof assertCurrent==='function'&&typeof idFactory==='function'&&Number.isSafeInteger(maxCommands)&&maxCommands>=1,'InvalidContract','durable authorized identity owner');
 try{const fd=openSync(path,'wx',0o600);closeSync(fd);}catch(e){if(e.code!=='EEXIST')throw e;}const stat=lstatSync(path);assert(stat.isFile()&&!stat.isSymbolicLink()&&(stat.mode&0o077)===0,'IdentityStorePermissions','private identity database');
 const db=new DatabaseSync(path);db.exec("PRAGMA busy_timeout=5000; PRAGMA journal_mode=DELETE; PRAGMA synchronous=FULL; CREATE TABLE IF NOT EXISTS client_commands(id TEXT PRIMARY KEY,client_key TEXT NOT NULL UNIQUE,fingerprint TEXT NOT NULL,identity TEXT NOT NULL,state TEXT NOT NULL,expires INTEGER NOT NULL) STRICT;");let stopped=false;
 const current=(purpose,scope)=>assert(!stopped&&assertCurrent({purpose,scope})===true,'PermissionDenied','current client identity access');
 const tx=fn=>{db.exec('BEGIN IMMEDIATE');try{const out=fn();db.exec('COMMIT');return out;}catch(e){if(db.isTransaction)db.exec('ROLLBACK');throw e;}};
 const scopeValue=value=>{const s=closed(value,['application','subject','entry','tenant']);for(const k of ['application','subject','entry'])text(s[k]);assert(s.tenant===null||typeof s.tenant==='string'&&s.tenant.length>0,'InvalidContract','selected tenant scope');return s;};
 const keyOf=(scope,logicalCommand)=>{text(logicalCommand,'logical command',512);return sha256(canonical({scope:scopeValue(scope),logicalCommand}));};
 return Object.freeze({
  prepare({scope,logicalCommand,payload,entities=[],children=[],retentionMs=86400000}){current('allocate',scopeValue(scope));assert(Array.isArray(entities)&&entities.length<=64&&new Set(entities).size===entities.length,'InvalidContract','distinct bounded entity slots');for(const e of entities)text(e,'entity slot',128);assert(Array.isArray(children)&&children.length<=1024,'ResourceLimit','bounded child effect occurrences');const occurrences=children.map(value=>{const c=closed(value,['callSite','occurrence']);text(c.callSite);text(c.occurrence);return c;});assert(new Set(occurrences.map(c=>canonical(c))).size===occurrences.length,'InvalidContract','child occurrences must be disambiguated');assert(Number.isSafeInteger(retentionMs)&&retentionMs>=1&&retentionMs<=31536000000,'InvalidContract','bounded retention window');const id=keyOf(scope,logicalCommand),fingerprint=sha256(canonical({payload,entities:[...entities].sort(),children:occurrences.map(c=>canonical(c)).sort(),retentionMs}));
   return tx(()=>{current('allocate',scopeValue(scope));const prior=db.prepare('SELECT * FROM client_commands WHERE id=?').get(id);if(prior){assert(prior.fingerprint===fingerprint,'CommandPayloadConflict','original command input/allocation contract required');assert(prior.expires>now(),'CommandIdentityExpired','expired command must be inspected through original owner; never allocate replacement');return freeze(JSON.parse(prior.identity));}assert(db.prepare('SELECT COUNT(*) AS n FROM client_commands').get().n<maxCommands,'CommandCapacity','retained command capacity');const client_key=idFactory();text(client_key,'client key',128);const allocated=Object.create(null);for(const name of entities){const value=idFactory();text(value,'allocated entity ID',128);allocated[name]=value;}const identity={client_key,header:Buffer.from(client_key,'utf8').toString('base64url'),entities:allocated,children:occurrences.map(c=>({...c,occurrenceId:sha256(canonical({client_key,...c}))}))};db.prepare("INSERT INTO client_commands VALUES(?,?,?,?,'prepared',?)").run(id,client_key,fingerprint,canonical(identity),now()+retentionMs);return freeze(JSON.parse(canonical(identity)));});
  },
  observe({scope,logicalCommand,state}){current('observe',scopeValue(scope));assert(['unknown','completed'].includes(state),'InvalidContract','explicit client observation');return tx(()=>{current('observe',scopeValue(scope));const id=keyOf(scope,logicalCommand),row=db.prepare('SELECT * FROM client_commands WHERE id=?').get(id);assert(row,'CommandIdentityMissing','original allocated command required');assert(row.state!=='completed'||state==='completed','InvalidContract','completed command cannot become unknown');db.prepare('UPDATE client_commands SET state=? WHERE id=?').run(state,id);return freeze({state,identity:JSON.parse(row.identity),expired:row.expires<=now()});});},
  inspect({scope,logicalCommand}){current('inspect',scopeValue(scope));const row=db.prepare('SELECT * FROM client_commands WHERE id=?').get(keyOf(scope,logicalCommand));return row?freeze({state:row.state,identity:JSON.parse(row.identity),expired:row.expires<=now()}):null;},
  close(){if(!stopped){stopped=true;db.close();}}
 });
}
