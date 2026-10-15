import assert from "node:assert/strict";
import {createHash} from "node:crypto";
import {EventEmitter} from "node:events";
import {mkdtempSync, readFileSync, rmSync, writeFileSync} from "node:fs";
import {tmpdir} from "node:os";
import {join, resolve} from "node:path";
import {PassThrough} from "node:stream";
import test from "node:test";

import {
  composeDefineContext,
  compileDefinitionPackToAlch,
  createAppServerDefineAgent,
  createDefineContextSufficiencyAdapter,
  createDefineSessionClient,
  createDurableDefineRuntime,
  evaluateDefineLanguageQuality,
  evaluateDefinitionPackAlchHandoff,
  evaluateDefineScopeReadiness,
  InMemorySessionRepository,
  JsonFileSessionRepository,
  resolveDefineContextCandidates,
  runDefineCli,
  runDefineConversation,
  runDefineSession,
  renderDefinitionPackAlch,
  sessionStateDigest,
  validateDefinitionPack,
} from "../index.mjs";
import {digest} from "../src/canonical.mjs";
import {codexGatewayLifecycleParameterPosture} from "../../agent-reasoning-engine/packages/codex-app-server-wrapper/src/host-method-policy.mjs";

const repositoryRoot = resolve(import.meta.dirname, "../../../..");
const fixture = resolve(import.meta.dirname, "../fixtures/smoke-input.json");
const languageQualityConversationFixtures = JSON.parse(readFileSync(
  resolve(import.meta.dirname, "../fixtures/language-quality-conversations.json"),
  "utf8",
));
const compiledDefineServiceRoot = resolve(import.meta.dirname, "../generated/define-service");
const scope = {
  goal: "Define a release channel",
  intent: "Remove ambiguity for a local consumer",
  context: "A release channel names how candidate output reaches a consumer.",
  consumer: "define-cli-test",
};

function capture() {
  const stream = new PassThrough();
  let value = "";
  stream.on("data", (chunk) => { value += chunk.toString("utf8"); });
  return {stream, value: () => value};
}

function scopeReview(options) {
  const terms = options.map((candidate) => candidate.term);
  const language = {
    user_phrases: ["shared vocabulary", "teams use overlapping terms", ...terms],
    terms,
    distinctions: ["candidate vocabulary is not canonical terminology"],
    relationships: ["term owners answer challenges about terms"],
    constraints: ["Atlas project boundary"],
    owners: ["atlas-team"],
    open_questions: ["Who can promote a candidate term?"],
  };
  const grounding = [];
  for (const field of ["terms", "distinctions", "relationships", "constraints", "owners", "open_questions"]) {
    for (let index = 0; index < language[field].length; index += 1) {
      grounding.push({field, item_index: index, source_phrase_index: field === "terms" ? index + 2 : 0, posture: "candidate-inference", rationale: "Candidate interpretation is visibly bound to supplied user language."});
    }
  }
  const nonCollapse = [];
  for (let left = 0; left < terms.length; left += 1) {
    for (let right = left + 1; right < terms.length; right += 1) {
      nonCollapse.push({left_term_index: left, right_term_index: right, status: "related", difference: `${terms[left]} and ${terms[right]} answer different meaning questions.`});
    }
  }
  return {
    schema_version: "cav2.define-conversation-turn/v2",
    phase: "scope-review",
    message: "I can now reflect the scope back before we examine its meaning.",
    question: null,
    scope_ready: true,
    covered_dimensions: [
      "domain-and-subject", "desired-outcome", "consumers", "terms",
      "distinctions-and-relationships", "constraints", "ownership", "open-questions",
    ],
    scope: {
      domain: "knowledge systems",
      subject: "shared vocabulary",
      project: "Atlas",
      context: "Teams currently use overlapping terms.",
      desired_outcome: "Create a consistent bounded vocabulary",
      intent: "Reduce ambiguity between teams",
      consumer: "atlas-team",
      language,
      language_quality: {
        schema_version: "cav2.define-language-quality/v1",
        grounding,
        non_collapse: nonCollapse,
        orthogonality: {
          applicability: "not-applicable",
          rationale: "This scope does not introduce two classification axes.",
          axes: [],
          pair_checks: [],
        },
      },
    },
    options,
  };
}

function option(id, term, meaning) {
  return {option_id: id, term, question: `What should ${term} mean?`, why_it_matters: `${term} changes how teams communicate.`, candidate_definition: meaning, boundary: "Candidate meaning for Atlas only."};
}

function realisticQualityTurn(fixtureCase, blocked) {
  const candidates = fixtureCase.options.map((candidate) => option(
    candidate.option_id,
    candidate.term,
    candidate.candidate_definition,
  ));
  const turn = scopeReview(candidates);
  turn.scope.language.user_phrases = [fixtureCase.opening, ...candidates.map((candidate) => candidate.term)];
  for (const grounding of turn.scope.language_quality.grounding) {
    grounding.source_phrase_index = grounding.field === "terms" ? grounding.item_index + 1 : 0;
  }
  if (fixtureCase.defect === "non-collapse" && blocked) {
    turn.scope.language_quality.non_collapse[0] = {
      left_term_index: 0,
      right_term_index: 1,
      status: "collapsed",
      difference: "The response has not established an operational difference.",
    };
  }
  if (fixtureCase.defect === "semantic-grounding") {
    const termGrounding = turn.scope.language_quality.grounding.find((item) => item.field === "terms" && item.item_index === 0);
    if (blocked) {
      termGrounding.posture = "direct";
      termGrounding.source_phrase_index = 0;
      termGrounding.rationale = "The response incorrectly claims the user's release language directly names this term.";
    }
  }
  if (fixtureCase.defect === "orthogonality") {
    turn.scope.language_quality.orthogonality = {
      applicability: "applicable",
      rationale: "Maturity and authority both classify a definition.",
      axes: [
        {axis_id: "maturity", label: "Maturity", unique_question: "How developed is it?", values: ["draft", "stable"]},
        {axis_id: "authority", label: "Authority", unique_question: "Has its owner adopted it?", values: ["candidate", "adopted"]},
      ],
      pair_checks: [{
        left_axis_id: "maturity",
        right_axis_id: "authority",
        status: blocked ? "redundant" : "independent",
        difference: blocked
          ? "The response treats stable as equivalent to adopted."
          : "A stable definition can remain unadopted, and an owner can adopt a definition at a declared maturity.",
        coupling_type: null,
        coupling_owner: null,
        coupling_effect: null,
      }],
    };
  }
  return turn;
}

function scriptedAnswers(values) {
  const queue = [...values];
  return async () => queue.shift() ?? "";
}

function handoffReadyResult() {
  const reviewed = scopeReview([
    option("option:vocabulary", "shared vocabulary", "The bounded set of terms used consistently by Atlas teams."),
    option("option:owner", "term owner", "The role accountable for answering challenges about one Atlas term."),
  ]);
  const evaluation = evaluateDefineLanguageQuality(reviewed.scope, reviewed.options, {user_confirmed: true});
  return runDefineSession({
    goal: reviewed.scope.desired_outcome,
    intent: reviewed.scope.intent,
    context: reviewed.scope.context,
    consumer: reviewed.scope.consumer,
    context_result: composeDefineContext(scope, repositoryRoot),
    concepts: reviewed.options.map((candidate) => ({concept_id: candidate.option_id, term: candidate.term})),
    responses: reviewed.options.map((candidate) => ({concept_id: candidate.option_id, action: "propose", payload: {
      definition: candidate.candidate_definition,
      plain_explanation: candidate.candidate_definition,
      boundary: candidate.boundary,
    }})),
    language_scope: reviewed.scope.language,
    language_quality_evidence: reviewed.scope.language_quality,
    language_quality_evaluation: evaluation,
  });
}

