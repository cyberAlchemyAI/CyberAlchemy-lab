type EnumRecord = Readonly<Record<string, string>>;

declare const enumMembers: unique symbol;

type OwnedEnum<T extends EnumRecord = EnumRecord> = Readonly<T> & {
  readonly [enumMembers]: T;
};

type MembersOf<T> = T extends {
  readonly [enumMembers]: infer Members extends EnumRecord;
}
  ? Members
  : never;

type UnionToIntersection<T> = (
  T extends unknown ? (value: T) => void : never
) extends (value: infer Intersection) => void
  ? Intersection
  : never;

type ComponentRecord = Readonly<Record<string, OwnedEnum>>;

type ComposedMembers<Components extends ComponentRecord> =
  UnionToIntersection<MembersOf<Components[keyof Components]>> extends infer Members extends EnumRecord
    ? Members
    : never;

type EnumMetadata = Readonly<{
  entries: readonly (readonly [string, string])[];
  contributors: ReadonlySet<symbol>;
}>;

const ownership = new WeakMap<object, EnumMetadata>();

const unsafeKeys = new Set(["__proto__", "constructor", "prototype"]);

class EnumContractError extends TypeError {
  readonly code: string;

  constructor(code: string, message: string) {
    super(`${code}: ${message}`);
    this.name = "EnumContractError";
    this.code = code;
  }
}

const fail: (code: string, message: string) => never = (code, message) => {
  throw new EnumContractError(code, message);
};

const assertRecord: (
  value: unknown,
  inputCode: string,
  prototypeCode: string,
) => asserts value is object = (value, inputCode, prototypeCode) => {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    fail(inputCode, "expected a non-null object record");
  }

  const prototype = Object.getPrototypeOf(value);
  if (prototype !== Object.prototype && prototype !== null) {
    fail(prototypeCode, "record must use Object.prototype or a null prototype");
  }
};

const readDataEntries = (
  record: object,
  codes: Readonly<{
    empty: string;
    symbol: string;
    accessor: string;
    unsafeKey: string;
  }>,
): readonly (readonly [string, unknown])[] => {
  const keys = Reflect.ownKeys(record);
  if (keys.length === 0) {
    fail(codes.empty, "record must contain at least one entry");
  }

  const entries: Array<readonly [string, unknown]> = [];
  for (const key of keys) {
    if (typeof key !== "string") {
      fail(codes.symbol, "symbol keys are not part of the Enum protocol");
    }
    if (unsafeKeys.has(key)) {
      fail(codes.unsafeKey, `unsafe key ${JSON.stringify(key)} is not allowed`);
    }

    const descriptor = Object.getOwnPropertyDescriptor(record, key);
    if (descriptor === undefined) {
      fail(codes.accessor, `missing descriptor for ${JSON.stringify(key)}`);
    }
    if (!("value" in descriptor)) {
      fail(codes.accessor, `accessor member ${JSON.stringify(key)} is not allowed`);
    }
    entries.push([key, descriptor.value]);
  }

  return entries.sort(([left], [right]) => left.localeCompare(right));
};

const containsDataCycle = (root: object): boolean => {
  const visiting = new Set<object>();
  const visited = new Set<object>();

  const visit = (value: unknown): boolean => {
    if (typeof value !== "object" || value === null) {
      return false;
    }
    if (visiting.has(value)) {
      return true;
    }
    if (visited.has(value)) {
      return false;
    }

    visiting.add(value);
    for (const key of Reflect.ownKeys(value)) {
      const descriptor = Object.getOwnPropertyDescriptor(value, key);
      if (descriptor !== undefined && "value" in descriptor && visit(descriptor.value)) {
        return true;
      }
    }
    visiting.delete(value);
    visited.add(value);
    return false;
  };

  return visit(root);
};

const materialize = <Members extends EnumRecord>(
  entries: readonly (readonly [string, string])[],
  contributors: ReadonlySet<symbol>,
): OwnedEnum<Members> => {
  const output: Record<string, string> = {};
  for (const [key, value] of entries) {
    Object.defineProperty(output, key, {
      configurable: false,
      enumerable: true,
      value,
      writable: false,
    });
  }
  Object.freeze(output);

  const immutableEntries = Object.freeze(
    entries.map(([key, value]) => Object.freeze([key, value] as const)),
  );
  ownership.set(output, {
    entries: immutableEntries,
    contributors: new Set(contributors),
  });

  return output as OwnedEnum<Members>;
};

