#!/usr/bin/env node
import {execFileSync} from "node:child_process";
import {resolve} from "node:path";
import {createCodexAppServerWrapper, loadRepositoryProfile, protocolBindingCheck, recoverReasoningStateLedger, runStdioProxy} from "../index.mjs";

function argument(name) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : null;
}

const configArg = argument("--config");
const repositoryRootArg = argument("--repository-root");
const reasoningStateLogArg = argument("--reasoning-state-log");
const codexCommandArg = argument("--codex-command") ?? "codex";
if (!configArg || !repositoryRootArg) {
  process.stderr.write("Usage: are-codex-app-server --config <profile.json> --repository-root <repository> [--codex-command <path>] [--reasoning-state-log <events.jsonl>]\n");
  process.exitCode = 2;
} else {
  const repositoryRoot = resolve(repositoryRootArg);
  const loaded = loadRepositoryProfile(resolve(configArg), repositoryRoot);
  if (!loaded.ok) {
    process.stderr.write(`${JSON.stringify(loaded)}\n`);
    process.exitCode = 3;
  } else {
    let version = "unavailable";
    try {
      version = execFileSync(codexCommandArg, ["--version"], {encoding: "utf8"}).trim();
    } catch {
      version = "unavailable";
    }
    const protocol = protocolBindingCheck(loaded.value.protocol_binding, version);
    if (!protocol.ok) {
      process.stderr.write(`${JSON.stringify(protocol)}\n`);
      process.exitCode = 4;
    } else {
      const recovered = reasoningStateLogArg
        ? recoverReasoningStateLedger({path: resolve(reasoningStateLogArg), ledger_id: loaded.value.reasoning_state.ledger_id})
        : null;
      if (recovered && !recovered.ok) {
        process.stderr.write(`${JSON.stringify(recovered)}\n`);
        process.exitCode = 5;
      } else {
        const wrapper = createCodexAppServerWrapper({
          loaded_profile: loaded.value,
          decision_profile: loaded.decision_profile,
          definition_catalog: loaded.definition_catalog,
          ontology_snapshot: loaded.ontology_snapshot,
          source_snapshot: loaded.source_snapshot,
          context_source_provider: loaded.context_source_provider,
          semantic_profile: loaded.semantic_profile,
          reasoning_ledger: recovered?.ledger,
        });
        runStdioProxy({wrapper, command: codexCommandArg});
      }
    }
  }
}
