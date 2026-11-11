import { digest } from './verified-projection.mjs';

const forbidden = new Set(['__proto__', 'prototype', 'constructor']);

function decode(bytes) {
  return JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes));
}

function segments(pointer) {
  if (!pointer.startsWith('/')) throw Error('absolute-member-pointer-required');
  const parts = pointer.slice(1).split('/').map(part => part.replaceAll('~1', '/').replaceAll('~0', '~'));
  if (parts.some(part => forbidden.has(part))) throw Error('unsafe-member-pointer');
  return parts;
}

function select(value, pointer) {
  for (const part of segments(pointer)) {
    if (value === null || typeof value !== 'object' || !Object.hasOwn(value, part)) {
      throw Error('original-member-missing');
    }
    value = value[part];
  }
  return value;
}

function merge(target, key, value) {
  if (!Object.hasOwn(target, key)) {
    target[key] = structuredClone(value);
    return;
  }
  const existing = target[key];
  if (existing && value && typeof existing === 'object' && typeof value === 'object'
      && !Array.isArray(existing) && !Array.isArray(value)) {
    for (const member of Object.keys(value)) {
      if (forbidden.has(member)) throw Error('unsafe-member-pointer');
      merge(existing, member, value[member]);
    }
    return;
  }
  if (JSON.stringify(existing) !== JSON.stringify(value)) throw Error('verified-members-conflict');
}

function assign(target, pointer, value) {
  const parts = segments(pointer);
  let cursor = target;
  for (const part of parts.slice(0, -1)) {
    if (!Object.hasOwn(cursor, part)) cursor[part] = {};
    if (cursor[part] === null || typeof cursor[part] !== 'object' || Array.isArray(cursor[part])) {
      throw Error('verified-members-conflict');
    }
    cursor = cursor[part];
  }
  merge(cursor, parts.at(-1), value);
}

export async function issuePlanningInput({
  selectionBytes, expectedSelectionDigest, operation, scope, cut, originals,
  authenticate, validateOriginal, validateInput, seal
}) {
  const selectionRaw = Buffer.from(selectionBytes);
  if (digest(selectionRaw) !== expectedSelectionDigest) throw Error('issuance-selection-mismatch');
  const selection = decode(selectionRaw);
  if (selection.version !== 1 || selection.operation !== operation || selection.scope !== scope) {
    throw Error('issuance-context-mismatch');
  }
  if (!selection.requirements.length || originals.length !== selection.requirements.length) {
    throw Error('original-evidence-set-mismatch');
  }
  const requirements = new Map(selection.requirements.map(item => [item.predicate, item]));
  if (requirements.size !== selection.requirements.length) throw Error('issuance-requirement-duplicate');

  // Capture all bytes before awaiting a verifier.
  const captured = originals.map(item => ({
    receipt: Buffer.from(item.receiptBytes), artifact: Buffer.from(item.artifactBytes)
  }));
  const input = {};
  const provenance = [];
  const seen = new Set();
  for (const { receipt, artifact } of captured) {
    const receiptDigest = digest(receipt);
    if (await authenticate(Buffer.from(receipt)) !== receiptDigest) {
      throw Error('original-receipt-authentication-failed');
    }
    const claim = decode(receipt);
    const requirement = requirements.get(claim.predicate);
    if (!requirement || seen.has(claim.predicate)) throw Error('original-evidence-set-mismatch');
    if (claim.version !== 1 || claim.operation !== operation || claim.scope !== scope || claim.cut !== cut) {
      throw Error('original-receipt-context-mismatch');
    }
    if (claim.artifact.sha256 !== digest(artifact) || claim.artifact.bytes !== artifact.length) {
      throw Error('original-receipt-artifact-mismatch');
    }
    const original = decode(artifact);
    if (await validateOriginal(requirement.schema, Buffer.from(artifact)) !== digest(artifact)) {
      throw Error('original-artifact-schema-invalid');
    }
    for (const mapping of requirement.mappings) {
      assign(input, mapping.to, select(original, mapping.from));
      provenance.push({
        predicate: claim.predicate, receipt: receiptDigest,
        artifact: digest(artifact), from: mapping.from, to: mapping.to
      });
    }
    seen.add(claim.predicate);
  }
  const artifactBytes = Buffer.from(JSON.stringify({
    operation, scope, cut, input, provenance, issuance_selection: expectedSelectionDigest
  }));
  if (await validateInput(operation, structuredClone(input)) !== true) {
    throw Error('projected-input-schema-invalid');
  }
  const receiptBytes = Buffer.from(await seal(Buffer.from(JSON.stringify({
    version: 1, predicate: 'verified-planning-input', operation, scope, cut,
    artifact: { sha256: digest(artifactBytes), bytes: artifactBytes.length }
  }))));
  return { artifactBytes, receiptBytes };
}
