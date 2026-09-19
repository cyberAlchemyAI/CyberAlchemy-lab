// Candidate public API. All decisions and receipts remain non-authorizing.
export {loadRepositoryProfile} from "./src/config.mjs";
export {materializeDefinitionCatalog, materializeOntologySnapshot} from "./src/source-adapters.mjs";
export {evaluateTurnPreflight} from "./src/preflight.mjs";
export {buildRequestContext, REQUEST_CONTEXT_KEY} from "./src/request-context.mjs";
export {evaluateEffectRequest, bindApprovalResponse} from "./src/effect-boundary.mjs";
export {
  evaluateDualLaneContinuation,
  isContinuationReference,
  materializeObjectiveFrontier,
  normalizeContinuationProposals,
  projectObjectiveFrontierForTurnStart,
} from "./src/continuation.mjs";
export {createEvidenceLedger} from "./src/evidence-ledger.mjs";
export {createCodexAppServerWrapper} from "./src/wrapper.mjs";
export {
  acquireReasoningStateWriterLock,
  bindCacheTelemetryObservation,
  appendReasoningCounterevidence,
  appendReasoningStateReduction,
  assessReasoningStateTransition,
  checkpointReasoningStateByRisk,
  compareReasoningProvenance,
  createAppendOnlyFileReasoningStateSink,
  createMemoryReasoningStateSink,
  createReasoningStateLedger,
  createReasoningStateBranch,
  deriveReasoningReplayFixture,
  executeReasoningStateTransition,
  exportPortableReasoningEpoch,
  importPortableReasoningEpoch,
  materializeCacheAffinityProjection,
  materializeContextBoundCacheAffinityProjection,
  REASONING_CACHE_TELEMETRY_OBSERVATION_SCHEMA,
  planReasoningStateTransition,
  getReasoningStateFrontier,
  getReasoningStateEpoch,
  listReasoningStateFrontiers,
  listReasoningStateEpochs,
  rebuildReasoningStateIndexes,
  recoverReasoningStateLedger,
  selectReasoningCheckpointPolicy,
  selectReusableCounterevidence,
  sealReasoningStateFrontier,
  selectRecoverableCheckpoint,
  verifyReasoningStateFrontier,
  verifyReasoningStateTransitionPlan,
  verifyReasoningStateTransitionReceipt,
  verifyReasoningReplayFixture,
  verifyPortableReasoningEpoch,
  verifyReasoningStateLog,
} from "../reasoning-state-runtime/index.mjs";
export {
  assessReasoningEvolution,
  composeReasoningEvolution,
  loadReasoningPolicy,
  materializeContextReductionPlan,
} from "../reasoning-policy-runtime/index.mjs";
export {CODEX_SEMANTIC_COMPLETION_SCHEMA, evaluateSemanticCompletion} from "./src/semantic-completion.mjs";
export {CODEX_EVOLUTION_SIGNAL_EMISSION_SCHEMA, emitCompletionImprovementSignals} from "./src/evolution-signals.mjs";
export {addIntentLifecycleContext, CODEX_INTENT_LIFECYCLE_SCHEMA, INTENT_CONTEXT_KEY, prepareCodexIntentLifecycle} from "./src/intent-lifecycle.mjs";
export {
  deriveReasoningReceiptConstraints,
  isVerifiedReasoningReceiptConstraints,
  REASONING_RECEIPT_CONSTRAINT_SCHEMA,
} from "./src/reasoning-receipt-constraints.mjs";
export {runStdioProxy} from "./src/stdio-proxy.mjs";
export {resolveBackendCommand, spawnCodexBackend} from "./src/backend.mjs";
export {
  ACKNOWLEDGED_CONTINUITY_MODE,
  createPersistentGateway,
  GATEWAY_ACK_SCHEMA,
  GATEWAY_CONNECT_SCHEMA,
  GATEWAY_CONNECTED_SCHEMA,
  GATEWAY_DELIVERY_SCHEMA,
  GATEWAY_SESSION_EXPIRATION_SCHEMA,
  GATEWAY_REQUEST_META_KEY,
} from "./src/gateway.mjs";
export {deriveGatewayReasoningStateProfile} from "./src/gateway-reasoning-state.mjs";
export {CACHE_TELEMETRY_EXTRACTION_SCHEMA, compareProviderCacheObservations, extractProviderCacheUsage, PROVIDER_CACHE_USAGE_SCHEMA} from "./src/cache-telemetry.mjs";
export {
  CODEX_CONTEXT_WINDOW_OBSERVATION_SCHEMA,
  CODEX_CONTEXT_WINDOW_TELEMETRY_SCHEMA,
  createCodexContextWindowTracker,
  extractCodexContextWindowObservation,
} from "./src/context-window-telemetry.mjs";
export {
  createFileGatewaySessionStore,
  createMemoryGatewaySessionStore,
  GATEWAY_SESSION_EVENT_SCHEMA,
  GATEWAY_SESSION_INDEX_SCHEMA,
} from "./src/gateway-session-store.mjs";
export {runGatewayClientProxy} from "./src/gateway-client.mjs";
export {connectGatewayRpcTransport} from "./src/gateway-client.mjs";
export {AppServerRpcError, createAppServerRpcClient, spawnAppServerRpcTransport} from "./src/rpc-client.mjs";
export * from "./src/protocol.mjs";
