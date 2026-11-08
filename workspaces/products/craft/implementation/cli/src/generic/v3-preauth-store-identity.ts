/** Metadata-only, read-only V3 pre-Auth store identity. No Auth or intent owner.
 * Open Questions: D15-05 must bind this handle to a genuine root READY; D15-09
 * must prove equality against the future origin-bearing full V3 store. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {DatabaseSync, constants as sqlite} from 'node:sqlite';
import {constants as fsFlags, openSync, closeSync, fstatSync, lstatSync, realpathSync} from 'node:fs';
import {canonicalJson, captureJson, dataDigest, type Json} from '../profile-engine/contracts.js';
import {pinCoreImplementation} from '../commerce/commerce-core-physical.js';
import {assertGenericRepositoryPlanOwner, type GenericRepositoryPlanOwner,
  type GenericApplicationPlanHandle} from './repository-plan.js';

const MAX_DB_BYTES = 67_108_864;
const MAX_COMPATIBILITY_BYTES = 1_048_576;
const METADATA_TABLE = '_craft_generic_metadata';
// Exact source009 value-codec.ts atomic metadata DDL; sqlite_schema omits ';'.
const METADATA_DDL = `CREATE TABLE "_craft_generic_metadata" (id INTEGER PRIMARY KEY CHECK(id=1), store_id TEXT NOT NULL, compatibility TEXT NOT NULL, revision_counter BLOB NOT NULL CHECK(typeof(revision_counter)='blob' AND length(revision_counter)=8), command_count INTEGER NOT NULL CHECK(command_count>=0), command_bytes INTEGER NOT NULL CHECK(command_bytes>=0)) STRICT`;
const SCHEMA_SQL = 'SELECT type,name,tbl_name,sql FROM sqlite_schema WHERE name=? LIMIT 2';
const METADATA_SQL = `SELECT id,CASE WHEN typeof(store_id)='text' AND length(CAST(store_id AS BLOB))=36 THEN store_id ELSE NULL END AS store_id,CASE WHEN typeof(compatibility)='text' AND length(CAST(compatibility AS BLOB))<=${MAX_COMPATIBILITY_BYTES} THEN compatibility ELSE NULL END AS compatibility FROM "_craft_generic_metadata" LIMIT 2`;
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
// Separate from source009's frozen V1/V2 repository implementation closure.
// Pin this accessor and its physical/digest helpers at module load, then
// re-read their physical files before and after each authority-bearing use.
const ext = path.extname(fileURLToPath(import.meta.url));
const accessorPin = pinCoreImplementation(import.meta.url, [
  '../commerce/commerce-core-physical' + ext,
  '../commerce/commerce-core-syntax' + ext,
  '../profile-engine/contracts' + ext,
]);

export type V3PreAuthStoreFailure = 'InvalidRequest' | 'StoreUnavailable';
export class V3PreAuthStoreError extends Error {
  constructor(readonly code: V3PreAuthStoreFailure) { super(code); }
}
const unavailable = (): never => { throw new V3PreAuthStoreError('StoreUnavailable'); };
const identity = (s: ReturnType<typeof fstatSync>): string => [s.dev, s.ino, s.mode].join(':');

function parentChain(directory: string): string {
  let current = path.parse(directory).root;
  const parts: [string, string][] = [];
  for (const component of directory.slice(current.length).split(path.sep).filter(Boolean)) {
    current = path.join(current, component);
    const found = lstatSync(current);
    if (!found.isDirectory() || found.isSymbolicLink()) return unavailable();
    parts.push([current, identity(found)]);
  }
  return dataDigest(parts);
}

interface State {
  readonly accessorImplementationSha256: string;
  readonly plans: GenericRepositoryPlanOwner;
  readonly application: GenericApplicationPlanHandle;
  readonly sourceCaptureSha256: string;
  readonly executableSemanticsSha256: string;
  readonly profileSha256: string;
  readonly codeEpochSha256: string;
  readonly file: string;
  readonly directory: string;
  readonly parent: number;
  readonly descriptor: number;
  readonly anchored: string;
  readonly parentsSha256: string;
  readonly physical: string;
  readonly size: number;
  readonly storeId: string;
  readonly compatibilityText: string;
  readonly compatibility: Json;
  readonly storeEpochSha256: string;
  taken: boolean;
  closed: boolean;
}

export interface OriginalV3PreAuthStoreHandle {
  readonly kind: 'private-original-v3-preauth-store/v1-candidate';
}
const handles = new WeakMap<OriginalV3PreAuthStoreHandle, State>();

function accessorCurrent(state?: State): void {
  try {
    if (state && state.accessorImplementationSha256 !== accessorPin.sha256) unavailable();
    accessorPin.assertCurrent();
  } catch { unavailable(); }
}

function selectedSource(plans: GenericRepositoryPlanOwner,
    application: GenericApplicationPlanHandle) {
  assertGenericRepositoryPlanOwner(plans);
  plans.assertCurrent(application);
  const selected = plans.inspectSourceApplication(application);
  if (selected.contract.admission_mode !== 'external-write-entry' &&
      !(selected.contract.admission_mode === 'event-handoff-entry' && selected.contract.write_bindings.length > 0) ||
      typeof selected.source_capture_sha256 !== 'string' ||
      typeof selected.executable_semantics_sha256 !== 'string' ||
      typeof selected.derivation.profile_sha256 !== 'string' ||
      typeof selected.code_epoch_sha256 !== 'string') unavailable();
  return {
    sourceCaptureSha256: selected.source_capture_sha256,
    executableSemanticsSha256: selected.executable_semantics_sha256,
    profileSha256: selected.derivation.profile_sha256,
    codeEpochSha256: selected.code_epoch_sha256,
  };
}

function selectedCurrent(state: State): void {
  try {
    const selected = selectedSource(state.plans, state.application);
    if (selected.sourceCaptureSha256 !== state.sourceCaptureSha256 ||
        selected.executableSemanticsSha256 !== state.executableSemanticsSha256 ||
        selected.profileSha256 !== state.profileSha256 ||
        selected.codeEpochSha256 !== state.codeEpochSha256) unavailable();
  } catch { unavailable(); }
}

function stateFor(handle: OriginalV3PreAuthStoreHandle): State {
  const state = handle && typeof handle === 'object' ? handles.get(handle) : undefined;
  if (!state || state.closed) return unavailable();
  return state;
}

function physicalCurrent(state: State): void {
  try {
    if (parentChain(state.directory) !== state.parentsSha256 ||
        identity(fstatSync(state.parent)) !== identity(lstatSync(state.directory)) ||
        identity(fstatSync(state.descriptor)) !== state.physical ||
        identity(lstatSync(state.anchored)) !== state.physical ||
        identity(lstatSync(state.file)) !== state.physical ||
        fstatSync(state.descriptor).size !== state.size || state.size > MAX_DB_BYTES) unavailable();
  } catch { unavailable(); }
}

/** Compare a registered peer file with the held, anchored V3 store descriptor.
 * This is a physical-only assertion: no peer SQLite connection or store row is
 * opened, and no physical identity is returned to the caller. */
