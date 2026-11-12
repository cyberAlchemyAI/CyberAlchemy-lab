import { DatabaseSync } from 'node:sqlite';
import { mkdirSync, chmodSync } from 'node:fs';
import path from 'node:path';
import { digest } from './verified-projection.mjs';
import { evaluate,evaluateHistorical } from './kernel.mjs';
import {verifyPlanningEvidence} from './evidence.mjs';

const encode = value => JSON.stringify(value);

export class Journal {
  constructor(filename, {readOnly=false,trust=null} = {}) {
    this.trust=trust;
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
    for(const name of ['evidence_digest','model']){
      if(!columns.has(name))this.db.exec("ALTER TABLE commands ADD COLUMN "+name+" TEXT NOT NULL DEFAULT ''");
    }
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
      if(!this.trust || !command.evidence_digest || digest(Buffer.from(command.evidence))!==command.evidence_digest)throw Error('join-authentication-evidence-missing-or-corrupt');
      const original=JSON.parse(command.evidence);
      const checked=verifyPlanningEvidence(original,this.trust,{historical:true});
      const value=checked.input.value,key=value.join_key;
      if(checked.bytes.toString()!==command.artifact || original.command!==receipt.command
        || key.workspace!==workspace || key.run_ref!==run || key.operation!==row.operation
        || Number(key.id)!==row.id || Number(key.operation_key)!==row.id
        || value.cut!==row.cut || value.phase!==phase || Number(value.revision)!==revision
        || receipt.workspace!==workspace || receipt.run!==run || receipt.operation!==row.operation
        || receipt.source_cut!==row.cut || JSON.stringify(receipt.past_fact)!==JSON.stringify(value.past_fact))
        throw Error('join-retained-context-mismatch');
      phase = receipt.phase;
      revision = receipt.revision;
    }
    if (phase !== row.phase || revision !== row.revision) throw Error('join-state-history-mismatch');
    return { ...row, events };
  }

  async verifyHistory(workspace,run){
    const row=this.inspect(workspace,run);
    for(const receipt of row.events){
      const command=this.db.prepare('SELECT * FROM commands WHERE workspace=? AND run=? AND command=?').get(workspace,run,receipt.command);
      const request=JSON.parse(command.evidence),checked=verifyPlanningEvidence(request,this.trust,{historical:true});
      const original=this.trust.historical_artifacts?.[digest(checked.bytes)];
      const evalModel=(operation,input)=>original?.model_archive
        ? evaluateHistorical(operation,input,original.model_archive) : evaluate(operation,input);
      await evalModel('AssessJoinTransition',checked.input);
      if(await evalModel('ProposeJoinTransition',checked.input)!==receipt.phase)throw Error('join-retained-transition-mismatch');
    }
    return row;
  }

  async qualifyHistory(workspace,run){
    if(!this.trust)throw Error('join-verification-trust-required');
    const rows=this.db.prepare('SELECT * FROM commands WHERE workspace=? AND run=?').all(workspace,run);
    this.db.exec('BEGIN IMMEDIATE');
    try{
      for(const command of rows){
        const evidence=JSON.parse(command.evidence);
        const checked=verifyPlanningEvidence(evidence,this.trust,{historical:true});
        if(checked.bytes.toString()!==command.artifact)throw Error('join-original-artifact-mismatch');
        const original=this.trust.historical_artifacts?.[digest(checked.bytes)];
        this.db.prepare('UPDATE commands SET evidence_digest=?,model=? WHERE workspace=? AND run=? AND command=?')
          .run(digest(Buffer.from(command.evidence)),JSON.stringify(original??{implementation:checked.implementation}),workspace,run,command.command);
      }
      const result=await this.verifyHistory(workspace,run);this.db.exec('COMMIT');return result;
    }catch(error){this.db.exec('ROLLBACK');throw error;}
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
        await this.verifyHistory(key.workspace, key.run_ref);
        if (prior.digest !== commandDigest) throw Error('join-command-conflict');
        this.db.exec('COMMIT');
        return { ...JSON.parse(prior.receipt), replayed: true };
      }
      const current = await this.verifyHistory(key.workspace, key.run_ref);
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
      this.db.prepare('INSERT INTO commands(workspace,run,command,digest,receipt,artifact,evidence,evidence_digest,model) VALUES(?,?,?,?,?,?,?,?,?)')
        .run(key.workspace, key.run_ref, command, commandDigest, encode(receipt), Buffer.from(fullArtifact).toString(), JSON.stringify(evidence),digest(Buffer.from(JSON.stringify(evidence))),JSON.stringify({implementation:verifyPlanningEvidence(evidence,this.trust).implementation}));
      this.db.exec('COMMIT');
      return receipt;
    } catch (error) {
      this.db.exec('ROLLBACK');
      throw error;
    }
  }

  close() { this.db.close(); }
}
