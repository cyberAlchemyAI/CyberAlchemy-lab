import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {digest} from './canonical.mjs';
export function inspectRuntime(options = {}) {
  const root = options.root ?? resolve(import.meta.dirname, '../../../..');
  const manifest = JSON.parse(readFileSync(options.manifestPath ?? resolve(import.meta.dirname, '../runtime-manifest.json')));
  if(manifest.unresolved_relative_imports?.length || manifest.external_module_imports?.length) throw new Error('define.runtime-unresolved-dependencies');
  if(digest(manifest.files)!==manifest.inventory_sha256)throw new Error('define.runtime-manifest-inventory-mismatch');
  const failures=[];
  for(const row of manifest.files) {
    try {if(digest(readFileSync(resolve(root,row.path)))!==row.sha256)failures.push(row.path);}
    catch {failures.push(row.path);}
  }
  if(failures.length)throw new Error(`define.runtime-source-drift:${failures.join(',')}`);
  return {status:'PASS',checked_files:manifest.files.length,source_inventory_sha256:manifest.inventory_sha256,authority_effect:'none'};
}