function refreshPackId(pack) {
  const {pack_id: ignored, ...material} = pack;
  pack.pack_id = `definition-pack:${digest(material)}`;
  return pack;
}

test("language quality requires grounding and user confirmation for candidate inference", () => {
  const turn = scopeReview([
    option("option:vocabulary", "shared vocabulary", "A bounded set of terms."),
    option("option:owner", "term owner", "A role accountable for one term."),
  ]);
  const beforeConfirmation = evaluateDefineLanguageQuality(turn.scope);
  assert.equal(beforeConfirmation.status, "review");
  assert.equal(beforeConfirmation.checks.semantic_grounding, "review");
  const afterConfirmation = evaluateDefineLanguageQuality(turn.scope, turn.options, {user_confirmed: true});
  assert.equal(afterConfirmation.status, "pass");
  assert.deepEqual(afterConfirmation.checks, {semantic_grounding: "pass", non_collapse: "pass", orthogonality: "pass"});

  const missing = structuredClone(turn.scope);
  missing.language_quality.grounding.pop();
  const rejected = evaluateDefineLanguageQuality(missing, turn.options, {user_confirmed: true});
  assert.equal(rejected.status, "block");
  assert.match(rejected.reason_codes.join("\n"), /quality\.grounding-missing/);
});

test("compiled multi-entry Define service retains Alch source, ontology, Craft projects, and executable boundaries", async () => {
  const source = readFileSync(resolve(import.meta.dirname, "../alch/define-runtime.alch"));
  const manifest = JSON.parse(readFileSync(resolve(compiledDefineServiceRoot, "manifest.json"), "utf8"));
  const ontology = JSON.parse(readFileSync(resolve(compiledDefineServiceRoot, "provenance/service/ontology.json"), "utf8"));
  const readinessRoot = resolve(compiledDefineServiceRoot, "entries/LanguageReadiness");
  const craftProject = JSON.parse(readFileSync(resolve(readinessRoot, "provenance/lowering/project/project.json"), "utf8"));
  assert.equal(manifest.schema_version, "alchlang.service-build/v1");
  assert.equal(manifest.source_sha256, createHash("sha256").update(source).digest("hex"));
  assert.deepEqual(readFileSync(resolve(compiledDefineServiceRoot, "provenance/service/source.alch")), source);
  for (const [relativePath, expectedDigest] of Object.entries(manifest.files)) {
    assert.equal(createHash("sha256").update(readFileSync(resolve(compiledDefineServiceRoot, relativePath))).digest("hex"), expectedDigest, relativePath);
  }
  assert.equal(ontology.schema_version, "alchlang.service-ontology/v1");
  assert.equal(ontology.source_format, "alchlang");
  assert.equal(ontology.ontology_admitted, false);
  assert.equal(craftProject.schema_version, "domainspec.project/v2");
  assert.ok(craftProject.features.includes("define-language-readiness"));
  const {invoke} = await import("../generated/define-service/app/service/index.mjs");
  assert.deepEqual(
    await invoke("LanguageReadiness", {semantic_grounding: "pass", non_collapse: "block", orthogonality: "pass", user_confirmed: false}),
    {status: "block", repair_focus: "non-collapse", authority_effect: "none"},
  );
  assert.deepEqual(
    await invoke("LanguageReadiness", {semantic_grounding: "pass", non_collapse: "pass", orthogonality: "pass", user_confirmed: false}),
    {status: "review", repair_focus: "user-confirmation", authority_effect: "none"},
  );
  assert.deepEqual(
    await invoke("GroundingEvidence", {posture: "candidate-inference", rationale_present: true}),
    {status: "review", repair_focus: "user-confirmation", requires_direct_match: false, authority_effect: "none"},
  );
  assert.deepEqual(
    await invoke("NonCollapseEvidence", {relation: "collapsed", difference_present: true}),
    {status: "block", repair_focus: "collapsed", authority_effect: "none"},
  );
  assert.deepEqual(
    await invoke("OrthogonalityEvidence", {relation: "coupled", difference_present: true, coupling_named: false}),
    {status: "block", repair_focus: "coupling", authority_effect: "none"},
  );
  assert.deepEqual(manifest.entries, ["SemanticGrounding", "GroundingEvidence", "NonCollapse", "NonCollapseEvidence", "Orthogonality", "OrthogonalityEvidence", "LanguageReadiness", "ScopeReadiness", "ConceptDisposition", "PackReadiness", "AlchHandoffReadiness"]);
});

test("handoff-ready Definition Pack becomes deterministic Alch, ontology, Craft, and runtime evidence", () => {
  const result = handoffReadyResult();
  assert.equal(result.validation.handoff_ready, true);
  const rendered = renderDefinitionPackAlch(result.definition_pack);
  assert.match(rendered.source, /profile semantic-contract-v1/);
  assert.match(rendered.source, /shared vocabulary/);
  assert.match(rendered.source, /term owner/);
  assert.match(rendered.source, /CandidateProjectionHasNoAuthority/);

  const directory = mkdtempSync(join(tmpdir(), "define-alch-handoff-test-"));
  try {
    const firstPath = join(directory, "first");
    const secondPath = join(directory, "second");
    const first = compileDefinitionPackToAlch(result, firstPath, {repository_root: repositoryRoot});
    const second = compileDefinitionPackToAlch(result, secondPath, {repository_root: repositoryRoot});
    assert.deepEqual(second.receipt, first.receipt);
    assert.equal(readFileSync(join(firstPath, "definition-pack.alch"), "utf8"), readFileSync(join(secondPath, "definition-pack.alch"), "utf8"));
    assert.equal(readFileSync(join(firstPath, "compiled/manifest.json"), "utf8"), readFileSync(join(secondPath, "compiled/manifest.json"), "utf8"));
    const manifest = JSON.parse(readFileSync(join(firstPath, "compiled/manifest.json"), "utf8"));
    assert.deepEqual(manifest.pipeline, ["alch-source", "semantic-contract-ontology", "craft-project", "domainspec-compile", "runtime-projection", "fixture-validation"]);
    assert.equal(manifest.ontology_admitted, false);
    assert.equal(JSON.parse(readFileSync(join(firstPath, "compiled/provenance/ontology.json"), "utf8")).source_format, "alchlang");
    assert.equal(JSON.parse(readFileSync(join(firstPath, "compiled/provenance/craft/project/project.json"), "utf8")).schema_version, "domainspec.project/v1");
    assert.equal(JSON.parse(readFileSync(join(firstPath, "compiled/evidence/craft/certificate.json"), "utf8")).authority_effect, "none");
    assert.equal(JSON.parse(readFileSync(join(firstPath, "handoff-receipt.json"), "utf8")).receipt_digest, first.receipt.receipt_digest);
  } finally {
    rmSync(directory, {recursive: true, force: true});
  }
});

