export type TypeScriptEnumWireMemberV1 = Readonly<{
  member_id: string;
  wire_value: string;
}>;

export type TypeScriptEnumWireProbeV1 = Readonly<{
  schema_version: "TypeScriptEnumWireProbe/v1";
  known: readonly Readonly<{
    wire_value: string;
    outcome: "member";
    parsed_member_id: string;
  }>[];
  unknown: Readonly<{
    wire_value: string;
    outcome: "structured-failure";
    error_code: "DOMAINSPEC_ENUM_UNKNOWN_WIRE";
    parsed_member_id: null;
  }>;
  algorithm: "closed-owner-bound-wire-map/v1";
  authority_effect: "none";
}>;

export class TypeScriptEnumWireError extends Error {
  readonly code: "DOMAINSPEC_ENUM_UNKNOWN_WIRE";
  readonly wire_value: string;

  constructor(wireValue: string) {
    super(`DOMAINSPEC_ENUM_UNKNOWN_WIRE:${wireValue}`);
    this.name = "TypeScriptEnumWireError";
    this.code = "DOMAINSPEC_ENUM_UNKNOWN_WIRE";
    this.wire_value = wireValue;
  }
}

const exactWireMap = (
  members: readonly TypeScriptEnumWireMemberV1[],
): ReadonlyMap<string, string> => {
  if (members.length === 0) throw new Error("TS_ENUM_WIRE_MEMBERS_EMPTY");
  const map = new Map<string, string>();
  const memberIds = new Set<string>();
  for (const member of members) {
    if (member.member_id.length === 0 || member.wire_value.length === 0) {
      throw new Error("TS_ENUM_WIRE_MEMBER_INVALID");
    }
    if (memberIds.has(member.member_id)) throw new Error("TS_ENUM_WIRE_MEMBER_DUPLICATE");
    if (map.has(member.wire_value)) throw new Error("TS_ENUM_WIRE_VALUE_DUPLICATE");
    memberIds.add(member.member_id);
    map.set(member.wire_value, member.member_id);
  }
  return map;
};

export const parseTypeScriptEnumWire = (
  members: readonly TypeScriptEnumWireMemberV1[],
  wireValue: string,
): string => {
  const memberId = exactWireMap(members).get(wireValue);
  if (memberId === undefined) throw new TypeScriptEnumWireError(wireValue);
  return memberId;
};

export const runTypeScriptEnumWireProbe = (
  members: readonly TypeScriptEnumWireMemberV1[],
  unknownWireValue = "__domainspec_unknown__",
): TypeScriptEnumWireProbeV1 => {
  const wires = new Set(members.map(({ wire_value }) => wire_value));
  if (wires.has(unknownWireValue)) throw new Error("TS_ENUM_UNKNOWN_PROBE_NOT_OUTSIDE_WIRES");
  const known = members.map(({ member_id, wire_value }) => {
    const parsedMemberId = parseTypeScriptEnumWire(members, wire_value);
    return Object.freeze({
      wire_value,
      outcome: "member" as const,
      parsed_member_id: parsedMemberId,
      ...(parsedMemberId === member_id ? {} : { mismatch: member_id }),
    });
  });
  let unknown: TypeScriptEnumWireProbeV1["unknown"] | undefined;
  try {
    parseTypeScriptEnumWire(members, unknownWireValue);
  } catch (error) {
    if (error instanceof TypeScriptEnumWireError &&
        error.code === "DOMAINSPEC_ENUM_UNKNOWN_WIRE" &&
        error.wire_value === unknownWireValue) {
      unknown = Object.freeze({
        wire_value: unknownWireValue,
        outcome: "structured-failure" as const,
        error_code: "DOMAINSPEC_ENUM_UNKNOWN_WIRE" as const,
        parsed_member_id: null,
      });
    } else {
      throw error;
    }
  }
  if (unknown === undefined) throw new Error("TS_ENUM_UNKNOWN_WIRE_ACCEPTED");
  return Object.freeze({
    schema_version: "TypeScriptEnumWireProbe/v1",
    known: Object.freeze(known),
    unknown,
    algorithm: "closed-owner-bound-wire-map/v1",
    authority_effect: "none",
  });
};
