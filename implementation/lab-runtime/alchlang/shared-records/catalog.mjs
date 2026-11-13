import {currentLocation} from './locations.mjs';
import { readFileSync, realpathSync } from 'node:fs';
import path from 'node:path';
import {activation} from './activation.mjs';
import {loadTrust} from './implementation.mjs';
import {isDeepStrictEqual} from 'node:util';
import { Snapshots } from './snapshots.mjs';
import { validateSchema } from './schema.mjs';

export function readPublishedCatalog(database, workspace, reader = 'lab.catalog-reader', providedTrust = null) {
  let trust=providedTrust;
  if(!trust){
    const active=activation({required:true});
    if(realpathSync(database)!==realpathSync(active.database)||workspace!==active.workspace)throw Error('catalog-external-trust-required');
    trust=loadTrust(active.trust,active.root);
  }
  const snapshots = new Snapshots(database,{readOnly:true,trust});
  try {
    const selected = snapshots.current(workspace);
    if (!selected) throw Error('published-workspace-not-found');
    const sourceMaterial=snapshots.material(selected.digest,'source.json');
    const publication=snapshots.inspectPublication(workspace,sourceMaterial.manifest.operation);
    if(!publication||!isDeepStrictEqual(publication.selected,{...selected}))throw Error('catalog-publication-not-selected');
    const source = JSON.parse(sourceMaterial.bytes);
    if (source.reader_protocol !== 'snapshot-selector/v1' || !source.readers.includes(reader)) throw Error('snapshot-reader-unqualified');
    const registry = snapshots.material(selected.digest, 'registry.json');
    validateSchema(JSON.parse(readFileSync(path.join(import.meta.dirname,'contracts/definition-registry-v2.schema.json'))), registry.bytes);
    const document = JSON.parse(registry.bytes);
    const entries = document.entries.map(entry => {
      const location=currentLocation(entry,source,b=>snapshots.material(selected.digest,b.ref??b.path).bytes);
      const body = snapshots.material(selected.digest, entry.body.path);
      if (body.binding.sha256 !== entry.body.sha256 || Number(body.binding.bytes) !== entry.body.bytes) {
        throw Error('published-definition-binding-mismatch');
      }
      const value = JSON.parse(body.bytes);
      if (value.definition_id !== entry.definition_id || value.version !== entry.version) throw Error('published-definition-identity-mismatch');
      return {
        definition_id: entry.definition_id, version: entry.version, term: value.term,
        path: 'lab-snapshot:' + selected.digest + '/' + (location?.expected??entry.body.path),
        canonical_path:location?.expected??entry.body.path,original_binding:entry.body,
        sha256: body.binding.sha256, carrier: entry.carrier.ref, standing: entry.standing
      };
    });
    return { registry_bytes: registry.bytes, selected, entries,current_entries:entries.filter(e=>document.current_lookup[e.definition_id]===e.definition_id+'@'+e.version), current_lookup: document.current_lookup };
  } finally { snapshots.close(); }
}
