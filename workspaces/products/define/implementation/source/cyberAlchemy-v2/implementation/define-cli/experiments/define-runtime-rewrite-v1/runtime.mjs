import {invoke} from "./generated/app/function/index.mjs";

const nonempty = value => typeof value === "string" && value.trim().length > 0;

export function createSession({context_sufficient = true} = {}) {
  return {
    revision: 1,
    context_sufficient,
    current_question: null,
    questions: [],
    answers: [],
    gaps: [],
    lifecycle_state: context_sufficient ? "ready" : "awaiting-context",
    authority_effect: "none",
  };
}

function factsFor(state, command) {
  const currentQuestionPresent = state.current_question !== null;
  const questionMatches = currentQuestionPresent && command.question_id === state.current_question.question_id;
  const payloadComplete = command.type === "open-question"
    ? nonempty(command.question_id) && nonempty(command.question) && nonempty(command.owner_route)
    : command.type === "record-answer"
      ? nonempty(command.question_id) && nonempty(command.answer)
      : nonempty(command.question_id);
  return {
    command: command.type,
    context_sufficient: state.context_sufficient,
    current_question_present: currentQuestionPresent,
    question_matches: questionMatches,
    payload_complete: payloadComplete,
  };
}

export async function transition(state, command) {
  const decision = await invoke(factsFor(state, command));
  if (decision.status === "block") return {state, decision};

  const next = structuredClone(state);
  next.revision += 1;
  if (command.type === "open-question") {
    const question = {
      question_id: command.question_id.trim(),
      question: command.question.trim(),
      owner_route: command.owner_route.trim(),
      state: "open",
    };
    next.questions.push(question);
    next.current_question = question;
  } else {
    const question = next.questions.find(item => item.question_id === command.question_id);
    if (command.type === "record-answer") {
      question.state = "answered";
      next.answers.push({question_id: command.question_id, answer: command.answer.trim()});
    } else {
      question.state = "deferred";
      next.gaps.push({question_id: command.question_id, status: "open"});
    }
    next.current_question = null;
  }
  next.lifecycle_state = decision.next_state;
  return {state: next, decision};
}
