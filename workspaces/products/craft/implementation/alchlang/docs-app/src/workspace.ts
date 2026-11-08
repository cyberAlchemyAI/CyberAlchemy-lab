export const defaultWorkspaceSource = `domain customer-approval "Customer approval"
owner customer-domain-owner
logic sfol-v1

entity Customer:
  customerId: identifier required
  status: string required
  amount: decimal required

actor CreditOperator

rule approved-release:
  status == "approved"

boundary credit-release-authority:
  owner customer-domain-owner

permission release-credit:
  actor CreditOperator
  action ReleaseCredit
  when approved-release
  boundary credit-release-authority

action ReleaseCredit:
  actor CreditOperator
  subject Customer
  input amount
  requires approved-release
  permission release-credit
  boundary credit-release-authority
  emits credit-released

event credit-released:
  subject Customer
  payload customerId, amount
  boundary credit-release-authority`;

export const workspaceCommands = {
  check: "domainspec check workspace.alch",
  build: "domainspec build workspace.alch --out generated",
  patterns: "domainspec patterns --available",
  run: `domainspec run workspace.alch ReleaseCredit --actor CreditOperator --facts '{"customerId":"c-1","status":"approved","amount":100}' --grant credit-release-authority`,
} as const;

export type WorkspaceResult = {
  command: string;
  status: "success" | "error" | "info";
  output: string;
};

async function digest(source: string): Promise<string> {
  const bytes = new TextEncoder().encode(source.replace(/\r\n/g, "\n"));
  const hash = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(hash)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

function json(value: unknown) {
  return JSON.stringify(value, null, 2);
}

export async function runWorkspaceCommand(command: string, source: string): Promise<WorkspaceResult> {
  const normalized = command.trim().replace(/\s+/g, " ");
  if (!normalized) return { command, status: "info", output: "Type help to list browser-sandbox commands." };
  if (normalized === "help") {
    return {
      command,
      status: "info",
      output: ["Fixed-example browser simulation; no compiler or action executes:", workspaceCommands.check, workspaceCommands.build, workspaceCommands.patterns, workspaceCommands.run, "clear"].join("\n"),
    };
  }

  if (normalized === workspaceCommands.patterns) {
    return {
      command,
      status: "info",
      output: json({
        illustrated_patterns: [
          { pattern_id: "operation-port", availability: "available", generated_artifacts: ["domain.tools.ts"] },
          { pattern_id: "transactional-outbox", availability: "available", generated_artifacts: ["domain.outbox.port.ts", "domain.outbox.sqlite.ts", "domain.outbox.migration.sql", "domain.outbox.worker.ts", "domain.outbox.provider.ts", "domain.outbox.test.ts", "domain.generation-manifest.json"] },
        ],
        authority_effect: "none",
        execution_surface: "browser-fixed-simulation",
        claim_ceiling: "fixed-example-only-no-compiler-or-runtime",
      }),
    };
  }

  if (source !== defaultWorkspaceSource) return { command, status: "error", output: "FIXED_EXAMPLE_ONLY: this browser simulation cannot validate edited source; use the installed CLI" };
  const sourceDigest = await digest(source);

  if (normalized === workspaceCommands.check) {
    return {
      command,
      status: "info",
      output: json({
        simulation_status: "illustrated-check",
        source: "workspace.alch",
        domain_id: "customer-approval",
        source_digest: sourceDigest,
        authority_effect: "none",
        execution_surface: "browser-fixed-simulation",
        claim_ceiling: "fixed-example-only-no-compiler-or-runtime",
      }),
    };
  }

  if (normalized === workspaceCommands.build) {
    return {
      command,
      status: "info",
      output: json({
        simulation_status: "illustrated-build",
        domain_id: "customer-approval",
        illustrated_files: ["domain.carrier.json", "domain.types.ts", "domain.schema.ts", "domain.machine.ts", "domain.events.ts", "domain.operations.ts", "domain.workflows.ts", "domain.interfaces.ts", "domain.tools.ts", "domain.graph.json", "domain.test-obligations.json", "traceability.json", "unsupported-residue.json", "manifest.json"],
        source_digest: sourceDigest,
        authority_effect: "none",
        execution_surface: "browser-fixed-simulation",
        claim_ceiling: "fixed-example-only-no-compiler-or-runtime",
      }),
    };
  }

  if (command.trim() === workspaceCommands.run || command.trim() === workspaceCommands.run.replace('"approved"', '"pending"')) {
    const illustratedApproval = command.trim() === workspaceCommands.run;
    return {
      command,
      status: "info",
      output: json({
        simulation_status: illustratedApproval ? "illustrated-approval" : "illustrated-denial",
        action_id: "ReleaseCredit",
        illustrated_outcome: illustratedApproval ? "would-complete" : "would-deny",
        illustrated_events: illustratedApproval ? ["credit-released"] : [],
        illustrated_rule_results: { "approved-release": illustratedApproval },
        authority_effect: "none",
        execution_surface: "browser-fixed-simulation",
        claim_ceiling: "fixed-example-only-no-compiler-or-runtime",
      }),
    };
  }

  if (normalized.startsWith("domainspec run workspace.alch ")) return { command, status: "error", output: "FIXED_COMMAND_ONLY: this browser simulation supports only the two illustrated action inputs; use the installed CLI" };

  return { command, status: "error", output: `COMMAND_UNSUPPORTED: ${normalized}\nType help for available commands.` };
}
