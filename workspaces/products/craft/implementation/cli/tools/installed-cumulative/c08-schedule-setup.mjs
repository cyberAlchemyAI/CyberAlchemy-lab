/** Coordinate only the original command-journal probe before the intended two-read race.
 * Actual SQL, business reads, permissions, revision checks and all oracles stay unchanged.
 * Open Questions: README.md#open-questions. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
function replaceOnce(text,before,after){assert.equal(text.split(before).length,2,'exact original scheduling setup');return text.replace(before,after);}
export function coordinateC08InitialJournal(tests){
 const parent=path.join(tests,'C08.test.mjs'),worker=path.join(tests,'schedule-worker.mjs');
 let s=readFileSync(parent,'utf8');
 s=replaceOnce(s,'Int32Array.BYTES_PER_ELEMENT*7','Int32Array.BYTES_PER_ELEMENT*8');
 assert.equal(s.split('[2,3,5,6]').length,4,'all parent failure/cleanup barriers');
 s=s.replaceAll('[2,3,5,6]','[2,3,5,6,7]');writeFileSync(parent,s);
 s=readFileSync(worker,'utf8');
 s=replaceOnce(s,'const norm=sql=>',"let initialJournalStarted=false,initialJournalDone=false;const storeConnections=new WeakMap();\nfunction isStore(db){if(!storeConnections.has(db)){const rows=originalPrepare.call(db,'PRAGMA database_list').all();storeConnections.set(db,rows.some(row=>row.name==='main'&&path.resolve(row.file)===path.resolve(d.storePath)));}return storeConnections.get(db);}\nconst norm=sql=>");
 s=replaceOnce(s,'function beforeSql(db,sql){',"function beforeSql(db,sql){if(armed&&hits===0&&!initialJournalStarted&&norm(sql)==='BEGIN IMMEDIATE'&&isStore(db)){if(d.index===1)wait(7);initialJournalStarted=true;observations.push('initial-journal-probe-started');}");
 s=replaceOnce(s,'function afterSql(db,sql){',"function afterSql(db,sql){\n if(armed&&initialJournalStarted&&!initialJournalDone&&hits===0&&isStore(db)&&['COMMIT','ROLLBACK'].includes(norm(sql))){initialJournalDone=true;observations.push('initial-journal-probe-completed');if(d.index===0){Atomics.store(state,7,1);Atomics.notify(state,7);}}\n");
 s=replaceOnce(s,'for(const i of[2,3,5,6])','for(const i of[2,3,5,6,7])');
 writeFileSync(worker,s);
}
