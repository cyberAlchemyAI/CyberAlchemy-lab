import { canonicalJson, sha256 } from "../input/source-manifest.js";
import type { DecodedRelationship } from "../input/project-model.js";
import {
  TypedContractError,
  type RuleExpression,
  type TypedOperationContract,
  type TypedRecordContract,
  type TypedRuleContract,
  type TypedSumContract,
  type TypedType,
  type ValueExpression,
} from "./contracts.js";

export type TypedNodeContract = TypedRecordContract | TypedSumContract | TypedRuleContract | TypedOperationContract;

export interface TypedClosureSourceNode {
  readonly feature_id: string;
  readonly node_id: string;
  readonly kind: string;
  readonly typed_contract: TypedNodeContract | null;
}

export interface TypedClosureNode {
  readonly selector: string;
  readonly kind: string;
  readonly typed_contract: TypedNodeContract;
}

export interface TypedPropertyClosureRow {
  readonly ontology_property: string;
  readonly domainspec_selector: string;
  readonly type: TypedType;
}

export interface TypedVariantClosureRow {
  readonly ontology_variant: string;
  readonly domainspec_selector: string;
  readonly payload: TypedType | null;
}

export interface TypedRuleClosureRow {
  readonly ontology_rule: string;
  readonly domainspec_selector: string;
}

export interface TypedOperationClosureV1 {
  readonly schema_version: "domainspec.typed-operation-closure/v1";
  readonly root_selector: string;
  readonly nodes: readonly TypedClosureNode[];
  readonly relationships: readonly DecodedRelationship[];
  readonly properties: readonly TypedPropertyClosureRow[];
  readonly variants: readonly TypedVariantClosureRow[];
  readonly rules: readonly TypedRuleClosureRow[];
  readonly operation: TypedOperationContract;
  readonly closure_sha256: string;
  readonly authority_effect: "none";
}

export interface TypedRuleClosureV1 {
  readonly schema_version: "domainspec.typed-rule-closure/v1";
  readonly root_selector: string;
  readonly nodes: readonly TypedClosureNode[];
  readonly relationships: readonly DecodedRelationship[];
  readonly properties: readonly TypedPropertyClosureRow[];
  readonly variants: readonly TypedVariantClosureRow[];
  readonly rules: readonly TypedRuleClosureRow[];
  readonly rule: TypedRuleContract;
  readonly closure_sha256: string;
  readonly authority_effect: "none";
}

export type TypedSemanticClosureV1 = TypedOperationClosureV1 | TypedRuleClosureV1;

function fail(code: string, pointer: string, message: string): never {
  throw new TypedContractError(code, pointer, message);
}

function selector(node: Pick<TypedClosureSourceNode, "feature_id" | "node_id">): string {
  return `${node.feature_id}:${node.node_id}`;
}

function contractSchema(contract: TypedNodeContract): string {
  return contract.schema_version;
}

function namedTypeSelectors(type: TypedType): readonly string[] {
  if (type.kind === "named") return [type.selector];
  if (type.kind === "set" || type.kind === "list" || type.kind === "optional") return namedTypeSelectors(type.element);
  if (type.kind === "sum") return type.variants.flatMap(({ payload }) => payload === null ? [] : namedTypeSelectors(payload));
  return [];
}

function expressionDependencies(expression: RuleExpression): { nodeSelectors: string[]; propertySelectors: string[] } {
  const nodeSelectors: string[] = [];
  const propertySelectors: string[] = [];
  const value = (candidate: ValueExpression): void => {
    if (candidate.op === "path") propertySelectors.push(...candidate.properties);
    else if (candidate.op === "to_set") value(candidate.value);
  };
  const visit = (candidate: RuleExpression): void => {
    if (candidate.op === "all" || candidate.op === "any") candidate.terms.forEach(visit);
    else if (candidate.op === "not") visit(candidate.term);
    else if (candidate.op === "eq" || candidate.op === "lt" || candidate.op === "set_equal" || candidate.op === "contains") {
      value(candidate.left);
      value(candidate.right);
    } else if (candidate.op === "exactly_one" || candidate.op === "unique" || candidate.op === "exists") {
      value(candidate.collection);
      visit(candidate.where);
    } else if (candidate.op === "rule_ref") {
      nodeSelectors.push(candidate.selector);
      candidate.arguments.forEach((argument) => value(argument.value));
    }
  };
  visit(expression);
  return { nodeSelectors, propertySelectors };
}

