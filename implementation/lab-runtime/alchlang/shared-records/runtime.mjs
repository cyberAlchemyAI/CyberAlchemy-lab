import { readFileSync } from 'node:fs';
import { isDeepStrictEqual } from 'node:util';
import { projectVerified, digest } from './verified-projection.mjs';
import { authenticatePacket, authentication, validateContext } from './security.mjs';
import { evaluate } from './kernel.mjs';
import { Snapshots, sameBinding, bind } from './snapshots.mjs';
import { Journal } from './journal.mjs';
import { validateSchema } from './schema.mjs';
import path from 'node:path';
import { nativePort, registryAssessment } from './ports.mjs';

export async function projected(request, trust) {
  const receipt = authenticatePacket(request.receipt, trust);
  const bytes = Buffer.from(request.artifact, 'base64');
  const input = await projectVerified({
    operation: request.operation, scope: request.scope, cut: request.cut,
    artifactBytes: bytes, receiptBytes: receipt.bytes,
    authenticate: authentication([request.receipt], trust)
  });
  validateContext(input, request, trust);
  return { input, bytes };
}

export async function transition(request, trust, filename) {
  if (request.operation !== 'AssessJoinTransition') throw Error('join-transition-operation-required');
  const { input, bytes } = await projected(request, trust);
  const journal = new Journal(filename);
  try { return await journal.transition(input.value, request.command, bytes, request); }
  finally { journal.close(); }
}

