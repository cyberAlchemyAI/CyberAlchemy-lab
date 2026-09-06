import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  BODY_WAR_RUNTIME_ARTIFACTS,
  BODY_WAR_RUNTIME_COMPATIBILITY,
  BODY_WAR_RUNTIME_EVIDENCE_LANE,
  BODY_WAR_RUNTIME_SOURCE_MODE,
  decodeBodyWarRuntimeContractFamily,
  decodeBodyWarRuntimeProjectionResult,
  decodeBodyWarRuntimeSnapshot,
  type BodyWarRuntimeProjectionResult,
  type BodyWarRuntimeSnapshot,
} from "../contracts/body-war-runtime-snapshot.js";

type JsonObject = Record<string, unknown>;

const thisDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(thisDir, "..");
const snapshotSchema = resolve(
  packageRoot,
  "contracts/body-war-runtime-snapshot.schema.json",
);
const projectionSchema = resolve(
  packageRoot,
  "contracts/body-war-runtime-projection-result.schema.json",
);

function goldenSnapshot(): BodyWarRuntimeSnapshot {
  return {
    schema_version: "domainspec.orodi.body-war-runtime-snapshot/v1",
    snapshot_id: "bw-runtime-snapshot-001",
    run_id: "bw-canary-run-001",
    captured_at: "2026-08-27T00:01:11Z",
    source_mode: BODY_WAR_RUNTIME_SOURCE_MODE,
    evidence_lane: BODY_WAR_RUNTIME_EVIDENCE_LANE,
    runtime_admission: "denied",
    raw_evidence_pack_sha256: "a".repeat(64),
    compatibility: {
      docker_engine_version: BODY_WAR_RUNTIME_COMPATIBILITY.docker_engine_version,
      docker_compose_version: BODY_WAR_RUNTIME_COMPATIBILITY.docker_compose_version,
      platform: BODY_WAR_RUNTIME_COMPATIBILITY.platform,
    },
    artifacts: {
      stable_body_war_image_id: BODY_WAR_RUNTIME_ARTIFACTS.body_war_image_id,
      candidate_body_war_image_id: BODY_WAR_RUNTIME_ARTIFACTS.body_war_image_id,
      gateway_image_id: "sha256:" + "b".repeat(64),
      prometheus_image_id: BODY_WAR_RUNTIME_ARTIFACTS.prometheus_image_id,
    },
    provenance: {
      fault_origin: "experiment-gateway",
      application_bytes_equal: true,
    },
    timing: {
      fault_window: {
        started_at: "2026-08-27T00:00:00Z",
        ended_at: "2026-08-27T00:00:45Z",
        started_monotonic_ms: 1_000,
        ended_monotonic_ms: 46_000,
        duration_ms: 45_000,
      },
      evaluation_window: {
        started_at: "2026-08-27T00:00:10Z",
        ended_at: "2026-08-27T00:00:40Z",
        started_monotonic_ms: 11_000,
        ended_monotonic_ms: 41_000,
        duration_ms: 30_000,
      },
      rollback_window: {
        started_at: "2026-08-27T00:00:45Z",
        ended_at: "2026-08-27T00:00:55Z",
        started_monotonic_ms: 46_000,
        ended_monotonic_ms: 56_000,
        duration_ms: 10_000,
      },
    },
    workload: {
      scheduled: 400,
      issued: 400,
      completed: 400,
      classified: 400,
      max_in_flight: 8,
      p99_issue_lateness_ms: 20,
      stable: {
        good: 360,
        bad: 0,
        total: 360,
      },
      candidate: {
        good: 0,
        bad: 40,
        total: 40,
      },
    },
    telemetry: {
      offered: 400,
      queued: 400,
      exported: 400,
      rejected: 0,
      dropped: 0,
      pending: 0,
      partial_success: 0,
    },
    decision: {
      evaluated_at: "2026-08-27T00:00:40Z",
      telemetry_complete: true,
      candidate_assessment: "unacceptable",
      decision: "rollback",
    },
    observer: {
      observed_at: "2026-08-27T00:00:56Z",
      restoration_verified: true,
      rollback_deadline_met: true,
      stable_image_unchanged: true,
      gateway_status_good_count: 20,
      direct_stable_good_count: 5,
      candidate_reference_denominator: {
        gateway_target: null,
        gateway_weight: 0,
        reference_gauge: 0,
        candidate_container: "absent",
        candidate_endpoint: "absent",
      },
    },
    teardown: {
      verified: true,
      verified_at: "2026-08-27T00:01:10Z",
      runtime_project_residue: {
        containers: 0,
        networks: 0,
        volumes: 0,
        endpoints: 0,
      },
      declared_preparation_residue: [
        "body-war-image",
        "gateway-image",
        "prometheus-image",
      ],
      evidence_residue_retained: true,
    },
    projection_ceiling: {
      observation_plane: "product",
      observation_mode: "simulation",
      runtime_admitted_observation_ids: [],
      eligible_control_ids: [],
      runtime_admission: "denied",
      authority_effect: "none",
    },
    authority_effect: "none",
  };
}

