import { admitMetaTypeDescriptorV2 } from "../../kernel/codecs/decode-meta-type-descriptor-v2.js";
import type {
  MetaTypeAdmissionV2,
  MetaTypeDescriptorV2,
} from "../../kernel/contracts/meta-type-descriptor-v2.js";
import type { ValidatedHandle } from "../../kernel/contracts/validated-handle.js";
import { classifyFactoryReadiness } from "../../kernel/scaffolding/readiness-classifier.js";
import { exactKeys, fail, isRecord } from "../shared/canonical.js";

export type FactoryKitPackageV1 = Readonly<{
  schema_version: "FactoryKitPackage/v1";
  admission: MetaTypeAdmissionV2;
  descriptor: MetaTypeDescriptorV2;
  reference_documents: Readonly<Record<string, string>>;
  authority_effect: "none";
}>;

export const inspectFactoryKitPackage = async (value: unknown): Promise<Readonly<{
  result: "ready" | "refused";
  readiness: ReturnType<typeof classifyFactoryReadiness>;
  descriptor: ValidatedHandle<MetaTypeDescriptorV2>;
  provider_ref_count: number;
  authority_effect: "none";
}>> => {
  const record = isRecord(value) ? value : fail("FACTORY_KIT_PACKAGE_INVALID");
  exactKeys(record, ["schema_version", "admission", "descriptor", "reference_documents", "authority_effect"],
    "FACTORY_KIT_PACKAGE_INVALID");
  if (record.schema_version !== "FactoryKitPackage/v1" || record.authority_effect !== "none" ||
      !isRecord(record.admission) || !isRecord(record.descriptor) ||
      !isRecord(record.reference_documents) ||
      Object.values(record.reference_documents).some((bytes) => typeof bytes !== "string")) {
    fail("FACTORY_KIT_PACKAGE_INVALID");
  }
  const documents = record.reference_documents as Record<string, string>;
  const descriptor = await admitMetaTypeDescriptorV2(
    JSON.stringify(record.descriptor),
    JSON.stringify(record.admission),
    (ref) => documents[ref.id] ?? fail("FACTORY_KIT_REFERENCE_MISSING", ref.id),
  );
  const readiness = classifyFactoryReadiness({
    admission: record.admission as unknown as MetaTypeAdmissionV2,
    descriptor,
  });
  return Object.freeze({
    result: readiness.result,
    readiness,
    descriptor,
    provider_ref_count: Object.keys(
      (record.descriptor as Record<string, unknown>).provider_refs as Record<string, unknown>,
    ).length,
    authority_effect: "none",
  });
};
