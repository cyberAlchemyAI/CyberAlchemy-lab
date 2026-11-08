import assert from "node:assert/strict";
import {createHash} from "node:crypto";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import test from "node:test";

import {containsPhrase, semanticContract, semanticKey} from "./consumer-runtime.mjs";
import {createModulePort} from "../../../../../../../implementation/agent-reasoning-engine/packages/module-port/index.mjs";
import {createSemanticTextFacade, semanticTextOutputValidators} from "../../../../../../../implementation/agent-reasoning-engine/packages/module-port/semantic-text.mjs";
import {createAlchSemanticAdapter} from "../../../../../../../implementation/agent-reasoning-engine/packages/module-port/alch-semantic-adapter.mjs";

const extensionRoot = import.meta.dirname;
const repositoryRoot = resolve(extensionRoot, "../../../../../../..");
const bindings = JSON.parse(readFileSync(resolve(extensionRoot, "consumer-bindings.json"), "utf8"));
const fixtures = JSON.parse(readFileSync(resolve(extensionRoot, "consumer-parity.fixtures.json"), "utf8"));
const sha256 = (path) => createHash("sha256").update(readFileSync(path)).digest("hex");

test("all declared consumers bind the same compiled semantic artifact", () => {
  assert.equal(bindings.binding_kind, "shared-compiled-artifact-with-are-module-port");
  assert.deepEqual(bindings.consumers.map((item) => item.consumer_id), [
    "define-language-quality", "router-signal-matching", "are-define-intake",
  ]);
  assert.equal(sha256(resolve(repositoryRoot, bindings.canonical_source.path)), bindings.canonical_source.sha256);
  assert.equal(sha256(resolve(repositoryRoot, bindings.compiled_runtime.path)), bindings.compiled_runtime.sha256);
  assert.equal(sha256(resolve(repositoryRoot, bindings.runtime_wrapper.path)), bindings.runtime_wrapper.sha256);
  for (const consumer of bindings.consumers) {
    const source = readFileSync(resolve(repositoryRoot, consumer.source), "utf8");
    if (consumer.integration === "direct-compiled-artifact") {
      assert.match(source, /semantic-contract-v1\/consumer-runtime\.mjs/);
    } else {
      assert.equal(consumer.integration, "injected-module-port");
      assert.doesNotMatch(source, /semantic-contract-v1\/consumer-runtime\.mjs/);
      assert.match(source, /module-port\/semantic-text\.mjs/);
      const adapterSource = readFileSync(resolve(repositoryRoot, consumer.adapter_source), "utf8");
      assert.match(adapterSource, /requireSemanticRuntime/);
      assert.match(adapterSource, /createAlchSemanticAdapter\(runtime\)/);
      assert.match(readFileSync(resolve(repositoryRoot, consumer.facade_source), "utf8"), /text\.semantic-key\/v1/);
    }
  }
  assert.equal(bindings.authority_effect, "none");
  assert.equal(semanticContract.authority_effect, "none");
});

test("shared normalization, phrase matching, non-collapse, and orthogonality fixtures pass", () => {
  const semanticText = createSemanticTextFacade(createModulePort({adapters: [createAlchSemanticAdapter({semanticKey, containsPhrase})], output_validators: semanticTextOutputValidators}), {consumer_id: "parity-test"});
  for (const fixture of fixtures.cases) {
    const observed = fixture.operation === "semantic-key"
      ? semanticKey(fixture.input)
      : containsPhrase(fixture.input.text, fixture.input.phrase);
    assert.deepEqual(observed, fixture.expected, fixture.case_id);
    const throughPort = fixture.operation === "semantic-key"
      ? semanticText.semanticKey(fixture.input, {invocation_id: `parity.${fixture.case_id}`}).value.key
      : semanticText.containsPhrase(fixture.input.text, fixture.input.phrase, {invocation_id: `parity.${fixture.case_id}`}).value.matched;
    assert.deepEqual(throughPort, fixture.expected, `${fixture.case_id}:module-port`);
  }
});
