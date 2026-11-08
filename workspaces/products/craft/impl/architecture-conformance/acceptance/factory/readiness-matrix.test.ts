import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../..");

describe("non-authorizing remaining meta-type queue", () => {
  it("accounts for all 25 stable IDs without promoting candidate mappings", async () => {
    const matrix = JSON.parse(await readFile(resolve(repositoryRoot,
      "projects/domainspec-v2/development/meta-type-realization-factory/runs/MTF-029/readiness-matrix.json"), "utf8")) as {
      status: string;
      counts: Record<string, number>;
      ordered_queue: string[];
      meta_types: Array<{
        meta_type_id: string; disposition: string; scaffolder_readiness: string;
      }>;
    };
    expect(matrix.status).toBe("non-authorizing-read-model");
    expect(matrix.meta_types).toHaveLength(25);
    expect(new Set(matrix.meta_types.map(({ meta_type_id: id }) => id)).size).toBe(25);
    expect(matrix.counts).toEqual({
      total: 25,
      bounded_proof_complete: 3,
      mapping_prerequisite: 2,
      queued: 8,
      owner_admission_required: 9,
      owner_disposition_required: 2,
      tombstone: 1,
      scaffolder_ready: 0,
    });
    expect(matrix.ordered_queue.slice(0, 2)).toEqual(["DS-D1.1", "DS-D1.2"]);
    expect(matrix.meta_types.every(({ scaffolder_readiness }) =>
      scaffolder_readiness.startsWith("REFUSED_"))).toBe(true);
  });
});
