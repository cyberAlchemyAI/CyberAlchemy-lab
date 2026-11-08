import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {getCrossGeneratorSource as source, CROSS_GENERATOR_SOURCE_CAPSULE_SHA256} from './cross-generator-sources.js';
import {createCrossGeneratorBoundary} from './reconciled-cross-generator-boundary.js';
import {createCrossGeneratorPolicyControls} from './reconciled-cross-generator-policy.js';
import {createCrossGeneratorStateMachineControls} from './reconciled-cross-generator-state-machine.js';
import {createCrossGeneratorFactoryControls} from './reconciled-cross-generator-factory.js';
import {createCrossGeneratorOwnedValueControls} from './reconciled-cross-generator-owned-values.js';
import {createCrossGeneratorValueProducerControls} from './reconciled-cross-generator-value-producer.js';
import {createCrossGeneratorFactorySurface, createCrossGeneratorOwnedValueSurface, createCrossGeneratorValueProducerSurface} from './reconciled-cross-generator-factory-surface.js';
import {createCrossGeneratorOperationControls} from './reconciled-cross-generator-operation.js';
import {createCrossGeneratorWorkflowControls} from './reconciled-cross-generator-workflow.js';
import {createCrossGeneratorWorkflowSurface} from './reconciled-cross-generator-workflow-surface.js';
import {createCrossGeneratorWorkflowAudit} from './reconciled-cross-generator-workflow-audit.js';

export const CROSS_GENERATOR_PUBLIC_DEFINITION_SHA256 = '1dfac8d1cb4991bcd1b3670af4b16e0b59b5ae6c238afa965003cb820b078b8c';
const families = ['policy', 'state-machine', 'factory-rule', 'owned-values', 'value-producer', 'operation', 'workflow'] as const;
export type CrossGeneratorFamily = typeof families[number];
type Witness = {family: CrossGeneratorFamily; selector: string; kind: 'family-protocol-selected' | 'original-wrapper-identity-required'};
type Obligation = {
  family: CrossGeneratorFamily; selector: string; state: 'ready' | 'not_evaluable' | 'inapplicable' | 'fail';
  reason: string | null; case_count: number; batch_count: number;
  protocol_edges: readonly string[]; identity_edges: readonly string[];
};
const fail = (reason: string): never => {throw new TypeError('CROSS_GENERATOR_PUBLIC:' + reason);};
function freeze<T>(v: T): T {
  if (v && typeof v === 'object' && !Object.isFrozen(v)) {Object.values(v).forEach(freeze); Object.freeze(v);}
  return v;
}
function capture<T>(build: () => T) {
  try {return {state: 'prepared' as const, value: build()};}
  catch (error) {return {state: 'fail' as const, reason: error instanceof Error ? error.message : String(error)};}
}
const kinds: Record<CrossGeneratorFamily, readonly string[]> = {
  policy: ['Policy'], 'state-machine': ['State Machine'], 'factory-rule': ['Entity', 'Value Object'],
  'owned-values': ['Entity', 'Value Object'], 'value-producer': ['Enum'], operation: ['Operation'], workflow: ['Workflow']
};

