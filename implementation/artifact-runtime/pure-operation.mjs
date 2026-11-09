/** Generic exact-artifact adapter. No domain rules or domain record composition. */
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import path from 'node:path';
const hash=raw=>createHash('sha256').update(raw).digest('hex');
const loaded=new Map();
export async function evaluateArtifact(directory,member,input,options={}){
 const manifestRaw=readFileSync(path.join(directory,'manifest.json'));
 if(options.manifest_sha256&&hash(manifestRaw)!==options.manifest_sha256)throw Error('executable-manifest-drift');
 const manifest=JSON.parse(manifestRaw);
 const entry=manifest.files.find(row=>row.path===member);
 if(!entry||path.basename(member)!==member||!member.endsWith('.mjs'))throw Error('unselected-executable-member');
 const raw=readFileSync(path.join(directory,member));
 if(raw.length!==entry.bytes||hash(raw)!==entry.sha256)throw Error('executable-member-drift');
 // Import the verified bytes, avoiding a second path read between verification and evaluation.
 let executable=loaded.get(entry.sha256);
 if(!executable){executable=await import('data:text/javascript;base64,'+raw.toString('base64'));loaded.set(entry.sha256,executable);}
 return executable.evaluate(new TextEncoder().encode(JSON.stringify(input)));
}