test("Alch handoff blocks missing quality, independent quality defects, and overwrite attempts", () => {
  const result = handoffReadyResult();
  const withoutQuality = structuredClone(result.definition_pack);
  delete withoutQuality.language_quality_evaluation;
  delete withoutQuality.language_quality_evidence;
  delete withoutQuality.language_scope;
  refreshPackId(withoutQuality);
  assert.equal(evaluateDefinitionPackAlchHandoff(withoutQuality).repair_focus, "language-quality");

  const collapsed = structuredClone(result.definition_pack);
  collapsed.language_quality_evaluation.checks.non_collapse = "block";
  collapsed.language_quality_evaluation.status = "block";
  refreshPackId(collapsed);
  assert.equal(evaluateDefinitionPackAlchHandoff(collapsed).repair_focus, "non-collapse");

  const ungrounded = structuredClone(result.definition_pack);
  ungrounded.language_quality_evaluation.checks.semantic_grounding = "block";
  ungrounded.language_quality_evaluation.status = "block";
  refreshPackId(ungrounded);
  assert.equal(evaluateDefinitionPackAlchHandoff(ungrounded).repair_focus, "semantic-grounding");

  const coupled = structuredClone(result.definition_pack);
  coupled.language_quality_evaluation.checks.orthogonality = "block";
  coupled.language_quality_evaluation.status = "block";
  refreshPackId(coupled);
  assert.equal(evaluateDefinitionPackAlchHandoff(coupled).repair_focus, "orthogonality");

  const open = structuredClone(result.definition_pack);
  open.open_questions.push({question: "Who adopts this language?", blocking: true});
  refreshPackId(open);
  assert.equal(evaluateDefinitionPackAlchHandoff(open).repair_focus, "definition-pack");

  const tampered = structuredClone(result.definition_pack);
  tampered.intent = "A different intent after review.";
  const tamperedDecision = evaluateDefinitionPackAlchHandoff(tampered);
  assert.equal(tamperedDecision.repair_focus, "definition-pack");
  assert.match(tamperedDecision.pack_validation.reason_codes.join("\n"), /pack\.identity-digest-mismatch/);

  const existing = mkdtempSync(join(tmpdir(), "define-alch-existing-"));
  try {
    assert.throws(() => compileDefinitionPackToAlch(result, existing, {repository_root: repositoryRoot}), /output directory already exists/);
  } finally {
    rmSync(existing, {recursive: true, force: true});
  }
});

test("CLI compile reports the user-facing Alch handoff and keeps authority absent", async () => {
  const directory = mkdtempSync(join(tmpdir(), "define-alch-cli-test-"));
  try {
    const inputPath = join(directory, "definition-pack.json");
    const outputPath = join(directory, "compiled-pack");
    writeFileSync(inputPath, `${JSON.stringify(handoffReadyResult())}\n`);
    const stdout = capture();
    const stderr = capture();
    const code = await runDefineCli(["compile", "--input", inputPath, "--out", outputPath], {repositoryRoot, stdout: stdout.stream, stderr: stderr.stream});
    assert.equal(code, 0, stderr.value());
    assert.match(stdout.value(), /Definition Pack compiled through Alch/);
    assert.match(stdout.value(), /Ontology and Craft evidence/);
    assert.match(stdout.value(), /Authority effect: none/);
    assert.doesNotMatch(stdout.value(), /define-alch-handoff\./);
  } finally {
    rmSync(directory, {recursive: true, force: true});
  }
});

test("compiled scope readiness keeps missing scope and language repair orthogonal", () => {
  assert.deepEqual(
    evaluateDefineScopeReadiness({context: "bounded", desired_outcome: "shared meaning", intent: "define terms"}, true, "pass"),
    {status: "ready", next_focus: "none", authority_effect: "none"},
  );
  assert.equal(evaluateDefineScopeReadiness({context: "bounded", desired_outcome: "shared meaning", intent: ""}, true, "pass").next_focus, "intent");
  assert.equal(evaluateDefineScopeReadiness({context: "bounded", desired_outcome: "shared meaning", intent: "define terms"}, true, "block").next_focus, "language-quality");
});

test("language quality blocks collapsed terms", () => {
  const turn = scopeReview([
    option("option:vocabulary", "shared vocabulary", "A bounded set of terms."),
    option("option:lexicon", "team lexicon", "A bounded set of terms."),
  ]);
  turn.scope.language_quality.non_collapse[0] = {
    left_term_index: 0,
    right_term_index: 1,
    status: "distinct",
    difference: "The agent claims that these terms differ.",
  };
  let result = evaluateDefineLanguageQuality(turn.scope, turn.options, {user_confirmed: true});
  assert.equal(result.status, "block");
  assert.match(result.reason_codes.join("\n"), /quality\.non-collapse-definition-collision:0:1/);

  turn.options[1].candidate_definition = "A separately published glossary.";
  turn.scope.language_quality.non_collapse[0].status = "collapsed";
  turn.scope.language_quality.non_collapse[0].difference = "No operational difference has been established.";
  result = evaluateDefineLanguageQuality(turn.scope, turn.options, {user_confirmed: true});
  assert.equal(result.status, "block");
  assert.match(result.reason_codes.join("\n"), /quality\.non-collapse-collapsed:0:1/);
});

test("compiled evidence entries own grounding, pair-relation, and coupling posture", () => {
  const turn = scopeReview([
    option("option:vocabulary", "shared vocabulary", "A bounded set of terms."),
    option("option:owner", "term owner", "A role accountable for one term."),
  ]);
  turn.scope.language_quality.grounding[0].posture = "invented";
  turn.scope.language_quality.non_collapse[0].status = "invented";
  let result = evaluateDefineLanguageQuality(turn.scope, turn.options, {user_confirmed: true});
  assert.match(result.reason_codes.join("\n"), /quality\.grounding-evidence-invalid:terms:0/);
  assert.match(result.reason_codes.join("\n"), /quality\.non-collapse-evidence-invalid:0:1/);

  turn.scope.language_quality.grounding[0].posture = "candidate-inference";
  turn.scope.language_quality.non_collapse[0].status = "related";
  turn.scope.language_quality.orthogonality = {
    applicability: "applicable",
    rationale: "Maturity and authority answer separate questions.",
    axes: [
      {axis_id: "maturity", label: "Maturity", unique_question: "How developed?", values: ["draft", "stable"]},
      {axis_id: "authority", label: "Authority", unique_question: "Who decided?", values: ["candidate", "adopted"]},
    ],
    pair_checks: [{
      left_axis_id: "maturity", right_axis_id: "authority", status: "coupled",
      difference: "A promotion gate relates otherwise distinct axes.",
      coupling_type: "promotion-gate", coupling_owner: "definitions-governance", coupling_effect: "",
    }],
  };
  result = evaluateDefineLanguageQuality(turn.scope, turn.options, {user_confirmed: true});
  assert.match(result.reason_codes.join("\n"), /quality\.orthogonality-unnamed-coupling:0:1/);
});

