import { createHash } from 'node:crypto';

export function digest(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

function decode(bytes) {
  return JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes));
}

export async function projectVerified({ operation, scope, cut, artifactBytes, receiptBytes, authenticate }) {
  // Copy once so verification and projection use the same bytes across the await.
  const artifact = Buffer.from(artifactBytes);
  const receipt = Buffer.from(receiptBytes);
  const receiptDigest = digest(receipt);
  if (await authenticate(Buffer.from(receipt)) !== receiptDigest) {
    throw Error('receipt-authentication-failed');
  }

  const claim = decode(receipt);
  if (claim.version !== 1 || claim.predicate !== 'verified-planning-input'
      || claim.operation !== operation || claim.scope !== scope || claim.cut !== cut) {
    throw Error('receipt-context-mismatch');
  }
  if (claim.artifact.sha256 !== digest(artifact) || claim.artifact.bytes !== artifact.length) {
    throw Error('receipt-artifact-mismatch');
  }

  const verified = decode(artifact);
  if (verified.operation !== operation || verified.scope !== scope || verified.cut !== cut
      || typeof verified.input !== 'object' || verified.input === null || Array.isArray(verified.input)) {
    throw Error('artifact-context-mismatch');
  }
  return verified.input;
}
