import {existsSync, readFileSync, readdirSync, rmdirSync} from "node:fs";
import {describe, expect, it} from "vitest";
import {runEventParity} from "../../acceptance/event/wp-rmt-002/replay/run-event-parity.js";

const cargoRoot = "projects/domainspec-v2/development/remaining-meta-types/runs/event/cargo-target";
const removeWhenEmpty = async () => {
  for (let index = 0; index < 300; index++) {
    if (!existsSync(cargoRoot)) return;
    if (readdirSync(cargoRoot).length === 0) { rmdirSync(cargoRoot); return; }
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error("RMT_EVENT_FACTORY_CARGO_ROOT_NOT_EMPTY");
};

describe("WP-RMT-002 Event factory candidate fixture", () => {
  it("executes exactly three direct unregistered providers under the full S1 split", async () => {
    const fixture = JSON.parse(readFileSync("projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/rmt-event-wp-rmt-002.request.json", "utf8"));
    expect(fixture.provider_ids).toEqual(["event-typescript-v1", "event-python-v1", "event-rust-v1"]);
    expect(fixture.provider_registration_status).toBe("unregistered");
    expect(fixture.semantic_plan_epoch_id).toBe("WP-RMT-002/S1/2026-08-16");
    expect(fixture.s1_proof_owner_split).toEqual({"RMT-EVENT-006": 7, "RMT-EVENT-007": 2});
    const result = await runEventParity();
    expect(result).toMatchObject({result: "pass", provider_ids: fixture.provider_ids, provider_attempt_count: 12, recovery_replay_stable: true, non_idempotent_retry_rejected_by_all_providers: true, parity_receipt: {sha256: "17fbbf95a213973cdd08d30f44f37124696f7634aaa049d28af912b5201d6053"}});
    await removeWhenEmpty();
  }, 120_000);
});