test("language quality independently catches normalization and direct-grounding defects", () => {
  const turn = scopeReview([
    option("option:a", "Release Gate", "A required release condition."),
    option("option:b", "release-gate", "A separately asserted concept."),
  ]);
  turn.scope.language_quality.grounding[0].posture = "direct";
  turn.scope.language_quality.grounding[0].source_phrase_index = 0;
  const result = evaluateDefineLanguageQuality(turn.scope, turn.options, {user_confirmed: true});
  assert.equal(result.status, "block");
  assert.match(result.reason_codes.join("\n"), /quality\.term-normalized-collision/);
  assert.match(result.reason_codes.join("\n"), /quality\.grounding-direct-mismatch:terms:0/);
});

test("compiled semantic prelude handles separator equivalence without substring collapse", () => {
  const turn = scopeReview([
    option("option:release-gate", "release gate", "A condition that must hold before release."),
  ]);
  turn.scope.language.user_phrases[2] = "The release-gate controls publication.";
  turn.scope.language_quality.grounding[0].posture = "direct";
  turn.scope.language_quality.grounding[0].source_phrase_index = 2;
  let result = evaluateDefineLanguageQuality(turn.scope, turn.options, {user_confirmed: true});
  assert.equal(result.status, "pass");

  turn.scope.language.terms[0] = "define";
  turn.scope.language.user_phrases[2] = "A predefined runtime exists.";
  turn.options[0].term = "define";
  result = evaluateDefineLanguageQuality(turn.scope, turn.options, {user_confirmed: true});
  assert.equal(result.status, "block");
  assert.match(result.reason_codes.join("\n"), /quality\.grounding-direct-mismatch:terms:0/);
});

test("language quality blocks redundant axes and requires named coupling", () => {
  const turn = scopeReview([option("option:vocabulary", "shared vocabulary", "A bounded set of terms.")]);
  turn.scope.language_quality.orthogonality = {
    applicability: "applicable",
    rationale: "Two classification axes affect how candidate language is reviewed.",
    axes: [
      {axis_id: "maturity", label: "Maturity", unique_question: "How developed is it?", values: ["draft", "stable"]},
      {axis_id: "authority", label: "Authority", unique_question: "Who may decide?", values: ["candidate", "adopted"]},
    ],
    pair_checks: [{left_axis_id: "maturity", right_axis_id: "authority", status: "redundant", difference: "The proposed response treats stable as adopted.", coupling_type: null, coupling_owner: null, coupling_effect: null}],
  };
  let result = evaluateDefineLanguageQuality(turn.scope, {user_confirmed: true});
  assert.equal(result.status, "block");
  assert.match(result.reason_codes.join("\n"), /quality\.orthogonality-redundant/);

  turn.scope.language_quality.orthogonality.pair_checks[0] = {
    left_axis_id: "maturity", right_axis_id: "authority", status: "coupled",
    difference: "Maturity and authority answer different questions but a promotion gate relates them.",
    coupling_type: "promotion-gate", coupling_owner: "definitions-governance", coupling_effect: "eligible-for-owner-review",
  };
  result = evaluateDefineLanguageQuality(turn.scope, {user_confirmed: true});
  assert.equal(result.status, "pass");
  assert.equal(result.checks.orthogonality, "pass");
});

test("ARE composition selects Define and projects inline meaning", () => {
  const result = composeDefineContext(scope, repositoryRoot);
  assert.equal(result.ok, true);
  assert.equal(result.route_decision.selected.route_id, "CA2-ROUTE-DEFINE");
  assert.equal(result.context_envelope.authority_effect, "none");
  assert.ok(result.context_envelope.included_items.some((item) => item.context_item_id === "definition:CAV2-DEFINE-CAND-001" && item.content.text.includes("CyberAlchemy Define")));
  assert.ok(result.context_envelope.included_items.some((item) => item.context_item_id === "ontology-node:define-session-runtime.CliInterface" && item.content.intent));
  assert.ok(result.context_envelope.inline_bytes <= 32 * 1024);
});

test("same selected sources and request produce byte-stable context", () => {
  const first = composeDefineContext(scope, repositoryRoot);
  const second = composeDefineContext(scope, repositoryRoot);
  assert.deepEqual(second, first);
});

test("session produces exactly one candidate disposition per concept", () => {
  const contextResult = composeDefineContext(scope, repositoryRoot);
  const result = runDefineSession({
    ...scope,
    context_result: contextResult,
    concepts: [{concept_id: "concept:channel", term: "release channel"}],
    responses: [{concept_id: "concept:channel", action: "propose", payload: {definition: "A named candidate delivery path."}}],
  });
  assert.equal(result.ok, true);
  assert.equal(result.definition_pack.concept_dispositions.length, 1);
  assert.equal(result.definition_pack.concept_dispositions[0].disposition, "propose");
  assert.equal(result.validation.handoff_ready, true);
  assert.deepEqual(validateDefinitionPack(result.definition_pack), result.validation);
});

test("defer preserves an open question and never invents a definition", () => {
  const contextResult = composeDefineContext(scope, repositoryRoot);
  const result = runDefineSession({
    ...scope,
    context_result: contextResult,
    concepts: [{concept_id: "concept:channel", term: "release channel"}],
    responses: [{concept_id: "concept:channel", action: "defer", payload: {reason: "Owner unavailable"}}],
  });
  assert.equal(result.ok, true);
  assert.equal(result.definition_pack.concept_dispositions[0].disposition, "open");
  assert.equal(result.definition_pack.concept_dispositions[0].candidate_definition, undefined);
  assert.equal(result.validation.handoff_ready, false);
  assert.equal(result.session.state, "blocked-open-meaning");
});

test("CLI scripted canary writes deterministic result only when explicitly requested", async () => {
  const directory = mkdtempSync(join(tmpdir(), "define-cli-test-"));
  try {
    const outputPath = join(directory, "pack.json");
    const stdout = capture();
    const stderr = capture();
    const code = await runDefineCli([
      "run", "--goal", scope.goal, "--intent", scope.intent, "--context", scope.context,
      "--consumer", scope.consumer, "--input", fixture, "--output", outputPath, "--json",
    ], {repositoryRoot, stdin: new PassThrough(), stdout: stdout.stream, stderr: stderr.stream});
    assert.equal(code, 0, stderr.value());
    assert.equal(stderr.value(), "");
    const written = JSON.parse(readFileSync(outputPath, "utf8"));
    const displayed = JSON.parse(stdout.value());
    delete displayed.output_path;
    assert.deepEqual(displayed, written);
    assert.equal(written.route.route_id, "CA2-ROUTE-DEFINE");
  } finally {
    rmSync(directory, {recursive: true, force: true});
  }
});

test("CLI preserves unresolved non-interactive concepts with exit code 4", async () => {
  const stdout = capture();
  const stderr = capture();
  const code = await runDefineCli([
    "run", "--goal", scope.goal, "--intent", scope.intent, "--context", scope.context,
    "--consumer", scope.consumer, "--concept", "release channel", "--json",
  ], {repositoryRoot, stdin: new PassThrough(), stdout: stdout.stream, stderr: stderr.stream});
  assert.equal(code, 4, stderr.value());
  const result = JSON.parse(stdout.value());
  assert.equal(result.validation.handoff_ready, false);
  assert.equal(result.definition_pack.open_questions.length, 1);
});

