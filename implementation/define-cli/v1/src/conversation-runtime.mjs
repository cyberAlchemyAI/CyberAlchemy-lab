import {callLab, composeDefineContext} from "./context-adapter.mjs";
import {digest} from "./canonical.mjs";
import {evaluateDefineLanguageQuality} from "./language-quality.mjs";
import {runDefineSession} from "./session-runtime.mjs";
import {execute as executeCompiledScopeReadiness} from "../generated/define-service/entries/ScopeReadiness/app/function/behavior.mjs";

const YES = new Set(["y", "yes", "confirm", "confirmed", "looks right", "correct"]);

function normalized(value, fallback = null) {
  const text = String(value ?? "").trim();
  return text || fallback;
}

function renderList(values, fallback = "none named") {
  return Array.isArray(values) && values.length > 0 ? values.join("; ") : fallback;
}

function renderScope(scope) {
  return [
    "\nHere is the scope I heard:",
    `  Domain: ${normalized(scope.domain, "not named")}`,
    `  Subject: ${normalized(scope.subject, "not named")}`,
    `  Project: ${normalized(scope.project, "not named")}`,
    `  Context: ${normalized(scope.context, "not named")}`,
    `  Desired outcome: ${normalized(scope.desired_outcome, "not named")}`,
    `  Intent: ${normalized(scope.intent, "not named")}`,
    `  Consumer: ${normalized(scope.consumer, "human:define-cli")}`,
    "  Language:",
    `    Your phrases: ${renderList(scope.language?.user_phrases)}`,
    `    Candidate terms: ${renderList(scope.language?.terms)}`,
    `    Distinctions: ${renderList(scope.language?.distinctions)}`,
    `    Relationships: ${renderList(scope.language?.relationships)}`,
    `    Constraints: ${renderList(scope.language?.constraints)}`,
    `    Owners: ${renderList(scope.language?.owners, "unknown")}`,
    `    Open questions: ${renderList(scope.language?.open_questions)}`,
  ].join("\n");
}

function renderQuality(evaluation) {
  return [
    "\nLanguage quality checks:",
    `  Semantic grounding: ${evaluation.checks.semantic_grounding}`,
    `  Non-collapse: ${evaluation.checks.non_collapse}`,
    `  Orthogonality: ${evaluation.checks.orthogonality}`,
    `  Overall: ${evaluation.status}`,
    ...(evaluation.status === "block" ? ["  Another answer is needed before this language can be confirmed."] : []),
  ].join("\n");
}

function qualityRepairQuestion(scope, evaluation) {
  const focus = evaluation.repair_focus;
  const reason = evaluation.reason_codes.find((candidate) => focus === "non-collapse"
    ? candidate.includes("non-collapse") || candidate === "quality.term-normalized-collision"
    : focus === "semantic-grounding"
      ? candidate.includes("grounding")
      : focus === "orthogonality"
        ? candidate.includes("orthogonality")
        : true) ?? evaluation.reason_codes[0] ?? "";
  const pair = reason.match(/:(\d+):(\d+)$/);
  if (focus === "non-collapse") {
    const left = pair ? scope.language.terms[Number(pair[1])] : scope.language.terms[0];
    const right = pair ? scope.language.terms[Number(pair[2])] : scope.language.terms[1];
    if (left && right) return `What operational difference separates “${left}” from “${right}”? If there is none, should they become one term?`;
    return "Which candidate terms describe the same thing, and which distinction should remain?";
  }
  if (focus === "semantic-grounding") {
    const target = reason.match(/:(terms|distinctions|relationships|constraints|owners|open_questions):(\d+)$/);
    const item = target ? scope.language[target[1]]?.[Number(target[2])] : null;
    return item
      ? `Which exact words of yours support “${item}”, or should I remove it from the candidate language?`
      : "Which part of the candidate language is not grounded in what you said, and what should replace it?";
  }
  if (focus === "orthogonality") {
    const orthogonality = scope.language_quality.orthogonality;
    const axes = orthogonality.axes.map((axis) => `“${axis.label}”`).join(" and ");
    return axes
      ? `Can ${axes} change independently? If not, what connects them, who owns that connection, and what does it affect?`
      : "Which classification dimensions are present, and what different question does each one answer?";
  }
  return "What should I correct before treating this candidate language as ready for your confirmation?";
}

function renderOption(option, index, total) {
  return [
    `\nOption ${index + 1} of ${total}: ${option.term}`,
    `  Why it matters: ${option.why_it_matters}`,
    `  Candidate meaning: ${normalized(option.candidate_definition, "No meaning proposed yet")}`,
    `  Boundary: ${normalized(option.boundary, "Candidate only; no canonical or effect status")}`,
    "  Actions: [a]ccept  [d]iscuss  [e]dit  [o]pen/defer  [q]uit",
  ].join("\n");
}