export function assertOriginalV3PreAuthDistinctFile(
    handle: OriginalV3PreAuthStoreHandle, peerFile: string): void {
  const state=stateFor(handle);
  try {
    accessorCurrent(state); selectedCurrent(state); physicalCurrent(state);
    if(typeof peerFile!=='string'||!path.isAbsolute(peerFile)||path.normalize(peerFile)!==peerFile) unavailable();
    const before=lstatSync(peerFile,{bigint:true});
    const held=fstatSync(state.descriptor,{bigint:true});
    if(!before.isFile()||before.isSymbolicLink()||(before.mode&0o777n)!==0o600n||
       before.dev===held.dev&&before.ino===held.ino) unavailable();
    physicalCurrent(state);
    const after=lstatSync(peerFile,{bigint:true});
    if(!after.isFile()||after.isSymbolicLink()||
       before.dev!==after.dev||before.ino!==after.ino||before.mode!==after.mode) unavailable();
  } catch { unavailable(); }
}

function metadataOnlyRead(descriptor: number, selected: ReturnType<typeof selectedSource>):
    {storeId: string; compatibilityText: string; compatibility: Json} {
  // SQLite opens the *held file*, not the mutable caller pathname. No writable
  // connection and no transaction or SQLite handle survives this function.
  const db = new DatabaseSync('/proc/self/fd/' + descriptor, {
    readOnly: true, enableForeignKeyConstraints: true,
    enableDoubleQuotedStringLiterals: false, allowExtension: false,
    timeout: 0, defensive: true,
  });
  try {
    db.setAuthorizer((action, table, column, database, trigger) => {
      if (trigger !== null) return sqlite.SQLITE_DENY;
      if (action === sqlite.SQLITE_SELECT) return sqlite.SQLITE_OK;
      if (action === sqlite.SQLITE_PRAGMA && column === null &&
          (table === 'encoding' || table === 'journal_mode')) return sqlite.SQLITE_OK;
      if (action === sqlite.SQLITE_FUNCTION && table === null &&
          (column === 'typeof' || column === 'length')) return sqlite.SQLITE_OK;
      if (action === sqlite.SQLITE_READ && database === 'main' &&
          ((table === 'sqlite_master' || table === 'sqlite_schema') &&
            (column === 'type' || column === 'name' || column === 'tbl_name' || column === 'sql') ||
           table === METADATA_TABLE &&
            (column === 'id' || column === 'store_id' || column === 'compatibility'))) return sqlite.SQLITE_OK;
      return sqlite.SQLITE_DENY;
    });
    if ((db.prepare('PRAGMA encoding').get() as {encoding?: unknown})?.encoding !== 'UTF-8' ||
        (db.prepare('PRAGMA journal_mode').get() as {journal_mode?: unknown})?.journal_mode !== 'delete') unavailable();
    const schema = db.prepare(SCHEMA_SQL).all(METADATA_TABLE) as Record<string, unknown>[];
    const definition = schema[0];
    if (schema.length !== 1 || !definition || definition.type !== 'table' ||
        definition.name !== METADATA_TABLE || definition.tbl_name !== METADATA_TABLE ||
        definition.sql !== METADATA_DDL) unavailable();
    const rows = db.prepare(METADATA_SQL).all() as Record<string, unknown>[];
    const row = rows[0];
    if (rows.length !== 1 || !row || row.id !== 1 ||
        typeof row.store_id !== 'string' || !uuid.test(row.store_id) ||
        typeof row.compatibility !== 'string') unavailable();
    const storeId = row!.store_id as string;
    const compatibilityText = row!.compatibility as string;
    const compatibility = captureJson(JSON.parse(compatibilityText));
    if (compatibility === null || typeof compatibility !== 'object' ||
        Array.isArray(compatibility) || canonicalJson(compatibility) !== compatibilityText) unavailable();
    const compatible = compatibility as Readonly<Record<string, Json>>;
    if (compatible.schema_version !== 'craft.generic-storage-compatibility/v1-candidate' ||
        compatible.executable_semantics_sha256 !== selected.executableSemanticsSha256 ||
        compatible.profile_sha256 !== selected.profileSha256) unavailable();
    return {storeId, compatibilityText, compatibility};
  } finally {
    db.close();
  }
}

