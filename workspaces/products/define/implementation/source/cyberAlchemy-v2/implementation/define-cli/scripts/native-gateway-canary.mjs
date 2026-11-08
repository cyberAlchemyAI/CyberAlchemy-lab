#!/usr/bin/env node
import assert from "node:assert/strict";
import {spawn, spawnSync} from "node:child_process";
import {createHash} from "node:crypto";
import {existsSync, mkdtempSync, mkdirSync, readFileSync, realpathSync, rmSync, writeFileSync} from "node:fs";
import {createServer} from "node:http";
import {tmpdir} from "node:os";
import {resolve} from "node:path";

import {createAppServerDefineAgent} from "../src/app-server-agent.mjs";
import {createCodexAppServerWrapper, createPersistentGateway, loadRepositoryProfile} from
  "../../agent-reasoning-engine/packages/codex-app-server-wrapper/index.mjs";

const checkoutRoot = resolve(import.meta.dirname, "../../..");
const repositoryRoot = resolve(checkoutRoot, "..");
const wrapperRoot = resolve(checkoutRoot, "implementation/agent-reasoning-engine/packages/codex-app-server-wrapper");
const report = {schema_version: "cav2.define-native-gateway-canary/v1", status: "FAIL", authority_effect: "none",
  provider: "loopback-fixed-response", external_model_calls: 0, current_desktop_task_touched: false};
const responseTurn = {
  schema_version: "cav2.define-conversation-turn/v2", phase: "discover", message: "Tell me more about the subject.",
  question: "Who will use it?", scope_ready: false, covered_dimensions: [],
  scope: {language: {user_phrases: [], terms: [], distinctions: [], relationships: [], constraints: [], owners: [], open_questions: []}},
  options: [],
};
let scratch;
let provider;
let gateway;
let agent;
let child;
let stderr = "";
const requests = [];

function responseEvents(id, text) {
  const item = {id: `msg_${id}`, type: "message", status: "completed", role: "assistant",
    content: [{type: "output_text", text, annotations: []}]};
  const events = [
    {type: "response.created", response: {id, object: "response", status: "in_progress", output: []}},
    {type: "response.output_item.added", output_index: 0, item: {...item, status: "in_progress"}},
    {type: "response.content_part.added", item_id: item.id, output_index: 0, content_index: 0,
      part: {type: "output_text", text: "", annotations: []}},
    {type: "response.output_text.delta", item_id: item.id, output_index: 0, content_index: 0, delta: text},
    {type: "response.output_item.done", output_index: 0, item},
    {type: "response.completed", response: {id, object: "response", status: "completed", output: [item],
      usage: {input_tokens: 20, output_tokens: 20, total_tokens: 40, input_tokens_details: {cached_tokens: 0}}}},
  ];
  return events.map((event) => `event: ${event.type}\ndata: ${JSON.stringify(event)}\n\n`).join("");
}