function goldenProjection(
  snapshot = goldenSnapshot(),
): BodyWarRuntimeProjectionResult {
  return {
    schema_version:
      "domainspec.orodi.body-war-runtime-projection-result/v1",
    projector_id: "domainspec.orodi.body-war-runtime-projector",
    projector_version: "1.0.0-candidate-local",
    evidence_lane: BODY_WAR_RUNTIME_EVIDENCE_LANE,
    projection_id: "bw-runtime-projection-001",
    snapshot_id: snapshot.snapshot_id,
    raw_evidence_pack_sha256: snapshot.raw_evidence_pack_sha256,
    source_mode: BODY_WAR_RUNTIME_SOURCE_MODE,
    projected_at: "2026-08-27T00:01:12Z",
    verdict: "projected",
    observation_id: "bw-runtime-observation-001",
    observation_plane: "product",
    observation_mode: "simulation",
    runtime_admitted_observation_ids: [],
    eligible_control_ids: [],
    eligibility_decision: "replay-only",
    runtime_admission: "denied",
    findings: [],
    authority_effect: "none",
  };
}

function clone<T>(value: T): T {
  return structuredClone(value);
}

function asObject(value: unknown): JsonObject {
  assert.ok(
    typeof value === "object" && value !== null && !Array.isArray(value),
    "expected object",
  );
  return value as JsonObject;
}

function replace(root: JsonObject, pointer: string, value: unknown): void {
  const segments = pointer.split("/").slice(1);
  assert.ok(segments.length > 0, "root replacement is not supported");
  let parent = root;
  for (const segment of segments.slice(0, -1)) {
    parent = asObject(parent[segment]);
  }
  parent[segments.at(-1)!] = value;
}

function addField(
  root: JsonObject,
  pointer: string,
  key: string,
  value: unknown,
): void {
  let parent = root;
  for (const segment of pointer.split("/").slice(1)) {
    parent = asObject(parent[segment]);
  }
  parent[key] = value;
}