/** Open only a private existing regular file and its exact metadata row. */
export function openOriginalV3PreAuthStoreIdentity(plans: GenericRepositoryPlanOwner,
    application: GenericApplicationPlanHandle, file: string): OriginalV3PreAuthStoreHandle {
  if (typeof file !== 'string' || !path.isAbsolute(file) || path.normalize(file) !== file)
    throw new V3PreAuthStoreError('InvalidRequest');
  let parent: number | undefined;
  let descriptor: number | undefined;
  try {
    accessorCurrent();
    const selected = selectedSource(plans, application);
    const directory = path.dirname(file);
    if (realpathSync(directory) !== directory) unavailable();
    const parentsSha256 = parentChain(directory);
    parent = openSync(directory, fsFlags.O_RDONLY | fsFlags.O_DIRECTORY | fsFlags.O_NOFOLLOW);
    const anchored = '/proc/self/fd/' + parent + '/' + path.basename(file);
    descriptor = openSync(anchored, fsFlags.O_RDONLY | fsFlags.O_NOFOLLOW);
    const st = fstatSync(descriptor);
    if (!st.isFile() || (st.mode & 0o777) !== 0o600 ||
        st.size === 0 || st.size > MAX_DB_BYTES) unavailable();
    const physical = identity(st);
    const provisional: State = {accessorImplementationSha256: accessorPin.sha256,
      plans, application, ...selected, file, directory, parent, descriptor, anchored,
      parentsSha256, physical, size: st.size, storeId: '', compatibilityText: '',
      compatibility: null, storeEpochSha256: '', taken: false, closed: false};
    physicalCurrent(provisional);
    const metadata = metadataOnlyRead(descriptor, selected);
    physicalCurrent(provisional);
    const storeEpochSha256 = dataDigest({
      store_id: metadata.storeId, physical, compatibility: metadata.compatibility,
    });
    accessorCurrent(provisional);
    const handle: OriginalV3PreAuthStoreHandle = Object.freeze({
      kind: 'private-original-v3-preauth-store/v1-candidate' as const,
    });
    handles.set(handle, {...provisional, ...metadata, storeEpochSha256});
    return handle;
  } catch {
    if (descriptor !== undefined) try { closeSync(descriptor); } catch { /* no successful close claim */ }
    if (parent !== undefined) try { closeSync(parent); } catch { /* no successful close claim */ }
    return unavailable();
  }
}

