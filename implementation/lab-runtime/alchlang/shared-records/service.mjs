import { readFileSync } from 'node:fs';
import path from 'node:path';
import { issuePlanningInput } from './original-receipt-issuance.mjs';
import { projectVerified, digest } from './verified-projection.mjs';
import { authenticatePacket, authentication, packetBytes, signPacket, validateContext } from './security.mjs';
import { validateSchema } from './schema.mjs';
import { evaluate } from './kernel.mjs';
import {verifyImplementation} from './implementation.mjs';
import {verifyPlanningEvidence} from './evidence.mjs';

export async function issue(request, trust, issuer, privateKey) {
  const implementation=verifyImplementation(trust.implementation);
  const selected = trust.selections[request.selection_id];
  if (!selected) throw Error('issuance-selection-untrusted');
  const selectionBytes = readFileSync(selected.path);
  const selection = JSON.parse(selectionBytes);
  const protocol = JSON.parse(readFileSync(path.join(import.meta.dirname,'contracts/verification-ports.schema.json')));
  validateSchema({...protocol,$ref:'#/$defs/IssuanceSelection'}, selectionBytes);
  const schemas = trust.schemas;
  const packets = request.originals.map(original => original.receipt);
  for (const packet of packets) {
    validateSchema({...protocol,$ref:'#/$defs/OriginalArtifactReceipt'}, packetBytes(packet));
  }
  const authenticate = authentication(packets, trust);
  let packet;
  const result = await issuePlanningInput({
    selectionBytes, expectedSelectionDigest: selected.sha256, implementation,
    operation: request.operation, scope: request.scope, cut: request.cut,
    originals: request.originals.map(original => ({
      receiptBytes: packetBytes(original.receipt),
      artifactBytes: Buffer.from(original.artifact, 'base64')
    })),
    authenticate,
    validateOriginal: async (id, bytes) => {
      const qualified = schemas[id];
      if (!qualified) throw Error('original-schema-untrusted');
      const raw = readFileSync(qualified.path);
      if (digest(raw) !== qualified.sha256) throw Error('original-schema-drift');
      return validateSchema(JSON.parse(raw), bytes);
    },
    validateInput: async (operation, input) => {
      const qualified = schemas[selection.input_schema];
      if (!qualified) throw Error('input-schema-untrusted');
      const raw = readFileSync(qualified.path);
      if (digest(raw) !== qualified.sha256) throw Error('input-schema-drift');
      validateSchema(JSON.parse(raw), Buffer.from(JSON.stringify(input)));
      return operation === request.operation;
    },
    seal: async bytes => {
      packet = signPacket(bytes, issuer, privateKey);
      authenticatePacket(packet, trust);
      return bytes;
    }
  });
  return { artifact: result.artifactBytes.toString('base64'), receipt: packet };
}

export async function execute(request, trust) {
  const {input}=verifyPlanningEvidence(request,trust);
  return { operation: request.operation, result: await evaluate(request.operation, input),
    artifact_sha256: digest(Buffer.from(request.artifact, 'base64')) };
}
