import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
// Exact workspace reference kit, not an installed protected distribution.
// Open Questions: OPERATOR.md.
export const here=dirname(fileURLToPath(import.meta.url));
export const base=resolve(here,'../..');
export const root=resolve(base,'../../../../../../..');
export const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
export function verifyFiles(workspace,manifest){
 if(manifest?.schema_version!=='alch.inference-reference-product/v1-candidate'||!manifest.files||typeof manifest.files!=='object'||Array.isArray(manifest.files)||!Object.keys(manifest.files).length)throw Error('INVALID_PRODUCT_MANIFEST');
 for(const [path,hash]of Object.entries(manifest.files)){
  if(typeof hash!=='string'||!/^[a-f0-9]{64}$/.test(hash))throw Error('INVALID_PRODUCT_HASH');
  if(sha(readFileSync(resolve(workspace,path)))!==hash)throw Error('PRODUCT_SOURCE_DRIFT: '+path);
 }
 return Object.keys(manifest.files).length;
}
export function verifyProduct(){
 const bytes=readFileSync(resolve(here,'manifest.json')),manifest=JSON.parse(bytes);
 return {files:verifyFiles(root,manifest),manifest_sha256:sha(bytes),manifest};
}
