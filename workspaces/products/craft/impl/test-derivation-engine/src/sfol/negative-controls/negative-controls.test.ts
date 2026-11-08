import { describe, expect, it } from "vitest";

import { digestSfolValue } from "../cases/index.js";
import {
  evaluateNegativeControls,
  NEGATIVE_CONTROL_PROFILE_VERSION,
  type FaultModel,
} from "./index.js";

const seams = ["semantic", "derivation", "binding", "observation", "lineage", "scope", "provider"] as const;

function faultModels(): FaultModel[] {
  return seams.map((seam) => ({
    fault_model_id: `fault.${seam}`,
    seam,
    fault: `${seam} identity is changed`,
    expected_detector_id: `detector.${seam}`,
    expected_reason: `changed-${seam}`,
    required: true,
  }));
}

describe("SFOL seam-level negative controls", () => {
  it("builds a deterministic passing detection matrix across every required seam", () => {
    const models = faultModels();
    const controls = models.map((model) => ({ control_id: `control.${model.seam}`, fault_model_id: model.fault_model_id, original_digest: "a".repeat(64), changed_digest: model.seam.padEnd(64, "b"), applicability: "applicable" as const }));
    const observations = models.map((model) => ({ control_id: `control.${model.seam}`, detector_id: model.expected_detector_id, outcome: "detected" as const, reason: model.expected_reason }));
    const first = evaluateNegativeControls({ profile_version: NEGATIVE_CONTROL_PROFILE_VERSION, fault_models: models, controls, observations });
    const second = evaluateNegativeControls({ profile_version: NEGATIVE_CONTROL_PROFILE_VERSION, fault_models: [...models].reverse(), controls: [...controls].reverse(), observations: [...observations].reverse() });
    expect(first.ok).toBe(true);
    expect(second.ok).toBe(true);
    if (!first.ok || !second.ok) return;
    expect(first.value.result).toBe("pass");
    expect(first.value.rows.map(({ seam }) => seam).sort()).toEqual([...seams].sort());
    const { receipt_digest: _receiptDigest, ...unsigned } = first.value;
    expect(first.value.receipt_digest).toBe(digestSfolValue(unsigned));
    expect(first.value.rows).toEqual(second.value.rows);
  });

  it("fails the gate when a required control survives", () => {
    const model = faultModels()[0]!;
    const result = evaluateNegativeControls({
      profile_version: NEGATIVE_CONTROL_PROFILE_VERSION,
      fault_models: [model],
      controls: [{ control_id: "control.semantic", fault_model_id: model.fault_model_id, original_digest: "a".repeat(64), changed_digest: "b".repeat(64), applicability: "applicable" }],
      observations: [{ control_id: "control.semantic", detector_id: model.expected_detector_id, outcome: "not-detected", reason: "no-diagnostic" }],
    });
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.value).toMatchObject({ result: "fail", surviving_count: 1 });
  });

  it("rejects incomplete observation closure", () => {
    const model = faultModels()[0]!;
    expect(evaluateNegativeControls({
      profile_version: NEGATIVE_CONTROL_PROFILE_VERSION,
      fault_models: [model],
      controls: [{ control_id: "control.semantic", fault_model_id: model.fault_model_id, original_digest: "a".repeat(64), changed_digest: "b".repeat(64), applicability: "applicable" }],
      observations: [],
    })).toMatchObject({ ok: false, diagnostics: [{ code: "SFOL_NEGATIVE_CONTROL_OBSERVATION_MISSING" }] });
  });

  it("keeps unsupported required controls explicit and non-passing", () => {
    const model = faultModels()[0]!;
    const result = evaluateNegativeControls({
      profile_version: NEGATIVE_CONTROL_PROFILE_VERSION,
      fault_models: [model],
      controls: [{ control_id: "control.unsupported", fault_model_id: model.fault_model_id, original_digest: "a".repeat(64), changed_digest: "b".repeat(64), applicability: "unsupported" }],
      observations: [{ control_id: "control.unsupported", detector_id: model.expected_detector_id, outcome: "indeterminate", reason: "adapter unavailable" }],
    });
    expect(result).toMatchObject({ ok: true, value: { result: "fail", unsupported_count: 1, rows: [{ classification: "unsupported" }] } });
  });
});