function exactScope(scope, consumer) {
  const contextParts = [
    scope.domain && `Domain: ${scope.domain}`,
    scope.subject && `Subject: ${scope.subject}`,
    scope.project && `Project: ${scope.project}`,
    scope.context && `Context: ${scope.context}`,
    scope.language?.user_phrases?.length && `User language: ${scope.language.user_phrases.join("; ")}`,
    scope.language?.terms?.length && `Candidate terms: ${scope.language.terms.join("; ")}`,
    scope.language?.distinctions?.length && `Distinctions: ${scope.language.distinctions.join("; ")}`,
    scope.language?.relationships?.length && `Relationships: ${scope.language.relationships.join("; ")}`,
    scope.language?.constraints?.length && `Constraints: ${scope.language.constraints.join("; ")}`,
    scope.language?.owners?.length && `Owners: ${scope.language.owners.join("; ")}`,
    scope.language?.open_questions?.length && `Open questions: ${scope.language.open_questions.join("; ")}`,
  ].filter(Boolean);
  return {
    goal: normalized(scope.desired_outcome),
    intent: normalized(scope.intent),
    context: contextParts.join("\n"),
    consumer: normalized(scope.consumer, consumer),
  };
}

export function evaluateDefineScopeReadiness(scope, agentScopeReady, languageStatus) {
  return executeCompiledScopeReadiness({input: {
    agent_scope_ready: agentScopeReady === true,
    context_present: normalized(scope?.context) !== null,
    desired_outcome_present: normalized(scope?.desired_outcome) !== null,
    intent_present: normalized(scope?.intent) !== null,
    language_not_blocked: languageStatus !== "block",
  }}, {});
}

function scopeRepairPrompt(decision) {
  const labels = {context: "context", "desired-outcome": "desired outcome", intent: "intent"};
  return labels[decision.next_focus]
    ? `Before scope review, tell me more about: ${labels[decision.next_focus]}.`
    : "Continue describing the domain, intended consumers, language, distinctions, constraints, owners, and open questions.";
}

function optionConcept(option) {
  const term = option.term.trim();
  return {
    concept_id: `concept:${digest(term).slice(0, 16)}`,
    term,
    question: option.question,
    owner_route: "Definitions Governance owner",
  };
}