/** Whole-project obligation preparation. No selected row is an executed check. */
export function prepareCrossGeneratorVerification(graph: CompiledProjectGraph, plan: ReconciledProjectPlan) {
  if (sha256(source('public')) !== CROSS_GENERATOR_PUBLIC_DEFINITION_SHA256) fail('definition drift');
  const boundary = createCrossGeneratorBoundary(graph, plan, source('verification'));
  const bindings = {
    policy: capture(() => ({controls: createCrossGeneratorPolicyControls(graph, plan, boundary, source('policy'))})),
    'state-machine': capture(() => ({controls: createCrossGeneratorStateMachineControls(graph, plan, boundary, source('state_machine'))})),
    'factory-rule': capture(() => {
      const controls = createCrossGeneratorFactoryControls(graph, plan, boundary, source('factory'));
      return {controls, surface: createCrossGeneratorFactorySurface(graph, plan, boundary, controls, source('factory_execution'))};
    }),
    'owned-values': capture(() => {
      const controls = createCrossGeneratorOwnedValueControls(graph, plan, boundary, source('owned_values'));
      return {controls, surface: createCrossGeneratorOwnedValueSurface(graph, plan, boundary, controls, source('owned_values_execution'))};
    }),
    'value-producer': capture(() => {
      const controls = createCrossGeneratorValueProducerControls(graph, plan, boundary, source('value_producer'));
      return {controls, surface: createCrossGeneratorValueProducerSurface(graph, plan, boundary, controls, source('value_producer'))};
    }),
    operation: capture(() => ({controls: createCrossGeneratorOperationControls(graph, plan, boundary, source('operation'), source('operation_protocol'))})),
    workflow: capture(() => {
      const controls = createCrossGeneratorWorkflowControls(graph, plan, boundary, source('workflow'), source('operation'), source('workflow_protocol'), source('workflow_cases'));
      const surface = createCrossGeneratorWorkflowSurface(graph, plan, boundary, source('workflow'), source('operation'));
      return {controls, surface, audit: createCrossGeneratorWorkflowAudit(graph, plan, surface)};
    })
  };
  const rows: Obligation[] = [], edgeById = new Map(boundary.edges.map(e => [e.edge_sha256, e]));
  const witnesses = new Map<string, Witness[]>(boundary.edges.map(e => [e.edge_sha256, []]));
  // Each wrapper identity requirement binds a single original source import;
  // it does not extend to the target's transitive behavior.
  const identityEdges = (from: string, to: string): string[] => {
    const edges = boundary.edges.filter(e => e.importer_path === from && e.target_path === to && e.category === 'generated-runtime');
    if (edges.length !== 1) fail('original wrapper incidence');
    return edges.map(e => e.edge_sha256);
  };
  const summaries = families.map(family => {
    const binding = bindings[family], selectors = graph.nodes.filter(n => kinds[family].includes(n.kind)).map(n => n.selector).sort();
    if (binding.state === 'fail') {
      for (const selector of selectors) rows.push({family, selector, state: 'fail', reason: binding.reason, case_count: 0, batch_count: 0, protocol_edges: [], identity_edges: []});
      return {family, state: 'fail' as const, reason: binding.reason, controls_sha256: null, row_count: selectors.length};
    }
    const controls = binding.value.controls;
    if (canonicalJson(controls.rows.map(r => r.selector).sort()) !== canonicalJson(selectors)) fail('complete family inventory:' + family);
    for (const row of controls.rows) {
      const protocol: string[] = [], identity: string[] = [];
      if (row.state === 'ready') {
        if ('protocol_edge_sha256s' in row) protocol.push(...row.protocol_edge_sha256s);
        else if ('protocol' in row) protocol.push(...row.protocol.map(p => p.edge_sha256));
        else if ('direct_edges' in row) {
          protocol.push(...row.direct_edges);
          identity.push(...identityEdges(row.relative_path, row.provider_path));
          if ('forward' in row) for (const operation of row.forward) identity.push(...identityEdges(operation.relative_path, operation.provider_path));
          else for (const module of row.modules) if (module.role === 'event-wrapper') {
            const imports = module.imports.filter(i => !i.type_only);
            if (imports.length !== 1) fail('Event wrapper incidence');
            identity.push(...identityEdges(module.relative_path, imports[0]!.target_path));
          }
        } else {
          // Policy and State Machine already bind exact wrapper and Rule
          // incidence, with all Rule call edges visited by the full family.
          for (const module of row.modules) for (const edge of module.edge_sha256s) {
            if (edgeById.get(edge)?.category === 'generated-runtime') protocol.push(edge);
          }
        }
      }
      const unique = (ids: string[]) => [...new Set(ids)].sort();
      for (const [ids, kind] of [[unique(protocol), 'family-protocol-selected'], [unique(identity), 'original-wrapper-identity-required']] as const) {
        for (const id of ids) {
          if (edgeById.get(id)?.category !== 'generated-runtime') fail('foreign or non-runtime protocol edge');
          witnesses.get(id)!.push({family, selector: row.selector, kind});
        }
      }
      rows.push({family, selector: row.selector, state: row.state, reason: row.state === 'ready' ? null : row.reason,
        case_count: row.state === 'ready' ? row.cases.length : 0, batch_count: row.state === 'ready' && 'batches' in row ? row.batches.length : row.state === 'ready' ? 1 : 0,
        protocol_edges: unique(protocol), identity_edges: unique(identity)});
    }
    return {family, state: 'prepared' as const, reason: null, controls_sha256: controls.controls_sha256, row_count: controls.rows.length};
  });
  const edges = boundary.edges.map(edge => ({
    ...edge, behavior_required: edge.category === 'generated-runtime' && edge.cross_generator_kind,
    witnesses: witnesses.get(edge.edge_sha256)!,
    selection_status: edge.category !== 'generated-runtime' ? 'separate-native-obligation' as const : witnesses.get(edge.edge_sha256)!.length ? 'protocol-selected' as const : 'not_evaluable' as const,
    execution_status: 'not_evaluable' as const
  }));
  const body = {
    schema_version: 'domainspec.cross-generator-public-preparation/v1-candidate' as const,
    definition_sha256: CROSS_GENERATOR_PUBLIC_DEFINITION_SHA256, contract_capsule_sha256: CROSS_GENERATOR_SOURCE_CAPSULE_SHA256,
    project_plan_sha256: plan.plan_sha256, source_manifest_sha256: graph.source_manifest.manifest_sha256, boundary_sha256: boundary.boundary_sha256,
    requests: boundary.requests, modules: boundary.modules, roots: boundary.roots, edges, families: summaries, rows,
    remaining: rows.filter(r => r.state === 'not_evaluable' || r.state === 'fail'),
    uncovered_required_edges: edges.filter(e => e.behavior_required && !e.witnesses.length).map(e => e.edge_sha256),
    behavior_status: 'not_evaluable' as const, authority_effect: 'none' as const
  };
  const result = freeze({...body, preparation_sha256: sha256(canonicalJson(body))});
  registered.set(result, freeze({graph, plan, boundary, bindings}));
  return result;
}
export type CrossGeneratorPreparation = ReturnType<typeof prepareCrossGeneratorVerification>;
type BindingState = {
  graph: CompiledProjectGraph; plan: ReconciledProjectPlan;
  boundary: ReturnType<typeof createCrossGeneratorBoundary>;
  bindings: {
    policy: ReturnType<typeof capture<{controls: ReturnType<typeof createCrossGeneratorPolicyControls>}>>;
    'state-machine': ReturnType<typeof capture<{controls: ReturnType<typeof createCrossGeneratorStateMachineControls>}>>;
    'factory-rule': ReturnType<typeof capture<{controls: ReturnType<typeof createCrossGeneratorFactoryControls>; surface: ReturnType<typeof createCrossGeneratorFactorySurface>}>>;
    'owned-values': ReturnType<typeof capture<{controls: ReturnType<typeof createCrossGeneratorOwnedValueControls>; surface: ReturnType<typeof createCrossGeneratorOwnedValueSurface>}>>;
    'value-producer': ReturnType<typeof capture<{controls: ReturnType<typeof createCrossGeneratorValueProducerControls>; surface: ReturnType<typeof createCrossGeneratorValueProducerSurface>}>>;
    operation: ReturnType<typeof capture<{controls: ReturnType<typeof createCrossGeneratorOperationControls>}>>;
    workflow: ReturnType<typeof capture<{controls: ReturnType<typeof createCrossGeneratorWorkflowControls>; surface: ReturnType<typeof createCrossGeneratorWorkflowSurface>; audit: ReturnType<typeof createCrossGeneratorWorkflowAudit>}>>;
  };
};
const registered = new WeakMap<object, BindingState>();
/** Internal execution bridge, not caller receipt admission. */
export function crossGeneratorPreparationBindings(value: CrossGeneratorPreparation, graph: CompiledProjectGraph, plan: ReconciledProjectPlan) {
  const state = value && typeof value === 'object' ? registered.get(value) : undefined;
  if (!state) return fail('registered preparation required');
  if (state.graph !== graph || state.plan !== plan) fail('foreign preparation input');
  return state;
}
