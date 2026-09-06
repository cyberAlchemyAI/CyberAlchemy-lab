import { createHash } from "node:crypto";

export type TypeWitnessSource = Readonly<{
  source: string;
  sha256: string;
  expected_union: readonly string[];
}>;

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));

export const deriveEnumTypeWitness = (
  generatedModuleSpecifier: string,
  exportName: string,
  typeName: string,
  expectedValues: readonly string[],
): TypeWitnessSource => {
  const expected = [...expectedValues].sort(compareUtf8);
  if (expected.length === 0 || new Set(expected).size !== expected.length) {
    throw Object.assign(new Error("ARCH_ENUM_TYPE_WITNESS_EXPECTATION_INVALID"), {
      code: "ARCH_ENUM_TYPE_WITNESS_EXPECTATION_INVALID",
    });
  }
  const union = expected.map((value) => JSON.stringify(value)).join(" | ");
  const source = [
    `import { ${exportName}, type ${typeName} } from ${JSON.stringify(generatedModuleSpecifier)};`,
    `type Expected = ${union};`,
    "type Equal<Left, Right> =",
    "  (<Value>() => Value extends Left ? 1 : 2) extends",
    "  (<Value>() => Value extends Right ? 1 : 2) ? true : false;",
    `const exact: Equal<${typeName}, Expected> = true;`,
    `export const runtimeValues = Object.values(${exportName});`,
    "export { exact };",
    "",
  ].join("\n");
  return Object.freeze({
    source,
    sha256: createHash("sha256").update(source).digest("hex"),
    expected_union: Object.freeze(expected),
  });
};
