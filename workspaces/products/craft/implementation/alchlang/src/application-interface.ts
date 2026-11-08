import { CompilationRejected } from "./model.js";
import type { ApplicationSourceSection } from "./formal-claim.js";
import type { ApplicationType, ApplicationInterfaceDeclaration, ApplicationPublicType } from "./application-source.js";

const fail = (line: number, message: string): never => { throw new CompilationRejected([{ code: "APPLICATION_INTERFACE", path: `$line:${line}`, message }]); };

/** Normalizes rows from the shared scanner, not a separate application parser. */
export function normalizeApplicationInterface(section: ApplicationSourceSection, parseType: (source: string, line: number) => ApplicationType): Omit<ApplicationInterfaceDeclaration, "ontology" | "meaning"> {
  const rows = section.rows; const indent = rows[0]?.indent;
  if (indent === undefined) return fail(section.line, "Interface requires explicit kind, version, compatibility, contracts and exposures");
  let boundary: "external" | "internal" | undefined, version: string | undefined, compatibility: "exact" | "backward" | undefined;
  const contracts: { id: string; source_line: number; fields: { name: string; type: ApplicationType; source_line: number }[] }[] = [];
  const members: { operation: string; request: ApplicationType; result: ApplicationType; source_line: number }[] = [];
  for (let i = 0; i < rows.length; i++) {
    const row = rows[i]!;
    if (row.indent !== indent) fail(row.line, "Interface clauses must share an indentation level");
    let match: RegExpExecArray | null;
    if ((match = /^kind (external|internal)$/.exec(row.text))) {
      if (boundary) fail(row.line, "duplicate kind"); boundary = match[1] as typeof boundary;
    } else if ((match = /^version ((?:0|[1-9][0-9]{0,63})\.(?:0|[1-9][0-9]{0,63})\.(?:0|[1-9][0-9]{0,63}))$/.exec(row.text))) {
      if (version) fail(row.line, "duplicate version"); version = match[1]!;
    } else if ((match = /^compatibility (exact|backward)$/.exec(row.text))) {
      if (compatibility) fail(row.line, "duplicate compatibility"); compatibility = match[1] as typeof compatibility;
    } else if ((match = /^(contract|exposes) ([A-Za-z_][\w-]*):$/.exec(row.text))) {
      const role = match[1]!, id = match[2]!, children: ApplicationSourceSection["rows"] = [];
      while (rows[i + 1] && rows[i + 1]!.indent! > indent) children.push(rows[++i]!);
      const childIndent = children[0]?.indent;
      if (children.some(child => child.indent !== childIndent)) fail(row.line, "contract/member clauses must share one nested indentation level");
      if (role === "contract") {
        if (contracts.some(c => c.id === id)) fail(row.line, "duplicate public contract");
        const fields = children.map(child => {
          const field = /^([A-Za-z_][\w-]*)(?::\s*|\s+)(.+)$/.exec(child.text);
          if (!field) return fail(child.line, "expected public fieldName Type");
          return { name: field[1]!, type: parseType(field[2]!, child.line), source_line: child.line };
        });
        if (new Set(fields.map(f => f.name)).size !== fields.length) fail(row.line, "duplicate public field");
        contracts.push({ id, fields, source_line: row.line });
      } else {
        if (members.some(m => m.operation === id)) fail(row.line, "duplicate exposure");
        let request: ApplicationType | undefined, result: ApplicationType | undefined;
        for (const child of children) {
          const field = /^(request|result) (.+)$/.exec(child.text);
          if (!field) fail(child.line, "exposure requires request and result types, not execution logic");
          if (field![1] === "request") { if (request) fail(child.line, "duplicate request"); request = parseType(field![2]!, child.line); }
          else { if (result) fail(child.line, "duplicate result"); result = parseType(field![2]!, child.line); }
        }
        if (!request || !result) fail(row.line, "exposure requires explicit request and result");
        members.push({ operation: id, request: request!, result: result!, source_line: row.line });
      }
    } else fail(row.line, "unsupported Interface clause");
  }
  if (!boundary || !version || !compatibility || !contracts.length || !members.length) fail(section.line, "explicit boundary kind, version, compatibility, public contracts and exposures are required");
  const publicType = (type: ApplicationType): ApplicationPublicType => {
    if (type.kind === "public-contract") {
      if (type.interface !== section.id) return fail(section.line, "public Interface values cannot embed a foreign public contract");
      return { kind: "contract", ref: type.contract };
    }
    if (type.kind === "declaration" && contracts.some(c => c.id === type.ref)) return { kind: "contract", ref: type.ref };
    if (type.kind === "optional" || type.kind === "list" || type.kind === "set") return { kind: type.kind, element: publicType(type.element) };
    if (type.kind === "scalar" || type.kind === "declaration" || type.kind === "reference" || type.kind === "sum") return type;
    return fail(section.line, "unsupported public type");
  };
  return { kind: "interface", id: section.id, source_line: section.line, boundary_kind: boundary!, version: version!, compatibility: compatibility!,
    contracts: contracts.map(c => ({ ...c, fields: c.fields.map(f => ({ ...f, type: publicType(f.type) })) })),
    members: members.map(m => ({ ...m, request: publicType(m.request), result: publicType(m.result) })) };
}