try {
  assert.ok(process.argv[2] && process.argv[3], "Usage: native-gateway-canary.mjs <installed-codex-binary> <exact-version>");
  const binary = realpathSync(process.argv[2]);
  const version = spawnSync(binary, ["--version"], {encoding: "utf8", timeout: 5000});
  assert.equal(version.status, 0, "canary.host-version-command-failed");
  assert.equal(version.stdout.trim(), process.argv[3], "canary.host-version-drift");
  report.host = {path: binary, version: process.argv[3],
    sha256: createHash("sha256").update(readFileSync(binary)).digest("hex")};

  scratch = mkdtempSync(resolve(tmpdir(), "are-define-native-"));
  const configRoot = resolve(scratch, "codex-home");
  mkdirSync(configRoot);
  provider = createServer(async (request, response) => {
    try {
      assert.equal(request.method, "POST");
      assert.ok(request.url.endsWith("/responses"));
      const chunks = [];
      let bytes = 0;
      for await (const chunk of request) {
        bytes += chunk.length;
        assert.ok(bytes <= 2 * 1024 * 1024, "canary.provider-request-too-large");
        chunks.push(chunk);
      }
      const body = JSON.parse(Buffer.concat(chunks).toString("utf8"));
      requests.push(body);
      assert.equal(requests.length, 1, "canary.unexpected-provider-retry");
      response.writeHead(200, {"content-type": "text/event-stream"});
      response.end(responseEvents("resp_are_define_1", JSON.stringify(responseTurn)));
    } catch (error) {
      report.provider_error = error.message;
      response.writeHead(500);
      response.end("fixture rejected request");
    }
  });
  await new Promise((done) => provider.listen(0, "127.0.0.1", done));
  const endpoint = `http://127.0.0.1:${provider.address().port}/v1`;
  writeFileSync(resolve(configRoot, "config.toml"), `model_provider = "are_fixture"\nmodel = "are-fixture"\n[model_providers.are_fixture]\nname = "ARE local fixed response fixture"\nbase_url = ${JSON.stringify(endpoint)}\nwire_api = "responses"\nrequires_openai_auth = false\nrequest_max_retries = 0\nstream_max_retries = 0\n`, {mode: 0o600});

  const loaded = loadRepositoryProfile(resolve(wrapperRoot, "profiles/repository-v1.json"), repositoryRoot);
  assert.equal(loaded.ok, true, `canary.wrapper-profile-unavailable:${JSON.stringify(loaded.reason_codes)}`);
  gateway = createPersistentGateway({listen_path: resolve(scratch, "gateway.sock"),
    expected_codex_version: process.argv[3], backend: {mode: "direct-stdio", command: binary},
    spawn_impl: (command, args, options) => {
      child = spawn(command, args, {cwd: scratch, ...options, env: {...process.env, CODEX_HOME: configRoot}});
      child.stderr.on("data", (chunk) => { stderr = `${stderr}${chunk}`.slice(-8192); });
      return child;
    },
    wrapper_factory: () => createCodexAppServerWrapper({loaded_profile: loaded.value,
      decision_profile: loaded.decision_profile, definition_catalog: loaded.definition_catalog,
      ontology_snapshot: loaded.ontology_snapshot, source_snapshot: loaded.source_snapshot}),
  });
  await gateway.start();
  agent = createAppServerDefineAgent({repository_root: repositoryRoot, gateway_socket: resolve(scratch, "gateway.sock"),
    model: "are-fixture", define_entrypoint_selected: true});
  const turn = await agent.respond({mode: "discovery", user_input: "I am defining an archive",
    scope_confirmed: false});
  assert.equal(turn.question, responseTurn.question, "canary.define-response-not-parsed");
  assert.equal(requests.length, 1, "canary.provider-request-count");
  const body = requests[0];
  report.provider_wire = {structured_output: Boolean(body.text?.format || body.response_format),
    input_contains_user_phrase: JSON.stringify(body.input).includes("I am defining an archive")};
  assert.equal(report.provider_wire.input_contains_user_phrase, true, "canary.define-input-not-on-provider-wire");
  report.gateway_session = {consumer_id: gateway.inspect().sessions[0]?.consumer_id ?? null,
    backend_initialized: gateway.inspect().sessions[0]?.initialization_status === "complete"};
  assert.equal(report.gateway_session.consumer_id, "codex:define-cli", "canary.define-consumer-not-isolated");
  assert.equal(report.gateway_session.backend_initialized, true, "canary.backend-not-initialized");
  report.status = "PASS";
} catch (error) {
  report.error = error.message;
  report.error_code = error.code ?? null;
  report.error_details = error.details ?? null;
  report.host_stderr_tail = stderr;
  process.exitCode = 1;
} finally {
  await agent?.close().catch(() => {});
  await gateway?.close().catch(() => {});
  if (child && child.exitCode === null && child.signalCode === null) {
    child.kill("SIGTERM");
    await Promise.race([new Promise((done) => child.once("exit", done)), new Promise((done) => setTimeout(done, 2000))]);
    if (child.exitCode === null && child.signalCode === null) child.kill("SIGKILL");
  }
  if (provider) {
    provider.closeAllConnections();
    await new Promise((done) => provider.close(done));
  }
  if (scratch) rmSync(scratch, {recursive: true, force: true});
  report.teardown = {temporary_configuration_removed: scratch ? !existsSync(scratch) : null,
    native_child_reaped: child ? child.exitCode !== null || child.signalCode !== null : null};
  process.stdout.write(`${JSON.stringify(report)}\n`);
}