export type EnumValue<Enum> = Enum extends {
  readonly [enumMembers]: infer Members extends EnumRecord;
}
  ? Members[keyof Members]
  : never;

export const defineEnum = <const Members extends EnumRecord>(
  members: Members,
): OwnedEnum<Members> => {
  assertRecord(members, "ENUM_INPUT_NOT_RECORD", "ENUM_INPUT_PROTOTYPE");
  const inputEntries = readDataEntries(members, {
    empty: "ENUM_EMPTY",
    symbol: "ENUM_MEMBER_SYMBOL",
    accessor: "ENUM_MEMBER_ACCESSOR",
    unsafeKey: "ENUM_MEMBER_KEY_UNSAFE",
  });

  const values = new Set<string>();
  const entries: Array<readonly [string, string]> = [];
  for (const [key, value] of inputEntries) {
    if (typeof value !== "string") {
      fail("ENUM_MEMBER_VALUE_NOT_STRING", `member ${JSON.stringify(key)} must be a string`);
    }
    if (value.length === 0) {
      fail("ENUM_MEMBER_VALUE_EMPTY", `member ${JSON.stringify(key)} must not be empty`);
    }
    if (values.has(value)) {
      fail("ENUM_DUPLICATE_VALUE", `duplicate value ${JSON.stringify(value)}`);
    }
    values.add(value);
    entries.push([key, value]);
  }

  return materialize<Members>(entries, new Set([Symbol("enum-contributor")]));
};

export const composeEnum = <const Components extends ComponentRecord>(
  components: Components,
): OwnedEnum<ComposedMembers<Components>> => {
  assertRecord(
    components,
    "ENUM_COMPONENTS_NOT_RECORD",
    "ENUM_COMPONENTS_PROTOTYPE",
  );
  const componentEntries = readDataEntries(components, {
    empty: "ENUM_COMPONENTS_EMPTY",
    symbol: "ENUM_COMPONENT_SYMBOL",
    accessor: "ENUM_COMPONENT_ACCESSOR",
    unsafeKey: "ENUM_COMPONENT_NAME_UNSAFE",
  });

  if (containsDataCycle(components)) {
    fail("ENUM_COMPONENT_CYCLE", "component graph contains a cycle");
  }

  const componentObjects = new Set<object>();
  const contributors = new Set<symbol>();
  const keys = new Set<string>();
  const values = new Set<string>();
  const entries: Array<readonly [string, string]> = [];

  for (const [componentName, component] of componentEntries) {
    if (typeof component !== "object" || component === null) {
      fail(
        "ENUM_COMPONENT_NOT_OWNED",
        `component ${JSON.stringify(componentName)} was not created by this provider`,
      );
    }
    if (componentObjects.has(component)) {
      fail(
        "ENUM_COMPONENT_REPEATED",
        `component ${JSON.stringify(componentName)} repeats an earlier component`,
      );
    }
    componentObjects.add(component);

    const metadata = ownership.get(component);
    if (metadata === undefined) {
      fail(
        "ENUM_COMPONENT_NOT_OWNED",
        `component ${JSON.stringify(componentName)} was not created by this provider`,
      );
    }

    for (const contributor of metadata.contributors) {
      if (contributors.has(contributor)) {
        fail(
          "ENUM_CONTRIBUTION_REPEATED",
          `component ${JSON.stringify(componentName)} repeats a transitive contribution`,
        );
      }
      contributors.add(contributor);
    }

    for (const [key, value] of metadata.entries) {
      if (keys.has(key)) {
        fail("ENUM_DUPLICATE_KEY", `duplicate member key ${JSON.stringify(key)}`);
      }
      if (values.has(value)) {
        fail("ENUM_DUPLICATE_VALUE", `duplicate member value ${JSON.stringify(value)}`);
      }
      keys.add(key);
      values.add(value);
      entries.push([key, value]);
    }
  }

  entries.sort(([left], [right]) => left.localeCompare(right));
  return materialize<ComposedMembers<Components>>(entries, contributors);
};