test("conversation starts broadly, confirms scope, and reviews options one at a time", async () => {
  const seen = [];
  const agent = {
    respond: async (request) => {
      seen.push(request);
      return scopeReview([
        option("option:vocabulary", "shared vocabulary", "The bounded set of terms used consistently by Atlas teams."),
        option("option:term-owner", "term owner", "The role responsible for answering challenges about one term."),
      ]);
    },
  };
  const output = [];
  const result = await runDefineConversation({
    agent,
    ask: scriptedAnswers(["yes", "accept", "open", "Owner is not identified", "yes"]),
    write: (text) => output.push(text),
    opening: "We are building Atlas, a knowledge system, and teams use inconsistent language.",
    consumer: "human:define-cli",
    repository_root: repositoryRoot,
  });
  assert.equal(seen[0].mode, "discovery");
  assert.equal(result.ok, true);
  assert.equal(result.definition_pack.required_concepts.length, 2);
  assert.equal(result.definition_pack.concept_dispositions[0].disposition === "propose" || result.definition_pack.concept_dispositions[1].disposition === "propose", true);
  assert.equal(result.definition_pack.open_questions.length, 1);
  assert.match(output.join(""), /Option 1 of 2/);
  assert.match(output.join(""), /Option 2 of 2/);
  assert.match(output.join(""), /Your phrases: shared vocabulary; teams use overlapping terms/);
  assert.match(output.join(""), /Semantic grounding: review/);
  assert.equal(result.definition_pack.language_quality_evaluation.status, "pass");
  assert.deepEqual(result.definition_pack.language_scope.terms, ["shared vocabulary", "term owner"]);
  assert.equal(result.definition_pack.language_quality_evidence.non_collapse.length, 1);
  assert.equal(result.validation.validation_scope, "deterministic-structure-and-language-quality");
});

test("conversation cannot reach confirmation while language quality is blocked", async () => {
  const candidates = [
    option("option:vocabulary", "shared vocabulary", "A bounded set of terms."),
    option("option:lexicon", "team lexicon", "A distinct team-owned glossary."),
  ];
  const blocked = scopeReview(candidates);
  blocked.scope.language_quality.non_collapse[0] = {
    left_term_index: 0,
    right_term_index: 1,
    status: "collapsed",
    difference: "The first response did not establish a difference.",
  };
  const corrected = scopeReview(candidates);
  let calls = 0;
  const output = [];
  const result = await runDefineConversation({
    agent: {respond: async () => (++calls === 1 ? blocked : corrected)},
    ask: scriptedAnswers(["Keep vocabulary as the set and lexicon as the published artifact.", "yes", "accept", "accept", "yes"]),
    write: (text) => output.push(text),
    opening: "Atlas needs a vocabulary and a team lexicon.",
    repository_root: repositoryRoot,
  });
  assert.equal(calls, 2);
  assert.equal(result.ok, true);
  assert.match(output.join(""), /Overall: block/);
  assert.match(output.join(""), /What operational difference separates “shared vocabulary” from “team lexicon”/);
  assert.doesNotMatch(output.join(""), /quality\.non-collapse-collapsed/);
});

test("realistic language defects produce focused repair responses before confirmation", async (t) => {
  assert.equal(languageQualityConversationFixtures.schema_version, "cav2.define-language-quality-conversation-fixtures/v1");
  for (const fixtureCase of languageQualityConversationFixtures.cases) {
    await t.test(fixtureCase.case_id, async () => {
      const blocked = realisticQualityTurn(fixtureCase, true);
      const corrected = realisticQualityTurn(fixtureCase, false);
      const evaluation = evaluateDefineLanguageQuality(blocked.scope, blocked.options, {user_confirmed: false});
      assert.equal(evaluation.status, "block");
      assert.equal(evaluation.checks[fixtureCase.expected_blocked_check], "block");

      let calls = 0;
      const output = [];
      const answers = [fixtureCase.correction, "yes", ...corrected.options.map(() => "accept"), "yes"];
      const result = await runDefineConversation({
        agent: {respond: async () => (++calls === 1 ? blocked : corrected)},
        ask: scriptedAnswers(answers),
        write: (text) => output.push(text),
        opening: fixtureCase.opening,
        repository_root: repositoryRoot,
      });

      const transcript = output.join("");
      assert.equal(calls, 2);
      assert.equal(result.ok, true);
      assert.equal(result.definition_pack.language_quality_evaluation.status, "pass");
      assert.ok(transcript.includes(fixtureCase.expected_question), transcript);
      assert.doesNotMatch(transcript, /quality\.(grounding|non-collapse|orthogonality)/);
    });
  }
});

test("incomplete discovery keeps the agent question ahead of the readiness gate", async () => {
  const candidate = option("option:vocabulary", "shared vocabulary", "A bounded set of terms.");
  const discovering = scopeReview([candidate]);
  discovering.phase = "discover";
  discovering.scope_ready = false;
  discovering.question = "Who will use this language first?";
  discovering.scope.language_quality.grounding = [];
  const ready = scopeReview([candidate]);
  let calls = 0;
  const output = [];
  const result = await runDefineConversation({
    agent: {respond: async () => (++calls === 1 ? discovering : ready)},
    ask: scriptedAnswers(["The Atlas product team.", "yes", "accept", "yes"]),
    write: (text) => output.push(text),
    opening: "Atlas needs shared vocabulary.",
    repository_root: repositoryRoot,
  });
  assert.equal(result.ok, true);
  assert.match(output.join(""), /Who will use this language first\?/);
  assert.doesNotMatch(output.join(""), /Which part of the candidate language is not grounded/);
});

test("discussion lets the agent revise only the current option before acceptance", async () => {
  const original = option("option:vocabulary", "shared vocabulary", "An initial meaning.");
  const revised = option("option:vocabulary", "shared vocabulary", "A revised meaning bounded to the Atlas project.");
  let calls = 0;
  const agent = {
    respond: async (request) => {
      calls += 1;
      if (request.mode === "discuss-option") return {...scopeReview([revised]), phase: "option-discussion", message: "I narrowed the candidate to the project boundary."};
      return scopeReview([original]);
    },
  };
  const result = await runDefineConversation({
    agent,
    ask: scriptedAnswers(["y", "discuss", "It is too broad", "accept", "y"]),
    write: () => {},
    opening: "Atlas needs a shared vocabulary.",
    repository_root: repositoryRoot,
  });
  assert.equal(calls, 2);
  assert.equal(result.definition_pack.concept_dispositions[0].candidate_definition.normative_voice, revised.candidate_definition);
});

test("discussion cannot replace the current option with a different identity", async () => {
  const original = option("option:vocabulary", "shared vocabulary", "An initial meaning.");
  const replacement = option("option:owner", "term owner", "A different concept.");
  const agent = {
    respond: async (request) => request.mode === "discuss-option"
      ? {...scopeReview([replacement]), phase: "option-discussion", message: "I replaced the option."}
      : scopeReview([original]),
  };
  await assert.rejects(
    runDefineConversation({
      agent,
      ask: scriptedAnswers(["yes", "discuss", "It is too broad"]),
      write: () => {},
      opening: "Atlas needs a shared vocabulary.",
      repository_root: repositoryRoot,
    }),
    /define-conversation\.discussion-option-identity-drift/,
  );
});

