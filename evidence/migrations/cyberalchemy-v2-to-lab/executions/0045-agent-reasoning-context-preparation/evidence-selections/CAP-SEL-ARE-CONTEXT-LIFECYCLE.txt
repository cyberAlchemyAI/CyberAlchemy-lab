// Candidate API only. These pure functions grant no admission, conformance,
// runtime, publication, deployment, or external-effect authority.
export {resolveDefinitionClosure} from "./src/definition-closure.mjs";
export {lockOntologySelectors} from "./src/ontology-selector-lock.mjs";
export {constructNecessaryContextBasis} from "./src/context-basis.mjs";
export {bindContextWindowView} from "./src/context-window-view.mjs";
export {composeContextBasis} from "./src/compose.mjs";
export {assembleContextEnvelope, reuseContextEnvelopeProjection} from "./src/context-envelope.mjs";
export {assessContextRefresh} from "./src/context-refresh.mjs";
export {composeContextLifecycle} from "./src/lifecycle.mjs";
export {selectRequestContext} from "./src/request-context-selector.mjs";
export {
  CONTEXT_COMPACTION_PROJECTION_SCHEMA,
  DEFAULT_CONTEXT_COMPACTION_POLICY,
  projectCompactionAwareContext,
  verifyCompactionProjection,
} from "./src/context-compaction-projection.mjs";
