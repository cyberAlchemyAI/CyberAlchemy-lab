import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const profilePath = "projects/domainspec-v2/impl/architecture-conformance/realizations/workflow/recovery-v1/profile.json";

describe("Workflow recovery three-language profile", () => {
  it("hash-closes all native targets, tests, and Workflow bindings", () => {
    const profile = JSON.parse(readFileSync(profilePath, "utf8"));
    expect(profile.language_profiles.map(({ language }: { language: string }) => language)).toEqual(["typescript", "python", "rust"]);
    for (const language of profile.language_profiles) {
      for (const role of ["target", "test", "workflow_binding"]) {
        const reference = language[role];
        const bytes = readFileSync(reference.path);
        expect(bytes.length, `${language.language}:${role}:size`).toBe(reference.size_bytes);
        expect(createHash("sha256").update(bytes).digest("hex"), `${language.language}:${role}:digest`).toBe(reference.sha256);
      }
    }
  });

  it("keeps compensation inside Workflow and preserves the durable-runtime boundary", () => {
    const profile = JSON.parse(readFileSync(profilePath, "utf8"));
    expect(profile).toMatchObject({
      meta_type_id: "DS-D1.9",
      adds_meta_type: false,
      relationship_contract: {
        source_type: "Workflow",
        relationship: "orchestrates",
        target_type: "Operation",
        new_relationship_verb: false,
        preflight_before_invocation: true,
      },
      claim_ceiling: {
        workflow_recovery_planning: true,
        exact_binding_preflight: true,
        in_process_invocation: true,
        durable_dispatch: false,
        claim: false,
        lease: false,
        durable_attempt: false,
        persisted_retry: false,
        terminal_disposition: false,
        restart_recovery: false,
      },
      authority_effect: "none",
    });
  });
});
