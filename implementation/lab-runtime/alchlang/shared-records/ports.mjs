import { spawnSync } from 'node:child_process';
import { isDeepStrictEqual } from 'node:util';
import { readFileSync, mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { digest } from './verified-projection.mjs';
import { sameBinding } from './snapshots.mjs';
import { validateSchema,validateSchemaBatch } from './schema.mjs';

export function nativePort(request) {
  const result = spawnSync('python3', ['-B', path.join(import.meta.dirname, 'native_port.py')],
    { input: JSON.stringify(request), encoding: 'utf8', maxBuffer: 32 * 1024 * 1024, timeout: 600000 });
  if (result.status !== 0) {
    if (request.action === 'apply') {
      const observed = spawnSync('python3', ['-B', path.join(import.meta.dirname, 'native_port.py')], {
        input: JSON.stringify({action:'committed',store:request.store,operation:request.proposal.proposal_id}),
        encoding:'utf8',maxBuffer:32*1024*1024,timeout:600000
      });
      if (observed.status === 0) {
        const actual = JSON.parse(observed.stdout);
        if (!isDeepStrictEqual(actual.proposal,request.proposal) || !isDeepStrictEqual(actual.approval,request.approval)) {
          throw Error('native-original-operation-conflict');
        }
        return {outcome:'Committed',reconciled:true,...actual};
      }
      if (result.error || result.signal || result.status === null) {
        return {outcome:'Unknown',operation:request.proposal.proposal_id,continuation:'inspect-original-operation'};
      }
    }
    throw Error('native-port-refused: ' + (result.stderr || result.error || result.stdout));
  }
  return JSON.parse(result.stdout);
}

function key(entry) { return entry.definition_id + '@' + entry.version; }

export function registryAssessment(previous, proposed, material, carriers, changes = []) {
  const supplied = material;
  material = binding => {
    const raw = Buffer.from(supplied(binding));
    if (digest(raw) !== binding.sha256 || raw.length !== Number(binding.bytes)) throw Error('registry-original-material-mismatch');
    return raw;
  };
  const old = new Map(previous.entries.map(entry => [key(entry), entry]));
  const entries = new Map(proposed.entries.map(entry => [key(entry), entry]));
  if (old.size !== previous.entries.length || entries.size !== proposed.entries.length) throw Error('registry-duplicate-version');
  const permitted = new Map(changes.map(change => [change.version, change]));
  if (permitted.size !== changes.length) throw Error('registry-duplicate-change');
  const schemaChecks=[];
  for (const [version, entry] of old) {
    const next = entries.get(version);
    if (!next) throw Error('registry-retained-version-missing');
    const oldDigest = entry.sha256 ?? entry.body.sha256;
    if (next.body.sha256 !== oldDigest) throw Error('registry-retained-body-changed');
    if (entry.admission_decision_ref && !permitted.has(version)) {
      const disposition = JSON.parse(material(next.owner_disposition));
      if (disposition.decision_ref !== entry.admission_decision_ref) throw Error('registry-retained-decision-changed');
    }
  }
  for (const [version, entry] of entries) {
    const change = permitted.get(version);
    if (change && change.postimage_sha256 !== digest(Buffer.from(JSON.stringify(entry)))) throw Error('registry-change-postimage-mismatch');
    const prior = old.get(version);
    if(prior?.body&&!sameBinding(entry.body,prior.body))throw Error('registry-immutable-body-changed');
    if(prior?.path&&((entry.body.path??entry.body.ref)!==prior.path||entry.body.sha256!==prior.sha256))throw Error('registry-immutable-body-changed');
    if (prior && !change) {
      const standing = previous.current_lookup[entry.definition_id] === version ? 'admitted-current' : 'admitted-retained';
      if (entry.standing !== standing || !isDeepStrictEqual(entry.predecessor, prior.body ? prior.predecessor : null)) throw Error('registry-unapproved-lifecycle-change');
    }
    if (!old.has(version) && !permitted.has(version)) throw Error('registry-unapproved-addition');
    if (prior?.owner_disposition && !sameBinding(entry.owner_disposition,prior.owner_disposition)) throw Error('registry-original-disposition-changed');
    const owner = JSON.parse(material(entry.owner_disposition));
    const inheritedLegacy=!!prior&&entry.carrier.ref==='cal.artifact-type.definition/v1'&&!!owner.original_decision;
    const legacyDecision=prior?.admission_decision_ref??(inheritedLegacy?owner.decision_ref:null);
    if (legacyDecision) {
      if(owner.decision_ref !== legacyDecision || !owner.original_decision) throw Error('registry-original-decision-required');
      const originalDecision=JSON.parse(material(owner.original_decision));
      if((originalDecision.decision_id ?? (originalDecision.kind==='decision'?originalDecision.name:null)) !== legacyDecision) throw Error('registry-original-decision-mismatch');
    } else {
      if(owner.owner!==JSON.parse(material(entry.body)).semantic_owner_ref || owner.scope!==JSON.parse(material(entry.body)).scope.authority_scope_ref || owner.target!==version || owner.outcome!=='Accepted' || !owner.original || !sameBinding(owner.original,entry.body)) throw Error('registry-owner-target-unbound');
      if(!owner.authorization || !owner.role_assignment) throw Error('registry-owner-authority-required');
      const authorization=JSON.parse(material(owner.authorization));
      const role=JSON.parse(material(owner.role_assignment));
      if(authorization.authorized!==true || !authorization.accepted_definitions?.some(item=>item.version===version && sameBinding(item.source,entry.body))
        || role.role_ref!==owner.owner || role.principal_ref!==owner.principal_ref || !sameBinding(role.basis,owner.authorization)) throw Error('registry-owner-authority-unverified');
    }
    const carrier = carriers[entry.carrier.ref];
    if (!carrier) throw Error('registry-carrier-unqualified');
    for (const field of ['schema', 'generator']) {
      if (!sameBinding(entry[field], carrier[field])) throw Error('registry-carrier-material-mismatch');
    }
    if (!sameBinding(entry.carrier.descriptor, carrier.descriptor)
        || !sameBinding(entry.carrier.admission, carrier.admission)) throw Error('registry-carrier-admission-mismatch');
    material(entry.carrier.descriptor);material(entry.carrier.admission);
    const body = material(entry.body);
    const schema = material(entry.schema);
    const generator = material(entry.generator);
    schemaChecks.push({schema:JSON.parse(schema),bytes:body});
    const parsed = JSON.parse(body);
    if (parsed.definition_id !== entry.definition_id || parsed.version !== entry.version
        || parsed.classification.artifact_type_ref !== entry.carrier.ref) throw Error('registry-body-identity-mismatch');
    // Render with the exact qualified existing generator in an isolated directory.
    const home = mkdtempSync(path.join(tmpdir(), 'lab-registry-render-'));
    try {
      writeFileSync(path.join(home, 'definition.json'), body);
      writeFileSync(path.join(home, 'generator.py'), generator);
      const output = path.join(home, 'DEFINITION.md');
      const run = spawnSync('python3', ['-B', path.join(home, 'generator.py'), path.join(home, 'definition.json'), '--output', output],
        { encoding: 'utf8', timeout: 30000, maxBuffer: 1024 * 1024 });
      if (run.status !== 0 || !readFileSync(output).equals(material(entry.projection))) throw Error('registry-projection-mismatch');
    } finally {
      rmSync(home, { recursive: true, force: true });
    }
  }
  validateSchemaBatch(schemaChecks);
  for (const [identity, version] of Object.entries(proposed.current_lookup)) {
    const entry = entries.get(version);
    if (!entry || entry.definition_id !== identity || entry.standing !== 'admitted-current') throw Error('registry-lookup-invalid');
    if (previous.current_lookup[identity] !== version && !permitted.has(version)) throw Error('registry-lookup-unapproved');
  }
  for (const entry of proposed.entries) {
    if (entry.standing === 'admitted-current' && proposed.current_lookup[entry.definition_id] !== key(entry)) {
      throw Error('registry-current-selection-missing');
    }
  }
  for (const identity of Object.keys(previous.current_lookup)) {
    if (!Object.hasOwn(proposed.current_lookup, identity)) {
      const priorVersion=previous.current_lookup[identity], next=entries.get(priorVersion);
      if(!next || next.standing!=='withdrawn' || !permitted.has(priorVersion)) throw Error('registry-current-identity-removed');
    }
  }
  return { retained: old.size, versions: entries.size, current: Object.keys(proposed.current_lookup).length };
}

export function impactClosure(manifest, root, read) {
  const subjects = new Map();
  for (const subject of manifest.subjects) {
    if (subjects.has(subject.ref)) throw Error('impact-duplicate-subject');
    const bytes = read(subject.binding);
    if (digest(bytes) !== subject.binding.sha256 || bytes.length !== Number(subject.binding.bytes)) throw Error('impact-material-mismatch');
    subjects.set(subject.ref, subject);
  }
  if (!subjects.has(root) || manifest.unresolved !== 0 || !manifest.cursor) throw Error('impact-universe-incomplete');
  for (const subject of subjects.values()) {
    if (subject.dependencies.some(ref => !subjects.has(ref))) throw Error('impact-unresolved-dependency');
  }
  const affected = new Set([root]);
  let changed = true;
  while (changed) {
    changed = false;
    for (const subject of subjects.values()) {
      if (!affected.has(subject.ref) && subject.dependencies.some(ref => affected.has(ref))) {
        affected.add(subject.ref);
        changed = true;
      }
    }
  }
  return { universe: manifest.subjects.length, affected: [...affected].sort(),
    cursor: manifest.cursor, source_cut: manifest.source_cut, truncated: false, unresolved: 0 };
}

export function independentAssessment(specs, output, executors, materials) {
  const material=binding=>{
    const selected=materials?.[binding?.ref??binding?.path];
    if(!selected||selected.sha256!==binding.sha256)throw Error('assessment-material-unqualified');
    const raw=readFileSync(selected.path);
    if(digest(raw)!==binding.sha256||raw.length!==Number(binding.bytes))throw Error('assessment-material-drift');
    return raw;
  };
  const originalOutput=material(output);
  return specs.map(spec => {
    const selected = executors?.[spec.executor.ref];
    if (!selected || selected.sha256 !== spec.executor.sha256) throw Error('check-executor-unqualified');
    const raw = readFileSync(selected.path);
    if (digest(raw) !== selected.sha256) throw Error('check-executor-drift');
    const fixture=material(spec.fixture),contract=material(spec.source);
    const home = mkdtempSync(path.join(tmpdir(), 'lab-independent-check-'));
    try {
      const script = path.join(home, path.basename(selected.path));
      writeFileSync(script, raw, { mode: 0o600 });
      const run = spawnSync(selected.command, [script], {
        input: JSON.stringify({ specification: spec, output, output_material:originalOutput.toString('base64'),fixture_material:fixture.toString('base64'),contract_material:contract.toString('base64') }), cwd:home, encoding: 'utf8',
        timeout: selected.timeout_ms ?? 30000, maxBuffer: 1024 * 1024, shell: false
      });
      return { specification: spec, output, passed: run.status === 0,
        outcome: run.error ? 'Unknown' : run.status === 0 ? 'Passed' : 'Failed',
        stdout_sha256: digest(Buffer.from(run.stdout ?? '')), stderr_sha256: digest(Buffer.from(run.stderr ?? '')) };
    } finally { rmSync(home, { recursive: true, force: true }); }
  });
}
