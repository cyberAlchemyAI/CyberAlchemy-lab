import { createPrivateKey, createPublicKey, sign, verify } from 'node:crypto';
import { digest } from './verified-projection.mjs';

export function packetBytes(packet) {
  if (typeof packet.body !== 'string') throw Error('receipt-body-required');
  const bytes = Buffer.from(packet.body, 'base64');
  if (bytes.toString('base64') !== packet.body) throw Error('receipt-body-encoding');
  return bytes;
}

export function authenticatePacket(packet, trust, now = Date.now()) {
  const bytes = packetBytes(packet);
  const principal = trust.principals[packet.issuer];
  if (!principal || !/^[0-9a-f]{128}$/.test(packet.signature)) throw Error('receipt-signer-untrusted');
  const encodedKey = principal.public_key;
  const key = /^[0-9a-f]{64}$/.test(encodedKey)
    ? createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),Buffer.from(encodedKey,'hex')]),format:'der',type:'spki'})
    : createPublicKey(encodedKey);
  if (key.asymmetricKeyType !== 'ed25519'
      || !verify(null, bytes, key, Buffer.from(packet.signature, 'hex'))) {
    throw Error('receipt-signature-invalid');
  }
  const statement = JSON.parse(bytes);
  const permitted = principal.grants.some(grant =>
    grant.predicate === statement.predicate && grant.operation === statement.operation
    && grant.scope === statement.scope && grant.cut === statement.cut
    && (!grant.expires || Date.parse(grant.expires) > now));
  if (!permitted) throw Error('receipt-grant-mismatch');
  return { bytes, statement, digest: digest(bytes) };
}

export function authentication(packets, trust) {
  const allowed = new Map();
  for (const packet of packets) {
    const verified = authenticatePacket(packet, trust);
    allowed.set(verified.digest, verified.bytes);
  }
  return async bytes => allowed.has(digest(bytes)) ? digest(bytes) : null;
}

export function signPacket(bytes, issuer, privateKey) {
  const key = createPrivateKey(privateKey);
  if (key.asymmetricKeyType !== 'ed25519') throw Error('ed25519-key-required');
  return { issuer, body: Buffer.from(bytes).toString('base64'),
    signature: sign(null, bytes, key).toString('hex') };
}

export function validateContext(input, request, trust) {
  const value = input.value;
  if (!value || typeof value !== 'object') return;
  const cut = value.source_cut ?? value.cut ?? value.expected_source_cut;
  if (cut && cut !== request.cut) throw Error('verified-input-cut-mismatch');
  if (value.workspace) {
    const scope = trust.workspaces?.[value.workspace]?.scope ?? value.workspace;
    if (scope !== request.scope) throw Error('verified-input-workspace-scope-mismatch');
  }
}