function schemaStatus(instance: unknown, schemaPath: string): number | null {
  const scratch = mkdtempSync(join(tmpdir(), "body-war-runtime-schema-"));
  try {
    const instancePath = join(scratch, "instance.json");
    writeFileSync(instancePath, JSON.stringify(instance, null, 2) + "\n");
    const checked = spawnSync(
      "python3",
      ["-m", "jsonschema", "-i", instancePath, schemaPath],
      { encoding: "utf8" },
    );
    assert.notEqual(
      checked.status,
      null,
      "jsonschema did not exit: " + checked.stdout + checked.stderr,
    );
    return checked.status;
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
}

test("the two contract schemas are valid closed JSON Schema documents", () => {
  const snapshot = JSON.parse(readFileSync(snapshotSchema, "utf8")) as JsonObject;
  const projection = JSON.parse(
    readFileSync(projectionSchema, "utf8"),
  ) as JsonObject;
  assert.equal(snapshot.additionalProperties, false);
  assert.equal(projection.additionalProperties, false);
  assert.equal(schemaStatus(goldenSnapshot(), snapshotSchema), 0);
  assert.equal(schemaStatus(goldenProjection(), projectionSchema), 0);
});

test("golden snapshot and projected result decode as one denied-admission family", () => {
  const snapshot = goldenSnapshot();
  const projection = goldenProjection(snapshot);
  const before = clone({ snapshot, projection });
  const decodedSnapshot = decodeBodyWarRuntimeSnapshot(snapshot);
  const decodedProjection = decodeBodyWarRuntimeProjectionResult(projection);
  const family = decodeBodyWarRuntimeContractFamily(snapshot, projection);
  assert.equal(decodedSnapshot.verdict, "pass", JSON.stringify(decodedSnapshot.findings));
  assert.equal(decodedProjection.verdict, "pass", JSON.stringify(decodedProjection.findings));
  assert.equal(family.verdict, "pass", JSON.stringify(family.findings));
  if (family.verdict === "pass") {
    assert.equal(family.value.snapshot.runtime_admission, "denied");
    assert.equal(family.value.snapshot.authority_effect, "none");
    assert.deepEqual(
      family.value.snapshot.projection_ceiling.runtime_admitted_observation_ids,
      [],
    );
    assert.deepEqual(family.value.projection_result.eligible_control_ids, []);
  }
  assert.deepEqual({ snapshot, projection }, before, "decoder mutated its inputs");
});

test("a closed rejected projection result remains non-authoritative", () => {
  const rejected = {
    ...goldenProjection(),
    verdict: "rejected",
    observation_id: null,
    findings: [
      {
        code: "BODY_WAR_RUNTIME_PROJECTOR_REJECTED",
        path: "/snapshot",
        detail: "snapshot could not be projected",
      },
    ],
  };
  const decoded = decodeBodyWarRuntimeProjectionResult(rejected);
  assert.equal(decoded.verdict, "pass", JSON.stringify(decoded.findings));
  assert.equal(schemaStatus(rejected, projectionSchema), 0);
  if (decoded.verdict === "pass") {
    assert.equal(decoded.value.runtime_admission, "denied");
    assert.equal(decoded.value.authority_effect, "none");
  }
});

const snapshotCases: readonly Readonly<{
  caseId: string;
  mutate: (snapshot: JsonObject) => void;
  expectedCode: string;
  schemaRejects: boolean;
}>[] = [
  {
    caseId: "unknown-field",
    mutate: (snapshot) => addField(snapshot, "", "unexpected", true),
    expectedCode: "BODY_WAR_RUNTIME_UNKNOWN_FIELD",
    schemaRejects: true,
  },
  {
    caseId: "malformed-pack-digest",
    mutate: (snapshot) =>
      replace(snapshot, "/raw_evidence_pack_sha256", "ABC"),
    expectedCode: "BODY_WAR_RUNTIME_DIGEST_INVALID",
    schemaRejects: true,
  },
  {
    caseId: "compatibility-mismatch",
    mutate: (snapshot) =>
      replace(snapshot, "/compatibility/docker_engine_version", "28.0.2"),
    expectedCode: "BODY_WAR_RUNTIME_COMPATIBILITY_MISMATCH",
    schemaRejects: true,
  },
  {
    caseId: "candidate-denominator-drift",
    mutate: (snapshot) =>
      replace(
        snapshot,
        "/observer/candidate_reference_denominator/gateway_weight",
        0.1,
      ),
    expectedCode: "BODY_WAR_RUNTIME_DENOMINATOR_DRIFT",
    schemaRejects: true,
  },
  {
    caseId: "runtime-admission-forgery",
    mutate: (snapshot) => replace(snapshot, "/runtime_admission", "admitted"),
    expectedCode: "BODY_WAR_RUNTIME_ADMISSION_FORGED",
    schemaRejects: true,
  },
  {
    caseId: "authority-forgery",
    mutate: (snapshot) => replace(snapshot, "/authority_effect", "promote"),
    expectedCode: "BODY_WAR_RUNTIME_AUTHORITY_FORGED",
    schemaRejects: true,
  },
  {
    caseId: "utc-monotonic-pair-drift",
    mutate: (snapshot) =>
      replace(snapshot, "/timing/fault_window/duration_ms", 44_999),
    expectedCode: "BODY_WAR_RUNTIME_TIME_PAIR_MISMATCH",
    schemaRejects: false,
  },
  {
    caseId: "rollback-overlaps-fault-window",
    mutate: (snapshot) => {
      replace(
        snapshot,
        "/timing/rollback_window/started_at",
        "2026-08-27T00:00:44Z",
      );
      replace(
        snapshot,
        "/timing/rollback_window/started_monotonic_ms",
        45_000,
      );
      replace(snapshot, "/timing/rollback_window/duration_ms", 11_000);
    },
    expectedCode: "BODY_WAR_RUNTIME_WINDOW_OVERLAP",
    schemaRejects: false,
  },
  {
    caseId: "cohort-accounting-drift",
    mutate: (snapshot) => replace(snapshot, "/workload/candidate/total", 39),
    expectedCode: "BODY_WAR_RUNTIME_ACCOUNTING_DRIFT",
    schemaRejects: false,
  },
  {
    caseId: "application-image-mismatch",
    mutate: (snapshot) =>
      replace(
        snapshot,
        "/artifacts/candidate_body_war_image_id",
        "sha256:" + "c".repeat(64),
      ),
    expectedCode: "BODY_WAR_RUNTIME_APPLICATION_BYTES_MISMATCH",
    schemaRejects: true,
  },
  {
    caseId: "event-after-capture",
    mutate: (snapshot) =>
      replace(snapshot, "/captured_at", "2026-08-27T00:01:00Z"),
    expectedCode: "BODY_WAR_RUNTIME_FUTURE_TIMESTAMP",
    schemaRejects: false,
  },
  {
    caseId: "non-finite-counter",
    mutate: (snapshot) => replace(snapshot, "/workload/scheduled", Number.NaN),
    expectedCode: "BODY_WAR_RUNTIME_INTEGER_INVALID",
    schemaRejects: false,
  },
];

for (const hostileCase of snapshotCases) {
  test(hostileCase.caseId + " rejects deterministically", () => {
    const snapshot = clone(goldenSnapshot()) as unknown as JsonObject;
    hostileCase.mutate(snapshot);
    const before = clone(snapshot);
    const first = decodeBodyWarRuntimeSnapshot(snapshot);
    const second = decodeBodyWarRuntimeSnapshot(snapshot);
    assert.equal(first.verdict, "reject", hostileCase.caseId);
    assert.deepEqual(first, second, hostileCase.caseId + " was nondeterministic");
    assert.ok(
      first.findings.some(({ code }) => code === hostileCase.expectedCode),
      hostileCase.caseId +
        ": expected " +
        hostileCase.expectedCode +
        "; got " +
        first.findings.map(({ code }) => code).join(","),
    );
    assert.deepEqual(snapshot, before, hostileCase.caseId + " mutated input");
    assert.deepEqual(
      first.findings,
      [...first.findings].sort((left, right) => {
        const a = left.path + "\u0000" + left.code + "\u0000" + left.detail;
        const b = right.path + "\u0000" + right.code + "\u0000" + right.detail;
        return a < b ? -1 : a > b ? 1 : 0;
      }),
    );
    if (hostileCase.schemaRejects) {
      assert.notEqual(schemaStatus(snapshot, snapshotSchema), 0);
    }
  });
}

for (const hostileCase of [
  {
    caseId: "projection-runtime-admission-forgery",
    pointer: "/runtime_admission",
    value: "admitted",
    expectedCode: "BODY_WAR_RUNTIME_ADMISSION_FORGED",
  },
  {
    caseId: "projection-authority-forgery",
    pointer: "/authority_effect",
    value: "promote",
    expectedCode: "BODY_WAR_RUNTIME_AUTHORITY_FORGED",
  },
  {
    caseId: "projection-eligible-control-forgery",
    pointer: "/eligible_control_ids",
    value: ["C12"],
    expectedCode: "BODY_WAR_RUNTIME_ADMISSION_FORGED",
  },
] as const) {
  test(hostileCase.caseId + " rejects in decoder and schema", () => {
    const projection = clone(goldenProjection()) as unknown as JsonObject;
    replace(projection, hostileCase.pointer, hostileCase.value);
    const first = decodeBodyWarRuntimeProjectionResult(projection);
    const second = decodeBodyWarRuntimeProjectionResult(projection);
    assert.equal(first.verdict, "reject");
    assert.deepEqual(first, second);
    assert.ok(first.findings.some(({ code }) => code === hostileCase.expectedCode));
    assert.notEqual(schemaStatus(projection, projectionSchema), 0);
  });
}

test("snapshot/result identity and raw-pack substitution reject at the family boundary", () => {
  for (const hostileCase of [
    {
      pointer: "/snapshot_id",
      value: "different-snapshot",
      expectedCode: "BODY_WAR_RUNTIME_SNAPSHOT_BINDING_MISMATCH",
    },
    {
      pointer: "/raw_evidence_pack_sha256",
      value: "c".repeat(64),
      expectedCode: "BODY_WAR_RUNTIME_RAW_PACK_BINDING_MISMATCH",
    },
    {
      pointer: "/projected_at",
      value: "2026-08-27T00:01:00Z",
      expectedCode: "BODY_WAR_RUNTIME_TIMESTAMP_ORDER",
    },
  ] as const) {
    const snapshot = goldenSnapshot();
    const projection = clone(goldenProjection(snapshot)) as unknown as JsonObject;
    replace(projection, hostileCase.pointer, hostileCase.value);
    const result = decodeBodyWarRuntimeContractFamily(snapshot, projection);
    assert.equal(result.verdict, "reject");
    assert.ok(result.findings.some(({ code }) => code === hostileCase.expectedCode));
  }
});