test("CLI defaults to conversational mode and keeps agent inference candidate", async () => {
  const agent = {
    respond: async () => ({...scopeReview([option("option:vocabulary", "shared vocabulary", "A reviewed project vocabulary.")]), phase: "options-ready"}),
    close: async () => {},
  };
  const stdout = capture();
  const stderr = capture();
  const code = await runDefineCli(["Atlas", "needs", "consistent", "language"], {
    repositoryRoot,
    stdin: new PassThrough(),
    stdout: stdout.stream,
    stderr: stderr.stream,
    agent,
    ask: scriptedAnswers(["yes", "accept", "yes"]),
    write: (text) => stdout.stream.write(text),
  });
  assert.equal(code, 0, stderr.value());
  assert.match(stdout.value(), /Here is the scope I heard/);
  assert.match(stdout.value(), /Candidate Definition Pack created/);
  assert.match(stdout.value(), /Authority effect: none/);
});

test("CLI waits for the broad opening before creating the app-server agent", async () => {
  let agentCreated = false;
  let agentOptions = null;
  const prompts = [];
  const agent = {
    respond: async () => ({...scopeReview([option("option:vocabulary", "shared vocabulary", "A reviewed project vocabulary.")]), phase: "options-ready"}),
    close: async () => {},
  };
  const stdout = capture();
  const stderr = capture();
  const answers = scriptedAnswers(["how can I build an escape room game", "yes", "accept", "yes"]);
  const code = await runDefineCli([], {
    repositoryRoot,
    stdin: new PassThrough(),
    stdout: stdout.stream,
    stderr: stderr.stream,
    ask: async (prompt) => {
      prompts.push(prompt);
      if (prompts.length === 1) assert.equal(agentCreated, false);
      return answers();
    },
    agent_factory: (options) => {
      agentCreated = true;
      agentOptions = options;
      return agent;
    },
    write: (text) => stdout.stream.write(text),
  });
  assert.equal(code, 0, stderr.value());
  assert.equal(agentCreated, true);
  assert.equal(agentOptions.transport_mode, "gateway");
  assert.equal(agentOptions.define_entrypoint_selected, true);
  assert.match(prompts[0], /domain, subject, context, or project/);
});

test("CLI exposes direct transport only as an explicit diagnostic option", async () => {
  let agentOptions = null;
  const agent = {
    respond: async () => ({...scopeReview([option("option:vocabulary", "shared vocabulary", "A reviewed project vocabulary.")]), phase: "options-ready"}),
    close: async () => {},
  };
  const code = await runDefineCli(["--direct", "Atlas", "vocabulary"], {
    repositoryRoot,
    stdin: new PassThrough(),
    stdout: capture().stream,
    stderr: capture().stream,
    agent_factory: (options) => { agentOptions = options; return agent; },
    ask: scriptedAnswers(["yes", "accept", "yes"]),
    write: () => {},
  });
  assert.equal(code, 0);
  assert.equal(agentOptions.transport_mode, "direct");
});

test("agent preserves an app-server exit reason that occurs before initialize", async () => {
  const child = new EventEmitter();
  child.stdin = new PassThrough();
  child.stdout = new PassThrough();
  child.stderr = new PassThrough();
  child.kill = () => true;
  const agent = createAppServerDefineAgent({
    repository_root: repositoryRoot,
    spawn_impl: () => {
      queueMicrotask(() => {
        child.stderr.write("profile failed to load");
        child.emit("close", 3, null);
      });
      return child;
    },
  });
  await assert.rejects(agent.respond({mode: "discovery", user_input: "escape room", scope_confirmed: false}), (error) => {
    assert.match(error.message, /App-server transport exited: 3/);
    assert.equal(error.details?.diagnostic?.preview, "profile failed to load");
    return true;
  });
  assert.match(agent.inspect().rpc.failure, /App-server transport exited: 3/);
});

test("agent delegates the app-server lifecycle to the shared RPC client", async () => {
  const calls = [];
  const turn = {...scopeReview([option("option:vocabulary", "shared vocabulary", "A bounded vocabulary.")]), phase: "options-ready"};
  const rpcClient = {
    initialize: async (params) => { calls.push(["initialize", params]); return {}; },
    startThread: async (params) => { calls.push(["thread/start", params]); return {thread: {id: "thread:define"}}; },
    runTurn: async (params) => {
      calls.push(["turn/start", params]);
      return {completed: {turn: {id: "turn:define", status: "completed"}}, text: JSON.stringify(turn)};
    },
    close: async () => { calls.push(["close"]); },
    inspect: () => ({kind: "test-rpc", authority_effect: "none"}),
  };
  const agent = createAppServerDefineAgent({repository_root: repositoryRoot, rpc_client: rpcClient});
  const result = await agent.respond({mode: "discovery", user_input: "Atlas vocabulary", scope_confirmed: false});
  assert.deepEqual(calls.map(([method]) => method), ["initialize", "thread/start", "turn/start"]);
  assert.equal(calls[0][1].capabilities.experimentalApi, true);
  assert.equal(calls[1][1].sandbox, "read-only");
  assert.equal(calls[1][1].approvalPolicy, "on-request");
  assert.equal(calls[2][1].approvalPolicy, "on-request");
  assert.equal(calls[2][1].outputSchema.properties.schema_version.const, "cav2.define-conversation-turn/v2");
  assert.deepEqual(codexGatewayLifecycleParameterPosture({method: "thread/start", params: calls[1][1]}), {kind: "admitted"});
  assert.deepEqual(codexGatewayLifecycleParameterPosture({method: "turn/start", params: calls[2][1]}), {kind: "admitted"});
  assert.deepEqual(Object.keys(calls[2][1].additionalContext), ["cyberalchemy.request-context"]);
  const prompt = calls[2][1].input[0].text;
  const applicationContext = JSON.parse(prompt.slice(prompt.indexOf("\n\n") + 2));
  assert.equal(applicationContext.schema_version, "cav2.define-conversation-request/v2");
  assert.ok(applicationContext.instructions.some((instruction) => instruction.includes("form candidate domain language")));
  const requestHint = JSON.parse(calls[2][1].additionalContext["cyberalchemy.request-context"].value);
  assert.equal(requestHint.schema_version, "are.request-context-hint/v1");
  assert.equal(requestHint.raw_request, "Atlas vocabulary");
  assert.equal(requestHint.objective_kind, "define-intake");
  assert.equal(requestHint.field_postures.objective_kind, "inferred");
  assert.equal(result.options[0].option_id, "option:vocabulary");
  await agent.close();
  assert.equal(calls.at(-1)[0], "close");
});

