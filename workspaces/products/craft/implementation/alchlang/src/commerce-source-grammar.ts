// GENERATED from Core COMMERCE-GRAMMAR-V1.ebnf; do not edit.
// Open Questions: private EC06/CONTEXT.md. Syntax only; no executable authority.
export const COMMERCE_GRAMMAR_SHA256="34de5b441f753ba8b397758f76bb5c38eceaa83dcff79e6a3305eeb698c88ce8";
export const COMMERCE_RESERVED_NAMES=Object.freeze(["map","filter","fold","indexed-fold","repeat","while-bounded","until-bounded","range","sort","match","true","false","none"] as const);
export interface CommerceGrammarProduction {readonly lhs:string;readonly rhs:readonly (string|{readonly literal:string})[]}
export const COMMERCE_GRAMMAR_PRODUCTIONS:readonly CommerceGrammarProduction[]=[
 {
  "lhs": "$2",
  "rhs": [
   "import-line",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$1",
  "rhs": []
 },
 {
  "lhs": "$1",
  "rhs": [
   "$2",
   "$1"
  ]
 },
 {
  "lhs": "$4",
  "rhs": [
   "declaration"
  ]
 },
 {
  "lhs": "$3",
  "rhs": []
 },
 {
  "lhs": "$3",
  "rhs": [
   "$4",
   "$3"
  ]
 },
 {
  "lhs": "source",
  "rhs": [
   "module-header",
   "NEWLINE",
   "$1",
   "declaration",
   "$3"
  ]
 },
 {
  "lhs": "$5",
  "rhs": [
   {
    "literal": "module"
   }
  ]
 },
 {
  "lhs": "$6",
  "rhs": [
   {
    "literal": "version"
   }
  ]
 },
 {
  "lhs": "$7",
  "rhs": [
   {
    "literal": "1"
   }
  ]
 },
 {
  "lhs": "module-header",
  "rhs": [
   "$5",
   "qualified-name",
   "$6",
   "$7"
  ]
 },
 {
  "lhs": "$8",
  "rhs": [
   {
    "literal": "use"
   }
  ]
 },
 {
  "lhs": "$11",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$10",
  "rhs": [
   "$11",
   "qualified-name"
  ]
 },
 {
  "lhs": "$9",
  "rhs": []
 },
 {
  "lhs": "$9",
  "rhs": [
   "$10",
   "$9"
  ]
 },
 {
  "lhs": "import-line",
  "rhs": [
   "$8",
   "qualified-name",
   "$9"
  ]
 },
 {
  "lhs": "$14",
  "rhs": [
   {
    "literal": "."
   }
  ]
 },
 {
  "lhs": "$13",
  "rhs": [
   "$14",
   "NAME"
  ]
 },
 {
  "lhs": "$12",
  "rhs": []
 },
 {
  "lhs": "$12",
  "rhs": [
   "$13",
   "$12"
  ]
 },
 {
  "lhs": "qualified-name",
  "rhs": [
   "NAME",
   "$12"
  ]
 },
 {
  "lhs": "$17",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$16",
  "rhs": [
   "$17",
   "qualified-name"
  ]
 },
 {
  "lhs": "$15",
  "rhs": []
 },
 {
  "lhs": "$15",
  "rhs": [
   "$16",
   "$15"
  ]
 },
 {
  "lhs": "name-list",
  "rhs": [
   "qualified-name",
   "$15"
  ]
 },
 {
  "lhs": "step-name",
  "rhs": [
   "STEP_NAME"
  ]
 },
 {
  "lhs": "$20",
  "rhs": [
   {
    "literal": "."
   }
  ]
 },
 {
  "lhs": "$19",
  "rhs": [
   "$20",
   "step-name"
  ]
 },
 {
  "lhs": "$18",
  "rhs": []
 },
 {
  "lhs": "$18",
  "rhs": [
   "$19",
   "$18"
  ]
 },
 {
  "lhs": "permission-name",
  "rhs": [
   "step-name",
   "$18"
  ]
 },
 {
  "lhs": "natural",
  "rhs": [
   "NATURAL"
  ]
 },
 {
  "lhs": "json-string",
  "rhs": [
   "JSON_STRING"
  ]
 },
 {
  "lhs": "reference",
  "rhs": [
   "REFERENCE"
  ]
 },
 {
  "lhs": "reference",
  "rhs": [
   "basename-reference"
  ]
 },
 {
  "lhs": "$21",
  "rhs": [
   {
    "literal": "."
   }
  ]
 },
 {
  "lhs": "$24",
  "rhs": [
   {
    "literal": "."
   }
  ]
 },
 {
  "lhs": "$23",
  "rhs": [
   "$24",
   "REFERENCE_COMPONENT"
  ]
 },
 {
  "lhs": "$22",
  "rhs": []
 },
 {
  "lhs": "$22",
  "rhs": [
   "$23",
   "$22"
  ]
 },
 {
  "lhs": "basename-reference",
  "rhs": [
   "REFERENCE_COMPONENT",
   "$21",
   "REFERENCE_COMPONENT",
   "$22"
  ]
 },
 {
  "lhs": "$25",
  "rhs": [
   {
    "literal": "UInt64"
   }
  ]
 },
 {
  "lhs": "$26",
  "rhs": [
   {
    "literal": "Bool"
   }
  ]
 },
 {
  "lhs": "$27",
  "rhs": [
   {
    "literal": "String"
   }
  ]
 },
 {
  "lhs": "$28",
  "rhs": [
   {
    "literal": "optional"
   }
  ]
 },
 {
  "lhs": "$29",
  "rhs": [
   {
    "literal": "<"
   }
  ]
 },
 {
  "lhs": "$30",
  "rhs": [
   {
    "literal": ">"
   }
  ]
 },
 {
  "lhs": "$31",
  "rhs": [
   {
    "literal": "List"
   }
  ]
 },
 {
  "lhs": "$32",
  "rhs": [
   {
    "literal": "<"
   }
  ]
 },
 {
  "lhs": "$33",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$34",
  "rhs": [
   {
    "literal": ">"
   }
  ]
 },
 {
  "lhs": "$35",
  "rhs": [
   {
    "literal": "literal"
   }
  ]
 },
 {
  "lhs": "$36",
  "rhs": [
   {
    "literal": "outcome"
   }
  ]
 },
 {
  "lhs": "$37",
  "rhs": [
   {
    "literal": "<"
   }
  ]
 },
 {
  "lhs": "$38",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$39",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$40",
  "rhs": [
   {
    "literal": ">"
   }
  ]
 },
 {
  "lhs": "type",
  "rhs": [
   "$25"
  ]
 },
 {
  "lhs": "type",
  "rhs": [
   "$26"
  ]
 },
 {
  "lhs": "type",
  "rhs": [
   "$27"
  ]
 },
 {
  "lhs": "type",
  "rhs": [
   "qualified-name"
  ]
 },
 {
  "lhs": "type",
  "rhs": [
   "$28",
   "$29",
   "type",
   "$30"
  ]
 },
 {
  "lhs": "type",
  "rhs": [
   "$31",
   "$32",
   "type",
   "$33",
   "natural",
   "$34"
  ]
 },
 {
  "lhs": "type",
  "rhs": [
   "$35",
   "json-string"
  ]
 },
 {
  "lhs": "type",
  "rhs": [
   "$36",
   "$37",
   "type",
   "$38",
   "type",
   "$39",
   "natural",
   "$40"
  ]
 },
 {
  "lhs": "$41",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "binder",
  "rhs": [
   "NAME",
   "$41",
   "type"
  ]
 },
 {
  "lhs": "$42",
  "rhs": [
   {
    "literal": "input"
   }
  ]
 },
 {
  "lhs": "parameter",
  "rhs": [
   "$42",
   "NAME",
   "type",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$43",
  "rhs": [
   {
    "literal": "context"
   }
  ]
 },
 {
  "lhs": "context",
  "rhs": [
   "$43",
   "NAME",
   "qualified-name",
   "NEWLINE"
  ]
 },
 {
  "lhs": "declaration",
  "rhs": [
   "record-declaration"
  ]
 },
 {
  "lhs": "declaration",
  "rhs": [
   "enum-declaration"
  ]
 },
 {
  "lhs": "declaration",
  "rhs": [
   "rule-declaration"
  ]
 },
 {
  "lhs": "declaration",
  "rhs": [
   "calculation-declaration"
  ]
 },
 {
  "lhs": "declaration",
  "rhs": [
   "mapping-declaration"
  ]
 },
 {
  "lhs": "declaration",
  "rhs": [
   "policy-declaration"
  ]
 },
 {
  "lhs": "declaration",
  "rhs": [
   "machine-declaration"
  ]
 },
 {
  "lhs": "declaration",
  "rhs": [
   "operation-declaration"
  ]
 },
 {
  "lhs": "declaration",
  "rhs": [
   "query-declaration"
  ]
 },
 {
  "lhs": "declaration",
  "rhs": [
   "workflow-declaration"
  ]
 },
 {
  "lhs": "declaration",
  "rhs": [
   "generic-workflow-declaration"
  ]
 },
 {
  "lhs": "declaration",
  "rhs": [
   "interface-declaration"
  ]
 },
 {
  "lhs": "declaration",
  "rhs": [
   "entry-declaration"
  ]
 },
 {
  "lhs": "declaration",
  "rhs": [
   "claim-declaration"
  ]
 },
 {
  "lhs": "$45",
  "rhs": [
   {
    "literal": "entity"
   }
  ]
 },
 {
  "lhs": "$46",
  "rhs": [
   {
    "literal": "value-object"
   }
  ]
 },
 {
  "lhs": "$47",
  "rhs": [
   {
    "literal": "event"
   }
  ]
 },
 {
  "lhs": "$44",
  "rhs": [
   "$45"
  ]
 },
 {
  "lhs": "$44",
  "rhs": [
   "$46"
  ]
 },
 {
  "lhs": "$44",
  "rhs": [
   "$47"
  ]
 },
 {
  "lhs": "$48",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$50",
  "rhs": [
   "record-clause"
  ]
 },
 {
  "lhs": "$49",
  "rhs": []
 },
 {
  "lhs": "$49",
  "rhs": [
   "$50",
   "$49"
  ]
 },
 {
  "lhs": "$51",
  "rhs": [
   {
    "literal": "event"
   }
  ]
 },
 {
  "lhs": "$52",
  "rhs": [
   {
    "literal": "version"
   }
  ]
 },
 {
  "lhs": "$53",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "record-declaration",
  "rhs": [
   "$44",
   "NAME",
   "$48",
   "NEWLINE",
   "INDENT",
   "record-clause",
   "$49",
   "DEDENT"
  ]
 },
 {
  "lhs": "record-declaration",
  "rhs": [
   "$51",
   "NAME",
   "$52",
   "natural",
   "$53",
   "NEWLINE",
   "INDENT",
   "event-clause",
   "event-clause",
   "event-clause",
   "DEDENT"
  ]
 },
 {
  "lhs": "$54",
  "rhs": [
   {
    "literal": "payload"
   }
  ]
 },
 {
  "lhs": "$55",
  "rhs": [
   {
    "literal": "from"
   }
  ]
 },
 {
  "lhs": "$56",
  "rhs": [
   {
    "literal": "delivered-to"
   }
  ]
 },
 {
  "lhs": "event-clause",
  "rhs": [
   "$54",
   "type",
   "NEWLINE"
  ]
 },
 {
  "lhs": "event-clause",
  "rhs": [
   "$55",
   "qualified-name",
   "NEWLINE"
  ]
 },
 {
  "lhs": "event-clause",
  "rhs": [
   "$56",
   "qualified-name",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$57",
  "rhs": [
   {
    "literal": "version"
   }
  ]
 },
 {
  "lhs": "$58",
  "rhs": [
   {
    "literal": "identity"
   }
  ]
 },
 {
  "lhs": "$59",
  "rhs": [
   {
    "literal": "unique"
   }
  ]
 },
 {
  "lhs": "$60",
  "rhs": [
   {
    "literal": "immutable"
   }
  ]
 },
 {
  "lhs": "$62",
  "rhs": [
   {
    "literal": "all"
   }
  ]
 },
 {
  "lhs": "$61",
  "rhs": [
   "$62"
  ]
 },
 {
  "lhs": "$61",
  "rhs": [
   "name-list"
  ]
 },
 {
  "lhs": "$63",
  "rhs": [
   {
    "literal": "invariant"
   }
  ]
 },
 {
  "lhs": "record-clause",
  "rhs": [
   "NAME",
   "type",
   "NEWLINE"
  ]
 },
 {
  "lhs": "record-clause",
  "rhs": [
   "$57",
   "natural",
   "NEWLINE"
  ]
 },
 {
  "lhs": "record-clause",
  "rhs": [
   "$58",
   "name-list",
   "NEWLINE"
  ]
 },
 {
  "lhs": "record-clause",
  "rhs": [
   "$59",
   "name-list",
   "NEWLINE"
  ]
 },
 {
  "lhs": "record-clause",
  "rhs": [
   "$60",
   "$61",
   "NEWLINE"
  ]
 },
 {
  "lhs": "record-clause",
  "rhs": [
   "$63",
   "expression",
   "NEWLINE"
  ]
 },
 {
  "lhs": "record-clause",
  "rhs": [
   "refinement-clause"
  ]
 },
 {
  "lhs": "$64",
  "rhs": [
   {
    "literal": "carrier"
   },
   {
    "literal": "String"
   }
  ]
 },
 {
  "lhs": "$65",
  "rhs": [
   {
    "literal": "representation"
   },
   {
    "literal": "transparent-scalar"
   }
  ]
 },
 {
  "lhs": "$66",
  "rhs": [
   {
    "literal": "unicode"
   },
   {
    "literal": "well-formed-scalars"
   }
  ]
 },
 {
  "lhs": "$67",
  "rhs": [
   {
    "literal": "utf8-bytes"
   }
  ]
 },
 {
  "lhs": "$68",
  "rhs": [
   {
    "literal": ".."
   }
  ]
 },
 {
  "lhs": "$69",
  "rhs": [
   {
    "literal": "unicode-scalars"
   }
  ]
 },
 {
  "lhs": "$70",
  "rhs": [
   {
    "literal": ".."
   }
  ]
 },
 {
  "lhs": "$71",
  "rhs": [
   {
    "literal": "pattern"
   }
  ]
 },
 {
  "lhs": "$72",
  "rhs": [
   {
    "literal": "equality"
   },
   {
    "literal": "exact-scalar-sequence"
   }
  ]
 },
 {
  "lhs": "$73",
  "rhs": [
   {
    "literal": "normalization"
   },
   {
    "literal": "none"
   }
  ]
 },
 {
  "lhs": "$74",
  "rhs": [
   {
    "literal": "case-fold"
   },
   {
    "literal": "none"
   }
  ]
 },
 {
  "lhs": "$75",
  "rhs": [
   {
    "literal": "trim"
   },
   {
    "literal": "none"
   }
  ]
 },
 {
  "lhs": "refinement-clause",
  "rhs": [
   "$64",
   "NEWLINE"
  ]
 },
 {
  "lhs": "refinement-clause",
  "rhs": [
   "$65",
   "NEWLINE"
  ]
 },
 {
  "lhs": "refinement-clause",
  "rhs": [
   "$66",
   "NEWLINE"
  ]
 },
 {
  "lhs": "refinement-clause",
  "rhs": [
   "$67",
   "natural",
   "$68",
   "natural",
   "NEWLINE"
  ]
 },
 {
  "lhs": "refinement-clause",
  "rhs": [
   "$69",
   "natural",
   "$70",
   "natural",
   "NEWLINE"
  ]
 },
 {
  "lhs": "refinement-clause",
  "rhs": [
   "$71",
   "json-string",
   "NEWLINE"
  ]
 },
 {
  "lhs": "refinement-clause",
  "rhs": [
   "$72",
   "NEWLINE"
  ]
 },
 {
  "lhs": "refinement-clause",
  "rhs": [
   "$73",
   "NEWLINE"
  ]
 },
 {
  "lhs": "refinement-clause",
  "rhs": [
   "$74",
   "NEWLINE"
  ]
 },
 {
  "lhs": "refinement-clause",
  "rhs": [
   "$75",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$76",
  "rhs": [
   {
    "literal": "enum"
   }
  ]
 },
 {
  "lhs": "$77",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$79",
  "rhs": [
   "enum-item"
  ]
 },
 {
  "lhs": "$78",
  "rhs": []
 },
 {
  "lhs": "$78",
  "rhs": [
   "$79",
   "$78"
  ]
 },
 {
  "lhs": "enum-declaration",
  "rhs": [
   "$76",
   "NAME",
   "$77",
   "NEWLINE",
   "INDENT",
   "enum-item",
   "$78",
   "DEDENT"
  ]
 },
 {
  "lhs": "$80",
  "rhs": [
   {
    "literal": "value"
   }
  ]
 },
 {
  "lhs": "$83",
  "rhs": [
   {
    "literal": "wire"
   }
  ]
 },
 {
  "lhs": "$82",
  "rhs": [
   "$83",
   "json-string"
  ]
 },
 {
  "lhs": "$81",
  "rhs": []
 },
 {
  "lhs": "$81",
  "rhs": [
   "$82"
  ]
 },
 {
  "lhs": "$84",
  "rhs": [
   {
    "literal": "variant"
   }
  ]
 },
 {
  "lhs": "$86",
  "rhs": [
   "NAME",
   "type"
  ]
 },
 {
  "lhs": "$85",
  "rhs": []
 },
 {
  "lhs": "$85",
  "rhs": [
   "$86",
   "$85"
  ]
 },
 {
  "lhs": "enum-item",
  "rhs": [
   "$80",
   "NAME",
   "$81",
   "NEWLINE"
  ]
 },
 {
  "lhs": "enum-item",
  "rhs": [
   "$84",
   "NAME",
   "$85",
   "NEWLINE"
  ]
 },
 {
  "lhs": "expression",
  "rhs": [
   "implication"
  ]
 },
 {
  "lhs": "$89",
  "rhs": [
   {
    "literal": "implies"
   }
  ]
 },
 {
  "lhs": "$88",
  "rhs": [
   "$89",
   "implication"
  ]
 },
 {
  "lhs": "$87",
  "rhs": []
 },
 {
  "lhs": "$87",
  "rhs": [
   "$88"
  ]
 },
 {
  "lhs": "implication",
  "rhs": [
   "disjunction",
   "$87"
  ]
 },
 {
  "lhs": "$92",
  "rhs": [
   {
    "literal": "or"
   }
  ]
 },
 {
  "lhs": "$91",
  "rhs": [
   "$92",
   "conjunction"
  ]
 },
 {
  "lhs": "$90",
  "rhs": []
 },
 {
  "lhs": "$90",
  "rhs": [
   "$91",
   "$90"
  ]
 },
 {
  "lhs": "disjunction",
  "rhs": [
   "conjunction",
   "$90"
  ]
 },
 {
  "lhs": "$95",
  "rhs": [
   {
    "literal": "and"
   }
  ]
 },
 {
  "lhs": "$94",
  "rhs": [
   "$95",
   "comparison"
  ]
 },
 {
  "lhs": "$93",
  "rhs": []
 },
 {
  "lhs": "$93",
  "rhs": [
   "$94",
   "$93"
  ]
 },
 {
  "lhs": "conjunction",
  "rhs": [
   "comparison",
   "$93"
  ]
 },
 {
  "lhs": "$99",
  "rhs": [
   {
    "literal": "=="
   }
  ]
 },
 {
  "lhs": "$100",
  "rhs": [
   {
    "literal": "!="
   }
  ]
 },
 {
  "lhs": "$101",
  "rhs": [
   {
    "literal": "<"
   }
  ]
 },
 {
  "lhs": "$102",
  "rhs": [
   {
    "literal": "<="
   }
  ]
 },
 {
  "lhs": "$103",
  "rhs": [
   {
    "literal": ">"
   }
  ]
 },
 {
  "lhs": "$104",
  "rhs": [
   {
    "literal": ">="
   }
  ]
 },
 {
  "lhs": "$98",
  "rhs": [
   "$99"
  ]
 },
 {
  "lhs": "$98",
  "rhs": [
   "$100"
  ]
 },
 {
  "lhs": "$98",
  "rhs": [
   "$101"
  ]
 },
 {
  "lhs": "$98",
  "rhs": [
   "$102"
  ]
 },
 {
  "lhs": "$98",
  "rhs": [
   "$103"
  ]
 },
 {
  "lhs": "$98",
  "rhs": [
   "$104"
  ]
 },
 {
  "lhs": "$105",
  "rhs": [
   {
    "literal": "in"
   }
  ]
 },
 {
  "lhs": "$97",
  "rhs": [
   "$98",
   "sum"
  ]
 },
 {
  "lhs": "$97",
  "rhs": [
   "$105",
   "list-expression"
  ]
 },
 {
  "lhs": "$96",
  "rhs": []
 },
 {
  "lhs": "$96",
  "rhs": [
   "$97"
  ]
 },
 {
  "lhs": "comparison",
  "rhs": [
   "sum",
   "$96"
  ]
 },
 {
  "lhs": "$109",
  "rhs": [
   {
    "literal": "+"
   }
  ]
 },
 {
  "lhs": "$110",
  "rhs": [
   {
    "literal": "-"
   }
  ]
 },
 {
  "lhs": "$108",
  "rhs": [
   "$109"
  ]
 },
 {
  "lhs": "$108",
  "rhs": [
   "$110"
  ]
 },
 {
  "lhs": "$107",
  "rhs": [
   "$108",
   "product"
  ]
 },
 {
  "lhs": "$106",
  "rhs": []
 },
 {
  "lhs": "$106",
  "rhs": [
   "$107",
   "$106"
  ]
 },
 {
  "lhs": "sum",
  "rhs": [
   "product",
   "$106"
  ]
 },
 {
  "lhs": "$114",
  "rhs": [
   {
    "literal": "*"
   }
  ]
 },
 {
  "lhs": "$115",
  "rhs": [
   {
    "literal": "/"
   }
  ]
 },
 {
  "lhs": "$113",
  "rhs": [
   "$114"
  ]
 },
 {
  "lhs": "$113",
  "rhs": [
   "$115"
  ]
 },
 {
  "lhs": "$112",
  "rhs": [
   "$113",
   "unary"
  ]
 },
 {
  "lhs": "$111",
  "rhs": []
 },
 {
  "lhs": "$111",
  "rhs": [
   "$112",
   "$111"
  ]
 },
 {
  "lhs": "product",
  "rhs": [
   "unary",
   "$111"
  ]
 },
 {
  "lhs": "$118",
  "rhs": [
   {
    "literal": "not"
   }
  ]
 },
 {
  "lhs": "$117",
  "rhs": [
   "$118"
  ]
 },
 {
  "lhs": "$116",
  "rhs": []
 },
 {
  "lhs": "$116",
  "rhs": [
   "$117"
  ]
 },
 {
  "lhs": "unary",
  "rhs": [
   "$116",
   "postfix"
  ]
 },
 {
  "lhs": "$121",
  "rhs": [
   {
    "literal": "."
   }
  ]
 },
 {
  "lhs": "$120",
  "rhs": [
   "$121",
   "NAME"
  ]
 },
 {
  "lhs": "$119",
  "rhs": []
 },
 {
  "lhs": "$119",
  "rhs": [
   "$120",
   "$119"
  ]
 },
 {
  "lhs": "postfix",
  "rhs": [
   "primary",
   "$119"
  ]
 },
 {
  "lhs": "$122",
  "rhs": [
   {
    "literal": "true"
   }
  ]
 },
 {
  "lhs": "$123",
  "rhs": [
   {
    "literal": "false"
   }
  ]
 },
 {
  "lhs": "$124",
  "rhs": [
   {
    "literal": "none"
   }
  ]
 },
 {
  "lhs": "$125",
  "rhs": [
   {
    "literal": "("
   }
  ]
 },
 {
  "lhs": "$126",
  "rhs": [
   {
    "literal": ")"
   }
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "natural"
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "$122"
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "$123"
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "json-string"
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "$124"
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "qualified-name"
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "list-expression"
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "$125",
   "expression",
   "$126"
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "invocation"
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "map-expression"
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "filter-expression"
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "fold-expression"
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "indexed-fold-expression"
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "repeat-expression"
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "condition-loop-expression"
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "range-expression"
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "sort-expression"
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "optional-match"
  ]
 },
 {
  "lhs": "primary",
  "rhs": [
   "inline-match"
  ]
 },
 {
  "lhs": "$127",
  "rhs": [
   {
    "literal": "["
   }
  ]
 },
 {
  "lhs": "$132",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$131",
  "rhs": [
   "$132",
   "expression"
  ]
 },
 {
  "lhs": "$130",
  "rhs": []
 },
 {
  "lhs": "$130",
  "rhs": [
   "$131",
   "$130"
  ]
 },
 {
  "lhs": "$129",
  "rhs": [
   "expression",
   "$130"
  ]
 },
 {
  "lhs": "$128",
  "rhs": []
 },
 {
  "lhs": "$128",
  "rhs": [
   "$129"
  ]
 },
 {
  "lhs": "$133",
  "rhs": [
   {
    "literal": "]"
   }
  ]
 },
 {
  "lhs": "list-expression",
  "rhs": [
   "$127",
   "$128",
   "$133"
  ]
 },
 {
  "lhs": "$134",
  "rhs": [
   {
    "literal": "("
   }
  ]
 },
 {
  "lhs": "$136",
  "rhs": [
   "arguments"
  ]
 },
 {
  "lhs": "$135",
  "rhs": []
 },
 {
  "lhs": "$135",
  "rhs": [
   "$136"
  ]
 },
 {
  "lhs": "$137",
  "rhs": [
   {
    "literal": ")"
   }
  ]
 },
 {
  "lhs": "invocation",
  "rhs": [
   "callable",
   "$134",
   "$135",
   "$137"
  ]
 },
 {
  "lhs": "callable",
  "rhs": [
   "qualified-name"
  ]
 },
 {
  "lhs": "callable",
  "rhs": [
   "intrinsic"
  ]
 },
 {
  "lhs": "$138",
  "rhs": [
   {
    "literal": "checked-add"
   }
  ]
 },
 {
  "lhs": "$139",
  "rhs": [
   {
    "literal": "checked-subtract"
   }
  ]
 },
 {
  "lhs": "$140",
  "rhs": [
   {
    "literal": "checked-multiply"
   }
  ]
 },
 {
  "lhs": "$141",
  "rhs": [
   {
    "literal": "checked-divide"
   }
  ]
 },
 {
  "lhs": "$142",
  "rhs": [
   {
    "literal": "some"
   }
  ]
 },
 {
  "lhs": "$143",
  "rhs": [
   {
    "literal": "present"
   }
  ]
 },
 {
  "lhs": "$144",
  "rhs": [
   {
    "literal": "absent"
   }
  ]
 },
 {
  "lhs": "$145",
  "rhs": [
   {
    "literal": "require-some"
   }
  ]
 },
 {
  "lhs": "$146",
  "rhs": [
   {
    "literal": "require-variant"
   }
  ]
 },
 {
  "lhs": "$147",
  "rhs": [
   {
    "literal": "length"
   }
  ]
 },
 {
  "lhs": "$148",
  "rhs": [
   {
    "literal": "tag"
   }
  ]
 },
 {
  "lhs": "$149",
  "rhs": [
   {
    "literal": "all-unique-exact"
   }
  ]
 },
 {
  "lhs": "$150",
  "rhs": [
   {
    "literal": "length-utf8"
   }
  ]
 },
 {
  "lhs": "$151",
  "rhs": [
   {
    "literal": "length-scalars"
   }
  ]
 },
 {
  "lhs": "intrinsic",
  "rhs": [
   "$138"
  ]
 },
 {
  "lhs": "intrinsic",
  "rhs": [
   "$139"
  ]
 },
 {
  "lhs": "intrinsic",
  "rhs": [
   "$140"
  ]
 },
 {
  "lhs": "intrinsic",
  "rhs": [
   "$141"
  ]
 },
 {
  "lhs": "intrinsic",
  "rhs": [
   "$142"
  ]
 },
 {
  "lhs": "intrinsic",
  "rhs": [
   "$143"
  ]
 },
 {
  "lhs": "intrinsic",
  "rhs": [
   "$144"
  ]
 },
 {
  "lhs": "intrinsic",
  "rhs": [
   "$145"
  ]
 },
 {
  "lhs": "intrinsic",
  "rhs": [
   "$146"
  ]
 },
 {
  "lhs": "intrinsic",
  "rhs": [
   "$147"
  ]
 },
 {
  "lhs": "intrinsic",
  "rhs": [
   "$148"
  ]
 },
 {
  "lhs": "intrinsic",
  "rhs": [
   "$149"
  ]
 },
 {
  "lhs": "intrinsic",
  "rhs": [
   "$150"
  ]
 },
 {
  "lhs": "intrinsic",
  "rhs": [
   "$151"
  ]
 },
 {
  "lhs": "$154",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$153",
  "rhs": [
   "$154",
   "expression"
  ]
 },
 {
  "lhs": "$152",
  "rhs": []
 },
 {
  "lhs": "$152",
  "rhs": [
   "$153",
   "$152"
  ]
 },
 {
  "lhs": "$157",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$156",
  "rhs": [
   "$157",
   "named-argument"
  ]
 },
 {
  "lhs": "$155",
  "rhs": []
 },
 {
  "lhs": "$155",
  "rhs": [
   "$156",
   "$155"
  ]
 },
 {
  "lhs": "arguments",
  "rhs": [
   "expression",
   "$152"
  ]
 },
 {
  "lhs": "arguments",
  "rhs": [
   "named-argument",
   "$155"
  ]
 },
 {
  "lhs": "$158",
  "rhs": [
   {
    "literal": "="
   }
  ]
 },
 {
  "lhs": "named-argument",
  "rhs": [
   "NAME",
   "$158",
   "expression"
  ]
 },
 {
  "lhs": "$159",
  "rhs": [
   {
    "literal": "map"
   }
  ]
 },
 {
  "lhs": "$160",
  "rhs": [
   {
    "literal": "("
   }
  ]
 },
 {
  "lhs": "$161",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$162",
  "rhs": [
   {
    "literal": "=>"
   }
  ]
 },
 {
  "lhs": "$163",
  "rhs": [
   {
    "literal": ")"
   }
  ]
 },
 {
  "lhs": "map-expression",
  "rhs": [
   "$159",
   "$160",
   "expression",
   "$161",
   "binder",
   "$162",
   "expression",
   "$163"
  ]
 },
 {
  "lhs": "$164",
  "rhs": [
   {
    "literal": "filter"
   }
  ]
 },
 {
  "lhs": "$165",
  "rhs": [
   {
    "literal": "("
   }
  ]
 },
 {
  "lhs": "$166",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$167",
  "rhs": [
   {
    "literal": "=>"
   }
  ]
 },
 {
  "lhs": "$168",
  "rhs": [
   {
    "literal": ")"
   }
  ]
 },
 {
  "lhs": "filter-expression",
  "rhs": [
   "$164",
   "$165",
   "expression",
   "$166",
   "binder",
   "$167",
   "expression",
   "$168"
  ]
 },
 {
  "lhs": "$169",
  "rhs": [
   {
    "literal": "fold"
   }
  ]
 },
 {
  "lhs": "$170",
  "rhs": [
   {
    "literal": "("
   }
  ]
 },
 {
  "lhs": "$171",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$172",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$173",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$174",
  "rhs": [
   {
    "literal": "=>"
   }
  ]
 },
 {
  "lhs": "$175",
  "rhs": [
   {
    "literal": ")"
   }
  ]
 },
 {
  "lhs": "fold-expression",
  "rhs": [
   "$169",
   "$170",
   "expression",
   "$171",
   "expression",
   "$172",
   "binder",
   "$173",
   "binder",
   "$174",
   "expression",
   "$175"
  ]
 },
 {
  "lhs": "$176",
  "rhs": [
   {
    "literal": "indexed-fold"
   }
  ]
 },
 {
  "lhs": "$177",
  "rhs": [
   {
    "literal": "("
   }
  ]
 },
 {
  "lhs": "$178",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$179",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$180",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$181",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$182",
  "rhs": [
   {
    "literal": "=>"
   }
  ]
 },
 {
  "lhs": "$183",
  "rhs": [
   {
    "literal": ")"
   }
  ]
 },
 {
  "lhs": "indexed-fold-expression",
  "rhs": [
   "$176",
   "$177",
   "expression",
   "$178",
   "expression",
   "$179",
   "binder",
   "$180",
   "binder",
   "$181",
   "binder",
   "$182",
   "expression",
   "$183"
  ]
 },
 {
  "lhs": "$184",
  "rhs": [
   {
    "literal": "repeat"
   }
  ]
 },
 {
  "lhs": "$185",
  "rhs": [
   {
    "literal": "("
   }
  ]
 },
 {
  "lhs": "$186",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$187",
  "rhs": [
   {
    "literal": "max"
   }
  ]
 },
 {
  "lhs": "$188",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$189",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$190",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$191",
  "rhs": [
   {
    "literal": "=>"
   }
  ]
 },
 {
  "lhs": "$192",
  "rhs": [
   {
    "literal": ")"
   }
  ]
 },
 {
  "lhs": "repeat-expression",
  "rhs": [
   "$184",
   "$185",
   "expression",
   "$186",
   "$187",
   "natural",
   "$188",
   "expression",
   "$189",
   "binder",
   "$190",
   "binder",
   "$191",
   "expression",
   "$192"
  ]
 },
 {
  "lhs": "$194",
  "rhs": [
   {
    "literal": "while-bounded"
   }
  ]
 },
 {
  "lhs": "$195",
  "rhs": [
   {
    "literal": "until-bounded"
   }
  ]
 },
 {
  "lhs": "$193",
  "rhs": [
   "$194"
  ]
 },
 {
  "lhs": "$193",
  "rhs": [
   "$195"
  ]
 },
 {
  "lhs": "$196",
  "rhs": [
   {
    "literal": "("
   }
  ]
 },
 {
  "lhs": "$197",
  "rhs": [
   {
    "literal": "max"
   }
  ]
 },
 {
  "lhs": "$198",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$199",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$200",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$201",
  "rhs": [
   {
    "literal": "=>"
   }
  ]
 },
 {
  "lhs": "$202",
  "rhs": [
   {
    "literal": ")"
   }
  ]
 },
 {
  "lhs": "condition-loop-expression",
  "rhs": [
   "$193",
   "$196",
   "$197",
   "natural",
   "$198",
   "expression",
   "$199",
   "binder",
   "$200",
   "expression",
   "$201",
   "expression",
   "$202"
  ]
 },
 {
  "lhs": "$203",
  "rhs": [
   {
    "literal": "range"
   }
  ]
 },
 {
  "lhs": "$204",
  "rhs": [
   {
    "literal": "("
   }
  ]
 },
 {
  "lhs": "$205",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$206",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$207",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$208",
  "rhs": [
   {
    "literal": "max"
   }
  ]
 },
 {
  "lhs": "$209",
  "rhs": [
   {
    "literal": ")"
   }
  ]
 },
 {
  "lhs": "range-expression",
  "rhs": [
   "$203",
   "$204",
   "expression",
   "$205",
   "expression",
   "$206",
   "expression",
   "$207",
   "$208",
   "natural",
   "$209"
  ]
 },
 {
  "lhs": "$210",
  "rhs": [
   {
    "literal": "sort"
   }
  ]
 },
 {
  "lhs": "$211",
  "rhs": [
   {
    "literal": "("
   }
  ]
 },
 {
  "lhs": "$212",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$213",
  "rhs": [
   {
    "literal": ")"
   }
  ]
 },
 {
  "lhs": "$214",
  "rhs": [
   {
    "literal": "sort"
   }
  ]
 },
 {
  "lhs": "$215",
  "rhs": [
   {
    "literal": "("
   }
  ]
 },
 {
  "lhs": "$216",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$217",
  "rhs": [
   {
    "literal": "=>"
   }
  ]
 },
 {
  "lhs": "$218",
  "rhs": [
   {
    "literal": "["
   }
  ]
 },
 {
  "lhs": "$221",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$220",
  "rhs": [
   "$221",
   "sort-key"
  ]
 },
 {
  "lhs": "$219",
  "rhs": []
 },
 {
  "lhs": "$219",
  "rhs": [
   "$220",
   "$219"
  ]
 },
 {
  "lhs": "$222",
  "rhs": [
   {
    "literal": "]"
   }
  ]
 },
 {
  "lhs": "$223",
  "rhs": [
   {
    "literal": ")"
   }
  ]
 },
 {
  "lhs": "sort-expression",
  "rhs": [
   "$210",
   "$211",
   "expression",
   "$212",
   "NAME",
   "direction",
   "sort-mode",
   "$213"
  ]
 },
 {
  "lhs": "sort-expression",
  "rhs": [
   "$214",
   "$215",
   "expression",
   "$216",
   "binder",
   "$217",
   "$218",
   "sort-key",
   "$219",
   "$222",
   "$223"
  ]
 },
 {
  "lhs": "sort-key",
  "rhs": [
   "expression",
   "direction",
   "sort-mode"
  ]
 },
 {
  "lhs": "$224",
  "rhs": [
   {
    "literal": "ascending"
   }
  ]
 },
 {
  "lhs": "$225",
  "rhs": [
   {
    "literal": "descending"
   }
  ]
 },
 {
  "lhs": "direction",
  "rhs": [
   "$224"
  ]
 },
 {
  "lhs": "direction",
  "rhs": [
   "$225"
  ]
 },
 {
  "lhs": "$226",
  "rhs": [
   {
    "literal": "numeric"
   }
  ]
 },
 {
  "lhs": "$227",
  "rhs": [
   {
    "literal": "lexical"
   }
  ]
 },
 {
  "lhs": "$228",
  "rhs": [
   {
    "literal": "natural"
   }
  ]
 },
 {
  "lhs": "$229",
  "rhs": [
   {
    "literal": "binary-utf8"
   }
  ]
 },
 {
  "lhs": "sort-mode",
  "rhs": [
   "$226"
  ]
 },
 {
  "lhs": "sort-mode",
  "rhs": [
   "$227"
  ]
 },
 {
  "lhs": "sort-mode",
  "rhs": [
   "$228"
  ]
 },
 {
  "lhs": "sort-mode",
  "rhs": [
   "$229"
  ]
 },
 {
  "lhs": "$230",
  "rhs": [
   {
    "literal": "match"
   }
  ]
 },
 {
  "lhs": "$231",
  "rhs": [
   {
    "literal": "some"
   }
  ]
 },
 {
  "lhs": "$232",
  "rhs": [
   {
    "literal": "("
   }
  ]
 },
 {
  "lhs": "$233",
  "rhs": [
   {
    "literal": ")"
   }
  ]
 },
 {
  "lhs": "$234",
  "rhs": [
   {
    "literal": "=>"
   }
  ]
 },
 {
  "lhs": "$235",
  "rhs": [
   {
    "literal": "else"
   }
  ]
 },
 {
  "lhs": "optional-match",
  "rhs": [
   "$230",
   "expression",
   "$231",
   "$232",
   "NAME",
   "$233",
   "$234",
   "expression",
   "$235",
   "expression"
  ]
 },
 {
  "lhs": "$236",
  "rhs": [
   {
    "literal": "match"
   }
  ]
 },
 {
  "lhs": "$237",
  "rhs": [
   {
    "literal": "=>"
   }
  ]
 },
 {
  "lhs": "$238",
  "rhs": [
   {
    "literal": "else"
   }
  ]
 },
 {
  "lhs": "inline-match",
  "rhs": [
   "$236",
   "postfix",
   "pattern-list",
   "$237",
   "expression",
   "$238",
   "expression"
  ]
 },
 {
  "lhs": "$241",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$240",
  "rhs": [
   "$241",
   "pattern"
  ]
 },
 {
  "lhs": "$239",
  "rhs": []
 },
 {
  "lhs": "$239",
  "rhs": [
   "$240",
   "$239"
  ]
 },
 {
  "lhs": "pattern-list",
  "rhs": [
   "pattern",
   "$239"
  ]
 },
 {
  "lhs": "$244",
  "rhs": [
   {
    "literal": "("
   }
  ]
 },
 {
  "lhs": "$245",
  "rhs": [
   {
    "literal": ")"
   }
  ]
 },
 {
  "lhs": "$243",
  "rhs": [
   "$244",
   "NAME",
   "$245"
  ]
 },
 {
  "lhs": "$242",
  "rhs": []
 },
 {
  "lhs": "$242",
  "rhs": [
   "$243"
  ]
 },
 {
  "lhs": "$246",
  "rhs": [
   {
    "literal": "true"
   }
  ]
 },
 {
  "lhs": "$247",
  "rhs": [
   {
    "literal": "false"
   }
  ]
 },
 {
  "lhs": "pattern",
  "rhs": [
   "qualified-name",
   "$242"
  ]
 },
 {
  "lhs": "pattern",
  "rhs": [
   "$246"
  ]
 },
 {
  "lhs": "pattern",
  "rhs": [
   "$247"
  ]
 },
 {
  "lhs": "$248",
  "rhs": [
   {
    "literal": "match"
   }
  ]
 },
 {
  "lhs": "$249",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$251",
  "rhs": [
   "match-case"
  ]
 },
 {
  "lhs": "$250",
  "rhs": []
 },
 {
  "lhs": "$250",
  "rhs": [
   "$251",
   "$250"
  ]
 },
 {
  "lhs": "expression-value",
  "rhs": [
   "expression",
   "NEWLINE"
  ]
 },
 {
  "lhs": "expression-value",
  "rhs": [
   "$248",
   "expression",
   "$249",
   "NEWLINE",
   "INDENT",
   "match-case",
   "$250",
   "DEDENT"
  ]
 },
 {
  "lhs": "$253",
  "rhs": [
   {
    "literal": "otherwise"
   }
  ]
 },
 {
  "lhs": "$252",
  "rhs": [
   "pattern-list"
  ]
 },
 {
  "lhs": "$252",
  "rhs": [
   "$253"
  ]
 },
 {
  "lhs": "$254",
  "rhs": [
   {
    "literal": "=>"
   }
  ]
 },
 {
  "lhs": "match-case",
  "rhs": [
   "$252",
   "$254",
   "expression",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$255",
  "rhs": [
   {
    "literal": "rule"
   }
  ]
 },
 {
  "lhs": "$256",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$258",
  "rhs": [
   "parameter"
  ]
 },
 {
  "lhs": "$257",
  "rhs": []
 },
 {
  "lhs": "$257",
  "rhs": [
   "$258",
   "$257"
  ]
 },
 {
  "lhs": "$259",
  "rhs": [
   {
    "literal": "expression"
   }
  ]
 },
 {
  "lhs": "rule-declaration",
  "rhs": [
   "$255",
   "NAME",
   "$256",
   "NEWLINE",
   "INDENT",
   "$257",
   "$259",
   "expression-value",
   "DEDENT"
  ]
 },
 {
  "lhs": "$260",
  "rhs": [
   {
    "literal": "calculation"
   }
  ]
 },
 {
  "lhs": "$261",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$262",
  "rhs": [
   {
    "literal": "pure"
   }
  ]
 },
 {
  "lhs": "$264",
  "rhs": [
   "parameter"
  ]
 },
 {
  "lhs": "$263",
  "rhs": []
 },
 {
  "lhs": "$263",
  "rhs": [
   "$264",
   "$263"
  ]
 },
 {
  "lhs": "$265",
  "rhs": [
   {
    "literal": "result"
   }
  ]
 },
 {
  "lhs": "$268",
  "rhs": [
   {
    "literal": "rounding"
   }
  ]
 },
 {
  "lhs": "$270",
  "rhs": [
   {
    "literal": "floor"
   }
  ]
 },
 {
  "lhs": "$271",
  "rhs": [
   {
    "literal": "ceil"
   }
  ]
 },
 {
  "lhs": "$272",
  "rhs": [
   {
    "literal": "reject"
   }
  ]
 },
 {
  "lhs": "$269",
  "rhs": [
   "$270"
  ]
 },
 {
  "lhs": "$269",
  "rhs": [
   "$271"
  ]
 },
 {
  "lhs": "$269",
  "rhs": [
   "$272"
  ]
 },
 {
  "lhs": "$267",
  "rhs": [
   "$268",
   "$269",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$266",
  "rhs": []
 },
 {
  "lhs": "$266",
  "rhs": [
   "$267"
  ]
 },
 {
  "lhs": "$273",
  "rhs": [
   {
    "literal": "expression"
   }
  ]
 },
 {
  "lhs": "$276",
  "rhs": [
   {
    "literal": "on-evaluation-error"
   }
  ]
 },
 {
  "lhs": "$275",
  "rhs": [
   "$276",
   "failure-action",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$274",
  "rhs": []
 },
 {
  "lhs": "$274",
  "rhs": [
   "$275"
  ]
 },
 {
  "lhs": "calculation-declaration",
  "rhs": [
   "$260",
   "NAME",
   "$261",
   "NEWLINE",
   "INDENT",
   "$262",
   "NEWLINE",
   "$263",
   "$265",
   "type",
   "NEWLINE",
   "$266",
   "$273",
   "expression-value",
   "$274",
   "DEDENT"
  ]
 },
 {
  "lhs": "$277",
  "rhs": [
   {
    "literal": "mapping"
   }
  ]
 },
 {
  "lhs": "$278",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$280",
  "rhs": [
   "parameter"
  ]
 },
 {
  "lhs": "$279",
  "rhs": []
 },
 {
  "lhs": "$279",
  "rhs": [
   "$280",
   "$279"
  ]
 },
 {
  "lhs": "$281",
  "rhs": [
   {
    "literal": "target"
   }
  ]
 },
 {
  "lhs": "$282",
  "rhs": [
   {
    "literal": "total"
   },
   {
    "literal": "true"
   }
  ]
 },
 {
  "lhs": "$285",
  "rhs": [
   {
    "literal": "requires"
   }
  ]
 },
 {
  "lhs": "$284",
  "rhs": [
   "$285",
   "expression",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$283",
  "rhs": []
 },
 {
  "lhs": "$283",
  "rhs": [
   "$284",
   "$283"
  ]
 },
 {
  "lhs": "mapping-declaration",
  "rhs": [
   "$277",
   "NAME",
   "$278",
   "NEWLINE",
   "INDENT",
   "$279",
   "$281",
   "type",
   "NEWLINE",
   "$282",
   "NEWLINE",
   "$283",
   "mapping-body",
   "DEDENT"
  ]
 },
 {
  "lhs": "$288",
  "rhs": [
   {
    "literal": "preserve"
   }
  ]
 },
 {
  "lhs": "$287",
  "rhs": [
   "$288",
   "name-list",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$286",
  "rhs": []
 },
 {
  "lhs": "$286",
  "rhs": [
   "$287"
  ]
 },
 {
  "lhs": "$290",
  "rhs": [
   "field-binding"
  ]
 },
 {
  "lhs": "$289",
  "rhs": []
 },
 {
  "lhs": "$289",
  "rhs": [
   "$290",
   "$289"
  ]
 },
 {
  "lhs": "$291",
  "rhs": [
   {
    "literal": "ordered-cases"
   },
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$293",
  "rhs": [
   "ordered-case"
  ]
 },
 {
  "lhs": "$292",
  "rhs": []
 },
 {
  "lhs": "$292",
  "rhs": [
   "$293",
   "$292"
  ]
 },
 {
  "lhs": "$294",
  "rhs": [
   {
    "literal": "expression"
   }
  ]
 },
 {
  "lhs": "mapping-body",
  "rhs": [
   "$286",
   "field-binding",
   "$289"
  ]
 },
 {
  "lhs": "mapping-body",
  "rhs": [
   "$291",
   "NEWLINE",
   "INDENT",
   "ordered-case",
   "$292",
   "DEDENT"
  ]
 },
 {
  "lhs": "mapping-body",
  "rhs": [
   "$294",
   "expression-value"
  ]
 },
 {
  "lhs": "$295",
  "rhs": [
   {
    "literal": "field"
   }
  ]
 },
 {
  "lhs": "$296",
  "rhs": [
   {
    "literal": "<-"
   }
  ]
 },
 {
  "lhs": "field-binding",
  "rhs": [
   "$295",
   "NAME",
   "$296",
   "expression",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$297",
  "rhs": [
   {
    "literal": "when"
   }
  ]
 },
 {
  "lhs": "$298",
  "rhs": [
   {
    "literal": "->"
   }
  ]
 },
 {
  "lhs": "$299",
  "rhs": [
   {
    "literal": "otherwise"
   }
  ]
 },
 {
  "lhs": "$300",
  "rhs": [
   {
    "literal": "->"
   }
  ]
 },
 {
  "lhs": "ordered-case",
  "rhs": [
   "step-name",
   "$297",
   "expression",
   "$298",
   "expression",
   "NEWLINE"
  ]
 },
 {
  "lhs": "ordered-case",
  "rhs": [
   "step-name",
   "$299",
   "$300",
   "expression",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$301",
  "rhs": [
   {
    "literal": "policy"
   }
  ]
 },
 {
  "lhs": "$302",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$304",
  "rhs": [
   "parameter"
  ]
 },
 {
  "lhs": "$303",
  "rhs": []
 },
 {
  "lhs": "$303",
  "rhs": [
   "$304",
   "$303"
  ]
 },
 {
  "lhs": "$305",
  "rhs": [
   {
    "literal": "result"
   }
  ]
 },
 {
  "lhs": "$306",
  "rhs": [
   {
    "literal": "ordered-cases"
   },
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$308",
  "rhs": [
   "policy-case"
  ]
 },
 {
  "lhs": "$307",
  "rhs": []
 },
 {
  "lhs": "$307",
  "rhs": [
   "$308",
   "$307"
  ]
 },
 {
  "lhs": "$309",
  "rhs": [
   {
    "literal": "otherwise"
   }
  ]
 },
 {
  "lhs": "$310",
  "rhs": [
   {
    "literal": "->"
   }
  ]
 },
 {
  "lhs": "policy-declaration",
  "rhs": [
   "$301",
   "NAME",
   "$302",
   "NEWLINE",
   "INDENT",
   "$303",
   "$305",
   "type",
   "NEWLINE",
   "$306",
   "NEWLINE",
   "INDENT",
   "policy-case",
   "$307",
   "$309",
   "$310",
   "invocation",
   "NEWLINE",
   "DEDENT",
   "DEDENT"
  ]
 },
 {
  "lhs": "$311",
  "rhs": [
   {
    "literal": "when"
   }
  ]
 },
 {
  "lhs": "$312",
  "rhs": [
   {
    "literal": "->"
   }
  ]
 },
 {
  "lhs": "policy-case",
  "rhs": [
   "step-name",
   "$311",
   "expression",
   "$312",
   "invocation",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$313",
  "rhs": [
   {
    "literal": "state-machine"
   }
  ]
 },
 {
  "lhs": "$314",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$315",
  "rhs": [
   {
    "literal": "state"
   }
  ]
 },
 {
  "lhs": "$316",
  "rhs": [
   {
    "literal": "input"
   }
  ]
 },
 {
  "lhs": "$317",
  "rhs": [
   {
    "literal": "initial"
   }
  ]
 },
 {
  "lhs": "$320",
  "rhs": [
   {
    "literal": "terminal"
   }
  ]
 },
 {
  "lhs": "$319",
  "rhs": [
   "$320",
   "name-list",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$318",
  "rhs": []
 },
 {
  "lhs": "$318",
  "rhs": [
   "$319"
  ]
 },
 {
  "lhs": "$322",
  "rhs": [
   "machine-transition"
  ]
 },
 {
  "lhs": "$321",
  "rhs": []
 },
 {
  "lhs": "$321",
  "rhs": [
   "$322",
   "$321"
  ]
 },
 {
  "lhs": "$323",
  "rhs": [
   {
    "literal": "otherwise"
   }
  ]
 },
 {
  "lhs": "$325",
  "rhs": [
   {
    "literal": "stay"
   }
  ]
 },
 {
  "lhs": "$326",
  "rhs": [
   {
    "literal": "reject"
   }
  ]
 },
 {
  "lhs": "$324",
  "rhs": [
   "$325"
  ]
 },
 {
  "lhs": "$324",
  "rhs": [
   "$326",
   "step-name"
  ]
 },
 {
  "lhs": "machine-declaration",
  "rhs": [
   "$313",
   "NAME",
   "$314",
   "NEWLINE",
   "INDENT",
   "$315",
   "type",
   "NEWLINE",
   "$316",
   "type",
   "NEWLINE",
   "$317",
   "qualified-name",
   "NEWLINE",
   "$318",
   "machine-transition",
   "$321",
   "$323",
   "$324",
   "NEWLINE",
   "DEDENT"
  ]
 },
 {
  "lhs": "$327",
  "rhs": [
   {
    "literal": "transition"
   }
  ]
 },
 {
  "lhs": "$330",
  "rhs": [
   {
    "literal": "when"
   }
  ]
 },
 {
  "lhs": "$329",
  "rhs": [
   "$330",
   "expression"
  ]
 },
 {
  "lhs": "$328",
  "rhs": []
 },
 {
  "lhs": "$328",
  "rhs": [
   "$329"
  ]
 },
 {
  "lhs": "$331",
  "rhs": [
   {
    "literal": "->"
   }
  ]
 },
 {
  "lhs": "machine-transition",
  "rhs": [
   "$327",
   "qualified-name",
   "qualified-name",
   "$328",
   "$331",
   "qualified-name",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$332",
  "rhs": [
   {
    "literal": "operation"
   }
  ]
 },
 {
  "lhs": "$333",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$335",
  "rhs": [
   "parameter"
  ]
 },
 {
  "lhs": "$335",
  "rhs": [
   "context"
  ]
 },
 {
  "lhs": "$334",
  "rhs": []
 },
 {
  "lhs": "$334",
  "rhs": [
   "$335",
   "$334"
  ]
 },
 {
  "lhs": "$336",
  "rhs": [
   {
    "literal": "output"
   }
  ]
 },
 {
  "lhs": "$337",
  "rhs": [
   "operation-statements"
  ]
 },
 {
  "lhs": "$337",
  "rhs": [
   "native-capture-body"
  ]
 },
 {
  "lhs": "$337",
  "rhs": [
   "replay-protocol"
  ]
 },
 {
  "lhs": "operation-declaration",
  "rhs": [
   "$332",
   "NAME",
   "$333",
   "NEWLINE",
   "INDENT",
   "$334",
   "$336",
   "type",
   "NEWLINE",
   "$337",
   "DEDENT"
  ]
 },
 {
  "lhs": "$339",
  "rhs": [
   "operation-statement"
  ]
 },
 {
  "lhs": "$338",
  "rhs": []
 },
 {
  "lhs": "$338",
  "rhs": [
   "$339",
   "$338"
  ]
 },
 {
  "lhs": "operation-statements",
  "rhs": [
   "operation-statement",
   "$338"
  ]
 },
 {
  "lhs": "operation-statement",
  "rhs": [
   "enforce-statement"
  ]
 },
 {
  "lhs": "operation-statement",
  "rhs": [
   "preflight"
  ]
 },
 {
  "lhs": "operation-statement",
  "rhs": [
   "guard"
  ]
 },
 {
  "lhs": "operation-statement",
  "rhs": [
   "let-statement"
  ]
 },
 {
  "lhs": "operation-statement",
  "rhs": [
   "read-statement"
  ]
 },
 {
  "lhs": "operation-statement",
  "rhs": [
   "call-statement"
  ]
 },
 {
  "lhs": "operation-statement",
  "rhs": [
   "condition-statement"
  ]
 },
 {
  "lhs": "operation-statement",
  "rhs": [
   "present-statement"
  ]
 },
 {
  "lhs": "operation-statement",
  "rhs": [
   "when-statement"
  ]
 },
 {
  "lhs": "operation-statement",
  "rhs": [
   "read-set"
  ]
 },
 {
  "lhs": "operation-statement",
  "rhs": [
   "transaction"
  ]
 },
 {
  "lhs": "operation-statement",
  "rhs": [
   "return-statement"
  ]
 },
 {
  "lhs": "operation-statement",
  "rhs": [
   "acknowledgement"
  ]
 },
 {
  "lhs": "$340",
  "rhs": [
   {
    "literal": "enforce"
   }
  ]
 },
 {
  "lhs": "enforce-statement",
  "rhs": [
   "$340",
   "invocation",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$341",
  "rhs": [
   {
    "literal": "preflight"
   },
   {
    "literal": "contract"
   }
  ]
 },
 {
  "lhs": "preflight",
  "rhs": [
   "$341",
   "qualified-name",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$342",
  "rhs": [
   {
    "literal": "requires"
   }
  ]
 },
 {
  "lhs": "$345",
  "rhs": [
   {
    "literal": "on-false"
   }
  ]
 },
 {
  "lhs": "$344",
  "rhs": [
   "$345",
   "action"
  ]
 },
 {
  "lhs": "$343",
  "rhs": []
 },
 {
  "lhs": "$343",
  "rhs": [
   "$344"
  ]
 },
 {
  "lhs": "guard",
  "rhs": [
   "$342",
   "expression",
   "$343",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$346",
  "rhs": [
   {
    "literal": "let"
   }
  ]
 },
 {
  "lhs": "$347",
  "rhs": [
   {
    "literal": "="
   }
  ]
 },
 {
  "lhs": "$349",
  "rhs": [
   {
    "literal": "count"
   }
  ]
 },
 {
  "lhs": "$348",
  "rhs": [
   "expression"
  ]
 },
 {
  "lhs": "$348",
  "rhs": [
   "$349",
   "qualified-name"
  ]
 },
 {
  "lhs": "$352",
  "rhs": [
   {
    "literal": "on-error"
   }
  ]
 },
 {
  "lhs": "$351",
  "rhs": [
   "$352",
   "action"
  ]
 },
 {
  "lhs": "$350",
  "rhs": []
 },
 {
  "lhs": "$350",
  "rhs": [
   "$351"
  ]
 },
 {
  "lhs": "let-statement",
  "rhs": [
   "$346",
   "NAME",
   "$347",
   "$348",
   "$350",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$353",
  "rhs": [
   {
    "literal": "read"
   }
  ]
 },
 {
  "lhs": "$354",
  "rhs": [
   {
    "literal": "by"
   }
  ]
 },
 {
  "lhs": "$359",
  "rhs": [
   "read-handler"
  ]
 },
 {
  "lhs": "$358",
  "rhs": []
 },
 {
  "lhs": "$358",
  "rhs": [
   "$359",
   "$358"
  ]
 },
 {
  "lhs": "$357",
  "rhs": [
   "INDENT",
   "read-handler",
   "$358",
   "DEDENT"
  ]
 },
 {
  "lhs": "$362",
  "rhs": [
   "read-handler"
  ]
 },
 {
  "lhs": "$361",
  "rhs": []
 },
 {
  "lhs": "$361",
  "rhs": [
   "$362",
   "$361"
  ]
 },
 {
  "lhs": "$360",
  "rhs": [
   "read-handler",
   "$361"
  ]
 },
 {
  "lhs": "$356",
  "rhs": [
   "$357"
  ]
 },
 {
  "lhs": "$356",
  "rhs": [
   "$360"
  ]
 },
 {
  "lhs": "$355",
  "rhs": []
 },
 {
  "lhs": "$355",
  "rhs": [
   "$356"
  ]
 },
 {
  "lhs": "$363",
  "rhs": [
   {
    "literal": "read"
   }
  ]
 },
 {
  "lhs": "$364",
  "rhs": [
   {
    "literal": "from"
   }
  ]
 },
 {
  "lhs": "$369",
  "rhs": [
   "read-handler"
  ]
 },
 {
  "lhs": "$368",
  "rhs": []
 },
 {
  "lhs": "$368",
  "rhs": [
   "$369",
   "$368"
  ]
 },
 {
  "lhs": "$367",
  "rhs": [
   "INDENT",
   "read-handler",
   "$368",
   "DEDENT"
  ]
 },
 {
  "lhs": "$372",
  "rhs": [
   "read-handler"
  ]
 },
 {
  "lhs": "$371",
  "rhs": []
 },
 {
  "lhs": "$371",
  "rhs": [
   "$372",
   "$371"
  ]
 },
 {
  "lhs": "$370",
  "rhs": [
   "read-handler",
   "$371"
  ]
 },
 {
  "lhs": "$366",
  "rhs": [
   "$367"
  ]
 },
 {
  "lhs": "$366",
  "rhs": [
   "$370"
  ]
 },
 {
  "lhs": "$365",
  "rhs": []
 },
 {
  "lhs": "$365",
  "rhs": [
   "$366"
  ]
 },
 {
  "lhs": "read-statement",
  "rhs": [
   "$353",
   "NAME",
   "qualified-name",
   "$354",
   "bindings",
   "NEWLINE",
   "$355"
  ]
 },
 {
  "lhs": "read-statement",
  "rhs": [
   "$363",
   "NAME",
   "$364",
   "invocation",
   "NEWLINE",
   "$365"
  ]
 },
 {
  "lhs": "$373",
  "rhs": [
   {
    "literal": "="
   }
  ]
 },
 {
  "lhs": "$376",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$377",
  "rhs": [
   {
    "literal": "="
   }
  ]
 },
 {
  "lhs": "$375",
  "rhs": [
   "$376",
   "NAME",
   "$377",
   "expression"
  ]
 },
 {
  "lhs": "$374",
  "rhs": []
 },
 {
  "lhs": "$374",
  "rhs": [
   "$375",
   "$374"
  ]
 },
 {
  "lhs": "bindings",
  "rhs": [
   "NAME",
   "$373",
   "expression",
   "$374"
  ]
 },
 {
  "lhs": "$379",
  "rhs": [
   {
    "literal": "on-missing"
   }
  ]
 },
 {
  "lhs": "$380",
  "rhs": [
   {
    "literal": "on-unavailable"
   }
  ]
 },
 {
  "lhs": "$381",
  "rhs": [
   {
    "literal": "on-malformed"
   }
  ]
 },
 {
  "lhs": "$378",
  "rhs": [
   "$379"
  ]
 },
 {
  "lhs": "$378",
  "rhs": [
   "$380"
  ]
 },
 {
  "lhs": "$378",
  "rhs": [
   "$381"
  ]
 },
 {
  "lhs": "$384",
  "rhs": [
   {
    "literal": ";"
   },
   {
    "literal": "do-not-ack"
   }
  ]
 },
 {
  "lhs": "$383",
  "rhs": [
   "$384"
  ]
 },
 {
  "lhs": "$382",
  "rhs": []
 },
 {
  "lhs": "$382",
  "rhs": [
   "$383"
  ]
 },
 {
  "lhs": "read-handler",
  "rhs": [
   "$378",
   "action",
   "$382",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$385",
  "rhs": [
   {
    "literal": "call"
   }
  ]
 },
 {
  "lhs": "$389",
  "rhs": [
   "call-handler"
  ]
 },
 {
  "lhs": "$388",
  "rhs": []
 },
 {
  "lhs": "$388",
  "rhs": [
   "$389",
   "$388"
  ]
 },
 {
  "lhs": "$387",
  "rhs": [
   "INDENT",
   "call-handler",
   "$388",
   "DEDENT"
  ]
 },
 {
  "lhs": "$386",
  "rhs": []
 },
 {
  "lhs": "$386",
  "rhs": [
   "$387"
  ]
 },
 {
  "lhs": "call-statement",
  "rhs": [
   "$385",
   "NAME",
   "invocation",
   "NEWLINE",
   "$386"
  ]
 },
 {
  "lhs": "$391",
  "rhs": [
   {
    "literal": "on-transport-error"
   }
  ]
 },
 {
  "lhs": "$392",
  "rhs": [
   {
    "literal": "on-invalid-response"
   }
  ]
 },
 {
  "lhs": "$393",
  "rhs": [
   {
    "literal": "on-error"
   }
  ]
 },
 {
  "lhs": "$390",
  "rhs": [
   "$391"
  ]
 },
 {
  "lhs": "$390",
  "rhs": [
   "$392"
  ]
 },
 {
  "lhs": "$390",
  "rhs": [
   "$393"
  ]
 },
 {
  "lhs": "call-handler",
  "rhs": [
   "$390",
   "action",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$394",
  "rhs": [
   {
    "literal": "on"
   }
  ]
 },
 {
  "lhs": "$395",
  "rhs": [
   "expression"
  ]
 },
 {
  "lhs": "$395",
  "rhs": [
   "pattern-list"
  ]
 },
 {
  "lhs": "$395",
  "rhs": [
   "postfix",
   "pattern-list"
  ]
 },
 {
  "lhs": "$398",
  "rhs": [
   {
    "literal": "when"
   }
  ]
 },
 {
  "lhs": "$397",
  "rhs": [
   "$398",
   "expression"
  ]
 },
 {
  "lhs": "$396",
  "rhs": []
 },
 {
  "lhs": "$396",
  "rhs": [
   "$397"
  ]
 },
 {
  "lhs": "$400",
  "rhs": [
   "before-order"
  ]
 },
 {
  "lhs": "$399",
  "rhs": []
 },
 {
  "lhs": "$399",
  "rhs": [
   "$400"
  ]
 },
 {
  "lhs": "condition-statement",
  "rhs": [
   "$394",
   "$395",
   "$396",
   "action",
   "$399",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$401",
  "rhs": [
   {
    "literal": "on-present"
   }
  ]
 },
 {
  "lhs": "$403",
  "rhs": [
   "postfix"
  ]
 },
 {
  "lhs": "$402",
  "rhs": []
 },
 {
  "lhs": "$402",
  "rhs": [
   "$403"
  ]
 },
 {
  "lhs": "$405",
  "rhs": [
   {
    "literal": "require"
   }
  ]
 },
 {
  "lhs": "$406",
  "rhs": [
   {
    "literal": "else"
   }
  ]
 },
 {
  "lhs": "$408",
  "rhs": [
   "before-order"
  ]
 },
 {
  "lhs": "$407",
  "rhs": []
 },
 {
  "lhs": "$407",
  "rhs": [
   "$408"
  ]
 },
 {
  "lhs": "$404",
  "rhs": [
   "$405",
   "expression",
   "$406",
   "action",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$404",
  "rhs": [
   "action",
   "$407",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$404",
  "rhs": [
   "transaction"
  ]
 },
 {
  "lhs": "present-statement",
  "rhs": [
   "$401",
   "$402",
   "$404"
  ]
 },
 {
  "lhs": "$409",
  "rhs": [
   {
    "literal": "when"
   }
  ]
 },
 {
  "lhs": "$410",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$413",
  "rhs": [
   {
    "literal": "otherwise"
   },
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$412",
  "rhs": [
   "$413",
   "NEWLINE",
   "INDENT",
   "operation-statements",
   "DEDENT"
  ]
 },
 {
  "lhs": "$411",
  "rhs": []
 },
 {
  "lhs": "$411",
  "rhs": [
   "$412"
  ]
 },
 {
  "lhs": "when-statement",
  "rhs": [
   "$409",
   "expression",
   "$410",
   "NEWLINE",
   "INDENT",
   "operation-statements",
   "DEDENT",
   "$411"
  ]
 },
 {
  "lhs": "$414",
  "rhs": [
   {
    "literal": "before"
   }
  ]
 },
 {
  "lhs": "$417",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$416",
  "rhs": [
   "$417",
   "step-name"
  ]
 },
 {
  "lhs": "$415",
  "rhs": []
 },
 {
  "lhs": "$415",
  "rhs": [
   "$416",
   "$415"
  ]
 },
 {
  "lhs": "before-order",
  "rhs": [
   "$414",
   "step-name",
   "$415"
  ]
 },
 {
  "lhs": "$419",
  "rhs": [
   {
    "literal": "return"
   }
  ]
 },
 {
  "lhs": "$420",
  "rhs": [
   {
    "literal": "returns"
   }
  ]
 },
 {
  "lhs": "$418",
  "rhs": [
   "$419"
  ]
 },
 {
  "lhs": "$418",
  "rhs": [
   "$420"
  ]
 },
 {
  "lhs": "return-statement",
  "rhs": [
   "$418",
   "expression",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$422",
  "rhs": [
   {
    "literal": "reject"
   }
  ]
 },
 {
  "lhs": "$423",
  "rhs": [
   {
    "literal": "fail"
   }
  ]
 },
 {
  "lhs": "$421",
  "rhs": [
   "$422"
  ]
 },
 {
  "lhs": "$421",
  "rhs": [
   "$423"
  ]
 },
 {
  "lhs": "failure-action",
  "rhs": [
   "$421",
   "step-name"
  ]
 },
 {
  "lhs": "$424",
  "rhs": [
   {
    "literal": "return"
   }
  ]
 },
 {
  "lhs": "action",
  "rhs": [
   "$424",
   "expression"
  ]
 },
 {
  "lhs": "action",
  "rhs": [
   "failure-action"
  ]
 },
 {
  "lhs": "$425",
  "rhs": [
   {
    "literal": "read-set"
   }
  ]
 },
 {
  "lhs": "$426",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$427",
  "rhs": [
   {
    "literal": "for"
   }
  ]
 },
 {
  "lhs": "$428",
  "rhs": [
   {
    "literal": "in"
   }
  ]
 },
 {
  "lhs": "$429",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$430",
  "rhs": [
   {
    "literal": "bind"
   }
  ]
 },
 {
  "lhs": "$431",
  "rhs": [
   {
    "literal": "validate-all-before-writes"
   }
  ]
 },
 {
  "lhs": "read-set",
  "rhs": [
   "$425",
   "NAME",
   "$426",
   "NEWLINE",
   "INDENT",
   "$427",
   "NAME",
   "$428",
   "expression",
   "$429",
   "NEWLINE",
   "INDENT",
   "operation-statements",
   "$430",
   "collected-bindings",
   "NEWLINE",
   "DEDENT",
   "$431",
   "NEWLINE",
   "DEDENT"
  ]
 },
 {
  "lhs": "$434",
  "rhs": [
   {
    "literal": ","
   }
  ]
 },
 {
  "lhs": "$433",
  "rhs": [
   "$434",
   "collected-binding"
  ]
 },
 {
  "lhs": "$432",
  "rhs": []
 },
 {
  "lhs": "$432",
  "rhs": [
   "$433",
   "$432"
  ]
 },
 {
  "lhs": "collected-bindings",
  "rhs": [
   "collected-binding",
   "$432"
  ]
 },
 {
  "lhs": "$437",
  "rhs": [
   {
    "literal": "="
   }
  ]
 },
 {
  "lhs": "$436",
  "rhs": [
   "$437",
   "expression"
  ]
 },
 {
  "lhs": "$435",
  "rhs": []
 },
 {
  "lhs": "$435",
  "rhs": [
   "$436"
  ]
 },
 {
  "lhs": "collected-binding",
  "rhs": [
   "NAME",
   "$435"
  ]
 },
 {
  "lhs": "$438",
  "rhs": [
   {
    "literal": "transaction"
   }
  ]
 },
 {
  "lhs": "$439",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$440",
  "rhs": [
   {
    "literal": "atomic-participants"
   }
  ]
 },
 {
  "lhs": "$442",
  "rhs": [
   "transaction-statement"
  ]
 },
 {
  "lhs": "$441",
  "rhs": []
 },
 {
  "lhs": "$441",
  "rhs": [
   "$442",
   "$441"
  ]
 },
 {
  "lhs": "transaction",
  "rhs": [
   "$438",
   "NAME",
   "$439",
   "NEWLINE",
   "INDENT",
   "$440",
   "name-list",
   "NEWLINE",
   "transaction-statement",
   "$441",
   "DEDENT"
  ]
 },
 {
  "lhs": "transaction-statement",
  "rhs": [
   "enforce-statement"
  ]
 },
 {
  "lhs": "transaction-statement",
  "rhs": [
   "mutation"
  ]
 },
 {
  "lhs": "transaction-statement",
  "rhs": [
   "emit-statement"
  ]
 },
 {
  "lhs": "transaction-statement",
  "rhs": [
   "transaction-loop"
  ]
 },
 {
  "lhs": "transaction-statement",
  "rhs": [
   "transaction-condition"
  ]
 },
 {
  "lhs": "transaction-statement",
  "rhs": [
   "let-statement"
  ]
 },
 {
  "lhs": "transaction-statement",
  "rhs": [
   "transaction-guard"
  ]
 },
 {
  "lhs": "transaction-statement",
  "rhs": [
   "transaction-handler"
  ]
 },
 {
  "lhs": "$443",
  "rhs": [
   {
    "literal": "require-absent"
   }
  ]
 },
 {
  "lhs": "$444",
  "rhs": [
   {
    "literal": "require-retained-record-capacity"
   }
  ]
 },
 {
  "lhs": "transaction-guard",
  "rhs": [
   "$443",
   "qualified-name",
   "bindings",
   "NEWLINE"
  ]
 },
 {
  "lhs": "transaction-guard",
  "rhs": [
   "$444",
   "natural",
   "NEWLINE"
  ]
 },
 {
  "lhs": "transaction-guard",
  "rhs": [
   "guard"
  ]
 },
 {
  "lhs": "$445",
  "rhs": [
   {
    "literal": "create"
   }
  ]
 },
 {
  "lhs": "$446",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$447",
  "rhs": [
   {
    "literal": "create"
   }
  ]
 },
 {
  "lhs": "$448",
  "rhs": [
   {
    "literal": "from"
   }
  ]
 },
 {
  "lhs": "$449",
  "rhs": [
   {
    "literal": "update"
   }
  ]
 },
 {
  "lhs": "$450",
  "rhs": [
   {
    "literal": "by"
   }
  ]
 },
 {
  "lhs": "$451",
  "rhs": [
   {
    "literal": "expected-version"
   }
  ]
 },
 {
  "lhs": "$452",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$453",
  "rhs": [
   {
    "literal": "update"
   }
  ]
 },
 {
  "lhs": "$454",
  "rhs": [
   {
    "literal": "from"
   }
  ]
 },
 {
  "lhs": "$455",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$456",
  "rhs": [
   {
    "literal": "record-event"
   }
  ]
 },
 {
  "lhs": "$457",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "mutation",
  "rhs": [
   "$445",
   "NAME",
   "qualified-name",
   "$446",
   "NEWLINE",
   "INDENT",
   "assignments",
   "DEDENT"
  ]
 },
 {
  "lhs": "mutation",
  "rhs": [
   "$447",
   "NAME",
   "qualified-name",
   "$448",
   "expression",
   "NEWLINE"
  ]
 },
 {
  "lhs": "mutation",
  "rhs": [
   "$449",
   "NAME",
   "qualified-name",
   "$450",
   "bindings",
   "$451",
   "expression",
   "$452",
   "NEWLINE",
   "INDENT",
   "assignments",
   "DEDENT"
  ]
 },
 {
  "lhs": "mutation",
  "rhs": [
   "$453",
   "NAME",
   "qualified-name",
   "$454",
   "NAME",
   "$455",
   "NEWLINE",
   "INDENT",
   "assignments",
   "DEDENT"
  ]
 },
 {
  "lhs": "mutation",
  "rhs": [
   "$456",
   "NAME",
   "qualified-name",
   "$457",
   "NEWLINE",
   "INDENT",
   "assignments",
   "DEDENT"
  ]
 },
 {
  "lhs": "$458",
  "rhs": [
   {
    "literal": "emit"
   }
  ]
 },
 {
  "lhs": "$459",
  "rhs": [
   {
    "literal": "payload"
   }
  ]
 },
 {
  "lhs": "emit-statement",
  "rhs": [
   "$458",
   "qualified-name",
   "$459",
   "expression",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$460",
  "rhs": [
   {
    "literal": "<-"
   }
  ]
 },
 {
  "lhs": "$463",
  "rhs": [
   {
    "literal": "<-"
   }
  ]
 },
 {
  "lhs": "$462",
  "rhs": [
   "NAME",
   "$463",
   "expression",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$461",
  "rhs": []
 },
 {
  "lhs": "$461",
  "rhs": [
   "$462",
   "$461"
  ]
 },
 {
  "lhs": "assignments",
  "rhs": [
   "NAME",
   "$460",
   "expression",
   "NEWLINE",
   "$461"
  ]
 },
 {
  "lhs": "$464",
  "rhs": [
   {
    "literal": "for"
   }
  ]
 },
 {
  "lhs": "$465",
  "rhs": [
   {
    "literal": "in"
   }
  ]
 },
 {
  "lhs": "$466",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$468",
  "rhs": [
   "transaction-statement"
  ]
 },
 {
  "lhs": "$467",
  "rhs": []
 },
 {
  "lhs": "$467",
  "rhs": [
   "$468",
   "$467"
  ]
 },
 {
  "lhs": "transaction-loop",
  "rhs": [
   "$464",
   "NAME",
   "$465",
   "expression",
   "$466",
   "NEWLINE",
   "INDENT",
   "transaction-statement",
   "$467",
   "DEDENT"
  ]
 },
 {
  "lhs": "$469",
  "rhs": [
   {
    "literal": "when"
   }
  ]
 },
 {
  "lhs": "$470",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$472",
  "rhs": [
   "transaction-statement"
  ]
 },
 {
  "lhs": "$471",
  "rhs": []
 },
 {
  "lhs": "$471",
  "rhs": [
   "$472",
   "$471"
  ]
 },
 {
  "lhs": "$475",
  "rhs": [
   {
    "literal": "otherwise"
   },
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$477",
  "rhs": [
   "transaction-statement"
  ]
 },
 {
  "lhs": "$476",
  "rhs": []
 },
 {
  "lhs": "$476",
  "rhs": [
   "$477",
   "$476"
  ]
 },
 {
  "lhs": "$474",
  "rhs": [
   "$475",
   "NEWLINE",
   "INDENT",
   "transaction-statement",
   "$476",
   "DEDENT"
  ]
 },
 {
  "lhs": "$473",
  "rhs": []
 },
 {
  "lhs": "$473",
  "rhs": [
   "$474"
  ]
 },
 {
  "lhs": "transaction-condition",
  "rhs": [
   "$469",
   "expression",
   "$470",
   "NEWLINE",
   "INDENT",
   "transaction-statement",
   "$471",
   "DEDENT",
   "$473"
  ]
 },
 {
  "lhs": "$479",
  "rhs": [
   {
    "literal": "on-version-conflict"
   }
  ]
 },
 {
  "lhs": "$480",
  "rhs": [
   {
    "literal": "on-unique-conflict"
   }
  ]
 },
 {
  "lhs": "$481",
  "rhs": [
   {
    "literal": "on-proven-rollback"
   }
  ]
 },
 {
  "lhs": "$482",
  "rhs": [
   {
    "literal": "on-unknown-commit"
   }
  ]
 },
 {
  "lhs": "$483",
  "rhs": [
   {
    "literal": "on-arithmetic-error"
   }
  ]
 },
 {
  "lhs": "$484",
  "rhs": [
   {
    "literal": "on-invariant-error"
   }
  ]
 },
 {
  "lhs": "$478",
  "rhs": [
   "$479"
  ]
 },
 {
  "lhs": "$478",
  "rhs": [
   "$480"
  ]
 },
 {
  "lhs": "$478",
  "rhs": [
   "$481"
  ]
 },
 {
  "lhs": "$478",
  "rhs": [
   "$482"
  ]
 },
 {
  "lhs": "$478",
  "rhs": [
   "$483"
  ]
 },
 {
  "lhs": "$478",
  "rhs": [
   "$484"
  ]
 },
 {
  "lhs": "$487",
  "rhs": [
   {
    "literal": "retaining"
   },
   {
    "literal": "original"
   },
   {
    "literal": "scope"
   },
   {
    "literal": ","
   },
   {
    "literal": "fingerprint"
   }
  ]
 },
 {
  "lhs": "$486",
  "rhs": [
   "$487"
  ]
 },
 {
  "lhs": "$485",
  "rhs": []
 },
 {
  "lhs": "$485",
  "rhs": [
   "$486"
  ]
 },
 {
  "lhs": "$490",
  "rhs": [
   {
    "literal": ";"
   },
   {
    "literal": "do-not-ack"
   }
  ]
 },
 {
  "lhs": "$489",
  "rhs": [
   "$490"
  ]
 },
 {
  "lhs": "$488",
  "rhs": []
 },
 {
  "lhs": "$488",
  "rhs": [
   "$489"
  ]
 },
 {
  "lhs": "transaction-handler",
  "rhs": [
   "$478",
   "transaction-recovery",
   "$485",
   "$488",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$491",
  "rhs": [
   {
    "literal": "rollback-all"
   },
   {
    "literal": "then"
   }
  ]
 },
 {
  "lhs": "$492",
  "rhs": [
   {
    "literal": "resolve"
   },
   {
    "literal": "original"
   },
   {
    "literal": "replay-record"
   },
   {
    "literal": ";"
   },
   {
    "literal": "never"
   },
   {
    "literal": "create"
   },
   {
    "literal": "second"
   },
   {
    "literal": "order"
   }
  ]
 },
 {
  "lhs": "$493",
  "rhs": [
   {
    "literal": "reread"
   },
   {
    "literal": "original"
   },
   {
    "literal": "inbox"
   }
  ]
 },
 {
  "lhs": "$494",
  "rhs": [
   {
    "literal": "rollback-all"
   },
   {
    "literal": "then"
   },
   {
    "literal": "reread"
   },
   {
    "literal": "original"
   },
   {
    "literal": "inbox-or-shipment"
   }
  ]
 },
 {
  "lhs": "transaction-recovery",
  "rhs": [
   "action"
  ]
 },
 {
  "lhs": "transaction-recovery",
  "rhs": [
   "$491",
   "action"
  ]
 },
 {
  "lhs": "transaction-recovery",
  "rhs": [
   "$492"
  ]
 },
 {
  "lhs": "transaction-recovery",
  "rhs": [
   "$493"
  ]
 },
 {
  "lhs": "transaction-recovery",
  "rhs": [
   "$494"
  ]
 },
 {
  "lhs": "$495",
  "rhs": [
   {
    "literal": "acknowledge"
   },
   {
    "literal": "after"
   },
   {
    "literal": "committed"
   }
  ]
 },
 {
  "lhs": "$496",
  "rhs": [
   {
    "literal": "receipt"
   }
  ]
 },
 {
  "lhs": "acknowledgement",
  "rhs": [
   "$495",
   "qualified-name",
   "$496",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$497",
  "rhs": [
   {
    "literal": "query"
   }
  ]
 },
 {
  "lhs": "$498",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$500",
  "rhs": [
   "parameter"
  ]
 },
 {
  "lhs": "$500",
  "rhs": [
   "context"
  ]
 },
 {
  "lhs": "$499",
  "rhs": []
 },
 {
  "lhs": "$499",
  "rhs": [
   "$500",
   "$499"
  ]
 },
 {
  "lhs": "$501",
  "rhs": [
   "local-query"
  ]
 },
 {
  "lhs": "$501",
  "rhs": [
   "delegated-query"
  ]
 },
 {
  "lhs": "$501",
  "rhs": [
   "native-inspect-body"
  ]
 },
 {
  "lhs": "query-declaration",
  "rhs": [
   "$497",
   "NAME",
   "$498",
   "NEWLINE",
   "INDENT",
   "$499",
   "$501",
   "DEDENT"
  ]
 },
 {
  "lhs": "$502",
  "rhs": [
   {
    "literal": "source"
   }
  ]
 },
 {
  "lhs": "$505",
  "rhs": [
   {
    "literal": "join"
   }
  ]
 },
 {
  "lhs": "$506",
  "rhs": [
   {
    "literal": "on"
   }
  ]
 },
 {
  "lhs": "$504",
  "rhs": [
   "$505",
   "NAME",
   "qualified-name",
   "$506",
   "expression"
  ]
 },
 {
  "lhs": "$503",
  "rhs": []
 },
 {
  "lhs": "$503",
  "rhs": [
   "$504",
   "$503"
  ]
 },
 {
  "lhs": "$507",
  "rhs": [
   {
    "literal": "output"
   }
  ]
 },
 {
  "lhs": "$508",
  "rhs": [
   {
    "literal": "where"
   }
  ]
 },
 {
  "lhs": "$510",
  "rhs": [
   "query-clause"
  ]
 },
 {
  "lhs": "$509",
  "rhs": []
 },
 {
  "lhs": "$509",
  "rhs": [
   "$510",
   "$509"
  ]
 },
 {
  "lhs": "local-query",
  "rhs": [
   "$502",
   "NAME",
   "qualified-name",
   "$503",
   "NEWLINE",
   "$507",
   "type",
   "NEWLINE",
   "$508",
   "expression",
   "NEWLINE",
   "query-clause",
   "$509"
  ]
 },
 {
  "lhs": "$511",
  "rhs": [
   {
    "literal": "project"
   }
  ]
 },
 {
  "lhs": "$512",
  "rhs": [
   {
    "literal": "require"
   }
  ]
 },
 {
  "lhs": "$513",
  "rhs": [
   {
    "literal": "else"
   }
  ]
 },
 {
  "lhs": "$514",
  "rhs": [
   {
    "literal": "effects"
   },
   {
    "literal": "none"
   }
  ]
 },
 {
  "lhs": "query-clause",
  "rhs": [
   "$511",
   "expression",
   "NEWLINE"
  ]
 },
 {
  "lhs": "query-clause",
  "rhs": [
   "$512",
   "expression",
   "$513",
   "action",
   "NEWLINE"
  ]
 },
 {
  "lhs": "query-clause",
  "rhs": [
   "read-handler"
  ]
 },
 {
  "lhs": "query-clause",
  "rhs": [
   "$514",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$516",
  "rhs": [
   {
    "literal": "output"
   }
  ]
 },
 {
  "lhs": "$517",
  "rhs": [
   {
    "literal": "delegates"
   }
  ]
 },
 {
  "lhs": "$518",
  "rhs": [
   {
    "literal": "delegates"
   }
  ]
 },
 {
  "lhs": "$519",
  "rhs": [
   {
    "literal": "output"
   }
  ]
 },
 {
  "lhs": "$515",
  "rhs": [
   "$516",
   "type",
   "NEWLINE",
   "$517",
   "invocation",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$515",
  "rhs": [
   "$518",
   "invocation",
   "NEWLINE",
   "$519",
   "type",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$522",
  "rhs": [
   {
    "literal": "effects"
   },
   {
    "literal": "none"
   }
  ]
 },
 {
  "lhs": "$521",
  "rhs": [
   "$522",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$520",
  "rhs": []
 },
 {
  "lhs": "$520",
  "rhs": [
   "$521"
  ]
 },
 {
  "lhs": "delegated-query",
  "rhs": [
   "$515",
   "$520"
  ]
 },
 {
  "lhs": "$523",
  "rhs": [
   {
    "literal": "entry"
   }
  ]
 },
 {
  "lhs": "$524",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$525",
  "rhs": [
   {
    "literal": "invokes"
   }
  ]
 },
 {
  "lhs": "$526",
  "rhs": [
   {
    "literal": "interaction"
   }
  ]
 },
 {
  "lhs": "$528",
  "rhs": [
   {
    "literal": "request-response"
   }
  ]
 },
 {
  "lhs": "$529",
  "rhs": [
   {
    "literal": "event"
   }
  ]
 },
 {
  "lhs": "$531",
  "rhs": [
   "qualified-name"
  ]
 },
 {
  "lhs": "$530",
  "rhs": []
 },
 {
  "lhs": "$530",
  "rhs": [
   "$531"
  ]
 },
 {
  "lhs": "$527",
  "rhs": [
   "$528"
  ]
 },
 {
  "lhs": "$527",
  "rhs": [
   "$529",
   "$530"
  ]
 },
 {
  "lhs": "$534",
  "rhs": [
   {
    "literal": "bind"
   }
  ]
 },
 {
  "lhs": "$535",
  "rhs": [
   {
    "literal": "<-"
   }
  ]
 },
 {
  "lhs": "$533",
  "rhs": [
   "$534",
   "NAME",
   "$535",
   "expression",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$532",
  "rhs": []
 },
 {
  "lhs": "$532",
  "rhs": [
   "$533"
  ]
 },
 {
  "lhs": "$536",
  "rhs": [
   {
    "literal": "access"
   },
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$538",
  "rhs": [
   "access-clause"
  ]
 },
 {
  "lhs": "$537",
  "rhs": []
 },
 {
  "lhs": "$537",
  "rhs": [
   "$538",
   "$537"
  ]
 },
 {
  "lhs": "entry-declaration",
  "rhs": [
   "$523",
   "qualified-name",
   "$524",
   "NEWLINE",
   "INDENT",
   "$525",
   "qualified-name",
   "NEWLINE",
   "$526",
   "$527",
   "NEWLINE",
   "$532",
   "$536",
   "NEWLINE",
   "INDENT",
   "access-clause",
   "$537",
   "DEDENT",
   "DEDENT"
  ]
 },
 {
  "lhs": "$539",
  "rhs": [
   {
    "literal": "authenticated"
   }
  ]
 },
 {
  "lhs": "$541",
  "rhs": [
   {
    "literal": "customer"
   }
  ]
 },
 {
  "lhs": "$542",
  "rhs": [
   {
    "literal": "service"
   }
  ]
 },
 {
  "lhs": "$543",
  "rhs": [
   {
    "literal": "operator"
   }
  ]
 },
 {
  "lhs": "$544",
  "rhs": [
   {
    "literal": "relay"
   }
  ]
 },
 {
  "lhs": "$540",
  "rhs": [
   "$541"
  ]
 },
 {
  "lhs": "$540",
  "rhs": [
   "$542"
  ]
 },
 {
  "lhs": "$540",
  "rhs": [
   "$543"
  ]
 },
 {
  "lhs": "$540",
  "rhs": [
   "$544"
  ]
 },
 {
  "lhs": "$545",
  "rhs": [
   {
    "literal": "permission"
   }
  ]
 },
 {
  "lhs": "$547",
  "rhs": [
   {
    "literal": "auth-resource"
   }
  ]
 },
 {
  "lhs": "$548",
  "rhs": [
   {
    "literal": "auth-scope"
   }
  ]
 },
 {
  "lhs": "$549",
  "rhs": [
   {
    "literal": "caller"
   }
  ]
 },
 {
  "lhs": "$550",
  "rhs": [
   {
    "literal": "producer"
   }
  ]
 },
 {
  "lhs": "$546",
  "rhs": [
   "$547"
  ]
 },
 {
  "lhs": "$546",
  "rhs": [
   "$548"
  ]
 },
 {
  "lhs": "$546",
  "rhs": [
   "$549"
  ]
 },
 {
  "lhs": "$546",
  "rhs": [
   "$550"
  ]
 },
 {
  "lhs": "$551",
  "rhs": [
   {
    "literal": "auth-action"
   }
  ]
 },
 {
  "lhs": "$552",
  "rhs": [
   {
    "literal": "auth-route"
   }
  ]
 },
 {
  "lhs": "$553",
  "rhs": [
   {
    "literal": "context"
   }
  ]
 },
 {
  "lhs": "$554",
  "rhs": [
   {
    "literal": "native-requires"
   }
  ]
 },
 {
  "lhs": "$555",
  "rhs": [
   {
    "literal": "current-action"
   },
   {
    "literal": "before"
   },
   {
    "literal": "replay-and-effects"
   }
  ]
 },
 {
  "lhs": "$556",
  "rhs": [
   {
    "literal": "resource-binding"
   }
  ]
 },
 {
  "lhs": "$557",
  "rhs": [
   {
    "literal": "from"
   }
  ]
 },
 {
  "lhs": "$558",
  "rhs": [
   {
    "literal": "resource-condition"
   }
  ]
 },
 {
  "lhs": "$559",
  "rhs": [
   {
    "literal": "on-resource-false"
   },
   {
    "literal": "reject"
   },
   {
    "literal": "forbidden"
   },
   {
    "literal": "before"
   },
   {
    "literal": "effects"
   }
  ]
 },
 {
  "lhs": "$560",
  "rhs": [
   {
    "literal": "on-resource-missing-or-false"
   },
   {
    "literal": "missing"
   },
   {
    "literal": "resource-not-found"
   },
   {
    "literal": "before"
   },
   {
    "literal": "projection"
   }
  ]
 },
 {
  "lhs": "$561",
  "rhs": [
   {
    "literal": "principal-from"
   },
   {
    "literal": "registered"
   },
   {
    "literal": "authenticated"
   },
   {
    "literal": "subject"
   },
   {
    "literal": ","
   },
   {
    "literal": "never"
   },
   {
    "literal": "request"
   },
   {
    "literal": "fields"
   }
  ]
 },
 {
  "lhs": "$562",
  "rhs": [
   {
    "literal": "worker-from"
   },
   {
    "literal": "original"
   },
   {
    "literal": "registered"
   },
   {
    "literal": "local"
   },
   {
    "literal": "lifecycle"
   },
   {
    "literal": "owner"
   }
  ]
 },
 {
  "lhs": "$563",
  "rhs": [
   {
    "literal": "invocation-decision"
   },
   {
    "literal": "fresh"
   },
   {
    "literal": "and"
   },
   {
    "literal": "separate"
   },
   {
    "literal": "from"
   },
   {
    "literal": "worker"
   },
   {
    "literal": "lifetime"
   },
   {
    "literal": "capability"
   }
  ]
 },
 {
  "lhs": "$564",
  "rhs": [
   {
    "literal": "occurrence-from"
   },
   {
    "literal": "original"
   },
   {
    "literal": "registered"
   },
   {
    "literal": "event"
   },
   {
    "literal": "ingress"
   }
  ]
 },
 {
  "lhs": "$565",
  "rhs": [
   {
    "literal": "acknowledge"
   },
   {
    "literal": "after"
   },
   {
    "literal": "committed"
   },
   {
    "literal": "inbox-and-result"
   }
  ]
 },
 {
  "lhs": "access-clause",
  "rhs": [
   "$539",
   "$540",
   "NEWLINE"
  ]
 },
 {
  "lhs": "access-clause",
  "rhs": [
   "$545",
   "permission-name",
   "NEWLINE"
  ]
 },
 {
  "lhs": "access-clause",
  "rhs": [
   "$546",
   "step-name",
   "NEWLINE"
  ]
 },
 {
  "lhs": "access-clause",
  "rhs": [
   "$551",
   "permission-name",
   "NEWLINE"
  ]
 },
 {
  "lhs": "access-clause",
  "rhs": [
   "$552",
   "reference",
   "NEWLINE"
  ]
 },
 {
  "lhs": "access-clause",
  "rhs": [
   "$553",
   "qualified-name",
   "NEWLINE"
  ]
 },
 {
  "lhs": "access-clause",
  "rhs": [
   "$554",
   "reference",
   "NEWLINE"
  ]
 },
 {
  "lhs": "access-clause",
  "rhs": [
   "$555",
   "NEWLINE"
  ]
 },
 {
  "lhs": "access-clause",
  "rhs": [
   "$556",
   "NAME",
   "qualified-name",
   "$557",
   "reference",
   "NEWLINE"
  ]
 },
 {
  "lhs": "access-clause",
  "rhs": [
   "$558",
   "expression",
   "NEWLINE"
  ]
 },
 {
  "lhs": "access-clause",
  "rhs": [
   "$559",
   "NEWLINE"
  ]
 },
 {
  "lhs": "access-clause",
  "rhs": [
   "$560",
   "NEWLINE"
  ]
 },
 {
  "lhs": "access-clause",
  "rhs": [
   "$561",
   "NEWLINE"
  ]
 },
 {
  "lhs": "access-clause",
  "rhs": [
   "$562",
   "NEWLINE"
  ]
 },
 {
  "lhs": "access-clause",
  "rhs": [
   "$563",
   "NEWLINE"
  ]
 },
 {
  "lhs": "access-clause",
  "rhs": [
   "$564",
   "NEWLINE"
  ]
 },
 {
  "lhs": "access-clause",
  "rhs": [
   "$565",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$566",
  "rhs": [
   {
    "literal": "workflow"
   }
  ]
 },
 {
  "lhs": "$567",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$568",
  "rhs": [
   {
    "literal": "owner"
   }
  ]
 },
 {
  "lhs": "$569",
  "rhs": [
   {
    "literal": "scope"
   },
   {
    "literal": "cross-service"
   }
  ]
 },
 {
  "lhs": "$571",
  "rhs": [
   "parameter"
  ]
 },
 {
  "lhs": "$571",
  "rhs": [
   "context"
  ]
 },
 {
  "lhs": "$570",
  "rhs": []
 },
 {
  "lhs": "$570",
  "rhs": [
   "$571",
   "$570"
  ]
 },
 {
  "lhs": "$572",
  "rhs": [
   {
    "literal": "correlation"
   }
  ]
 },
 {
  "lhs": "$573",
  "rhs": [
   {
    "literal": "input-entry"
   }
  ]
 },
 {
  "lhs": "$574",
  "rhs": [
   {
    "literal": "input-producer"
   }
  ]
 },
 {
  "lhs": "$575",
  "rhs": [
   {
    "literal": "input-inbox"
   },
   {
    "literal": "identity"
   }
  ]
 },
 {
  "lhs": "$576",
  "rhs": [
   {
    "literal": "compare"
   }
  ]
 },
 {
  "lhs": "$577",
  "rhs": [
   {
    "literal": "durable-state"
   }
  ]
 },
 {
  "lhs": "$578",
  "rhs": [
   {
    "literal": "ownership"
   },
   {
    "literal": "compare-and-set"
   }
  ]
 },
 {
  "lhs": "$579",
  "rhs": [
   {
    "literal": "recovery"
   },
   {
    "literal": "no-lease-steal"
   },
   {
    "literal": ";"
   },
   {
    "literal": "native"
   },
   {
    "literal": "quiescent-predecessor"
   },
   {
    "literal": "evidence"
   },
   {
    "literal": "required"
   }
  ]
 },
 {
  "lhs": "$580",
  "rhs": [
   {
    "literal": "input-ack"
   },
   {
    "literal": "after"
   },
   {
    "literal": "inbox-and-work-schedule"
   },
   {
    "literal": "commit"
   }
  ]
 },
 {
  "lhs": "$582",
  "rhs": [
   "workflow-step"
  ]
 },
 {
  "lhs": "$581",
  "rhs": []
 },
 {
  "lhs": "$581",
  "rhs": [
   "$582",
   "$581"
  ]
 },
 {
  "lhs": "$584",
  "rhs": [
   "workflow-terminal"
  ]
 },
 {
  "lhs": "$583",
  "rhs": []
 },
 {
  "lhs": "$583",
  "rhs": [
   "$584",
   "$583"
  ]
 },
 {
  "lhs": "workflow-declaration",
  "rhs": [
   "$566",
   "NAME",
   "$567",
   "NEWLINE",
   "INDENT",
   "$568",
   "step-name",
   "NEWLINE",
   "$569",
   "NEWLINE",
   "$570",
   "$572",
   "expression",
   "NEWLINE",
   "$573",
   "qualified-name",
   "NEWLINE",
   "$574",
   "step-name",
   "NEWLINE",
   "$575",
   "name-list",
   "$576",
   "expression",
   "NEWLINE",
   "$577",
   "qualified-name",
   "NEWLINE",
   "$578",
   "name-list",
   "NEWLINE",
   "$579",
   "NEWLINE",
   "$580",
   "NEWLINE",
   "snapshot-driver",
   "claim-driver",
   "observation-driver",
   "resume-block",
   "workflow-step",
   "$581",
   "workflow-terminal",
   "$583",
   "DEDENT"
  ]
 },
 {
  "lhs": "$585",
  "rhs": [
   {
    "literal": "input"
   }
  ]
 },
 {
  "lhs": "$586",
  "rhs": [
   {
    "literal": "<-"
   }
  ]
 },
 {
  "lhs": "driver-input",
  "rhs": [
   "$585",
   "NAME",
   "$586",
   "expression",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$587",
  "rhs": [
   {
    "literal": "result"
   }
  ]
 },
 {
  "lhs": "driver-result",
  "rhs": [
   "$587",
   "NAME",
   "type",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$588",
  "rhs": [
   {
    "literal": "snapshot-operation"
   }
  ]
 },
 {
  "lhs": "$590",
  "rhs": [
   "driver-input"
  ]
 },
 {
  "lhs": "$589",
  "rhs": []
 },
 {
  "lhs": "$589",
  "rhs": [
   "$590",
   "$589"
  ]
 },
 {
  "lhs": "$591",
  "rhs": [
   {
    "literal": "require"
   }
  ]
 },
 {
  "lhs": "$592",
  "rhs": [
   {
    "literal": "immutable-inputs"
   }
  ]
 },
 {
  "lhs": "$593",
  "rhs": [
   {
    "literal": "before-each-step"
   },
   {
    "literal": "reread"
   },
   {
    "literal": "current"
   },
   {
    "literal": "order/progress"
   },
   {
    "literal": "versions"
   },
   {
    "literal": "and"
   },
   {
    "literal": "ownership"
   }
  ]
 },
 {
  "lhs": "$594",
  "rhs": [
   {
    "literal": "on-missing"
   }
  ]
 },
 {
  "lhs": "$595",
  "rhs": [
   {
    "literal": "on-unavailable"
   },
   {
    "literal": "suspend"
   },
   {
    "literal": "same-state"
   }
  ]
 },
 {
  "lhs": "snapshot-driver",
  "rhs": [
   "$588",
   "qualified-name",
   "NEWLINE",
   "INDENT",
   "$589",
   "driver-result",
   "$591",
   "expression",
   "NEWLINE",
   "$592",
   "name-list",
   "NEWLINE",
   "$593",
   "NEWLINE",
   "$594",
   "failure-action",
   "NEWLINE",
   "$595",
   "NEWLINE",
   "DEDENT"
  ]
 },
 {
  "lhs": "$596",
  "rhs": [
   {
    "literal": "claim-operation"
   }
  ]
 },
 {
  "lhs": "$598",
  "rhs": [
   "driver-input"
  ]
 },
 {
  "lhs": "$597",
  "rhs": []
 },
 {
  "lhs": "$597",
  "rhs": [
   "$598",
   "$597"
  ]
 },
 {
  "lhs": "$599",
  "rhs": [
   {
    "literal": "bind-native-claim"
   },
   {
    "literal": "worker"
   },
   {
    "literal": "to"
   },
   {
    "literal": "committed"
   },
   {
    "literal": "claim"
   },
   {
    "literal": "before"
   },
   {
    "literal": "dispatch"
   }
  ]
 },
 {
  "lhs": "$600",
  "rhs": [
   {
    "literal": "on-contention"
   },
   {
    "literal": "stop-this-worker"
   }
  ]
 },
 {
  "lhs": "$601",
  "rhs": [
   {
    "literal": "on-unknown"
   },
   {
    "literal": "suspend"
   },
   {
    "literal": "ownership-unresolved"
   }
  ]
 },
 {
  "lhs": "claim-driver",
  "rhs": [
   "$596",
   "qualified-name",
   "NEWLINE",
   "INDENT",
   "$597",
   "driver-result",
   "$599",
   "NEWLINE",
   "$600",
   "NEWLINE",
   "$601",
   "NEWLINE",
   "DEDENT"
  ]
 },
 {
  "lhs": "$602",
  "rhs": [
   {
    "literal": "observation-operation"
   }
  ]
 },
 {
  "lhs": "$604",
  "rhs": [
   "driver-input"
  ]
 },
 {
  "lhs": "$603",
  "rhs": []
 },
 {
  "lhs": "$603",
  "rhs": [
   "$604",
   "$603"
  ]
 },
 {
  "lhs": "$605",
  "rhs": [
   {
    "literal": "after-observation"
   },
   {
    "literal": "reread"
   },
   {
    "literal": "snapshot"
   },
   {
    "literal": ";"
   },
   {
    "literal": "then-target"
   },
   {
    "literal": "requires"
   },
   {
    "literal": "observed"
   },
   {
    "literal": "."
   },
   {
    "literal": "fresh"
   },
   {
    "literal": "and"
   },
   {
    "literal": "matching"
   },
   {
    "literal": "current"
   },
   {
    "literal": "state"
   },
   {
    "literal": ","
   },
   {
    "literal": "otherwise"
   },
   {
    "literal": "resume"
   }
  ]
 },
 {
  "lhs": "$606",
  "rhs": [
   {
    "literal": "on-contention"
   },
   {
    "literal": "reread"
   },
   {
    "literal": "snapshot"
   },
   {
    "literal": "then"
   },
   {
    "literal": "reapply"
   },
   {
    "literal": "original"
   },
   {
    "literal": "observation"
   },
   {
    "literal": ";"
   },
   {
    "literal": "never"
   },
   {
    "literal": "repeat"
   },
   {
    "literal": "remote"
   },
   {
    "literal": "call"
   }
  ]
 },
 {
  "lhs": "$607",
  "rhs": [
   {
    "literal": "on-unknown"
   },
   {
    "literal": "invokes"
   }
  ]
 },
 {
  "lhs": "$608",
  "rhs": [
   {
    "literal": ";"
   },
   {
    "literal": "no"
   },
   {
    "literal": "fresh"
   },
   {
    "literal": "continuation"
   },
   {
    "literal": "ticket"
   },
   {
    "literal": "or"
   },
   {
    "literal": "rollback"
   },
   {
    "literal": "inference"
   }
  ]
 },
 {
  "lhs": "$609",
  "rhs": [
   {
    "literal": "on-evidence-conflict"
   },
   {
    "literal": "persist"
   },
   {
    "literal": "EvidenceConflict"
   },
   {
    "literal": "using"
   },
   {
    "literal": "original"
   },
   {
    "literal": "step"
   },
   {
    "literal": "command"
   }
  ]
 },
 {
  "lhs": "observation-driver",
  "rhs": [
   "$602",
   "qualified-name",
   "NEWLINE",
   "INDENT",
   "$603",
   "driver-result",
   "$605",
   "NEWLINE",
   "$606",
   "NEWLINE",
   "$607",
   "invocation",
   "$608",
   "NEWLINE",
   "$609",
   "NEWLINE",
   "DEDENT"
  ]
 },
 {
  "lhs": "$610",
  "rhs": [
   {
    "literal": "resume"
   },
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$612",
  "rhs": [
   "resume-case"
  ]
 },
 {
  "lhs": "$611",
  "rhs": []
 },
 {
  "lhs": "$611",
  "rhs": [
   "$612",
   "$611"
  ]
 },
 {
  "lhs": "resume-block",
  "rhs": [
   "$610",
   "NEWLINE",
   "INDENT",
   "resume-case",
   "$611",
   "DEDENT"
  ]
 },
 {
  "lhs": "$615",
  "rhs": [
   {
    "literal": "when"
   }
  ]
 },
 {
  "lhs": "$614",
  "rhs": [
   "$615",
   "expression"
  ]
 },
 {
  "lhs": "$613",
  "rhs": []
 },
 {
  "lhs": "$613",
  "rhs": [
   "$614"
  ]
 },
 {
  "lhs": "$616",
  "rhs": [
   {
    "literal": "->"
   }
  ]
 },
 {
  "lhs": "resume-case",
  "rhs": [
   "qualified-name",
   "$613",
   "$616",
   "workflow-action",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$617",
  "rhs": [
   {
    "literal": "finish"
   }
  ]
 },
 {
  "lhs": "$618",
  "rhs": [
   {
    "literal": "suspend"
   }
  ]
 },
 {
  "lhs": "$619",
  "rhs": [
   {
    "literal": "suspend"
   }
  ]
 },
 {
  "lhs": "$620",
  "rhs": [
   {
    "literal": "resume"
   }
  ]
 },
 {
  "lhs": "$621",
  "rhs": [
   {
    "literal": "stop-this-worker"
   }
  ]
 },
 {
  "lhs": "workflow-action",
  "rhs": [
   "step-name"
  ]
 },
 {
  "lhs": "workflow-action",
  "rhs": [
   "$617",
   "step-name"
  ]
 },
 {
  "lhs": "workflow-action",
  "rhs": [
   "$618",
   "qualified-name"
  ]
 },
 {
  "lhs": "workflow-action",
  "rhs": [
   "$619",
   "step-name"
  ]
 },
 {
  "lhs": "workflow-action",
  "rhs": [
   "$620"
  ]
 },
 {
  "lhs": "workflow-action",
  "rhs": [
   "$621"
  ]
 },
 {
  "lhs": "$622",
  "rhs": [
   {
    "literal": "step"
   }
  ]
 },
 {
  "lhs": "$623",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$624",
  "rhs": [
   "remote-step"
  ]
 },
 {
  "lhs": "$624",
  "rhs": [
   "local-step"
  ]
 },
 {
  "lhs": "$624",
  "rhs": [
   "review-step"
  ]
 },
 {
  "lhs": "workflow-step",
  "rhs": [
   "$622",
   "step-name",
   "$623",
   "NEWLINE",
   "INDENT",
   "$624",
   "DEDENT"
  ]
 },
 {
  "lhs": "$625",
  "rhs": [
   {
    "literal": "invokes"
   }
  ]
 },
 {
  "lhs": "$627",
  "rhs": [
   "driver-input"
  ]
 },
 {
  "lhs": "$626",
  "rhs": []
 },
 {
  "lhs": "$626",
  "rhs": [
   "$627",
   "$626"
  ]
 },
 {
  "lhs": "$629",
  "rhs": [
   "step-branch"
  ]
 },
 {
  "lhs": "$628",
  "rhs": []
 },
 {
  "lhs": "$628",
  "rhs": [
   "$629",
   "$628"
  ]
 },
 {
  "lhs": "remote-step",
  "rhs": [
   "$625",
   "qualified-name",
   "NEWLINE",
   "$626",
   "driver-result",
   "step-branch",
   "$628"
  ]
 },
 {
  "lhs": "$630",
  "rhs": [
   {
    "literal": "on"
   }
  ]
 },
 {
  "lhs": "$633",
  "rhs": [
   {
    "literal": "when"
   }
  ]
 },
 {
  "lhs": "$632",
  "rhs": [
   "$633",
   "expression"
  ]
 },
 {
  "lhs": "$631",
  "rhs": []
 },
 {
  "lhs": "$631",
  "rhs": [
   "$632"
  ]
 },
 {
  "lhs": "$634",
  "rhs": [
   {
    "literal": "on-success"
   },
   {
    "literal": "require"
   }
  ]
 },
 {
  "lhs": "$635",
  "rhs": [
   {
    "literal": "then"
   }
  ]
 },
 {
  "lhs": "$636",
  "rhs": [
   {
    "literal": "on-call-failure"
   }
  ]
 },
 {
  "lhs": "$637",
  "rhs": [
   {
    "literal": "on-contention"
   },
   {
    "literal": "reread"
   },
   {
    "literal": "snapshot"
   },
   {
    "literal": "then"
   },
   {
    "literal": "resume"
   }
  ]
 },
 {
  "lhs": "$638",
  "rhs": [
   {
    "literal": "on-unavailable"
   }
  ]
 },
 {
  "lhs": "$639",
  "rhs": [
   {
    "literal": "on-evidence-conflict"
   }
  ]
 },
 {
  "lhs": "$640",
  "rhs": [
   {
    "literal": "on-unknown"
   },
   {
    "literal": "continue"
   }
  ]
 },
 {
  "lhs": "$643",
  "rhs": [
   {
    "literal": ";"
   }
  ]
 },
 {
  "lhs": "$645",
  "rhs": [
   {
    "literal": "do-not-release"
   }
  ]
 },
 {
  "lhs": "$646",
  "rhs": [
   {
    "literal": "do-not-assume-rollback"
   }
  ]
 },
 {
  "lhs": "$644",
  "rhs": [
   "$645"
  ]
 },
 {
  "lhs": "$644",
  "rhs": [
   "$646"
  ]
 },
 {
  "lhs": "$642",
  "rhs": [
   "$643",
   "$644"
  ]
 },
 {
  "lhs": "$641",
  "rhs": []
 },
 {
  "lhs": "$641",
  "rhs": [
   "$642"
  ]
 },
 {
  "lhs": "step-branch",
  "rhs": [
   "$630",
   "pattern-list",
   "$631",
   "branch-action",
   "NEWLINE"
  ]
 },
 {
  "lhs": "step-branch",
  "rhs": [
   "$634",
   "expression",
   "$635",
   "workflow-action",
   "NEWLINE"
  ]
 },
 {
  "lhs": "step-branch",
  "rhs": [
   "$636",
   "branch-action",
   "NEWLINE"
  ]
 },
 {
  "lhs": "step-branch",
  "rhs": [
   "$637",
   "NEWLINE"
  ]
 },
 {
  "lhs": "step-branch",
  "rhs": [
   "$638",
   "workflow-action",
   "NEWLINE"
  ]
 },
 {
  "lhs": "step-branch",
  "rhs": [
   "$639",
   "branch-action",
   "NEWLINE"
  ]
 },
 {
  "lhs": "step-branch",
  "rhs": [
   "$640",
   "step-name",
   "$641",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$649",
  "rhs": [
   {
    "literal": "require"
   }
  ]
 },
 {
  "lhs": "$650",
  "rhs": [
   {
    "literal": "then"
   }
  ]
 },
 {
  "lhs": "$648",
  "rhs": [
   "$649",
   "expression",
   "$650"
  ]
 },
 {
  "lhs": "$647",
  "rhs": []
 },
 {
  "lhs": "$647",
  "rhs": [
   "$648"
  ]
 },
 {
  "lhs": "$653",
  "rhs": [
   {
    "literal": "retaining"
   },
   {
    "literal": "original"
   }
  ]
 },
 {
  "lhs": "$655",
  "rhs": [
   {
    "literal": "command"
   }
  ]
 },
 {
  "lhs": "$656",
  "rhs": [
   {
    "literal": "attempt"
   }
  ]
 },
 {
  "lhs": "$654",
  "rhs": [
   "$655"
  ]
 },
 {
  "lhs": "$654",
  "rhs": [
   "$656"
  ]
 },
 {
  "lhs": "$652",
  "rhs": [
   "$653",
   "$654"
  ]
 },
 {
  "lhs": "$651",
  "rhs": []
 },
 {
  "lhs": "$651",
  "rhs": [
   "$652"
  ]
 },
 {
  "lhs": "$659",
  "rhs": [
   {
    "literal": ";"
   }
  ]
 },
 {
  "lhs": "$661",
  "rhs": [
   {
    "literal": "do-not-release"
   }
  ]
 },
 {
  "lhs": "$662",
  "rhs": [
   {
    "literal": "do-not-assume-rollback"
   }
  ]
 },
 {
  "lhs": "$660",
  "rhs": [
   "$661"
  ]
 },
 {
  "lhs": "$660",
  "rhs": [
   "$662"
  ]
 },
 {
  "lhs": "$658",
  "rhs": [
   "$659",
   "$660"
  ]
 },
 {
  "lhs": "$657",
  "rhs": []
 },
 {
  "lhs": "$657",
  "rhs": [
   "$658"
  ]
 },
 {
  "lhs": "$663",
  "rhs": [
   {
    "literal": "observe"
   }
  ]
 },
 {
  "lhs": "$664",
  "rhs": [
   {
    "literal": "then"
   }
  ]
 },
 {
  "lhs": "branch-action",
  "rhs": [
   "$647",
   "workflow-action",
   "$651",
   "$657"
  ]
 },
 {
  "lhs": "branch-action",
  "rhs": [
   "$663",
   "expression",
   "$664",
   "workflow-action"
  ]
 },
 {
  "lhs": "$665",
  "rhs": [
   {
    "literal": "local-observation"
   }
  ]
 },
 {
  "lhs": "$666",
  "rhs": [
   {
    "literal": "commit-before"
   }
  ]
 },
 {
  "lhs": "$667",
  "rhs": [
   {
    "literal": "on-unknown"
   },
   {
    "literal": "inspect"
   },
   {
    "literal": "original"
   },
   {
    "literal": "observation"
   },
   {
    "literal": "before"
   },
   {
    "literal": "any"
   },
   {
    "literal": "provider"
   },
   {
    "literal": "dispatch"
   }
  ]
 },
 {
  "lhs": "$668",
  "rhs": [
   {
    "literal": "next"
   }
  ]
 },
 {
  "lhs": "$669",
  "rhs": [
   {
    "literal": "only"
   },
   {
    "literal": "after"
   },
   {
    "literal": "fresh"
   },
   {
    "literal": "acknowledged"
   },
   {
    "literal": "local"
   },
   {
    "literal": "commit"
   },
   {
    "literal": "or"
   },
   {
    "literal": "native"
   },
   {
    "literal": "never-dispatched"
   },
   {
    "literal": "journal"
   },
   {
    "literal": "evidence"
   }
  ]
 },
 {
  "lhs": "local-step",
  "rhs": [
   "$665",
   "expression",
   "NEWLINE",
   "$666",
   "step-name",
   "NEWLINE",
   "$667",
   "NEWLINE",
   "$668",
   "step-name",
   "$669",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$670",
  "rhs": [
   {
    "literal": "requires"
   },
   {
    "literal": "persisted"
   }
  ]
 },
 {
  "lhs": "$671",
  "rhs": [
   {
    "literal": "suspend"
   }
  ]
 },
 {
  "lhs": "review-step",
  "rhs": [
   "$670",
   "expression",
   "NEWLINE",
   "$671",
   "step-name",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$672",
  "rhs": [
   {
    "literal": "terminal"
   }
  ]
 },
 {
  "lhs": "$673",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$674",
  "rhs": [
   {
    "literal": "require"
   },
   {
    "literal": "persisted"
   }
  ]
 },
 {
  "lhs": "$675",
  "rhs": [
   {
    "literal": "effects"
   },
   {
    "literal": "none"
   }
  ]
 },
 {
  "lhs": "workflow-terminal",
  "rhs": [
   "$672",
   "step-name",
   "$673",
   "NEWLINE",
   "INDENT",
   "$674",
   "expression",
   "NEWLINE",
   "$675",
   "NEWLINE",
   "DEDENT"
  ]
 },
 {
  "lhs": "$676",
  "rhs": [
   {
    "literal": "workflow"
   }
  ]
 },
 {
  "lhs": "$677",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$678",
  "rhs": [
   {
    "literal": "owner"
   }
  ]
 },
 {
  "lhs": "$679",
  "rhs": [
   {
    "literal": "scope"
   },
   {
    "literal": "generated-recoverable"
   }
  ]
 },
 {
  "lhs": "$680",
  "rhs": [
   {
    "literal": "profile"
   }
  ]
 },
 {
  "lhs": "$682",
  "rhs": [
   "parameter"
  ]
 },
 {
  "lhs": "$681",
  "rhs": []
 },
 {
  "lhs": "$681",
  "rhs": [
   "$682",
   "$681"
  ]
 },
 {
  "lhs": "$683",
  "rhs": [
   {
    "literal": "correlation"
   }
  ]
 },
 {
  "lhs": "$684",
  "rhs": [
   {
    "literal": "durable-state"
   }
  ]
 },
 {
  "lhs": "$685",
  "rhs": [
   {
    "literal": "start"
   }
  ]
 },
 {
  "lhs": "$687",
  "rhs": [
   "generic-workflow-step"
  ]
 },
 {
  "lhs": "$686",
  "rhs": []
 },
 {
  "lhs": "$686",
  "rhs": [
   "$687",
   "$686"
  ]
 },
 {
  "lhs": "$688",
  "rhs": [
   {
    "literal": "recovery"
   },
   {
    "literal": "needed-compensations-only"
   },
   {
    "literal": "reverse-completion"
   }
  ]
 },
 {
  "lhs": "generic-workflow-declaration",
  "rhs": [
   "$676",
   "NAME",
   "$677",
   "NEWLINE",
   "INDENT",
   "$678",
   "step-name",
   "NEWLINE",
   "$679",
   "NEWLINE",
   "$680",
   "reference",
   "NEWLINE",
   "parameter",
   "$681",
   "$683",
   "NAME",
   "NEWLINE",
   "$684",
   "qualified-name",
   "NEWLINE",
   "$685",
   "qualified-name",
   "NEWLINE",
   "generic-workflow-step",
   "$686",
   "$688",
   "NEWLINE",
   "DEDENT"
  ]
 },
 {
  "lhs": "generic-workflow-step",
  "rhs": [
   "local-workflow-step"
  ]
 },
 {
  "lhs": "generic-workflow-step",
  "rhs": [
   "provider-workflow-step"
  ]
 },
 {
  "lhs": "generic-workflow-step",
  "rhs": [
   "event-workflow-step"
  ]
 },
 {
  "lhs": "generic-workflow-step",
  "rhs": [
   "plain-workflow-step"
  ]
 },
 {
  "lhs": "$689",
  "rhs": [
   {
    "literal": "step"
   }
  ]
 },
 {
  "lhs": "$690",
  "rhs": [
   {
    "literal": "invokes"
   }
  ]
 },
 {
  "lhs": "plain-workflow-step",
  "rhs": [
   "$689",
   "step-name",
   "$690",
   "qualified-name",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$691",
  "rhs": [
   {
    "literal": "step"
   }
  ]
 },
 {
  "lhs": "$692",
  "rhs": [
   {
    "literal": "invokes"
   }
  ]
 },
 {
  "lhs": "$693",
  "rhs": [
   {
    "literal": "compensate-with"
   }
  ]
 },
 {
  "lhs": "local-workflow-step",
  "rhs": [
   "$691",
   "step-name",
   "$692",
   "qualified-name",
   "$693",
   "qualified-name",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$694",
  "rhs": [
   {
    "literal": "step"
   }
  ]
 },
 {
  "lhs": "$695",
  "rhs": [
   {
    "literal": "invokes"
   }
  ]
 },
 {
  "lhs": "$696",
  "rhs": [
   {
    "literal": "on-unknown"
   },
   {
    "literal": "resume-original-command"
   }
  ]
 },
 {
  "lhs": "$697",
  "rhs": [
   {
    "literal": "on-definite-failure"
   },
   {
    "literal": "compensate"
   }
  ]
 },
 {
  "lhs": "provider-workflow-step",
  "rhs": [
   "$694",
   "step-name",
   "$695",
   "qualified-name",
   "$696",
   "$697",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$698",
  "rhs": [
   {
    "literal": "step"
   }
  ]
 },
 {
  "lhs": "$699",
  "rhs": [
   {
    "literal": "awaits"
   }
  ]
 },
 {
  "lhs": "$700",
  "rhs": [
   {
    "literal": "delivered-to"
   }
  ]
 },
 {
  "lhs": "event-workflow-step",
  "rhs": [
   "$698",
   "step-name",
   "$699",
   "qualified-name",
   "$700",
   "qualified-name",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$701",
  "rhs": [
   {
    "literal": "interface"
   }
  ]
 },
 {
  "lhs": "$702",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$703",
  "rhs": [
   {
    "literal": "kind"
   }
  ]
 },
 {
  "lhs": "$705",
  "rhs": [
   "interface-clause"
  ]
 },
 {
  "lhs": "$704",
  "rhs": []
 },
 {
  "lhs": "$704",
  "rhs": [
   "$705",
   "$704"
  ]
 },
 {
  "lhs": "interface-declaration",
  "rhs": [
   "$701",
   "NAME",
   "$702",
   "NEWLINE",
   "INDENT",
   "$703",
   "interface-kind",
   "NEWLINE",
   "interface-clause",
   "$704",
   "DEDENT"
  ]
 },
 {
  "lhs": "$706",
  "rhs": [
   {
    "literal": "internal"
   }
  ]
 },
 {
  "lhs": "$707",
  "rhs": [
   {
    "literal": "external"
   }
  ]
 },
 {
  "lhs": "$708",
  "rhs": [
   {
    "literal": "bounded-schema"
   }
  ]
 },
 {
  "lhs": "$709",
  "rhs": [
   {
    "literal": "native-producer"
   }
  ]
 },
 {
  "lhs": "$710",
  "rhs": [
   {
    "literal": "trusted-context"
   }
  ]
 },
 {
  "lhs": "$711",
  "rhs": [
   {
    "literal": "native-auth-owner"
   }
  ]
 },
 {
  "lhs": "$712",
  "rhs": [
   {
    "literal": "technical-profile-family"
   }
  ]
 },
 {
  "lhs": "$713",
  "rhs": [
   {
    "literal": "application-composition"
   }
  ]
 },
 {
  "lhs": "interface-kind",
  "rhs": [
   "$706"
  ]
 },
 {
  "lhs": "interface-kind",
  "rhs": [
   "$707"
  ]
 },
 {
  "lhs": "interface-kind",
  "rhs": [
   "$708"
  ]
 },
 {
  "lhs": "interface-kind",
  "rhs": [
   "$709"
  ]
 },
 {
  "lhs": "interface-kind",
  "rhs": [
   "$710"
  ]
 },
 {
  "lhs": "interface-kind",
  "rhs": [
   "$711"
  ]
 },
 {
  "lhs": "interface-kind",
  "rhs": [
   "$712"
  ]
 },
 {
  "lhs": "interface-kind",
  "rhs": [
   "$713"
  ]
 },
 {
  "lhs": "$714",
  "rhs": [
   {
    "literal": "exposes"
   }
  ]
 },
 {
  "lhs": "$715",
  "rhs": [
   {
    "literal": "visibility"
   },
   {
    "literal": "service-private"
   },
   {
    "literal": "owner"
   }
  ]
 },
 {
  "lhs": "$717",
  "rhs": [
   {
    "literal": "abi"
   }
  ]
 },
 {
  "lhs": "$718",
  "rhs": [
   {
    "literal": "signatures"
   }
  ]
 },
 {
  "lhs": "$719",
  "rhs": [
   {
    "literal": "fields"
   }
  ]
 },
 {
  "lhs": "$720",
  "rhs": [
   {
    "literal": "methods"
   }
  ]
 },
 {
  "lhs": "$721",
  "rhs": [
   {
    "literal": "variants"
   }
  ]
 },
 {
  "lhs": "$716",
  "rhs": [
   "$717"
  ]
 },
 {
  "lhs": "$716",
  "rhs": [
   "$718"
  ]
 },
 {
  "lhs": "$716",
  "rhs": [
   "$719"
  ]
 },
 {
  "lhs": "$716",
  "rhs": [
   "$720"
  ]
 },
 {
  "lhs": "$716",
  "rhs": [
   "$721"
  ]
 },
 {
  "lhs": "$722",
  "rhs": [
   {
    "literal": "custody"
   }
  ]
 },
 {
  "lhs": "$723",
  "rhs": [
   {
    "literal": "serializable"
   },
   {
    "literal": "false"
   }
  ]
 },
 {
  "lhs": "$724",
  "rhs": [
   {
    "literal": "public-constructor"
   },
   {
    "literal": "forbidden"
   }
  ]
 },
 {
  "lhs": "$725",
  "rhs": [
   {
    "literal": "implementation"
   },
   {
    "literal": "required-later-native-asset"
   }
  ]
 },
 {
  "lhs": "$726",
  "rhs": [
   {
    "literal": "on-unresolved"
   },
   {
    "literal": "reject"
   },
   {
    "literal": "NativeImplementationUnavailable"
   }
  ]
 },
 {
  "lhs": "$727",
  "rhs": [
   {
    "literal": "admission"
   },
   {
    "literal": "auth-foundation-authorization-admission-service"
   }
  ]
 },
 {
  "lhs": "$728",
  "rhs": [
   {
    "literal": "decision"
   },
   {
    "literal": "auth-foundation-authorization-ready-decision"
   },
   {
    "literal": "."
   },
   {
    "literal": "authorize"
   }
  ]
 },
 {
  "lhs": "$729",
  "rhs": [
   {
    "literal": "protocol"
   }
  ]
 },
 {
  "lhs": "$731",
  "rhs": [
   {
    "literal": "request"
   }
  ]
 },
 {
  "lhs": "$732",
  "rhs": [
   {
    "literal": "result"
   }
  ]
 },
 {
  "lhs": "$730",
  "rhs": [
   "$731"
  ]
 },
 {
  "lhs": "$730",
  "rhs": [
   "$732"
  ]
 },
 {
  "lhs": "$734",
  "rhs": [
   {
    "literal": "binding"
   }
  ]
 },
 {
  "lhs": "$735",
  "rhs": [
   {
    "literal": "family-contract"
   }
  ]
 },
 {
  "lhs": "$736",
  "rhs": [
   {
    "literal": "obligations"
   }
  ]
 },
 {
  "lhs": "$733",
  "rhs": [
   "$734"
  ]
 },
 {
  "lhs": "$733",
  "rhs": [
   "$735"
  ]
 },
 {
  "lhs": "$733",
  "rhs": [
   "$736"
  ]
 },
 {
  "lhs": "$737",
  "rhs": [
   {
    "literal": "input"
   },
   {
    "literal": "checked"
   },
   {
    "literal": "technical"
   },
   {
    "literal": "Craft"
   },
   {
    "literal": "model"
   },
   {
    "literal": "with"
   },
   {
    "literal": "original"
   },
   {
    "literal": "owner"
   }
  ]
 },
 {
  "lhs": "$738",
  "rhs": [
   {
    "literal": "output"
   },
   {
    "literal": "derived"
   },
   {
    "literal": "candidate"
   },
   {
    "literal": "package"
   },
   {
    "literal": "with"
   },
   {
    "literal": "actual"
   },
   {
    "literal": "resolved"
   },
   {
    "literal": "native"
   },
   {
    "literal": "basis"
   }
  ]
 },
 {
  "lhs": "$739",
  "rhs": [
   {
    "literal": "callbacks"
   },
   {
    "literal": "forbidden"
   }
  ]
 },
 {
  "lhs": "$740",
  "rhs": [
   {
    "literal": "unknown-primitive"
   },
   {
    "literal": "reject"
   }
  ]
 },
 {
  "lhs": "$741",
  "rhs": [
   {
    "literal": "missing-producer"
   },
   {
    "literal": "reject"
   }
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "$714",
   "name-list",
   "NEWLINE"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "$715",
   "step-name",
   "NEWLINE"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "$716",
   "reference",
   "NEWLINE"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "$722",
   "custody-kind",
   "NEWLINE"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "$723",
   "NEWLINE"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "$724",
   "NEWLINE"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "$725",
   "NEWLINE"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "$726",
   "NEWLINE"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "$727",
   "NEWLINE"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "$728",
   "NEWLINE"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "$729",
   "PROTOCOL_NAME",
   "NEWLINE"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "$730",
   "type",
   "NEWLINE"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "$733",
   "reference",
   "NEWLINE"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "$737",
   "NEWLINE"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "$738",
   "NEWLINE"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "$739",
   "NEWLINE"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "$740",
   "NEWLINE"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "$741",
   "NEWLINE"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "value-domain-clause"
  ]
 },
 {
  "lhs": "interface-clause",
  "rhs": [
   "application-clause"
  ]
 },
 {
  "lhs": "$742",
  "rhs": [
   {
    "literal": "private-registered-source-profile-callsite"
   }
  ]
 },
 {
  "lhs": "$743",
  "rhs": [
   {
    "literal": "private-registered-entry-auth-owner"
   }
  ]
 },
 {
  "lhs": "$744",
  "rhs": [
   {
    "literal": "private-registered-local-worker-owner"
   }
  ]
 },
 {
  "lhs": "$745",
  "rhs": [
   {
    "literal": "private-registered-service-entry-owner"
   }
  ]
 },
 {
  "lhs": "$746",
  "rhs": [
   {
    "literal": "private-registered-parent-call-store-worker-or-event-owner"
   }
  ]
 },
 {
  "lhs": "custody-kind",
  "rhs": [
   "$742"
  ]
 },
 {
  "lhs": "custody-kind",
  "rhs": [
   "$743"
  ]
 },
 {
  "lhs": "custody-kind",
  "rhs": [
   "$744"
  ]
 },
 {
  "lhs": "custody-kind",
  "rhs": [
   "$745"
  ]
 },
 {
  "lhs": "custody-kind",
  "rhs": [
   "$746"
  ]
 },
 {
  "lhs": "$747",
  "rhs": [
   {
    "literal": "scalar"
   },
   {
    "literal": "UInt64"
   },
   {
    "literal": "wire"
   },
   {
    "literal": "canonical-decimal-string"
   },
   {
    "literal": "native"
   },
   {
    "literal": "bigint"
   },
   {
    "literal": "range"
   }
  ]
 },
 {
  "lhs": "$748",
  "rhs": [
   {
    "literal": ".."
   }
  ]
 },
 {
  "lhs": "$749",
  "rhs": [
   {
    "literal": "scalar"
   },
   {
    "literal": "Bool"
   },
   {
    "literal": "wire"
   },
   {
    "literal": "boolean"
   },
   {
    "literal": "native"
   },
   {
    "literal": "boolean"
   }
  ]
 },
 {
  "lhs": "$750",
  "rhs": [
   {
    "literal": "validates"
   }
  ]
 },
 {
  "lhs": "$751",
  "rhs": [
   {
    "literal": "using"
   }
  ]
 },
 {
  "lhs": "$753",
  "rhs": [
   {
    "literal": "declared-refinement"
   }
  ]
 },
 {
  "lhs": "$754",
  "rhs": [
   {
    "literal": "closed-enum"
   }
  ]
 },
 {
  "lhs": "$755",
  "rhs": [
   {
    "literal": "closed-fields-and-invariants"
   }
  ]
 },
 {
  "lhs": "$752",
  "rhs": [
   "qualified-name"
  ]
 },
 {
  "lhs": "$752",
  "rhs": [
   "$753"
  ]
 },
 {
  "lhs": "$752",
  "rhs": [
   "$754"
  ]
 },
 {
  "lhs": "$752",
  "rhs": [
   "$755"
  ]
 },
 {
  "lhs": "$756",
  "rhs": [
   {
    "literal": "codec"
   },
   {
    "literal": "strict-utf8-duplicate-aware-json"
   }
  ]
 },
 {
  "lhs": "$757",
  "rhs": [
   {
    "literal": "optional"
   },
   {
    "literal": "wire"
   },
   {
    "literal": "null-or-value"
   },
   {
    "literal": "native"
   },
   {
    "literal": "tagged-none-or-some"
   }
  ]
 },
 {
  "lhs": "$758",
  "rhs": [
   {
    "literal": "on-invalid"
   },
   {
    "literal": "reject"
   },
   {
    "literal": "invalid-request"
   },
   {
    "literal": "before"
   },
   {
    "literal": "business"
   },
   {
    "literal": "invocation"
   }
  ]
 },
 {
  "lhs": "value-domain-clause",
  "rhs": [
   "$747",
   "natural",
   "$748",
   "natural",
   "NEWLINE"
  ]
 },
 {
  "lhs": "value-domain-clause",
  "rhs": [
   "$749",
   "NEWLINE"
  ]
 },
 {
  "lhs": "value-domain-clause",
  "rhs": [
   "$750",
   "type",
   "$751",
   "$752",
   "NEWLINE"
  ]
 },
 {
  "lhs": "value-domain-clause",
  "rhs": [
   "$756",
   "NEWLINE"
  ]
 },
 {
  "lhs": "value-domain-clause",
  "rhs": [
   "$757",
   "NEWLINE"
  ]
 },
 {
  "lhs": "value-domain-clause",
  "rhs": [
   "$758",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$759",
  "rhs": [
   {
    "literal": "source"
   }
  ]
 },
 {
  "lhs": "$760",
  "rhs": [
   {
    "literal": "service"
   }
  ]
 },
 {
  "lhs": "$761",
  "rhs": [
   {
    "literal": "module"
   }
  ]
 },
 {
  "lhs": "$763",
  "rhs": [
   {
    "literal": "entry-catalog"
   }
  ]
 },
 {
  "lhs": "$764",
  "rhs": [
   {
    "literal": "implementation"
   }
  ]
 },
 {
  "lhs": "$762",
  "rhs": [
   "$763"
  ]
 },
 {
  "lhs": "$762",
  "rhs": [
   "$764"
  ]
 },
 {
  "lhs": "$765",
  "rhs": [
   {
    "literal": "coordination-records"
   }
  ]
 },
 {
  "lhs": "$766",
  "rhs": [
   {
    "literal": "required-output"
   }
  ]
 },
 {
  "lhs": "$767",
  "rhs": [
   {
    "literal": "formal-claims"
   },
   {
    "literal": "optional"
   }
  ]
 },
 {
  "lhs": "$768",
  "rhs": [
   {
    "literal": "hosting"
   },
   {
    "literal": "deferred"
   }
  ]
 },
 {
  "lhs": "application-clause",
  "rhs": [
   "$759",
   "reference",
   "NEWLINE"
  ]
 },
 {
  "lhs": "application-clause",
  "rhs": [
   "$760",
   "step-name",
   "$761",
   "qualified-name",
   "NEWLINE"
  ]
 },
 {
  "lhs": "application-clause",
  "rhs": [
   "$762",
   "qualified-name",
   "NEWLINE"
  ]
 },
 {
  "lhs": "application-clause",
  "rhs": [
   "application-reference",
   "reference",
   "NEWLINE"
  ]
 },
 {
  "lhs": "application-clause",
  "rhs": [
   "$765",
   "name-list",
   "NEWLINE"
  ]
 },
 {
  "lhs": "application-clause",
  "rhs": [
   "$766",
   "output-kind",
   "NEWLINE"
  ]
 },
 {
  "lhs": "application-clause",
  "rhs": [
   "$767",
   "NEWLINE"
  ]
 },
 {
  "lhs": "application-clause",
  "rhs": [
   "$768",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$769",
  "rhs": [
   {
    "literal": "parameters"
   }
  ]
 },
 {
  "lhs": "$770",
  "rhs": [
   {
    "literal": "http-bindings"
   }
  ]
 },
 {
  "lhs": "$771",
  "rhs": [
   {
    "literal": "external-bindings"
   }
  ]
 },
 {
  "lhs": "$772",
  "rhs": [
   {
    "literal": "external-config"
   }
  ]
 },
 {
  "lhs": "$773",
  "rhs": [
   {
    "literal": "value-domain"
   }
  ]
 },
 {
  "lhs": "$774",
  "rhs": [
   {
    "literal": "computation-bounds"
   }
  ]
 },
 {
  "lhs": "$775",
  "rhs": [
   {
    "literal": "provider-protocol"
   }
  ]
 },
 {
  "lhs": "$776",
  "rhs": [
   {
    "literal": "authorization"
   }
  ]
 },
 {
  "lhs": "$777",
  "rhs": [
   {
    "literal": "native-obligations"
   }
  ]
 },
 {
  "lhs": "$778",
  "rhs": [
   {
    "literal": "profile-family"
   }
  ]
 },
 {
  "lhs": "$779",
  "rhs": [
   {
    "literal": "coordination-contract"
   }
  ]
 },
 {
  "lhs": "$780",
  "rhs": [
   {
    "literal": "source-identities"
   }
  ]
 },
 {
  "lhs": "application-reference",
  "rhs": [
   "$769"
  ]
 },
 {
  "lhs": "application-reference",
  "rhs": [
   "$770"
  ]
 },
 {
  "lhs": "application-reference",
  "rhs": [
   "$771"
  ]
 },
 {
  "lhs": "application-reference",
  "rhs": [
   "$772"
  ]
 },
 {
  "lhs": "application-reference",
  "rhs": [
   "$773"
  ]
 },
 {
  "lhs": "application-reference",
  "rhs": [
   "$774"
  ]
 },
 {
  "lhs": "application-reference",
  "rhs": [
   "$775"
  ]
 },
 {
  "lhs": "application-reference",
  "rhs": [
   "$776"
  ]
 },
 {
  "lhs": "application-reference",
  "rhs": [
   "$777"
  ]
 },
 {
  "lhs": "application-reference",
  "rhs": [
   "$778"
  ]
 },
 {
  "lhs": "application-reference",
  "rhs": [
   "$779"
  ]
 },
 {
  "lhs": "application-reference",
  "rhs": [
   "$780"
  ]
 },
 {
  "lhs": "$781",
  "rhs": [
   {
    "literal": "code"
   }
  ]
 },
 {
  "lhs": "$782",
  "rhs": [
   {
    "literal": "api-contracts"
   }
  ]
 },
 {
  "lhs": "$783",
  "rhs": [
   {
    "literal": "business-graph"
   }
  ]
 },
 {
  "lhs": "$784",
  "rhs": [
   {
    "literal": "system-graph"
   }
  ]
 },
 {
  "lhs": "$785",
  "rhs": [
   {
    "literal": "business-system-bridge"
   }
  ]
 },
 {
  "lhs": "output-kind",
  "rhs": [
   "$781"
  ]
 },
 {
  "lhs": "output-kind",
  "rhs": [
   "$782"
  ]
 },
 {
  "lhs": "output-kind",
  "rhs": [
   "$783"
  ]
 },
 {
  "lhs": "output-kind",
  "rhs": [
   "$784"
  ]
 },
 {
  "lhs": "output-kind",
  "rhs": [
   "$785"
  ]
 },
 {
  "lhs": "$786",
  "rhs": [
   {
    "literal": "formal-claim"
   }
  ]
 },
 {
  "lhs": "$787",
  "rhs": [
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$788",
  "rhs": [
   {
    "literal": "language"
   }
  ]
 },
 {
  "lhs": "$790",
  "rhs": [
   {
    "literal": "lean4"
   }
  ]
 },
 {
  "lhs": "$791",
  "rhs": [
   {
    "literal": "smtlib2"
   }
  ]
 },
 {
  "lhs": "$792",
  "rhs": [
   {
    "literal": "alloy"
   }
  ]
 },
 {
  "lhs": "$793",
  "rhs": [
   {
    "literal": "tla-plus"
   }
  ]
 },
 {
  "lhs": "$794",
  "rhs": [
   {
    "literal": "souffle"
   }
  ]
 },
 {
  "lhs": "$789",
  "rhs": [
   "$790"
  ]
 },
 {
  "lhs": "$789",
  "rhs": [
   "$791"
  ]
 },
 {
  "lhs": "$789",
  "rhs": [
   "$792"
  ]
 },
 {
  "lhs": "$789",
  "rhs": [
   "$793"
  ]
 },
 {
  "lhs": "$789",
  "rhs": [
   "$794"
  ]
 },
 {
  "lhs": "$795",
  "rhs": [
   {
    "literal": "source"
   }
  ]
 },
 {
  "lhs": "$796",
  "rhs": [
   {
    "literal": "targets"
   }
  ]
 },
 {
  "lhs": "claim-declaration",
  "rhs": [
   "$786",
   "NAME",
   "$787",
   "NEWLINE",
   "INDENT",
   "$788",
   "$789",
   "NEWLINE",
   "$795",
   "reference",
   "NEWLINE",
   "$796",
   "name-list",
   "NEWLINE",
   "DEDENT"
  ]
 },
 {
  "lhs": "$797",
  "rhs": [
   {
    "literal": "native-protocol"
   }
  ]
 },
 {
  "lhs": "$798",
  "rhs": [
   {
    "literal": "intent"
   },
   {
    "literal": "immutable"
   }
  ]
 },
 {
  "lhs": "$799",
  "rhs": [
   {
    "literal": "same-key"
   },
   {
    "literal": "same-request"
   },
   {
    "literal": "returns"
   },
   {
    "literal": "current"
   },
   {
    "literal": "original-attempt"
   },
   {
    "literal": "status"
   },
   {
    "literal": ";"
   },
   {
    "literal": "never"
   },
   {
    "literal": "another"
   },
   {
    "literal": "effect"
   }
  ]
 },
 {
  "lhs": "$800",
  "rhs": [
   {
    "literal": "same-key"
   },
   {
    "literal": "different-request"
   },
   {
    "literal": "fails"
   },
   {
    "literal": "ProviderRequestConflict"
   },
   {
    "literal": "without"
   },
   {
    "literal": "mutation"
   }
  ]
 },
 {
  "lhs": "$801",
  "rhs": [
   {
    "literal": "may-return"
   }
  ]
 },
 {
  "lhs": "$802",
  "rhs": [
   {
    "literal": "on-malformed-request"
   },
   {
    "literal": "fails"
   },
   {
    "literal": "ProviderInputRejected"
   }
  ]
 },
 {
  "lhs": "$803",
  "rhs": [
   {
    "literal": "on-invalid-response"
   },
   {
    "literal": "fails"
   },
   {
    "literal": "ProviderProtocolRejected"
   }
  ]
 },
 {
  "lhs": "$804",
  "rhs": [
   {
    "literal": "on-transport-failure"
   },
   {
    "literal": "fails"
   },
   {
    "literal": "ProviderTransportUnknown"
   }
  ]
 },
 {
  "lhs": "native-capture-body",
  "rhs": [
   "$797",
   "qualified-name",
   "NEWLINE",
   "$798",
   "invocation",
   "NEWLINE",
   "$799",
   "NEWLINE",
   "$800",
   "NEWLINE",
   "$801",
   "name-list",
   "NEWLINE",
   "$802",
   "NEWLINE",
   "$803",
   "NEWLINE",
   "$804",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$805",
  "rhs": [
   {
    "literal": "output"
   }
  ]
 },
 {
  "lhs": "$806",
  "rhs": [
   {
    "literal": "native-protocol"
   }
  ]
 },
 {
  "lhs": "$807",
  "rhs": [
   {
    "literal": "compare"
   },
   {
    "literal": "original"
   },
   {
    "literal": "request"
   },
   {
    "literal": "using"
   }
  ]
 },
 {
  "lhs": "$808",
  "rhs": [
   {
    "literal": "on-existing"
   },
   {
    "literal": "returns"
   },
   {
    "literal": "current"
   },
   {
    "literal": "original-attempt"
   },
   {
    "literal": "status"
   }
  ]
 },
 {
  "lhs": "$809",
  "rhs": [
   {
    "literal": "on-missing"
   },
   {
    "literal": "returns"
   },
   {
    "literal": "UnknownKey"
   },
   {
    "literal": "with"
   },
   {
    "literal": "exact"
   },
   {
    "literal": "supplied"
   },
   {
    "literal": "identity"
   },
   {
    "literal": "and"
   },
   {
    "literal": "no"
   },
   {
    "literal": "reference"
   }
  ]
 },
 {
  "lhs": "$810",
  "rhs": [
   {
    "literal": "on-conflict"
   },
   {
    "literal": "fails"
   },
   {
    "literal": "ProviderRequestConflict"
   }
  ]
 },
 {
  "lhs": "$811",
  "rhs": [
   {
    "literal": "effects"
   },
   {
    "literal": "none"
   }
  ]
 },
 {
  "lhs": "native-inspect-body",
  "rhs": [
   "$805",
   "type",
   "NEWLINE",
   "$806",
   "qualified-name",
   "NEWLINE",
   "$807",
   "qualified-name",
   "NEWLINE",
   "$808",
   "NEWLINE",
   "$809",
   "NEWLINE",
   "$810",
   "NEWLINE",
   "$811",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$812",
  "rhs": [
   {
    "literal": "ordered-protocol"
   },
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$813",
  "rhs": [
   {
    "literal": "validate"
   },
   {
    "literal": "request-shape"
   },
   {
    "literal": "before"
   },
   {
    "literal": "replay-read"
   }
  ]
 },
 {
  "lhs": "$814",
  "rhs": [
   {
    "literal": "check"
   },
   {
    "literal": "current-action-access"
   },
   {
    "literal": "before"
   },
   {
    "literal": "replay-read"
   }
  ]
 },
 {
  "lhs": "$815",
  "rhs": [
   {
    "literal": "scope"
   }
  ]
 },
 {
  "lhs": "$816",
  "rhs": [
   {
    "literal": "fingerprint"
   }
  ]
 },
 {
  "lhs": "$817",
  "rhs": [
   {
    "literal": "fields"
   }
  ]
 },
 {
  "lhs": "$818",
  "rhs": [
   {
    "literal": "encoding"
   }
  ]
 },
 {
  "lhs": "$819",
  "rhs": [
   {
    "literal": "digest"
   },
   {
    "literal": "sha256"
   }
  ]
 },
 {
  "lhs": "$820",
  "rhs": [
   {
    "literal": "normalization"
   },
   {
    "literal": "none"
   }
  ]
 },
 {
  "lhs": "$821",
  "rhs": [
   {
    "literal": "read"
   },
   {
    "literal": "replay-record"
   },
   {
    "literal": "by"
   },
   {
    "literal": "scope"
   }
  ]
 },
 {
  "lhs": "$822",
  "rhs": [
   {
    "literal": "apply"
   }
  ]
 },
 {
  "lhs": "$824",
  "rhs": [
   "replay-contract-case"
  ]
 },
 {
  "lhs": "$823",
  "rhs": []
 },
 {
  "lhs": "$823",
  "rhs": [
   "$824",
   "$823"
  ]
 },
 {
  "lhs": "replay-protocol",
  "rhs": [
   "$812",
   "NEWLINE",
   "INDENT",
   "$813",
   "NEWLINE",
   "$814",
   "NEWLINE",
   "$815",
   "name-list",
   "NEWLINE",
   "$816",
   "reference",
   "NEWLINE",
   "INDENT",
   "$817",
   "name-list",
   "NEWLINE",
   "$818",
   "reference",
   "NEWLINE",
   "$819",
   "NEWLINE",
   "$820",
   "NEWLINE",
   "DEDENT",
   "$821",
   "NEWLINE",
   "$822",
   "qualified-name",
   "NEWLINE",
   "replay-contract-case",
   "$823",
   "DEDENT",
   "replay-retention",
   "replay-reconciliation"
  ]
 },
 {
  "lhs": "$825",
  "rhs": [
   {
    "literal": "on"
   },
   {
    "literal": "ReplayAccepted"
   },
   {
    "literal": "return"
   },
   {
    "literal": "stored"
   }
  ]
 },
 {
  "lhs": "$826",
  "rhs": [
   {
    "literal": "on"
   },
   {
    "literal": "ReplayPending"
   },
   {
    "literal": "retain"
   },
   {
    "literal": "original"
   },
   {
    "literal": "command"
   },
   {
    "literal": ";"
   },
   {
    "literal": "no"
   },
   {
    "literal": "second"
   },
   {
    "literal": "execution"
   }
  ]
 },
 {
  "lhs": "$827",
  "rhs": [
   {
    "literal": "on"
   },
   {
    "literal": "OutcomeUnknown"
   },
   {
    "literal": "retain"
   },
   {
    "literal": "original"
   },
   {
    "literal": "command"
   },
   {
    "literal": ";"
   },
   {
    "literal": "inspect"
   },
   {
    "literal": "authoritative"
   },
   {
    "literal": "record"
   },
   {
    "literal": "read-only"
   }
  ]
 },
 {
  "lhs": "$828",
  "rhs": [
   {
    "literal": "on"
   },
   {
    "literal": "FingerprintConflict"
   },
   {
    "literal": "retain"
   },
   {
    "literal": "original"
   },
   {
    "literal": "record"
   },
   {
    "literal": ";"
   },
   {
    "literal": "no"
   },
   {
    "literal": "new-effects"
   }
  ]
 },
 {
  "lhs": "$829",
  "rhs": [
   {
    "literal": "on"
   },
   {
    "literal": "CapacityUnavailable"
   },
   {
    "literal": "retain"
   },
   {
    "literal": "all"
   },
   {
    "literal": "existing"
   },
   {
    "literal": "records"
   },
   {
    "literal": ";"
   },
   {
    "literal": "no"
   },
   {
    "literal": "new-effects"
   }
  ]
 },
 {
  "lhs": "$830",
  "rhs": [
   {
    "literal": "on"
   },
   {
    "literal": "EvaluateFreshQuote"
   },
   {
    "literal": "evaluate"
   },
   {
    "literal": "owned"
   },
   {
    "literal": "quote"
   },
   {
    "literal": ";"
   },
   {
    "literal": "atomically"
   },
   {
    "literal": "claim"
   },
   {
    "literal": "scope"
   },
   {
    "literal": "with"
   },
   {
    "literal": "local"
   },
   {
    "literal": "acceptance"
   }
  ]
 },
 {
  "lhs": "replay-contract-case",
  "rhs": [
   "$825",
   "qualified-name",
   "before-order",
   "NEWLINE"
  ]
 },
 {
  "lhs": "replay-contract-case",
  "rhs": [
   "$826",
   "NEWLINE"
  ]
 },
 {
  "lhs": "replay-contract-case",
  "rhs": [
   "$827",
   "NEWLINE"
  ]
 },
 {
  "lhs": "replay-contract-case",
  "rhs": [
   "$828",
   "NEWLINE"
  ]
 },
 {
  "lhs": "replay-contract-case",
  "rhs": [
   "$829",
   "NEWLINE"
  ]
 },
 {
  "lhs": "replay-contract-case",
  "rhs": [
   "$830",
   "NEWLINE"
  ]
 },
 {
  "lhs": "$831",
  "rhs": [
   {
    "literal": "retention"
   },
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$832",
  "rhs": [
   {
    "literal": "capacity"
   }
  ]
 },
 {
  "lhs": "$833",
  "rhs": [
   {
    "literal": "per-orders-service"
   }
  ]
 },
 {
  "lhs": "$834",
  "rhs": [
   {
    "literal": "lifetime"
   },
   {
    "literal": "scratch-cell-lifetime"
   }
  ]
 },
 {
  "lhs": "$835",
  "rhs": [
   {
    "literal": "accepted"
   },
   {
    "literal": "never-evict"
   }
  ]
 },
 {
  "lhs": "$836",
  "rhs": [
   {
    "literal": "pending"
   },
   {
    "literal": "never-evict"
   }
  ]
 },
 {
  "lhs": "$837",
  "rhs": [
   {
    "literal": "indeterminate"
   },
   {
    "literal": "never-evict"
   }
  ]
 },
 {
  "lhs": "$838",
  "rhs": [
   {
    "literal": "full"
   },
   {
    "literal": "reject-new-work"
   }
  ]
 },
 {
  "lhs": "$839",
  "rhs": [
   {
    "literal": "key-reset"
   },
   {
    "literal": "forbidden"
   }
  ]
 },
 {
  "lhs": "$840",
  "rhs": [
   {
    "literal": "automatic-expiry"
   },
   {
    "literal": "forbidden"
   }
  ]
 },
 {
  "lhs": "replay-retention",
  "rhs": [
   "$831",
   "NEWLINE",
   "INDENT",
   "$832",
   "natural",
   "$833",
   "NEWLINE",
   "$834",
   "NEWLINE",
   "$835",
   "NEWLINE",
   "$836",
   "NEWLINE",
   "$837",
   "NEWLINE",
   "$838",
   "NEWLINE",
   "$839",
   "NEWLINE",
   "$840",
   "NEWLINE",
   "DEDENT"
  ]
 },
 {
  "lhs": "$841",
  "rhs": [
   {
    "literal": "reconciliation"
   },
   {
    "literal": ":"
   }
  ]
 },
 {
  "lhs": "$842",
  "rhs": [
   {
    "literal": "require"
   },
   {
    "literal": "current-action-access"
   },
   {
    "literal": "before"
   },
   {
    "literal": "authoritative-read"
   }
  ]
 },
 {
  "lhs": "$843",
  "rhs": [
   {
    "literal": "validate"
   },
   {
    "literal": "original"
   },
   {
    "literal": "request-shape"
   },
   {
    "literal": "before"
   },
   {
    "literal": "authoritative-read"
   }
  ]
 },
 {
  "lhs": "$844",
  "rhs": [
   {
    "literal": "read-only"
   },
   {
    "literal": "original"
   },
   {
    "literal": "scope"
   },
   {
    "literal": ","
   },
   {
    "literal": "fingerprint"
   }
  ]
 },
 {
  "lhs": "$845",
  "rhs": [
   {
    "literal": "accepted"
   },
   {
    "literal": "return"
   },
   {
    "literal": "original"
   }
  ]
 },
 {
  "lhs": "$846",
  "rhs": [
   {
    "literal": "pending"
   },
   {
    "literal": "remain"
   },
   {
    "literal": "ReplayPending"
   }
  ]
 },
 {
  "lhs": "$847",
  "rhs": [
   {
    "literal": "indeterminate"
   },
   {
    "literal": "remain"
   },
   {
    "literal": "OutcomeUnknown"
   }
  ]
 },
 {
  "lhs": "$848",
  "rhs": [
   {
    "literal": "absent-after-uncertainty"
   },
   {
    "literal": "remain"
   },
   {
    "literal": "OutcomeUnknown"
   }
  ]
 },
 {
  "lhs": "$849",
  "rhs": [
   {
    "literal": "proven-local-rollback"
   },
   {
    "literal": "retry"
   },
   {
    "literal": "original"
   },
   {
    "literal": "command"
   },
   {
    "literal": "with"
   },
   {
    "literal": "same"
   },
   {
    "literal": "scope"
   },
   {
    "literal": ","
   },
   {
    "literal": "fingerprint"
   }
  ]
 },
 {
  "lhs": "$850",
  "rhs": [
   {
    "literal": "unavailable"
   },
   {
    "literal": "remain"
   },
   {
    "literal": "OutcomeUnknown"
   }
  ]
 },
 {
  "lhs": "replay-reconciliation",
  "rhs": [
   "$841",
   "NEWLINE",
   "INDENT",
   "$842",
   "NEWLINE",
   "$843",
   "NEWLINE",
   "$844",
   "NEWLINE",
   "$845",
   "qualified-name",
   "NEWLINE",
   "$846",
   "NEWLINE",
   "$847",
   "NEWLINE",
   "$848",
   "NEWLINE",
   "$849",
   "NEWLINE",
   "$850",
   "NEWLINE",
   "DEDENT"
  ]
 }
];