function uniqueSorted(values: readonly string[]): readonly string[] {
  return Object.freeze([...new Set(values)].sort());
}

function sameSet(left: readonly string[], right: readonly string[]): boolean {
  return canonicalJson(uniqueSorted(left)) === canonicalJson(uniqueSorted(right));
}

function compileTypedClosure(
  rootSelector: string,
  sourceNodes: readonly TypedClosureSourceNode[],
  relationships: readonly DecodedRelationship[],
  expectedRoot: "operation" | "rule",
): TypedSemanticClosureV1 | null {
  const nodes = new Map(sourceNodes.map((node) => [selector(node), node]));
  const root = nodes.get(rootSelector);
  if (!root) fail("MTCLI_TYPED_CLOSURE_MISSING", "/node", `root node is missing:${rootSelector}`);
  if (root.typed_contract === null) return null;
  const isOperationRoot = ["Operation", "Query"].includes(root.kind) && contractSchema(root.typed_contract) === "domainspec.typed-operation/v1";
  const isRuleRoot = root.kind === "Rule" && contractSchema(root.typed_contract) === "domainspec.typed-rule/v1";
  if ((expectedRoot === "operation" && !isOperationRoot) || (expectedRoot === "rule" && !isRuleRoot)) {
    fail("MTCLI_TYPED_CLOSURE_ROOT", "/node", expectedRoot === "operation" ? "typed closure root must be an Operation or Query" : "typed closure root must be a Rule");
  }
  const operation = isOperationRoot ? root.typed_contract as TypedOperationContract : null;
  const rule = isRuleRoot ? root.typed_contract as TypedRuleContract : null;

  const propertyOwners = new Map<string, string>();
  const propertyDefinitions = new Map<string, Readonly<{ owner: string; type: TypedType }>>();
  const variantDefinitions = new Map<string, Readonly<{ owner: string; payload: TypedType | null }>>();
  const ruleDefinitions = new Map<string, TypedRuleContract>();
  for (const node of sourceNodes) {
    const contract = node.typed_contract;
    if (contract?.schema_version === "domainspec.typed-record/v1") {
      for (const property of contract.properties) {
        if (propertyOwners.has(property.ontology_property)) fail("MTCLI_TYPED_CLOSURE_DUPLICATE_PROPERTY", "/nodes", `duplicate ontology property:${property.ontology_property}`);
        propertyOwners.set(property.ontology_property, selector(node));
        propertyDefinitions.set(property.ontology_property, Object.freeze({ owner: selector(node), type: property.type }));
      }
    } else if (contract?.schema_version === "domainspec.typed-sum/v1") {
      for (const variant of contract.variants) variantDefinitions.set(variant.ontology_variant, Object.freeze({ owner: selector(node), payload: variant.payload }));
    } else if (contract?.schema_version === "domainspec.typed-rule/v1") {
      ruleDefinitions.set(selector(node), contract);
    }
  }

  const sameType = (left: TypedType, right: TypedType): boolean => canonicalJson(left) === canonicalJson(right);
  const validateRuleSemantics = (contract: TypedRuleContract, pointer: string): void => {
    const valueType = (value: ValueExpression, scopes: ReadonlyMap<string, TypedType>, valuePointer: string): TypedType => {
      if (value.op === "literal") return Object.freeze({ kind: "scalar", name: value.type });
      if (value.op === "variant") {
        const variant = variantDefinitions.get(value.selector);
        if (!variant || variant.payload !== null) fail("MTCLI_TYPED_RULE_TYPE", valuePointer, `Rule references an unknown or payload variant:${value.selector}`);
        return Object.freeze({ kind: "named", selector: variant.owner });
      }
      if (value.op === "to_set") {
        const source = valueType(value.value, scopes, `${valuePointer}/value`);
        if (source.kind !== "list") fail("MTCLI_TYPED_RULE_TYPE", valuePointer, "to_set requires a list");
        return Object.freeze({ kind: "set", element: source.element });
      }
      const rootType = scopes.get(value.root);
      if (!rootType) fail("MTCLI_TYPED_RULE_SCOPE", `${valuePointer}/root`, `Rule path references an unknown scope:${value.root}`);
      let current: TypedType = rootType;
      for (const [index, propertySelector] of value.properties.entries()) {
        const property = propertyDefinitions.get(propertySelector);
        if (!property) fail("MTCLI_TYPED_CLOSURE_PROPERTY", `${valuePointer}/properties/${index}`, `unresolved ontology property:${propertySelector}`);
        if (current.kind === "set" || current.kind === "list") {
          if (current.element.kind !== "named" || current.element.selector !== property.owner || index !== value.properties.length - 1) {
            fail("MTCLI_TYPED_RULE_TYPE", `${valuePointer}/properties/${index}`, `Rule collection projection owner mismatch:${propertySelector}`);
          }
          current = Object.freeze({ kind: current.kind, element: property.type });
        } else {
          if (current.kind !== "named" || current.selector !== property.owner) fail("MTCLI_TYPED_RULE_TYPE", `${valuePointer}/properties/${index}`, `Rule property owner mismatch:${propertySelector}`);
          current = property.type;
        }
      }
      return current;
    };
    const expression = (candidate: RuleExpression, scopes: ReadonlyMap<string, TypedType>, expressionPointer: string): void => {
      if (candidate.op === "all" || candidate.op === "any") {
        candidate.terms.forEach((term, index) => expression(term, scopes, `${expressionPointer}/terms/${index}`));
        return;
      }
      if (candidate.op === "not") {
        expression(candidate.term, scopes, `${expressionPointer}/term`);
        return;
      }
      if (candidate.op === "eq" || candidate.op === "lt" || candidate.op === "set_equal" || candidate.op === "contains") {
        const left = valueType(candidate.left, scopes, `${expressionPointer}/left`);
        const right = valueType(candidate.right, scopes, `${expressionPointer}/right`);
        if (candidate.op === "contains") {
          if ((left.kind !== "set" && left.kind !== "list") || !sameType(left.element, right)) fail("MTCLI_TYPED_RULE_TYPE", expressionPointer, "contains operands are type-incompatible");
        } else if (!sameType(left, right) || (candidate.op === "lt" && (left.kind !== "scalar" || left.name === "Bool"))) {
          fail("MTCLI_TYPED_RULE_TYPE", expressionPointer, `${candidate.op} operands are type-incompatible`);
        }
        return;
      }
      if (candidate.op === "rule_ref") {
        const target = ruleDefinitions.get(candidate.selector);
        if (!target) fail("MTCLI_TYPED_RULE_REFERENCE", expressionPointer, `Rule reference is unresolved:${candidate.selector}`);
        const supplied = new Map(candidate.arguments.map((argument) => [argument.parameter, argument.value]));
        if (supplied.size !== target.parameters.length || target.parameters.some(({ name }) => !supplied.has(name))) fail("MTCLI_TYPED_RULE_REFERENCE", expressionPointer, `Rule arguments do not exactly bind:${candidate.selector}`);
        for (const parameter of target.parameters) if (!sameType(valueType(supplied.get(parameter.name)!, scopes, `${expressionPointer}/arguments/${parameter.name}`), parameter.type)) fail("MTCLI_TYPED_RULE_TYPE", expressionPointer, `Rule argument type mismatch:${candidate.selector}:${parameter.name}`);
        return;
      }
      if (candidate.op !== "exactly_one" && candidate.op !== "exists" && candidate.op !== "unique") fail("MTCLI_TYPED_RULE_TYPE", expressionPointer, "unsupported Rule quantifier");
      const collection = valueType(candidate.collection, scopes, `${expressionPointer}/collection`);
      if (collection.kind !== "set" && collection.kind !== "list") fail("MTCLI_TYPED_RULE_TYPE", expressionPointer, `${candidate.op} requires a collection`);
      const nested = new Map(scopes);
      nested.set(candidate.binding, collection.element);
      if (candidate.op === "unique" && (candidate.where.op !== "eq" || canonicalJson(candidate.where.left) !== canonicalJson(candidate.where.right) || candidate.where.left.op !== "path")) {
        fail("MTCLI_TYPED_RULE_TYPE", `${expressionPointer}/where`, "unique requires an identical path equality naming the uniqueness key");
      }
      expression(candidate.where, nested, `${expressionPointer}/where`);
    };
    expression(contract.expression, new Map(contract.parameters.map((parameter) => [parameter.name, parameter.type])), `${pointer}/expression`);
  };

  const enforcingRules = operation === null ? [] : relationships
    .filter((edge) => edge.relationship === "enforces" && `${edge.target.feature_id}:${edge.target.node_id}` === rootSelector)
    .map((edge) => `${edge.source.feature_id}:${edge.source.node_id}`);
  if (operation !== null) {
    const incidentReads = relationships
      .filter((edge) => edge.relationship === "reads" && `${edge.source.feature_id}:${edge.source.node_id}` === rootSelector)
      .map((edge) => `${edge.target.feature_id}:${edge.target.node_id}`);
    if (!sameSet(incidentReads, operation.reads)) fail("MTCLI_TYPED_CLOSURE_READS", "/typed_contract/reads", "typed reads must exactly match authored reads relationships");
    if (root.kind === "Operation" && !enforcingRules.includes(operation.guard)) {
      fail("MTCLI_TYPED_CLOSURE_GUARD", "/typed_contract/guard", "guard Rule must enforce the selected Operation");
    }
  }

  const dependencies = (node: TypedClosureSourceNode): readonly string[] => {
    const contract = node.typed_contract;
    if (contract === null) fail("MTCLI_TYPED_CLOSURE_UNTYPED", `/nodes/${selector(node)}`, "typed closure dependency lacks typed contract");
    const result: string[] = [];
    if (contract.schema_version === "domainspec.typed-record/v1") {
      for (const property of contract.properties) result.push(...namedTypeSelectors(property.type));
    } else if (contract.schema_version === "domainspec.typed-sum/v1") {
      for (const variant of contract.variants) if (variant.payload !== null) result.push(...namedTypeSelectors(variant.payload));
    } else if (contract.schema_version === "domainspec.typed-rule/v1") {
      validateRuleSemantics(contract, `/nodes/${selector(node)}/typed_contract`);
      for (const parameter of contract.parameters) result.push(...namedTypeSelectors(parameter.type));
      const expression = expressionDependencies(contract.expression);
      result.push(...expression.nodeSelectors);
      for (const propertySelector of expression.propertySelectors) {
        const owner = propertyOwners.get(propertySelector);
        if (!owner) fail("MTCLI_TYPED_CLOSURE_PROPERTY", `/nodes/${selector(node)}/expression`, `unresolved ontology property:${propertySelector}`);
        result.push(owner);
      }
    } else {
      for (const input of contract.inputs) result.push(...namedTypeSelectors(input.type));
      result.push(...namedTypeSelectors(contract.output), contract.guard, ...contract.reads, ...contract.writes, ...contract.effects, ...enforcingRules);
    }
    return uniqueSorted(result);
  };

  const permanent = new Set<string>();
  const visiting = new Set<string>();
  const ordered: string[] = [];
  const visit = (currentSelector: string, stack: readonly string[]): void => {
    if (permanent.has(currentSelector)) return;
    if (visiting.has(currentSelector)) fail("MTCLI_TYPED_CLOSURE_CYCLE", "/closure", `dependency cycle:${[...stack, currentSelector].join(" -> ")}`);
    const current = nodes.get(currentSelector);
    if (!current) fail("MTCLI_TYPED_CLOSURE_MISSING", "/closure", `missing dependency:${currentSelector}`);
    visiting.add(currentSelector);
    for (const dependency of dependencies(current)) visit(dependency, [...stack, currentSelector]);
    visiting.delete(currentSelector);
    permanent.add(currentSelector);
    ordered.push(currentSelector);
  };
  visit(rootSelector, []);

  const closureNodes = Object.freeze(ordered.map((nodeSelector): TypedClosureNode => {
    const node = nodes.get(nodeSelector)!;
    if (node.typed_contract === null) fail("MTCLI_TYPED_CLOSURE_UNTYPED", `/nodes/${nodeSelector}`, "closure node lacks typed contract");
    return Object.freeze({ selector: nodeSelector, kind: node.kind, typed_contract: node.typed_contract });
  }));
  const closureSet = new Set(ordered);
  const closureRelationships = Object.freeze(relationships
    .filter((edge) => closureSet.has(`${edge.source.feature_id}:${edge.source.node_id}`) && closureSet.has(`${edge.target.feature_id}:${edge.target.node_id}`))
    .sort((left, right) => left.edge_id.localeCompare(right.edge_id)));
  const properties = Object.freeze(closureNodes.flatMap((node): readonly TypedPropertyClosureRow[] =>
    node.typed_contract.schema_version === "domainspec.typed-record/v1"
      ? node.typed_contract.properties.map((property) => Object.freeze({ ontology_property: property.ontology_property, domainspec_selector: `${node.selector}#${property.name}`, type: property.type }))
      : []
  ).sort((left, right) => left.ontology_property.localeCompare(right.ontology_property)));
  const variants = Object.freeze(closureNodes.flatMap((node): readonly TypedVariantClosureRow[] =>
    node.typed_contract.schema_version === "domainspec.typed-sum/v1"
      ? node.typed_contract.variants.map((variant) => Object.freeze({ ontology_variant: variant.ontology_variant, domainspec_selector: `${node.selector}#${variant.name}`, payload: variant.payload }))
      : []
  ).sort((left, right) => left.ontology_variant.localeCompare(right.ontology_variant)));
  const rules = Object.freeze(closureNodes.flatMap((node): readonly TypedRuleClosureRow[] =>
    node.typed_contract.schema_version === "domainspec.typed-rule/v1"
      ? [Object.freeze({ ontology_rule: node.typed_contract.ontology_rule, domainspec_selector: node.selector })]
      : []
  ).sort((left, right) => left.ontology_rule.localeCompare(right.ontology_rule)));
  const shared = {
    root_selector: rootSelector,
    nodes: closureNodes,
    relationships: closureRelationships,
    properties,
    variants,
    rules,
    authority_effect: "none" as const,
  };
  const body = operation !== null
    ? { schema_version: "domainspec.typed-operation-closure/v1" as const, ...shared, operation }
    : { schema_version: "domainspec.typed-rule-closure/v1" as const, ...shared, rule: rule! };
  return Object.freeze({ ...body, closure_sha256: sha256(canonicalJson(body)) });
}

export function compileTypedOperationClosure(
  rootSelector: string,
  sourceNodes: readonly TypedClosureSourceNode[],
  relationships: readonly DecodedRelationship[],
): TypedOperationClosureV1 | null {
  return compileTypedClosure(rootSelector, sourceNodes, relationships, "operation") as TypedOperationClosureV1 | null;
}

export function compileTypedRuleClosure(
  rootSelector: string,
  sourceNodes: readonly TypedClosureSourceNode[],
  relationships: readonly DecodedRelationship[],
): TypedRuleClosureV1 | null {
  return compileTypedClosure(rootSelector, sourceNodes, relationships, "rule") as TypedRuleClosureV1 | null;
}