test("Define uses the configured gateway consumer and pins the Codex adapter", async () => {
  const captures = [];
  const turn = {...scopeReview([option("option:vocabulary", "shared vocabulary", "A bounded vocabulary.")]), phase: "options-ready"};
  const makeAgent = () => createAppServerDefineAgent({repository_root: repositoryRoot,
    transport_factory: (options) => {
      captures.push(options);
      const input = new PassThrough();
      const output = new PassThrough();
      input.on("data", (bytes) => {
        for (const line of String(bytes).trim().split("\n")) {
          if (!line) continue;
          const request = JSON.parse(line);
          if (request.method === "initialize") output.write(`${JSON.stringify({id: request.id, result: {}})}\n`);
          if (request.method === "thread/start") output.write(`${JSON.stringify({id: request.id, result: {thread: {id: "thread:define"}}})}\n`);
          if (request.method === "turn/start") {
            output.write(`${JSON.stringify({id: request.id, result: {turn: {id: "turn:define"}}})}\n`);
            output.write(`${JSON.stringify({method: "turn/completed", params: {turn: {id: "turn:define", status: "completed", items: [{type: "agentMessage", text: JSON.stringify(turn)}]}}})}\n`);
          }
        }
      });
      return {input, output, ready: Promise.resolve({}), close: async () => { input.end(); output.end(); }};
    }});
  const first = makeAgent();
  const second = makeAgent();
  await first.respond({mode: "discovery", user_input: "one", scope_confirmed: false});
  await second.respond({mode: "discovery", user_input: "two", scope_confirmed: false});
  assert.equal(captures.length, 2);
  assert.equal(captures[0].consumer_id, "codex:define-cli");
  assert.equal(captures[1].consumer_id, "codex:define-cli");
  assert.notEqual(captures[0].consumer_id, "codex:human-chat");
  assert.ok(captures.every((entry) => entry.expected_backend_adapter_id === "codex-app-server/v1"));
  await first.close();
  await second.close();
});

test("agent rejects scope readiness before all user-language dimensions are covered", async () => {
  const premature = scopeReview([option("option:vocabulary", "shared vocabulary", "A bounded vocabulary.")]);
  premature.covered_dimensions = ["domain-and-subject", "desired-outcome", "consumers", "terms"];
  const rpcClient = {
    initialize: async () => ({}),
    startThread: async () => ({thread: {id: "thread:premature"}}),
    runTurn: async () => ({completed: {turn: {id: "turn:premature", status: "completed"}}, text: JSON.stringify(premature)}),
    close: async () => {},
  };
  const agent = createAppServerDefineAgent({repository_root: repositoryRoot, rpc_client: rpcClient});
  await assert.rejects(
    agent.respond({mode: "discovery", user_input: "I want to start something new", scope_confirmed: false}),
    /define-agent\.scope-ready-before-intake-covered/,
  );
  await agent.close();
});

test("agent resumes an initialized persistent gateway session without hiding other initialize failures", async () => {
  const calls = [];
  const turn = {...scopeReview([option("option:vocabulary", "shared vocabulary", "A bounded vocabulary.")]), phase: "options-ready"};
  const rpcClient = {
    ready: async () => ({ok: true, resumed: true}),
    initialize: async () => {
      calls.push("initialize");
      const error = new Error("initialize: Already initialized");
      error.details = {message: "Already initialized"};
      throw error;
    },
    startThread: async () => { calls.push("thread/start"); return {thread: {id: "thread:resumed"}}; },
    runTurn: async () => ({completed: {turn: {id: "turn:resumed", status: "completed"}}, text: JSON.stringify(turn)}),
    close: async () => {},
    inspect: () => ({kind: "test-rpc"}),
  };
  const agent = createAppServerDefineAgent({repository_root: repositoryRoot, rpc_client: rpcClient});
  const result = await agent.respond({mode: "discovery", user_input: "Atlas vocabulary", scope_confirmed: false});
  assert.deepEqual(calls, ["initialize", "thread/start"]);
  assert.equal(result.options[0].option_id, "option:vocabulary");
  await agent.close();
});

const runtimeActor = {
  actor_ref: "actor:define-owner",
  allowed_effects: ["create-session", "set-context-evaluation", "open-question", "record-answer", "defer-question"],
};

function runtimeCommand(commandId, commandType, sessionId, expectedRevision, payload, actor = runtimeActor) {
  return {
    schema_version: "cav2.define-session-command/v1",
    command_id: commandId,
    command_type: commandType,
    session_id: sessionId,
    expected_revision: expectedRevision,
    actor_access_context: actor,
    payload_schema_version: "v1",
    payload,
  };
}

function createRuntimeSession(runtime, sessionId = "define-session:durable-test") {
  return runtime.execute(runtimeCommand("command:create", "create-session", sessionId, 0, {
    goal: "Define a release channel",
    intent: "Remove ambiguity",
    context: "One shared candidate context.",
    consumer: "runtime-test",
    context_sufficiency_evaluation: {
      evaluation_id: "evaluation:fixture",
      status: "sufficient",
      derivation: "Pinned test fixture",
      residue: [],
      evaluator_receipt_ref: "receipt:fixture",
      authority_effect: "none",
    },
  }));
}

test("durable runtime resumes one confirmed session across CLI and chat clients", () => {
  const directory = mkdtempSync(join(tmpdir(), "define-runtime-test-"));
  try {
    const runtime = createDurableDefineRuntime({repository: new JsonFileSessionRepository(directory)});
    const cli = createDefineSessionClient(runtime, "cli");
    const chat = createDefineSessionClient(runtime, "chat");
    assert.equal(createRuntimeSession(runtime).outcome, "confirmed");
    assert.equal(cli.execute(runtimeCommand("command:open", "open-question", "define-session:durable-test", 1, {
      question_id: "question:channel",
      term: "release channel",
      question: "What should release channel mean?",
      owner_route: "Definitions Governance owner",
    })).outcome, "confirmed");
    assert.equal(chat.execute(runtimeCommand("command:answer", "record-answer", "define-session:durable-test", 2, {
      question_id: "question:channel",
      answer: "A named candidate delivery path.",
    })).outcome, "confirmed");
    const restarted = createDurableDefineRuntime({repository: new JsonFileSessionRepository(directory)});
    const resumed = createDefineSessionClient(restarted, "chat").resume("define-session:durable-test");
    assert.equal(resumed.revision, 3);
    assert.equal(resumed.current_question_id, null);
    assert.equal(resumed.answers[0].answer, "A named candidate delivery path.");
    assert.equal(sessionStateDigest(resumed), resumed.state_digest);
  } finally {
    rmSync(directory, {recursive: true, force: true});
  }
});

test("optimistic revision prevents a silent lost update", () => {
  const runtime = createDurableDefineRuntime();
  createRuntimeSession(runtime, "define-session:conflict");
  const first = runtime.execute(runtimeCommand("command:first", "open-question", "define-session:conflict", 1, {
    question_id: "question:first", question: "First?", owner_route: "owner:first",
  }));
  const second = runtime.execute(runtimeCommand("command:second", "open-question", "define-session:conflict", 1, {
    question_id: "question:second", question: "Second?", owner_route: "owner:second",
  }));
  assert.equal(first.outcome, "confirmed");
  assert.equal(second.outcome, "conflict");
  assert.equal(second.failure_class, "revision-conflict");
  assert.equal(runtime.inspect("define-session:conflict").current_question_id, "question:first");
});

