import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../..");
const sourcePath = "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/domain-meta-types.projection.json";
const outputPath = "projects/domainspec-v2/development/meta-type-realization-factory/runs/MTF-029/readiness-matrix.json";
const sha256 = (value) => createHash("sha256").update(value).digest("hex");

const proofDisposition = new Map([
  ["DS-D1.3", ["bounded-proof-complete", "two TypeScript Enum cases through the v2 registry"]],
  ["DS-D1.4", ["bounded-proof-complete", "one direct TypeScript Operation plus one Rule relation witness"]],
  ["DS-D1.7", ["bounded-proof-complete", "one Rule across TypeScript Python and Rust"]],
]);
const firstPrerequisites = new Set(["DS-D1.1", "DS-D1.2"]);
const orderedQueue = [
  "DS-D1.1", "DS-D1.2", "DS-D1.6", "DS-D1.5", "DS-D1.13",
  "DS-D1.8", "DS-D1.11", "DS-D1.12", "DS-D1.14", "DS-D1.9",
];

export const buildReadinessMatrix = async (options = {}) => {
  const sourceBytes = options.sourceBytes === undefined
    ? await readFile(resolve(repositoryRoot, sourcePath))
    : Buffer.from(options.sourceBytes, "utf8");
  const source = JSON.parse(sourceBytes.toString("utf8"));
  if (source.status !== "candidate-read-model" || source.authority_effect !== "none" ||
      !Array.isArray(source.meta_types) || source.meta_types.length !== 25) {
    throw new Error("FACTORY_READINESS_SOURCE_INVALID");
  }
  const items = [...source.meta_types]
    .sort((left, right) => Number(left.meta_type_id.split(".")[1]) -
      Number(right.meta_type_id.split(".")[1]))
    .map((item) => {
      const proof = proofDisposition.get(item.meta_type_id);
      let disposition;
      let next_step;
      if (proof) {
        disposition = proof[0];
        next_step = "inspect bounded evidence; any mapping promotion remains with its owner";
      } else if (item.maturity === "superseded") {
        disposition = "tombstone";
        next_step = `preserve identifier; replacement is ${item.replacement_ref}`;
      } else if (item.maturity === "deferred") {
        disposition = "owner-disposition-required";
        next_step = item.review_trigger;
      } else if (item.maturity === "candidate") {
        disposition = "owner-admission-required";
        next_step = item.review_trigger;
      } else if (firstPrerequisites.has(item.meta_type_id)) {
        disposition = "mapping-prerequisite";
        next_step = item.review_trigger;
      } else {
        disposition = "queued-after-structural-prerequisites";
        next_step = item.review_trigger;
      }
      const scaffolder_readiness = item.maturity !== "active"
        ? item.maturity === "candidate" ? "REFUSED_CANDIDATE"
          : item.maturity === "deferred" ? "REFUSED_DEFERRED"
            : "REFUSED_SUPERSEDED"
        : item.mapping_status === "candidate-mapped"
          ? "REFUSED_CANDIDATE_MAPPING" : "REFUSED_UNMAPPED";
      return Object.freeze({
        meta_type_id: item.meta_type_id,
        label: item.label,
        category: item.category,
        maturity: item.maturity,
        mapping_status: item.mapping_status,
        architecture_type_id: item.architecture_type_id,
        disposition,
        bounded_evidence: proof?.[1] ?? null,
        scaffolder_readiness,
        queue_position: orderedQueue.indexOf(item.meta_type_id) >= 0
          ? orderedQueue.indexOf(item.meta_type_id) + 1 : null,
        next_step,
        owner_route: item.owner_route,
        authority_effect: "none",
      });
    });
  const unique = new Set(items.map(({ meta_type_id: id }) => id));
  if (unique.size !== 25) throw new Error("FACTORY_READINESS_ID_ACCOUNTING_INVALID");
  const body = Object.freeze({
    schema_version: "MetaTypeFactoryReadinessMatrix/v1",
    status: "non-authorizing-read-model",
    source_projection: Object.freeze({
      path: sourcePath,
      sha256: sha256(sourceBytes),
      status: source.status,
    }),
    counts: Object.freeze({
      total: items.length,
      bounded_proof_complete: items.filter(({ disposition }) =>
        disposition === "bounded-proof-complete").length,
      mapping_prerequisite: items.filter(({ disposition }) =>
        disposition === "mapping-prerequisite").length,
      queued: items.filter(({ disposition }) =>
        disposition === "queued-after-structural-prerequisites").length,
      owner_admission_required: items.filter(({ disposition }) =>
        disposition === "owner-admission-required").length,
      owner_disposition_required: items.filter(({ disposition }) =>
        disposition === "owner-disposition-required").length,
      tombstone: items.filter(({ disposition }) => disposition === "tombstone").length,
      scaffolder_ready: items.filter(({ scaffolder_readiness }) =>
        scaffolder_readiness === "READY").length,
    }),
    ordered_queue: Object.freeze(orderedQueue),
    meta_types: Object.freeze(items),
    claim_ceiling: "queue and readiness projection only; it does not admit map promote implement release or deploy any meta-type",
    authority_effect: "none",
  });
  return Object.freeze({ ...body, matrix_sha256: sha256(JSON.stringify(body)) });
};

if (process.argv.includes("--write")) {
  buildReadinessMatrix().then(async (matrix) => {
    const output = resolve(repositoryRoot, outputPath);
    await mkdir(dirname(output), { recursive: true });
    await writeFile(output, `${JSON.stringify(matrix, null, 2)}\n`, {
      encoding: "utf8", flag: "wx",
    });
    process.stdout.write(`${JSON.stringify({
      status: "pass", output, count: matrix.meta_types.length,
      matrix_sha256: matrix.matrix_sha256, authority_effect: "none",
    })}\n`);
  }).catch((error) => {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 1;
  });
}