export async function runDefineConversation(input) {
  const {agent, ask, write, repository_root: repositoryRoot} = input;
  const consumer = input.consumer ?? "human:define-cli";
  let userText = normalized(input.opening);
  if (!userText) userText = normalized(await ask("What are you working on? You can begin with a domain, subject, context, or project.\n> "));
  if (!userText) return {ok: false, stopped: true, reason_codes: ["define-conversation.opening-required"], authority_effect: "none"};

  let scope = null;
  let options = [];
  let languageQualityEvaluation = null;
  let turnCount = 0;
  write("\nDefine — new-work and meaning discovery\nStart broadly. I will learn your scope and language, ask one useful question at a time, then let you confirm the result and review each candidate meaning.\n");
  while (!scope) {
    if (++turnCount > 24) return {ok: false, stopped: true, reason_codes: ["define-conversation.turn-limit"], authority_effect: "none"};
    write("\nDefine is considering that...\n");
    const turn = await agent.respond({mode: "discovery", user_input: userText, scope_confirmed: false});
    write(`\nDefine: ${turn.message}\n`);
    const quality = evaluateDefineLanguageQuality(turn.scope, turn.options, {user_confirmed: false});
    const scopeDecision = evaluateDefineScopeReadiness(turn.scope, turn.scope_ready, quality.status);
    const qualityBlocksReadiness = scopeDecision.next_focus === "language-quality";
    if (qualityBlocksReadiness) write(`${renderQuality(quality)}\n`);
    if (scopeDecision.status !== "ready") {
      if (qualityBlocksReadiness) write(`\n${qualityRepairQuestion(turn.scope, quality)}\n`);
      else if (turn.question) write(`\n${turn.question}\n`);
      else write(`\n${scopeRepairPrompt(scopeDecision)}\n`);
      userText = normalized(await ask("\nYou: "));
      if (userText === "/quit") return {ok: false, stopped: true, reason_codes: ["define-conversation.user-stopped"], authority_effect: "none"};
      if (userText === "/review") userText = "Summarize the scope now and expose anything still missing.";
      continue;
    }
    write(`${renderScope(turn.scope)}\n`);
    write(`${renderQuality(quality)}\n`);
    const confirmation = normalized(await ask("\nIs this the scope you mean? [y]es, or tell me what to change\n> "));
    if (YES.has(confirmation.toLowerCase())) {
      scope = turn.scope;
      options = turn.options;
      languageQualityEvaluation = evaluateDefineLanguageQuality(scope, options, {user_confirmed: true});
      if (languageQualityEvaluation.status !== "pass") {
        throw new Error(`define-conversation.confirmed-language-quality-${languageQualityEvaluation.status}`);
      }
      break;
    }
    if (confirmation === "/quit") return {ok: false, stopped: true, reason_codes: ["define-conversation.user-stopped"], authority_effect: "none"};
    userText = `The proposed scope is not confirmed. Revise it using this correction: ${confirmation}`;
  }

  if (options.length === 0) {
    write("\nDefine is preparing the review options...\n");
    const prepared = await agent.respond({mode: "prepare-options", user_input: "The scope is confirmed. Prepare the bounded meaning options for review.", scope_confirmed: true, confirmed_scope: scope});
    write(`\nDefine: ${prepared.message}\n`);
    options = prepared.options;
  }
  if (options.length === 0) return {ok: false, stopped: true, reason_codes: ["define-conversation.no-options"], authority_effect: "none"};
  languageQualityEvaluation = evaluateDefineLanguageQuality(scope, options, {user_confirmed: true});
  if (languageQualityEvaluation.status !== "pass") return {ok: false, stopped: true, reason_codes: languageQualityEvaluation.reason_codes, authority_effect: "none"};

  const concepts = [];
  const responses = [];
  for (let index = 0; index < options.length; index += 1) {
    let option = options[index];
    let resolved = false;
    while (!resolved) {
      write(`${renderOption(option, index, options.length)}\n`);
      const choice = normalized(await ask("> "), "o").toLowerCase();
      const concept = optionConcept(option);
      if (choice === "a" || choice === "accept") {
        if (!normalized(option.candidate_definition)) {
          write("\nThere is no candidate meaning to accept. Discuss, edit, or leave it open.\n");
          continue;
        }
        concepts.push(concept);
        responses.push({concept_id: concept.concept_id, action: "propose", payload: {definition: option.candidate_definition, plain_explanation: option.candidate_definition, boundary: normalized(option.boundary)}});
        resolved = true;
      } else if (choice === "e" || choice === "edit") {
        const revised = normalized(await ask("Your exact candidate meaning:\n> "));
        if (!revised) continue;
        concepts.push(concept);
        responses.push({concept_id: concept.concept_id, action: "propose", payload: {definition: revised, plain_explanation: revised, boundary: normalized(option.boundary)}});
        resolved = true;
      } else if (choice === "o" || choice === "open" || choice === "defer") {
        const reason = normalized(await ask("Why should this remain open? (optional)\n> "), "Deferred during one-by-one review");
        concepts.push(concept);
        responses.push({concept_id: concept.concept_id, action: "defer", payload: {reason}});
        resolved = true;
      } else if (choice === "d" || choice === "discuss") {
        const comment = normalized(await ask("What feels wrong or unclear?\n> "));
        write("\nDefine is reconsidering this option...\n");
        const discussed = await agent.respond({mode: "discuss-option", user_input: comment, scope_confirmed: true, confirmed_scope: scope, current_option: option});
        write(`\nDefine: ${discussed.message}\n`);
        if (discussed.options.length > 0) {
          const replacement = discussed.options[0];
          if (replacement.option_id !== option.option_id || replacement.term.trim().toLowerCase() !== option.term.trim().toLowerCase()) {
            throw new Error("define-conversation.discussion-option-identity-drift");
          }
          option = replacement;
        }
      } else if (choice === "q" || choice === "quit") {
        return {ok: false, stopped: true, reason_codes: ["define-conversation.user-stopped-during-review"], authority_effect: "none"};
      } else {
        write("\nChoose accept, discuss, edit, open, or quit.\n");
      }
    }
  }

  const finish = normalized(await ask("\nCreate the candidate Definition Pack from these reviewed options? [y/n]\n> "), "n").toLowerCase();
  if (!YES.has(finish)) return {ok: false, stopped: true, reason_codes: ["define-conversation.pack-not-confirmed"], authority_effect: "none"};
  languageQualityEvaluation = evaluateDefineLanguageQuality(scope, responses.map((r,index) => ({term:concepts[index].term,candidate_definition:r.payload.definition ?? ''})), {user_confirmed:true});
  if (languageQualityEvaluation.status !== 'pass') return {ok:false,reason_codes:languageQualityEvaluation.reason_codes,authority_effect:'none'};
  const sessionScope = exactScope(scope, consumer);
  if (!sessionScope.goal || !sessionScope.intent || !sessionScope.context) {
    return {ok: false, stopped: true, reason_codes: ["define-conversation.confirmed-scope-incomplete"], authority_effect: "none"};
  }
  const contextResult = composeDefineContext({...sessionScope, store:input.store, subject:input.subject, definition_refs:input.definition_refs}, repositoryRoot);
  if (!contextResult.ok) return contextResult;
  const result = runDefineSession({
    ...sessionScope,
    concepts,
    responses,
    context_result: contextResult,
    language_scope: scope.language,
    language_quality_evidence: scope.language_quality,
    language_quality_evaluation: languageQualityEvaluation,
  });
  if(result.ok) {result.schema_version='cal.define-cli-result/v1';result.lab_binding={source_snapshot_digest:contextResult.context_envelope.source_snapshot_digest, head:contextResult.context_envelope.head, envelope:contextResult.context_envelope, authority_effect:"none"};callLab("validate-result",{result},repositoryRoot);}
  return result;
}
