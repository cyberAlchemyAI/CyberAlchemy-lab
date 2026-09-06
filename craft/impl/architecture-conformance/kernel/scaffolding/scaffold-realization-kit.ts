import { createHash } from "node:crypto";

import type { MetaTypeDescriptorV2 } from "../contracts/meta-type-descriptor-v2.js";
import {
  readValidatedHandle,
  type ValidatedHandle,
} from "../contracts/validated-handle.js";
import type { FactoryReadinessV1 } from "./readiness-classifier.js";
import { emptyKitTemplates } from "./templates.js";

const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");

export type ExpectedRedKitV1 = Readonly<{
  schema_version: "ExpectedRedKitProjection/v1";
  kit_id: string;
  files: readonly Readonly<{ path: string; sha256: string; content: string }>[];
  kit_sha256: string;
  authority_effect: "none";
}>;

export const scaffoldExpectedRedKit = (input: Readonly<{
  readiness: FactoryReadinessV1;
  descriptor: ValidatedHandle<MetaTypeDescriptorV2>;
}>): ExpectedRedKitV1 => {
  const descriptor = readValidatedHandle(input.descriptor);
  if (input.readiness.result !== "ready" || input.readiness.code !== "READY" ||
      input.readiness.descriptor_id !== descriptor.descriptor_id) {
    throw Object.assign(new Error("FACTORY_SCAFFOLD_NOT_READY"), {
      code: "FACTORY_SCAFFOLD_NOT_READY",
    });
  }
  const files = Object.entries(emptyKitTemplates(descriptor))
    .sort(([left], [right]) => Buffer.from(left).compare(Buffer.from(right)))
    .map(([path, content]) => Object.freeze({ path, content, sha256: sha256(content) }));
  const body = Object.freeze({
    schema_version: "ExpectedRedKitProjection/v1" as const,
    kit_id: `expected-red.${descriptor.descriptor_id}`,
    files: Object.freeze(files),
    authority_effect: "none" as const,
  });
  return Object.freeze({
    ...body,
    kit_sha256: sha256(JSON.stringify(body)),
  });
};
