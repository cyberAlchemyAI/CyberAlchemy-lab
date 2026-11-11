import { DatabaseSync } from 'node:sqlite';
import { mkdirSync, chmodSync } from 'node:fs';
import path from 'node:path';
import { digest } from './verified-projection.mjs';
import { evaluate } from './kernel.mjs';

const encode = value => JSON.stringify(value);

export class Journal {
  constructor(filename, {readOnly=false} = {}) {
    if (readOnly) { this.db = new DatabaseSync(filename,{readOnly:true}); return; }
    mkdirSync(path.dirname(filename), { recursive: true, mode: 0o700 });
    this.db = new DatabaseSync(filename);
    chmodSync(filename, 0o600);
    this.db.exec("PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA busy_timeout=5000");
    this.db.exec(
      'CREATE TABLE IF NOT EXISTS runs(' +
      'id INTEGER PRIMARY KEY, workspace TEXT NOT NULL, run TEXT NOT NULL,' +
      'operation TEXT NOT NULL, cut TEXT NOT NULL, phase TEXT NOT NULL,' +
      'revision INTEGER NOT NULL, initial TEXT NOT NULL,' +
      'UNIQUE(workspace,run), UNIQUE(workspace,operation));' +
      'CREATE TABLE IF NOT EXISTS commands(' +
      'workspace TEXT NOT NULL, run TEXT NOT NULL, command TEXT NOT NULL,' +
      'digest TEXT NOT NULL, receipt TEXT NOT NULL, artifact TEXT NOT NULL, evidence TEXT NOT NULL, PRIMARY KEY(workspace,run,command));' +
      'CREATE TABLE IF NOT EXISTS events(' +
      'workspace TEXT NOT NULL, run TEXT NOT NULL, revision INTEGER NOT NULL,' +
      'event TEXT NOT NULL, PRIMARY KEY(workspace,run,revision));'
    );
    const columns = new Set(this.db.prepare('PRAGMA table_info(commands)').all().map(column => column.name));
    if (!columns.has('artifact')) this.db.exec("ALTER TABLE commands ADD COLUMN artifact TEXT NOT NULL DEFAULT ''");
    if (!columns.has('evidence')) this.db.exec("ALTER TABLE commands ADD COLUMN evidence TEXT NOT NULL DEFAULT '{}'");
  }

  inspect(workspace, run) {
    const row = this.db.prepare('SELECT * FROM runs WHERE workspace=? AND run=?').get(workspace, run);
    if (!row) throw Error('join-not-found');
    const events = this.db.prepare(
      'SELECT event FROM events WHERE workspace=? AND run=? ORDER BY revision'
    ).all(workspace, run).map(item => JSON.parse(item.event));
    let phase = 'Proposed';
    let revision = 1;
    for (const receipt of events) {
      const command = this.db.prepare('SELECT * FROM commands WHERE workspace=? AND run=? AND command=?')
        .get(workspace, run, receipt.command);
      const { receipt_digest: expected, ...core } = receipt;
      if (!command || !command.artifact || receipt.previous_phase !== phase || receipt.revision !== revision + 1
          || digest(Buffer.from(JSON.stringify(core))) !== expected || command.receipt !== JSON.stringify(receipt)
          || digest(Buffer.from(command.artifact)) !== command.digest || receipt.command_digest !== command.digest) {
        throw Error('join-history-integrity-mismatch');
      }
      phase = receipt.phase;
      revision = receipt.revision;
    }
    if (phase !== row.phase || revision !== row.revision) throw Error('join-state-history-mismatch');
    return { ...row, events };
  }

  async initialize(value) {
    if (Object.keys(value).some(key => !['workspace','run_ref','original_operation','source_cut'].includes(key))) throw Error('join-initialization-field-unknown');
    if (!value.workspace || !value.run_ref || !value.original_operation || !/^[a-f0-9]{64}$/.test(value.source_cut)) {
      throw Error('join-initialization-context-required');
    }
    value = structuredClone(value);
    await evaluate('AssessJoinInitialization', {value:{
      ...value, phase:'Proposed', current_source_cut:value.source_cut,
      native_outcome:'Unobserved', publication_outcome:'Unobserved',
      terminal_receipt:null,published_snapshot:null,published_verification:null
    }});
    const initial = encode(value);
    this.db.exec('BEGIN IMMEDIATE');
    try {
      const existing = this.db.prepare('SELECT * FROM runs WHERE workspace=? AND run=?')
        .get(value.workspace, value.run_ref);
      if (existing) {
        if (existing.initial !== initial) throw Error('join-identity-conflict');
        this.db.exec('COMMIT');
        return this.inspect(value.workspace, value.run_ref);
      }
      this.db.prepare(
        "INSERT INTO runs(workspace,run,operation,cut,phase,revision,initial) VALUES(?,?,?,?,'Proposed',1,?)"
      ).run(value.workspace, value.run_ref, value.original_operation, value.source_cut, initial);
      this.db.exec('COMMIT');
      return this.inspect(value.workspace, value.run_ref);
    } catch (error) {
      this.db.exec('ROLLBACK');
      throw error;
    }
  }

  async transition(value, command, fullArtifact, evidence = {}) {
    if (typeof command !== 'string' || !command) throw Error('join-command-required');
    value = structuredClone(value);
    const commandDigest = digest(Buffer.from(fullArtifact));
    this.db.exec('BEGIN IMMEDIATE');
    try {
      const key = value.join_key;
      const prior = this.db.prepare('SELECT * FROM commands WHERE workspace=? AND run=? AND command=?')
        .get(key.workspace, key.run_ref, command);
      if (prior) {
        this.inspect(key.workspace, key.run_ref);
        if (prior.digest !== commandDigest) throw Error('join-command-conflict');
        this.db.exec('COMMIT');
        return { ...JSON.parse(prior.receipt), replayed: true };
      }
      const current = this.inspect(key.workspace, key.run_ref);
      if (current.id !== Number(key.id) || current.id !== Number(key.operation_key)
          || current.operation !== key.operation || current.cut !== value.cut
          || current.revision !== Number(value.revision) || current.phase !== value.phase) {
        throw Error('join-persisted-precondition-mismatch');
      }
      await evaluate('AssessJoinTransition', { value });
      const next = await evaluate('ProposeJoinTransition', { value });
      const receipt = {
        workspace: key.workspace, run: key.run_ref, operation: key.operation,
        command, command_digest: commandDigest, previous_phase: current.phase,
        phase: next, revision: current.revision + 1, source_cut: current.cut,
        past_fact: value.past_fact, replayed: false
      };
      receipt.receipt_digest = digest(Buffer.from(JSON.stringify(receipt)));
      this.db.prepare('INSERT INTO events VALUES(?,?,?,?)')
        .run(key.workspace, key.run_ref, receipt.revision, encode(receipt));
      this.db.prepare('UPDATE runs SET phase=?,revision=? WHERE id=?')
        .run(next, receipt.revision, current.id);
      this.db.prepare('INSERT INTO commands(workspace,run,command,digest,receipt,artifact,evidence) VALUES(?,?,?,?,?,?,?)')
        .run(key.workspace, key.run_ref, command, commandDigest, encode(receipt), Buffer.from(fullArtifact).toString(), JSON.stringify(evidence));
      this.db.exec('COMMIT');
      return receipt;
    } catch (error) {
      this.db.exec('ROLLBACK');
      throw error;
    }
  }

  close() { this.db.close(); }
}
