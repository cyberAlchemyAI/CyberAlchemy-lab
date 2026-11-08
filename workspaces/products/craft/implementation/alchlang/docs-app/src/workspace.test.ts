import { describe, expect, it } from "vitest";
import { defaultWorkspaceSource, runWorkspaceCommand, workspaceCommands } from "./workspace";

describe("browser workspace", () => {
  it("illustrates a check without claiming compiler validation", async () => {
    const result = await runWorkspaceCommand(workspaceCommands.check, defaultWorkspaceSource);
    expect(result.status).toBe("info");
    expect(result.output).toContain('"simulation_status": "illustrated-check"');
    expect(result.output).toContain('"execution_surface": "browser-fixed-simulation"');
    expect(result.output).toContain('"claim_ceiling": "fixed-example-only-no-compiler-or-runtime"');
  });

  it("illustrates artifacts without claiming a build or generated output", async () => {
    const result = await runWorkspaceCommand(workspaceCommands.build, defaultWorkspaceSource);
    expect(result.status).toBe("info");
    expect(result.output).toContain('"simulation_status": "illustrated-build"');
    expect(result.output).toContain('"illustrated_files"');
    expect(result.output).not.toContain('"output": "virtual://generated"');
    expect(result.output).toContain('"domain.test-obligations.json"');
    expect(result.output).toContain('"domain.operations.ts"');
    expect(result.output).toContain('"domain.workflows.ts"');
    expect(result.output).toContain('"domain.interfaces.ts"');
  });

  it("illustrates operation patterns without claiming execution", async () => {
    const result = await runWorkspaceCommand(workspaceCommands.patterns, defaultWorkspaceSource);
    expect(result.status).toBe("info");
    expect(result.output).toContain('"pattern_id": "transactional-outbox"');
    expect(result.output).toContain('"authority_effect": "none"');
  });

  it("illustrates both fixed action outcomes without executing either", async () => {
    const passed = await runWorkspaceCommand(workspaceCommands.run, defaultWorkspaceSource);
    const denied = await runWorkspaceCommand(workspaceCommands.run.replace('"approved"', '"pending"'), defaultWorkspaceSource);
    expect(passed.status).toBe("info");
    expect(passed.output).toContain('"illustrated_outcome": "would-complete"');
    expect(denied.status).toBe("info");
    expect(denied.output).toContain('"illustrated_outcome": "would-deny"');
  });

  it("never returns a green check, build, or action for edited source", async () => {
    const edited = defaultWorkspaceSource.replace('status == "approved"', 'status == "pending"');
    for (const command of [workspaceCommands.check, workspaceCommands.build, workspaceCommands.run]) {
      const result = await runWorkspaceCommand(command, edited);
      expect(result).toMatchObject({ status: "error" });
      expect(result.output).toContain("FIXED_EXAMPLE_ONLY");
    }
  });

  it("rejects arbitrary action commands rather than interpreting them with fixed approvals", async () => {
    const altered = workspaceCommands.run.replace("ReleaseCredit", "OtherAction");
    const result = await runWorkspaceCommand(altered, defaultWorkspaceSource);
    expect(result).toMatchObject({ status: "error" });
    expect(result.output).toContain("FIXED_COMMAND_ONLY");
  });
});