/** Publicly usable pre-Auth projection contains only the epoch digest. */
export function inspectOriginalV3PreAuthEpoch(handle: OriginalV3PreAuthStoreHandle):
    Readonly<{store_epoch_sha256: string}> {
  const state = stateFor(handle);
  accessorCurrent(state);
  selectedCurrent(state);
  physicalCurrent(state);
  accessorCurrent(state);
  return Object.freeze({store_epoch_sha256: state.storeEpochSha256});
}

/** One-shot metadata/currentness check. It returns no private identity data and
 * does not mint or verify READY. D15-05 must own the actual READY-before-check
 * ordering and close the handle on every outcome. */
export function assertOriginalV3PreAuthMetadataCurrentOnce(
    handle: OriginalV3PreAuthStoreHandle): void {
  const state = stateFor(handle);
  if (state.taken) return unavailable();
  state.taken = true;
  try {
    accessorCurrent(state);
    selectedCurrent(state);
    physicalCurrent(state);
    const current = metadataOnlyRead(state.descriptor, state);
    physicalCurrent(state);
    if (current.storeId !== state.storeId ||
        current.compatibilityText !== state.compatibilityText ||
        dataDigest({store_id: current.storeId, physical: state.physical,
          compatibility: current.compatibility}) !== state.storeEpochSha256) unavailable();
    accessorCurrent(state);
    return;
  } catch { return unavailable(); }
}

/** Recheck the anchored descriptor and pathname before a later full-owner open. */
export function assertOriginalV3PreAuthPhysicalCurrent(handle: OriginalV3PreAuthStoreHandle): void {
  const state = stateFor(handle);
  accessorCurrent(state);
  selectedCurrent(state);
  physicalCurrent(state);
  accessorCurrent(state);
}

/** The caller must close this descriptor on every root Auth outcome. Cleanup
 * deliberately remains available even if the accessor source became stale. */
export function closeOriginalV3PreAuthStoreIdentity(handle: OriginalV3PreAuthStoreHandle): void {
  const state = stateFor(handle);
  state.closed = true;
  let failed = false;
  try { closeSync(state.descriptor); } catch { failed = true; }
  try { closeSync(state.parent); } catch { failed = true; }
  if (failed) unavailable();
}
