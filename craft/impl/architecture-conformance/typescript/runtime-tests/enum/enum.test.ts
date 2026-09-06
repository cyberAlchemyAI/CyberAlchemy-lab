import { describe, expect, expectTypeOf, it } from "vitest";

import {
  composeEnum,
  defineEnum,
  type EnumValue,
} from "../../runtime/enum/index.js";

const errorCode = (operation: () => unknown): string | undefined => {
  try {
    operation();
  } catch (error) {
    return (error as { readonly code?: string }).code;
  }
  return undefined;
};

describe("owned const-object Enum provider", () => {
  it("preserves literal value types and freezes a defensive copy", () => {
    const source = { Draft: "draft", Published: "published" } as const;
    const Status = defineEnum(source);
    type StatusValue = EnumValue<typeof Status>;

    expectTypeOf<StatusValue>().toEqualTypeOf<"draft" | "published">();
    expectTypeOf(Status.Draft).toEqualTypeOf<"draft">();
    expect(Status).toEqual({ Draft: "draft", Published: "published" });
    expect(Object.isFrozen(Status)).toBe(true);

    const accepted: StatusValue = "draft";
    expect(accepted).toBe("draft");

    // @ts-expect-error The provider-derived value type excludes unknown literals.
    const rejected: StatusValue = "archived";
    expect(rejected).toBe("archived");
  });

  it("composes named owned components directly and transitively", () => {
    const Status = defineEnum({ Draft: "draft", Published: "published" });
    const Access = defineEnum({ Public: "public", Private: "private" });
    const Lifecycle = composeEnum({ status: Status, access: Access });
    const Result = defineEnum({ Success: "success" });
    const Complete = composeEnum({ lifecycle: Lifecycle, result: Result });
    type CompleteValue = EnumValue<typeof Complete>;

    expectTypeOf<CompleteValue>().toEqualTypeOf<
      "draft" | "published" | "public" | "private" | "success"
    >();
    expect(Lifecycle).toEqual({
      Draft: "draft",
      Private: "private",
      Public: "public",
      Published: "published",
    });
    expect(Complete.Success).toBe("success");
    expect(Object.isFrozen(Lifecycle)).toBe(true);
    expect(Object.isFrozen(Complete)).toBe(true);
  });

  it("materializes deterministic member order independent of component order", () => {
    const First = defineEnum({ Zed: "zed" });
    const Second = defineEnum({ Alpha: "alpha" });

    expect(JSON.stringify(composeEnum({ first: First, second: Second }))).toBe(
      JSON.stringify(composeEnum({ second: Second, first: First })),
    );
  });

  it("blocks duplicate direct values and composition key/value collisions", () => {
    expect(
      errorCode(() => defineEnum({ First: "same", Second: "same" })),
    ).toBe("ENUM_DUPLICATE_VALUE");

    const KeyLeft = defineEnum({ Same: "left" });
    const KeyRight = defineEnum({ Same: "right" });
    expect(errorCode(() => composeEnum({ left: KeyLeft, right: KeyRight }))).toBe(
      "ENUM_DUPLICATE_KEY",
    );

    const ValueLeft = defineEnum({ Left: "same" });
    const ValueRight = defineEnum({ Right: "same" });
    expect(errorCode(() => composeEnum({ left: ValueLeft, right: ValueRight }))).toBe(
      "ENUM_DUPLICATE_VALUE",
    );
  });

  it("blocks prototype-sensitive, symbol, accessor, and non-string direct members", () => {
    const unsafe = Object.create(null) as Record<string, string>;
    unsafe.__proto__ = "unsafe";
    expect(errorCode(() => defineEnum(unsafe))).toBe("ENUM_MEMBER_KEY_UNSAFE");

    const symbolMember = { Good: "good", [Symbol("bad")]: "bad" };
    expect(errorCode(() => defineEnum(symbolMember))).toBe("ENUM_MEMBER_SYMBOL");

    const accessorMember = Object.create(null) as Record<string, string>;
    Object.defineProperty(accessorMember, "Bad", { get: () => "bad" });
    expect(errorCode(() => defineEnum(accessorMember))).toBe("ENUM_MEMBER_ACCESSOR");

    const nonString = { Bad: 1 } as unknown as Record<string, string>;
    expect(errorCode(() => defineEnum(nonString))).toBe(
      "ENUM_MEMBER_VALUE_NOT_STRING",
    );
  });

  it("admits only provider-owned named components", () => {
    const composeRuntime = composeEnum as unknown as (components: unknown) => unknown;

    expect(errorCode(() => composeRuntime({ fake: { Fake: "fake" } }))).toBe(
      "ENUM_COMPONENT_NOT_OWNED",
    );
    expect(errorCode(() => composeRuntime([]))).toBe("ENUM_COMPONENTS_NOT_RECORD");
    expect(errorCode(() => composeRuntime({}))).toBe("ENUM_COMPONENTS_EMPTY");

    if (false) {
      // @ts-expect-error Unowned const objects are not valid provider components.
      composeEnum({ fake: { Fake: "fake" } as const });
    }
  });

  it("blocks repeated direct and transitive contributions", () => {
    const A = defineEnum({ A: "a" });
    const B = defineEnum({ B: "b" });
    const C = defineEnum({ C: "c" });

    expect(errorCode(() => composeEnum({ first: A, again: A }))).toBe(
      "ENUM_COMPONENT_REPEATED",
    );

    const Left = composeEnum({ a: A, b: B });
    const Right = composeEnum({ b: B, c: C });
    expect(errorCode(() => composeEnum({ left: Left, right: Right }))).toBe(
      "ENUM_CONTRIBUTION_REPEATED",
    );
  });

  it("detects a cyclic raw component graph before ownership admission", () => {
    const cyclic: Record<string, unknown> = {};
    cyclic.self = cyclic;
    const composeRuntime = composeEnum as unknown as (components: unknown) => unknown;

    expect(errorCode(() => composeRuntime(cyclic))).toBe("ENUM_COMPONENT_CYCLE");
  });

  it("rejects non-string members at compile time", () => {
    if (false) {
      // @ts-expect-error Enum members are string-only.
      defineEnum({ Invalid: 1 });
    }
  });
});