export async function publish(request, trust, filename) {
  if (request.operation !== 'PlanPublication') throw Error('publication-operation-required');
  const { input, bytes } = await projected(request, trust);
  const value = input.value;
  const snapshots = new Snapshots(filename);
  try {
    const prior = snapshots.inspectPublication(value.workspace, value.operation_ref);
    if (prior) {
      if (prior.artifact_digest !== digest(bytes)) throw Error('publication-operation-conflict');
      return { ...prior, replayed: true };
    }
    const registryType = trust.registry_contract;
    if (!registryType) throw Error('registry-contract-admission-required');
    const descriptorBytes = Buffer.from(registryType.artifact, 'base64');
    if (!sameBinding(bind(value.registry_contract.ref, descriptorBytes), value.registry_contract)) throw Error('registry-contract-binding-mismatch');
    const admission = authenticatePacket(registryType.admission, trust);
    const admittedBytes = Buffer.from(registryType.admission_artifact, 'base64');
    if (admission.statement.predicate !== 'artifact-type-admission'
        || admission.statement.operation !== 'PlanPublication' || admission.statement.scope !== request.scope
        || admission.statement.cut !== request.cut || admission.statement.artifact.sha256 !== digest(admittedBytes)
        || admission.statement.artifact.bytes !== admittedBytes.length) throw Error('registry-contract-admission-mismatch');
    const admitted = JSON.parse(admittedBytes);
    const descriptor = JSON.parse(descriptorBytes);
    if (descriptor.artifact_type_ref !== 'cal.artifact-type.definition-registry/v2'
        || admitted.artifact_type_ref !== descriptor.artifact_type_ref
        || admitted.standing !== 'owner-admitted-current'
        || admitted.descriptor_sha256 !== digest(descriptorBytes)) throw Error('registry-contract-not-current');
    if (await evaluate('PlanPublication', input) !== 'PublicationPlanReady') throw Error('publication-not-ready');
    if (value.proposed_registry.ref !== 'registry.json' || value.snapshot.index.ref !== 'index.json'
        || value.snapshot.source.ref !== 'source.json') throw Error('snapshot-protocol-role-mismatch');
    const staged = snapshots.stage(value.workspace, value.operation_ref, value.source_cut, request.files);
    if (!sameBinding(staged.binding, value.bundle)) throw Error('publication-complete-bundle-mismatch');
    const material = binding => {
      const result = snapshots.material(staged.binding.sha256, binding.ref ?? binding.path);
      if (!sameBinding(result.binding, binding)) throw Error('publication-member-mismatch');
      return result.bytes;
    };
    material(value.proposed_registry);
    material(value.snapshot.index);
    material(value.snapshot.source);
    for (const body of value.target_bodies) material(body);
    const observed = snapshots.current(value.workspace);
    const selectorBytes = Buffer.from(JSON.stringify(observed));
    if (value.expected_selector.sha256 !== digest(selectorBytes)
        || Number(value.expected_selector.bytes) !== selectorBytes.length) throw Error('publication-selector-binding-mismatch');
    if (!Array.isArray(trust.required_readers) || trust.required_readers.length === 0) throw Error('publication-readers-unqualified');
    const source = JSON.parse(material(value.snapshot.source));
    if (JSON.stringify([...source.readers].sort()) !== JSON.stringify([...trust.required_readers].sort())
        || source.reader_protocol !== 'snapshot-selector/v1') throw Error('publication-readers-unqualified');
    const previousBytes = observed
      ? snapshots.material(observed.digest, value.expected_registry.ref).bytes
      : readFileSync(trust.initial_registry.path);
    if (!sameBinding(bind(value.expected_registry.ref, previousBytes), value.expected_registry)) throw Error('publication-predecessor-binding-mismatch');
    const previous = JSON.parse(previousBytes);
    if (!observed && digest(readFileSync(trust.initial_registry.path)) !== trust.initial_registry.sha256) throw Error('publication-initial-registry-drift');
    const registryBytes = material(value.proposed_registry);
    validateSchema(JSON.parse(readFileSync(path.join(import.meta.dirname,'contracts/definition-registry-v2.schema.json'))), registryBytes);
    const proposed = JSON.parse(registryBytes);
    registryAssessment(previous, proposed, material, trust.carriers, source.approved_changes);
    const index = JSON.parse(material(value.snapshot.index));
    const expectedIndex = proposed.entries.map(entry => ({
      version: entry.definition_id + '@' + entry.version,
      body: entry.body, projection: entry.projection
    })).sort((left, right) => left.version.localeCompare(right.version));
    if (!isDeepStrictEqual(index.current_lookup, proposed.current_lookup)
        || !isDeepStrictEqual(index.definitions, expectedIndex)) throw Error('publication-index-mismatch');
    const lifecyclePackets = source.lifecycle ?? [];
    for (const lifecycle of lifecyclePackets) {
      if (lifecycle.operation !== 'PlanLifecycleImpact') throw Error('lifecycle-operation-required');
      const checked = await projected(lifecycle, trust);
      if (await evaluate('PlanLifecycleImpact', checked.input) !== 'LifecyclePlanReady') throw Error('lifecycle-not-ready');
    }
    const oldVersions = new Set(previous.entries.map(entry => entry.definition_id + '@' + entry.version));
    for (const change of source.approved_changes) {
      if (oldVersions.has(change.version)) {
        const candidates = lifecyclePackets;
        const approved = candidates.some(candidate => {
          const body = JSON.parse(Buffer.from(candidate.artifact, 'base64')).input.value;
          const target = proposed.entries.find(entry => entry.definition_id + '@' + entry.version === change.version);
          if (body.current.sha256 !== target.body.sha256) return false;
          if (target.standing === 'withdrawn') return body.intent === 'Withdraw' && body.successor === null;
          const successor = proposed.entries.find(entry =>
            entry.definition_id === target.definition_id
            && proposed.current_lookup[entry.definition_id] === entry.definition_id + '@' + entry.version);
          return body.intent !== 'Withdraw' && successor && body.successor
            && sameBinding(body.successor, successor.body);
        });
        if (!approved) throw Error('lifecycle-transition-required');
      }
    }
    const native = nativePort({ action: 'committed', store: request.native_store, operation: value.operation_ref });
    if (!isDeepStrictEqual(native.proposal, JSON.parse(material(value.proposal)))
        || !isDeepStrictEqual(native.approval, JSON.parse(material(value.permission)))
        || !sameBinding(native.original_receipt, value.native_receipt.proof) || native.targets_digest !== value.expected_targets
        || native.expected_head !== value.native_head || native.source_cut !== value.native_receipt.source_cut) {
      throw Error('publication-native-receipt-mismatch');
    }
    if (!source.native_transaction || source.native_transaction.digest !== native.transaction
        || !isDeepStrictEqual(source.native_transaction.targets, native.targets)) throw Error('publication-native-consequences-mismatch');
    const bodies = value.target_bodies.map(body => JSON.parse(material(body)));
    if (native.targets.length !== bodies.length || native.resolved_records.some(record =>
      !bodies.some(body => isDeepStrictEqual(body, record)))) throw Error('publication-native-target-closure-mismatch');
    return snapshots.publish({
      workspace: value.workspace, operation: value.operation_ref,
      expected: observed, snapshot: staged.binding.sha256, artifactDigest: digest(bytes)
    });
  } finally { snapshots.close(); }
}

export async function initializeJoin(value, filename) {
  const journal = new Journal(filename);
  try { return await journal.initialize(value); } finally { journal.close(); }
}
