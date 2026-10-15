import {createSession, transition} from "./runtime.mjs";

let state = createSession();
const commands = [
  {
    type: "open-question",
    question_id: "question:customer",
    question: "Does customer mean the buyer, account owner, or recipient?",
    owner_route: "Definitions Governance owner",
  },
  {
    type: "record-answer",
    question_id: "question:customer",
    answer: "For this synthetic refund example, customer means the buyer.",
  },
  {
    type: "open-question",
    question_id: "question:refund-window",
    question: "When does the refund window begin?",
    owner_route: "Product owner",
  },
  {type: "defer-question", question_id: "question:refund-window"},
];

for (const command of commands) {
  const result = await transition(state, command);
  state = result.state;
  process.stdout.write(`${JSON.stringify({command: command.type, question_id: command.question_id, decision: result.decision, revision: state.revision, lifecycle_state: state.lifecycle_state})}\n`);
}
process.stdout.write(`${JSON.stringify({final_state: state}, null, 2)}\n`);
