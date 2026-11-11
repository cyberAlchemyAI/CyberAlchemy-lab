import { DatabaseSync } from 'node:sqlite';
import { mkdirSync, chmodSync } from 'node:fs';
import path from 'node:path';
import { digest } from './verified-projection.mjs';

export function bind(ref, bytes) {
  return { ref, sha256: digest(bytes), bytes: String(bytes.length) };
}
export function sameBinding(left, right) {
  return (left.ref ?? left.path) === (right.ref ?? right.path) && left.sha256 === right.sha256 && String(left.bytes) === String(right.bytes);
}
function safeName(name) {
  if (!name || name.startsWith('/') || name.includes(String.fromCharCode(92)) || name.split('/').some(part => !part || part === '.' || part === '..')) {
    throw Error('snapshot-path-invalid');
  }
}

export class Snapshots {
  constructor(filename, {readOnly=false} = {}) {
    if (readOnly) { this.db = new DatabaseSync(filename,{readOnly:true}); return; }
    mkdirSync(path.dirname(filename), { recursive: true, mode: 0o700 });
    this.db = new DatabaseSync(filename);
    chmodSync(filename,0o600);
    this.db.exec('PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA busy_timeout=5000');
    this.db.exec(
      'CREATE TABLE IF NOT EXISTS blobs(digest TEXT PRIMARY KEY, bytes BLOB NOT NULL);' +
      'CREATE TABLE IF NOT EXISTS snapshots(digest TEXT PRIMARY KEY, manifest TEXT NOT NULL);' +
      'CREATE TABLE IF NOT EXISTS selectors(workspace TEXT PRIMARY KEY, revision INTEGER NOT NULL, digest TEXT NOT NULL);' +
      'CREATE TABLE IF NOT EXISTS publications(workspace TEXT NOT NULL, operation TEXT NOT NULL, request TEXT NOT NULL, receipt TEXT NOT NULL, PRIMARY KEY(workspace,operation));'
    );
  }

  stage(workspace, operation, cut, files) {
    const entries = Object.entries(files).sort(([a], [b]) => a.localeCompare(b));
    if (!workspace || !operation || !entries.length || entries.length > 4096) throw Error('snapshot-context-invalid');
    const decoded = entries.map(([name, body]) => {
      safeName(name);
      const bytes = Buffer.from(body, 'base64');
      if (bytes.toString('base64') !== body || bytes.length > 8 * 1024 * 1024) throw Error('snapshot-file-bound');
      return { name, bytes, binding: bind(name, bytes) };
    });
    if (decoded.reduce((total, item) => total + item.bytes.length, 0) > 64 * 1024 * 1024) throw Error('snapshot-total-bound');
    const manifest = { version: 1, workspace, operation, cut, files: decoded.map(item => item.binding) };
    const raw = Buffer.from(JSON.stringify(manifest));
    const id = digest(raw);
    this.db.exec('BEGIN IMMEDIATE');
    try {
      for (const item of decoded) {
        this.db.prepare('INSERT OR IGNORE INTO blobs VALUES(?,?)').run(item.binding.sha256, item.bytes);
      }
      this.db.prepare('INSERT OR IGNORE INTO snapshots VALUES(?,?)').run(id, raw.toString());
      this.db.exec('COMMIT');
      return { binding: bind('snapshot:' + id, raw), manifest };
    } catch (error) {
      this.db.exec('ROLLBACK');
      throw error;
    }
  }

  material(id, name) {
    const row = this.db.prepare('SELECT manifest FROM snapshots WHERE digest=?').get(id);
    if (!row || digest(Buffer.from(row.manifest)) !== id) throw Error('snapshot-not-found-or-corrupt');
    const manifest = JSON.parse(row.manifest);
    const binding = manifest.files.find(file => file.ref === name);
    if (!binding) throw Error('snapshot-file-not-found');
    const blob = this.db.prepare('SELECT bytes FROM blobs WHERE digest=?').get(binding.sha256);
    if (!blob || !sameBinding(bind(name, blob.bytes), binding)) throw Error('snapshot-blob-corrupt');
    return { bytes: Buffer.from(blob.bytes), binding, manifest };
  }

  current(workspace) {
    return this.db.prepare('SELECT revision,digest FROM selectors WHERE workspace=?').get(workspace) ?? null;
  }

  publish({ workspace, operation, expected, snapshot, artifactDigest }) {
    this.db.exec('BEGIN IMMEDIATE');
    try {
      const request = JSON.stringify({ expected, snapshot, artifactDigest });
      const prior = this.db.prepare('SELECT request,receipt FROM publications WHERE workspace=? AND operation=?').get(workspace, operation);
      if (prior) {
        if (prior.request !== request) throw Error('publication-operation-conflict');
        this.db.exec('COMMIT');
        return { ...JSON.parse(prior.receipt), replayed: true };
      }
      const current = this.current(workspace);
      if (JSON.stringify(current) !== JSON.stringify(expected)) throw Error('publication-selector-conflict');
      const stored = this.db.prepare('SELECT manifest FROM snapshots WHERE digest=?').get(snapshot);
      if (!stored || digest(Buffer.from(stored.manifest)) !== snapshot) throw Error('snapshot-not-found-or-corrupt');
      const manifest = JSON.parse(stored.manifest);
      if (manifest.workspace !== workspace || manifest.operation !== operation) throw Error('snapshot-operation-mismatch');
      // Verify every object in the immutable snapshot before moving its selector.
      for (const file of manifest.files) this.material(snapshot, file.ref);
      const receipt = { workspace, operation, previous: current,
        selected: { revision: (current?.revision ?? 0) + 1, digest: snapshot },
        artifact_digest: artifactDigest, replayed: false };
      this.db.prepare('INSERT INTO selectors VALUES(?,?,?) ON CONFLICT(workspace) DO UPDATE SET revision=excluded.revision,digest=excluded.digest')
        .run(workspace, receipt.selected.revision, snapshot);
      this.db.prepare('INSERT INTO publications VALUES(?,?,?,?)').run(workspace, operation, request, JSON.stringify(receipt));
      this.db.exec('COMMIT');
      return receipt;
    } catch (error) {
      this.db.exec('ROLLBACK');
      throw error;
    }
  }

  inspectPublication(workspace, operation) {
    const row = this.db.prepare('SELECT receipt FROM publications WHERE workspace=? AND operation=?').get(workspace, operation);
    return row ? JSON.parse(row.receipt) : null;
  }

  close() { this.db.close(); }
}