test("exact command retry returns the prior result without a second transition", () => {
  const repository = new InMemorySessionRepository();
  const runtime = createDurableDefineRuntime({repository});
  const command = runtimeCommand("command:create-idempotent", "create-session", "define-session:idempotent", 0, {
    goal: "Define X", intent: "Bound X", context: "X is unclear", consumer: "test",
  });
  const first = runtime.execute(command);
  const second = runtime.execute(command);
  assert.deepEqual(second, first);
  const record = repository.load("define-session:idempotent");
  assert.equal(record.snapshot.revision, 1);
  assert.equal(record.events.length, 1);
});

test("failed persistence never advances the last confirmed snapshot", () => {
  const repository = new InMemorySessionRepository();
  const runtime = createDurableDefineRuntime({repository});
  createRuntimeSession(runtime, "define-session:storage-failure");
  const before = runtime.inspect("define-session:storage-failure");
  repository.injectStorageFailure();
  const result = runtime.execute(runtimeCommand("command:failed-open", "open-question", "define-session:storage-failure", 1, {
    question_id: "question:unsaved", question: "Unsaved?", owner_route: "owner:test",
  }));
  assert.equal(result.outcome, "storage-failure");
  assert.deepEqual(runtime.inspect("define-session:storage-failure"), before);
});

test("visibility does not grant answer authority", () => {
  const runtime = createDurableDefineRuntime();
  createRuntimeSession(runtime, "define-session:authority");
  runtime.execute(runtimeCommand("command:open-authority", "open-question", "define-session:authority", 1, {
    question_id: "question:authority", question: "Who decides?", owner_route: "owner:meaning",
  }));
  const visible = runtime.inspect("define-session:authority");
  assert.equal(visible.current_question_id, "question:authority");
  const denied = runtime.execute(runtimeCommand("command:denied-answer", "record-answer", "define-session:authority", 2, {
    question_id: "question:authority", answer: "The observer decides.",
  }, {actor_ref: "actor:observer", allowed_effects: []}));
  assert.equal(denied.outcome, "denied");
  assert.equal(runtime.inspect("define-session:authority").answers.length, 0);
});

test("only sufficient frozen context permits a meaning question", () => {
  const runtime = createDurableDefineRuntime();
  const sessionId = "define-session:context-gate";
  const created = runtime.execute(runtimeCommand("command:create-context-gate", "create-session", sessionId, 0, {
    goal: "Define X", intent: "Bound X", context: "Candidate context", consumer: "test",
  }));
  assert.equal(created.outcome, "confirmed");
  const blocked = runtime.execute(runtimeCommand("command:blocked-question", "open-question", sessionId, 1, {
    question_id: "question:blocked", question: "What is X?", owner_route: "owner:x",
  }));
  assert.equal(blocked.outcome, "invalid");
  assert.equal(blocked.failure_class, "domain.context-not-sufficient");
  const evaluated = runtime.execute(runtimeCommand("command:context-sufficient", "set-context-evaluation", sessionId, 1, {
    evaluation_id: "evaluation:context-gate",
    status: "sufficient",
    derivation: "Frozen fixture requirements are met.",
    residue: [],
    evaluator_receipt_ref: "receipt:context-gate",
  }));
  assert.equal(evaluated.outcome, "confirmed");
  const opened = runtime.execute(runtimeCommand("command:allowed-question", "open-question", sessionId, 2, {
    question_id: "question:allowed", question: "What is X?", owner_route: "owner:x",
  }));
  assert.equal(opened.outcome, "confirmed");
});

test("context resolution preserves source precedence and visible conflicts", () => {
  const result = resolveDefineContextCandidates({
    explicit_user: [{context_key: "project", content: "Atlas", source_ref: "user:opening"}],
    related_references: [{context_key: "domain", content: "Knowledge systems", source_ref: "ref:brief"}],
    current_window: [{context_key: "project", content: "Inferred Orion", source_ref: "window:1"}],
    saved_session: [{context_key: "goal", content: "Create shared meaning", source_ref: "session:prior"}],
  });
  assert.deepEqual(result.source_order, ["explicit-user", "related-reference", "current-window", "saved-session"]);
  assert.equal(result.candidates.length, 4);
  assert.equal(result.selected_candidate_ids.length, 3);
  assert.equal(result.conflicts.length, 1);
  assert.equal(result.conflicts[0].winner_candidate_id, result.candidates[0].candidate_id);
  assert.equal(result.user_correction_required, true);
});

test("Define evaluator adapter is deterministic and historical replay performs no reevaluation", () => {
  let calls = 0;
  const adapter = createDefineContextSufficiencyAdapter({evaluate: (request, telemetry) => {
    calls += 1;
    telemetry.evaluator_calls = (telemetry.evaluator_calls ?? 0) + 1;
    return {outcome: "RecommendedUnderSnapshot", derivation: [`request:${request.define_job_ref}`], residue: []};
  }});
  const request = {define_job_ref: "define-job:fixture", requirements: ["goal", "owner"], candidates: ["candidate:1"]};
  const first = adapter.evaluate(request);
  const second = adapter.evaluate({...request});
  const replayed = adapter.replay(request);
  assert.equal(first.status, "sufficient");
  assert.deepEqual(second, first);
  assert.deepEqual(replayed, first);
  assert.equal(calls, 1);
  assert.equal(first.authority_effect, "none");
});

test("runtime audit records contain no prompt, answer, or source content", () => {
  const records = [];
  const runtime = createDurableDefineRuntime({audit: (record) => records.push(record), clock: () => "2026-09-07T00:00:00.000Z"});
  createRuntimeSession(runtime, "define-session:audit");
  runtime.execute(runtimeCommand("command:open-audit", "open-question", "define-session:audit", 1, {
    question_id: "question:audit", question: "Sensitive prompt text", owner_route: "owner:audit",
  }));
  const serialized = JSON.stringify(records);
  assert.doesNotMatch(serialized, /Sensitive prompt text|One shared candidate context/);
  assert.equal(records[0].session_id_hash.length, 64);
  assert.equal(Object.hasOwn(records[0], "session_id"), false);
});

test("clean replay yields byte-identical snapshots and events", () => {
  function replay() {
    const repository = new InMemorySessionRepository();
    const runtime = createDurableDefineRuntime({repository});
    createRuntimeSession(runtime, "define-session:replay");
    runtime.execute(runtimeCommand("command:open-replay", "open-question", "define-session:replay", 1, {
      question_id: "question:replay", question: "Meaning?", owner_route: "owner:replay",
    }));
    runtime.execute(runtimeCommand("command:defer-replay", "defer-question", "define-session:replay", 2, {
      question_id: "question:replay", reason: "Owner review required",
    }));
    return repository.load("define-session:replay");
  }
  assert.deepEqual(replay(), replay());
});

test("file repository rejects a tampered confirmed snapshot", () => {
  const directory = mkdtempSync(join(tmpdir(), "define-runtime-tamper-"));
  try {
    const repository = new JsonFileSessionRepository(directory);
    const runtime = createDurableDefineRuntime({repository});
    createRuntimeSession(runtime, "define-session:tamper");
    const path = repository.pathFor("define-session:tamper");
    const record = JSON.parse(readFileSync(path, "utf8"));
    record.snapshot.context = "tampered";
    writeFileSync(path, JSON.stringify(record));
    assert.throws(() => repository.load("define-session:tamper"), /snapshot-digest-mismatch/);
  } finally {
    rmSync(directory, {recursive: true, force: true});
  }
});
