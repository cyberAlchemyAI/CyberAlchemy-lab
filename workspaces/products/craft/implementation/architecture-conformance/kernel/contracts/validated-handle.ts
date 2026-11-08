const validatedHandleBrand: unique symbol = Symbol("ValidatedHandle/v2");
const validatedHandles = new WeakSet<object>();

export type ValidatedHandle<T> = Readonly<{
  schema_version: "ValidatedHandle/v2";
  value: Readonly<T>;
  source_sha256: string;
  validated_refs: readonly ExactRefIdentity[];
  [validatedHandleBrand]: true;
}>;

export type ExactRefIdentity = Readonly<{
  id: string;
  sha256: string;
}>;

const deepFreeze = <T>(value: T): Readonly<T> => {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    for (const child of Object.values(value as Record<string, unknown>)) {
      deepFreeze(child);
    }
    Object.freeze(value);
  }
  return value;
};

export const createValidatedHandle = <T>(input: Readonly<{
  value: T;
  source_sha256: string;
  validated_refs: readonly ExactRefIdentity[];
}>): ValidatedHandle<T> => {
  const handle = {
    schema_version: "ValidatedHandle/v2" as const,
    value: deepFreeze(input.value),
    source_sha256: input.source_sha256,
    validated_refs: Object.freeze(
      input.validated_refs.map((ref) => Object.freeze({ ...ref })),
    ),
    [validatedHandleBrand]: true as const,
  };
  validatedHandles.add(handle);
  return Object.freeze(handle);
};

export const readValidatedHandle = <T>(
  handle: ValidatedHandle<T>,
): Readonly<T> => {
  if (handle === null || typeof handle !== "object" ||
      !validatedHandles.has(handle)) {
    throw Object.assign(new Error("FACTORY_HANDLE_NOT_VALIDATED"), {
      code: "FACTORY_HANDLE_NOT_VALIDATED",
    });
  }
  return handle.value;
};

export const isValidatedHandle = <T>(
  value: unknown,
): value is ValidatedHandle<T> =>
  value !== null && typeof value === "object" && validatedHandles.has(value);
