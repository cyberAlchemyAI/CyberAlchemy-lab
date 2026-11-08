// GENERATED Core EBNF data; tools/commerce-contracts/core-grammar.mjs owns it.
// Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions.
export type CoreGrammarNode={readonly op:"rule";readonly value:string}|{readonly op:"literal";readonly value:string}|{readonly op:"seq";readonly nodes:readonly CoreGrammarNode[]}|{readonly op:"alt";readonly nodes:readonly CoreGrammarNode[]}|{readonly op:"many";readonly node:CoreGrammarNode}|{readonly op:"maybe";readonly node:CoreGrammarNode};
export const CORE_COMMERCE_GRAMMAR_SHA256="34de5b441f753ba8b397758f76bb5c38eceaa83dcff79e6a3305eeb698c88ce8";
export const CORE_COMMERCE_RESERVED:readonly string[]=["map","filter","fold","indexed-fold","repeat","while-bounded","until-bounded","range","sort","match","true","false","none"];
export const CORE_COMMERCE_GRAMMAR:Readonly<Record<string,CoreGrammarNode>>={
 "source": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "module-header"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "many",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "rule",
       "value": "import-line"
      },
      {
       "op": "rule",
       "value": "NEWLINE"
      }
     ]
    }
   },
   {
    "op": "rule",
    "value": "declaration"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "declaration"
    }
   }
  ]
 },
 "module-header": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "module"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "literal",
    "value": "version"
   },
   {
    "op": "literal",
    "value": "1"
   }
  ]
 },
 "import-line": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "use"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "many",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": ","
      },
      {
       "op": "rule",
       "value": "qualified-name"
      }
     ]
    }
   }
  ]
 },
 "qualified-name": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "many",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "."
      },
      {
       "op": "rule",
       "value": "NAME"
      }
     ]
    }
   }
  ]
 },
 "name-list": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "many",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": ","
      },
      {
       "op": "rule",
       "value": "qualified-name"
      }
     ]
    }
   }
  ]
 },
 "step-name": {
  "op": "rule",
  "value": "STEP_NAME"
 },
 "permission-name": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "step-name"
   },
   {
    "op": "many",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "."
      },
      {
       "op": "rule",
       "value": "step-name"
      }
     ]
    }
   }
  ]
 },
 "natural": {
  "op": "rule",
  "value": "NATURAL"
 },
 "json-string": {
  "op": "rule",
  "value": "JSON_STRING"
 },
 "reference": {
  "op": "alt",
  "nodes": [
   {
    "op": "rule",
    "value": "REFERENCE"
   },
   {
    "op": "rule",
    "value": "basename-reference"
   }
  ]
 },
 "basename-reference": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "REFERENCE_COMPONENT"
   },
   {
    "op": "literal",
    "value": "."
   },
   {
    "op": "rule",
    "value": "REFERENCE_COMPONENT"
   },
   {
    "op": "many",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "."
      },
      {
       "op": "rule",
       "value": "REFERENCE_COMPONENT"
      }
     ]
    }
   }
  ]
 },
 "type": {
  "op": "alt",
  "nodes": [
   {
    "op": "literal",
    "value": "UInt64"
   },
   {
    "op": "literal",
    "value": "Bool"
   },
   {
    "op": "literal",
    "value": "String"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "optional"
     },
     {
      "op": "literal",
      "value": "<"
     },
     {
      "op": "rule",
      "value": "type"
     },
     {
      "op": "literal",
      "value": ">"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "List"
     },
     {
      "op": "literal",
      "value": "<"
     },
     {
      "op": "rule",
      "value": "type"
     },
     {
      "op": "literal",
      "value": ","
     },
     {
      "op": "rule",
      "value": "natural"
     },
     {
      "op": "literal",
      "value": ">"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "literal"
     },
     {
      "op": "rule",
      "value": "json-string"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "outcome"
     },
     {
      "op": "literal",
      "value": "<"
     },
     {
      "op": "rule",
      "value": "type"
     },
     {
      "op": "literal",
      "value": ","
     },
     {
      "op": "rule",
      "value": "type"
     },
     {
      "op": "literal",
      "value": ","
     },
     {
      "op": "rule",
      "value": "natural"
     },
     {
      "op": "literal",
      "value": ">"
     }
    ]
   }
  ]
 },
 "binder": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "type"
   }
  ]
 },
 "parameter": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "input"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "rule",
    "value": "type"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "context": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "context"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "declaration": {
  "op": "alt",
  "nodes": [
   {
    "op": "rule",
    "value": "record-declaration"
   },
   {
    "op": "rule",
    "value": "enum-declaration"
   },
   {
    "op": "rule",
    "value": "rule-declaration"
   },
   {
    "op": "rule",
    "value": "calculation-declaration"
   },
   {
    "op": "rule",
    "value": "mapping-declaration"
   },
   {
    "op": "rule",
    "value": "policy-declaration"
   },
   {
    "op": "rule",
    "value": "machine-declaration"
   },
   {
    "op": "rule",
    "value": "operation-declaration"
   },
   {
    "op": "rule",
    "value": "query-declaration"
   },
   {
    "op": "rule",
    "value": "workflow-declaration"
   },
   {
    "op": "rule",
    "value": "generic-workflow-declaration"
   },
   {
    "op": "rule",
    "value": "interface-declaration"
   },
   {
    "op": "rule",
    "value": "entry-declaration"
   },
   {
    "op": "rule",
    "value": "claim-declaration"
   }
  ]
 },
 "record-declaration": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "alt",
      "nodes": [
       {
        "op": "literal",
        "value": "entity"
       },
       {
        "op": "literal",
        "value": "value-object"
       },
       {
        "op": "literal",
        "value": "event"
       }
      ]
     },
     {
      "op": "rule",
      "value": "NAME"
     },
     {
      "op": "literal",
      "value": ":"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     },
     {
      "op": "rule",
      "value": "INDENT"
     },
     {
      "op": "rule",
      "value": "record-clause"
     },
     {
      "op": "many",
      "node": {
       "op": "rule",
       "value": "record-clause"
      }
     },
     {
      "op": "rule",
      "value": "DEDENT"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "event"
     },
     {
      "op": "rule",
      "value": "NAME"
     },
     {
      "op": "literal",
      "value": "version"
     },
     {
      "op": "rule",
      "value": "natural"
     },
     {
      "op": "literal",
      "value": ":"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     },
     {
      "op": "rule",
      "value": "INDENT"
     },
     {
      "op": "rule",
      "value": "event-clause"
     },
     {
      "op": "rule",
      "value": "event-clause"
     },
     {
      "op": "rule",
      "value": "event-clause"
     },
     {
      "op": "rule",
      "value": "DEDENT"
     }
    ]
   }
  ]
 },
 "event-clause": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "payload"
     },
     {
      "op": "rule",
      "value": "type"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "from"
     },
     {
      "op": "rule",
      "value": "qualified-name"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "delivered-to"
     },
     {
      "op": "rule",
      "value": "qualified-name"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   }
  ]
 },
 "record-clause": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "rule",
      "value": "NAME"
     },
     {
      "op": "rule",
      "value": "type"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "version"
     },
     {
      "op": "rule",
      "value": "natural"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "identity"
     },
     {
      "op": "rule",
      "value": "name-list"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "unique"
     },
     {
      "op": "rule",
      "value": "name-list"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "immutable"
     },
     {
      "op": "alt",
      "nodes": [
       {
        "op": "literal",
        "value": "all"
       },
       {
        "op": "rule",
        "value": "name-list"
       }
      ]
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "invariant"
     },
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "rule",
    "value": "refinement-clause"
   }
  ]
 },
 "refinement-clause": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "carrier String"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "representation transparent-scalar"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "unicode well-formed-scalars"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "utf8-bytes"
     },
     {
      "op": "rule",
      "value": "natural"
     },
     {
      "op": "literal",
      "value": ".."
     },
     {
      "op": "rule",
      "value": "natural"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "unicode-scalars"
     },
     {
      "op": "rule",
      "value": "natural"
     },
     {
      "op": "literal",
      "value": ".."
     },
     {
      "op": "rule",
      "value": "natural"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "pattern"
     },
     {
      "op": "rule",
      "value": "json-string"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "equality exact-scalar-sequence"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "normalization none"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "case-fold none"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "trim none"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   }
  ]
 },
 "enum-declaration": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "enum"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "rule",
    "value": "enum-item"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "enum-item"
    }
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "enum-item": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "value"
     },
     {
      "op": "rule",
      "value": "NAME"
     },
     {
      "op": "maybe",
      "node": {
       "op": "seq",
       "nodes": [
        {
         "op": "literal",
         "value": "wire"
        },
        {
         "op": "rule",
         "value": "json-string"
        }
       ]
      }
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "variant"
     },
     {
      "op": "rule",
      "value": "NAME"
     },
     {
      "op": "many",
      "node": {
       "op": "seq",
       "nodes": [
        {
         "op": "rule",
         "value": "NAME"
        },
        {
         "op": "rule",
         "value": "type"
        }
       ]
      }
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   }
  ]
 },
 "expression": {
  "op": "rule",
  "value": "implication"
 },
 "implication": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "disjunction"
   },
   {
    "op": "maybe",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "implies"
      },
      {
       "op": "rule",
       "value": "implication"
      }
     ]
    }
   }
  ]
 },
 "disjunction": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "conjunction"
   },
   {
    "op": "many",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "or"
      },
      {
       "op": "rule",
       "value": "conjunction"
      }
     ]
    }
   }
  ]
 },
 "conjunction": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "comparison"
   },
   {
    "op": "many",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "and"
      },
      {
       "op": "rule",
       "value": "comparison"
      }
     ]
    }
   }
  ]
 },
 "comparison": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "sum"
   },
   {
    "op": "maybe",
    "node": {
     "op": "alt",
     "nodes": [
      {
       "op": "seq",
       "nodes": [
        {
         "op": "alt",
         "nodes": [
          {
           "op": "literal",
           "value": "=="
          },
          {
           "op": "literal",
           "value": "!="
          },
          {
           "op": "literal",
           "value": "<"
          },
          {
           "op": "literal",
           "value": "<="
          },
          {
           "op": "literal",
           "value": ">"
          },
          {
           "op": "literal",
           "value": ">="
          }
         ]
        },
        {
         "op": "rule",
         "value": "sum"
        }
       ]
      },
      {
       "op": "seq",
       "nodes": [
        {
         "op": "literal",
         "value": "in"
        },
        {
         "op": "rule",
         "value": "list-expression"
        }
       ]
      }
     ]
    }
   }
  ]
 },
 "sum": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "product"
   },
   {
    "op": "many",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "alt",
       "nodes": [
        {
         "op": "literal",
         "value": "+"
        },
        {
         "op": "literal",
         "value": "-"
        }
       ]
      },
      {
       "op": "rule",
       "value": "product"
      }
     ]
    }
   }
  ]
 },
 "product": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "unary"
   },
   {
    "op": "many",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "alt",
       "nodes": [
        {
         "op": "literal",
         "value": "*"
        },
        {
         "op": "literal",
         "value": "/"
        }
       ]
      },
      {
       "op": "rule",
       "value": "unary"
      }
     ]
    }
   }
  ]
 },
 "unary": {
  "op": "seq",
  "nodes": [
   {
    "op": "maybe",
    "node": {
     "op": "literal",
     "value": "not"
    }
   },
   {
    "op": "rule",
    "value": "postfix"
   }
  ]
 },
 "postfix": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "primary"
   },
   {
    "op": "many",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "."
      },
      {
       "op": "rule",
       "value": "NAME"
      }
     ]
    }
   }
  ]
 },
 "primary": {
  "op": "alt",
  "nodes": [
   {
    "op": "rule",
    "value": "natural"
   },
   {
    "op": "literal",
    "value": "true"
   },
   {
    "op": "literal",
    "value": "false"
   },
   {
    "op": "rule",
    "value": "json-string"
   },
   {
    "op": "literal",
    "value": "none"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "list-expression"
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "("
     },
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "literal",
      "value": ")"
     }
    ]
   },
   {
    "op": "rule",
    "value": "invocation"
   },
   {
    "op": "rule",
    "value": "map-expression"
   },
   {
    "op": "rule",
    "value": "filter-expression"
   },
   {
    "op": "rule",
    "value": "fold-expression"
   },
   {
    "op": "rule",
    "value": "indexed-fold-expression"
   },
   {
    "op": "rule",
    "value": "repeat-expression"
   },
   {
    "op": "rule",
    "value": "condition-loop-expression"
   },
   {
    "op": "rule",
    "value": "range-expression"
   },
   {
    "op": "rule",
    "value": "sort-expression"
   },
   {
    "op": "rule",
    "value": "optional-match"
   },
   {
    "op": "rule",
    "value": "inline-match"
   }
  ]
 },
 "list-expression": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "["
   },
   {
    "op": "maybe",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "rule",
       "value": "expression"
      },
      {
       "op": "many",
       "node": {
        "op": "seq",
        "nodes": [
         {
          "op": "literal",
          "value": ","
         },
         {
          "op": "rule",
          "value": "expression"
         }
        ]
       }
      }
     ]
    }
   },
   {
    "op": "literal",
    "value": "]"
   }
  ]
 },
 "invocation": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "callable"
   },
   {
    "op": "literal",
    "value": "("
   },
   {
    "op": "maybe",
    "node": {
     "op": "rule",
     "value": "arguments"
    }
   },
   {
    "op": "literal",
    "value": ")"
   }
  ]
 },
 "callable": {
  "op": "alt",
  "nodes": [
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "intrinsic"
   }
  ]
 },
 "intrinsic": {
  "op": "alt",
  "nodes": [
   {
    "op": "literal",
    "value": "checked-add"
   },
   {
    "op": "literal",
    "value": "checked-subtract"
   },
   {
    "op": "literal",
    "value": "checked-multiply"
   },
   {
    "op": "literal",
    "value": "checked-divide"
   },
   {
    "op": "literal",
    "value": "some"
   },
   {
    "op": "literal",
    "value": "present"
   },
   {
    "op": "literal",
    "value": "absent"
   },
   {
    "op": "literal",
    "value": "require-some"
   },
   {
    "op": "literal",
    "value": "require-variant"
   },
   {
    "op": "literal",
    "value": "length"
   },
   {
    "op": "literal",
    "value": "tag"
   },
   {
    "op": "literal",
    "value": "all-unique-exact"
   },
   {
    "op": "literal",
    "value": "length-utf8"
   },
   {
    "op": "literal",
    "value": "length-scalars"
   }
  ]
 },
 "arguments": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "many",
      "node": {
       "op": "seq",
       "nodes": [
        {
         "op": "literal",
         "value": ","
        },
        {
         "op": "rule",
         "value": "expression"
        }
       ]
      }
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "rule",
      "value": "named-argument"
     },
     {
      "op": "many",
      "node": {
       "op": "seq",
       "nodes": [
        {
         "op": "literal",
         "value": ","
        },
        {
         "op": "rule",
         "value": "named-argument"
        }
       ]
      }
     }
    ]
   }
  ]
 },
 "named-argument": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": "="
   },
   {
    "op": "rule",
    "value": "expression"
   }
  ]
 },
 "map-expression": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "map"
   },
   {
    "op": "literal",
    "value": "("
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "rule",
    "value": "binder"
   },
   {
    "op": "literal",
    "value": "=>"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ")"
   }
  ]
 },
 "filter-expression": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "filter"
   },
   {
    "op": "literal",
    "value": "("
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "rule",
    "value": "binder"
   },
   {
    "op": "literal",
    "value": "=>"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ")"
   }
  ]
 },
 "fold-expression": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "fold"
   },
   {
    "op": "literal",
    "value": "("
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "rule",
    "value": "binder"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "rule",
    "value": "binder"
   },
   {
    "op": "literal",
    "value": "=>"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ")"
   }
  ]
 },
 "indexed-fold-expression": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "indexed-fold"
   },
   {
    "op": "literal",
    "value": "("
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "rule",
    "value": "binder"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "rule",
    "value": "binder"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "rule",
    "value": "binder"
   },
   {
    "op": "literal",
    "value": "=>"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ")"
   }
  ]
 },
 "repeat-expression": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "repeat"
   },
   {
    "op": "literal",
    "value": "("
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "literal",
    "value": "max"
   },
   {
    "op": "rule",
    "value": "natural"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "rule",
    "value": "binder"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "rule",
    "value": "binder"
   },
   {
    "op": "literal",
    "value": "=>"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ")"
   }
  ]
 },
 "condition-loop-expression": {
  "op": "seq",
  "nodes": [
   {
    "op": "alt",
    "nodes": [
     {
      "op": "literal",
      "value": "while-bounded"
     },
     {
      "op": "literal",
      "value": "until-bounded"
     }
    ]
   },
   {
    "op": "literal",
    "value": "("
   },
   {
    "op": "literal",
    "value": "max"
   },
   {
    "op": "rule",
    "value": "natural"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "rule",
    "value": "binder"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": "=>"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ")"
   }
  ]
 },
 "range-expression": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "range"
   },
   {
    "op": "literal",
    "value": "("
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ","
   },
   {
    "op": "literal",
    "value": "max"
   },
   {
    "op": "rule",
    "value": "natural"
   },
   {
    "op": "literal",
    "value": ")"
   }
  ]
 },
 "sort-expression": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "sort"
     },
     {
      "op": "literal",
      "value": "("
     },
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "literal",
      "value": ","
     },
     {
      "op": "rule",
      "value": "NAME"
     },
     {
      "op": "rule",
      "value": "direction"
     },
     {
      "op": "rule",
      "value": "sort-mode"
     },
     {
      "op": "literal",
      "value": ")"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "sort"
     },
     {
      "op": "literal",
      "value": "("
     },
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "literal",
      "value": ","
     },
     {
      "op": "rule",
      "value": "binder"
     },
     {
      "op": "literal",
      "value": "=>"
     },
     {
      "op": "literal",
      "value": "["
     },
     {
      "op": "rule",
      "value": "sort-key"
     },
     {
      "op": "many",
      "node": {
       "op": "seq",
       "nodes": [
        {
         "op": "literal",
         "value": ","
        },
        {
         "op": "rule",
         "value": "sort-key"
        }
       ]
      }
     },
     {
      "op": "literal",
      "value": "]"
     },
     {
      "op": "literal",
      "value": ")"
     }
    ]
   }
  ]
 },
 "sort-key": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "rule",
    "value": "direction"
   },
   {
    "op": "rule",
    "value": "sort-mode"
   }
  ]
 },
 "direction": {
  "op": "alt",
  "nodes": [
   {
    "op": "literal",
    "value": "ascending"
   },
   {
    "op": "literal",
    "value": "descending"
   }
  ]
 },
 "sort-mode": {
  "op": "alt",
  "nodes": [
   {
    "op": "literal",
    "value": "numeric"
   },
   {
    "op": "literal",
    "value": "lexical"
   },
   {
    "op": "literal",
    "value": "natural"
   },
   {
    "op": "literal",
    "value": "binary-utf8"
   }
  ]
 },
 "optional-match": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "match"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": "some"
   },
   {
    "op": "literal",
    "value": "("
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": ")"
   },
   {
    "op": "literal",
    "value": "=>"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": "else"
   },
   {
    "op": "rule",
    "value": "expression"
   }
  ]
 },
 "inline-match": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "match"
   },
   {
    "op": "rule",
    "value": "postfix"
   },
   {
    "op": "rule",
    "value": "pattern-list"
   },
   {
    "op": "literal",
    "value": "=>"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": "else"
   },
   {
    "op": "rule",
    "value": "expression"
   }
  ]
 },
 "pattern-list": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "pattern"
   },
   {
    "op": "many",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": ","
      },
      {
       "op": "rule",
       "value": "pattern"
      }
     ]
    }
   }
  ]
 },
 "pattern": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "rule",
      "value": "qualified-name"
     },
     {
      "op": "maybe",
      "node": {
       "op": "seq",
       "nodes": [
        {
         "op": "literal",
         "value": "("
        },
        {
         "op": "rule",
         "value": "NAME"
        },
        {
         "op": "literal",
         "value": ")"
        }
       ]
      }
     }
    ]
   },
   {
    "op": "literal",
    "value": "true"
   },
   {
    "op": "literal",
    "value": "false"
   }
  ]
 },
 "expression-value": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "match"
     },
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "literal",
      "value": ":"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     },
     {
      "op": "rule",
      "value": "INDENT"
     },
     {
      "op": "rule",
      "value": "match-case"
     },
     {
      "op": "many",
      "node": {
       "op": "rule",
       "value": "match-case"
      }
     },
     {
      "op": "rule",
      "value": "DEDENT"
     }
    ]
   }
  ]
 },
 "match-case": {
  "op": "seq",
  "nodes": [
   {
    "op": "alt",
    "nodes": [
     {
      "op": "rule",
      "value": "pattern-list"
     },
     {
      "op": "literal",
      "value": "otherwise"
     }
    ]
   },
   {
    "op": "literal",
    "value": "=>"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "rule-declaration": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "rule"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "parameter"
    }
   },
   {
    "op": "literal",
    "value": "expression"
   },
   {
    "op": "rule",
    "value": "expression-value"
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "calculation-declaration": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "calculation"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "literal",
    "value": "pure"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "parameter"
    }
   },
   {
    "op": "literal",
    "value": "result"
   },
   {
    "op": "rule",
    "value": "type"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "maybe",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "rounding"
      },
      {
       "op": "alt",
       "nodes": [
        {
         "op": "literal",
         "value": "floor"
        },
        {
         "op": "literal",
         "value": "ceil"
        },
        {
         "op": "literal",
         "value": "reject"
        }
       ]
      },
      {
       "op": "rule",
       "value": "NEWLINE"
      }
     ]
    }
   },
   {
    "op": "literal",
    "value": "expression"
   },
   {
    "op": "rule",
    "value": "expression-value"
   },
   {
    "op": "maybe",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "on-evaluation-error"
      },
      {
       "op": "rule",
       "value": "failure-action"
      },
      {
       "op": "rule",
       "value": "NEWLINE"
      }
     ]
    }
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "mapping-declaration": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "mapping"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "parameter"
    }
   },
   {
    "op": "literal",
    "value": "target"
   },
   {
    "op": "rule",
    "value": "type"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "total true"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "many",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "requires"
      },
      {
       "op": "rule",
       "value": "expression"
      },
      {
       "op": "rule",
       "value": "NEWLINE"
      }
     ]
    }
   },
   {
    "op": "rule",
    "value": "mapping-body"
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "mapping-body": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "maybe",
      "node": {
       "op": "seq",
       "nodes": [
        {
         "op": "literal",
         "value": "preserve"
        },
        {
         "op": "rule",
         "value": "name-list"
        },
        {
         "op": "rule",
         "value": "NEWLINE"
        }
       ]
      }
     },
     {
      "op": "rule",
      "value": "field-binding"
     },
     {
      "op": "many",
      "node": {
       "op": "rule",
       "value": "field-binding"
      }
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "ordered-cases:"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     },
     {
      "op": "rule",
      "value": "INDENT"
     },
     {
      "op": "rule",
      "value": "ordered-case"
     },
     {
      "op": "many",
      "node": {
       "op": "rule",
       "value": "ordered-case"
      }
     },
     {
      "op": "rule",
      "value": "DEDENT"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "expression"
     },
     {
      "op": "rule",
      "value": "expression-value"
     }
    ]
   }
  ]
 },
 "field-binding": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "field"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": "<-"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "ordered-case": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "rule",
      "value": "step-name"
     },
     {
      "op": "literal",
      "value": "when"
     },
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "literal",
      "value": "->"
     },
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "rule",
      "value": "step-name"
     },
     {
      "op": "literal",
      "value": "otherwise"
     },
     {
      "op": "literal",
      "value": "->"
     },
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   }
  ]
 },
 "policy-declaration": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "policy"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "parameter"
    }
   },
   {
    "op": "literal",
    "value": "result"
   },
   {
    "op": "rule",
    "value": "type"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "ordered-cases:"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "rule",
    "value": "policy-case"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "policy-case"
    }
   },
   {
    "op": "literal",
    "value": "otherwise"
   },
   {
    "op": "literal",
    "value": "->"
   },
   {
    "op": "rule",
    "value": "invocation"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "DEDENT"
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "policy-case": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "step-name"
   },
   {
    "op": "literal",
    "value": "when"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": "->"
   },
   {
    "op": "rule",
    "value": "invocation"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "machine-declaration": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "state-machine"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "literal",
    "value": "state"
   },
   {
    "op": "rule",
    "value": "type"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "input"
   },
   {
    "op": "rule",
    "value": "type"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "initial"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "maybe",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "terminal"
      },
      {
       "op": "rule",
       "value": "name-list"
      },
      {
       "op": "rule",
       "value": "NEWLINE"
      }
     ]
    }
   },
   {
    "op": "rule",
    "value": "machine-transition"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "machine-transition"
    }
   },
   {
    "op": "literal",
    "value": "otherwise"
   },
   {
    "op": "alt",
    "nodes": [
     {
      "op": "literal",
      "value": "stay"
     },
     {
      "op": "seq",
      "nodes": [
       {
        "op": "literal",
        "value": "reject"
       },
       {
        "op": "rule",
        "value": "step-name"
       }
      ]
     }
    ]
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "machine-transition": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "transition"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "maybe",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "when"
      },
      {
       "op": "rule",
       "value": "expression"
      }
     ]
    }
   },
   {
    "op": "literal",
    "value": "->"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "operation-declaration": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "operation"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "many",
    "node": {
     "op": "alt",
     "nodes": [
      {
       "op": "rule",
       "value": "parameter"
      },
      {
       "op": "rule",
       "value": "context"
      }
     ]
    }
   },
   {
    "op": "literal",
    "value": "output"
   },
   {
    "op": "rule",
    "value": "type"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "alt",
    "nodes": [
     {
      "op": "rule",
      "value": "operation-statements"
     },
     {
      "op": "rule",
      "value": "native-capture-body"
     },
     {
      "op": "rule",
      "value": "replay-protocol"
     }
    ]
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "operation-statements": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "operation-statement"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "operation-statement"
    }
   }
  ]
 },
 "operation-statement": {
  "op": "alt",
  "nodes": [
   {
    "op": "rule",
    "value": "enforce-statement"
   },
   {
    "op": "rule",
    "value": "preflight"
   },
   {
    "op": "rule",
    "value": "guard"
   },
   {
    "op": "rule",
    "value": "let-statement"
   },
   {
    "op": "rule",
    "value": "read-statement"
   },
   {
    "op": "rule",
    "value": "call-statement"
   },
   {
    "op": "rule",
    "value": "condition-statement"
   },
   {
    "op": "rule",
    "value": "present-statement"
   },
   {
    "op": "rule",
    "value": "when-statement"
   },
   {
    "op": "rule",
    "value": "read-set"
   },
   {
    "op": "rule",
    "value": "transaction"
   },
   {
    "op": "rule",
    "value": "return-statement"
   },
   {
    "op": "rule",
    "value": "acknowledgement"
   }
  ]
 },
 "enforce-statement": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "enforce"
   },
   {
    "op": "rule",
    "value": "invocation"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "preflight": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "preflight contract"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "guard": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "requires"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "maybe",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "on-false"
      },
      {
       "op": "rule",
       "value": "action"
      }
     ]
    }
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "let-statement": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "let"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": "="
   },
   {
    "op": "alt",
    "nodes": [
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "seq",
      "nodes": [
       {
        "op": "literal",
        "value": "count"
       },
       {
        "op": "rule",
        "value": "qualified-name"
       }
      ]
     }
    ]
   },
   {
    "op": "maybe",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "on-error"
      },
      {
       "op": "rule",
       "value": "action"
      }
     ]
    }
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "read-statement": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "read"
     },
     {
      "op": "rule",
      "value": "NAME"
     },
     {
      "op": "rule",
      "value": "qualified-name"
     },
     {
      "op": "literal",
      "value": "by"
     },
     {
      "op": "rule",
      "value": "bindings"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     },
     {
      "op": "maybe",
      "node": {
       "op": "alt",
       "nodes": [
        {
         "op": "seq",
         "nodes": [
          {
           "op": "rule",
           "value": "INDENT"
          },
          {
           "op": "rule",
           "value": "read-handler"
          },
          {
           "op": "many",
           "node": {
            "op": "rule",
            "value": "read-handler"
           }
          },
          {
           "op": "rule",
           "value": "DEDENT"
          }
         ]
        },
        {
         "op": "seq",
         "nodes": [
          {
           "op": "rule",
           "value": "read-handler"
          },
          {
           "op": "many",
           "node": {
            "op": "rule",
            "value": "read-handler"
           }
          }
         ]
        }
       ]
      }
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "read"
     },
     {
      "op": "rule",
      "value": "NAME"
     },
     {
      "op": "literal",
      "value": "from"
     },
     {
      "op": "rule",
      "value": "invocation"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     },
     {
      "op": "maybe",
      "node": {
       "op": "alt",
       "nodes": [
        {
         "op": "seq",
         "nodes": [
          {
           "op": "rule",
           "value": "INDENT"
          },
          {
           "op": "rule",
           "value": "read-handler"
          },
          {
           "op": "many",
           "node": {
            "op": "rule",
            "value": "read-handler"
           }
          },
          {
           "op": "rule",
           "value": "DEDENT"
          }
         ]
        },
        {
         "op": "seq",
         "nodes": [
          {
           "op": "rule",
           "value": "read-handler"
          },
          {
           "op": "many",
           "node": {
            "op": "rule",
            "value": "read-handler"
           }
          }
         ]
        }
       ]
      }
     }
    ]
   }
  ]
 },
 "bindings": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": "="
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "many",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": ","
      },
      {
       "op": "rule",
       "value": "NAME"
      },
      {
       "op": "literal",
       "value": "="
      },
      {
       "op": "rule",
       "value": "expression"
      }
     ]
    }
   }
  ]
 },
 "read-handler": {
  "op": "seq",
  "nodes": [
   {
    "op": "alt",
    "nodes": [
     {
      "op": "literal",
      "value": "on-missing"
     },
     {
      "op": "literal",
      "value": "on-unavailable"
     },
     {
      "op": "literal",
      "value": "on-malformed"
     }
    ]
   },
   {
    "op": "rule",
    "value": "action"
   },
   {
    "op": "maybe",
    "node": {
     "op": "literal",
     "value": "; do-not-ack"
    }
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "call-statement": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "call"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "rule",
    "value": "invocation"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "maybe",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "rule",
       "value": "INDENT"
      },
      {
       "op": "rule",
       "value": "call-handler"
      },
      {
       "op": "many",
       "node": {
        "op": "rule",
        "value": "call-handler"
       }
      },
      {
       "op": "rule",
       "value": "DEDENT"
      }
     ]
    }
   }
  ]
 },
 "call-handler": {
  "op": "seq",
  "nodes": [
   {
    "op": "alt",
    "nodes": [
     {
      "op": "literal",
      "value": "on-transport-error"
     },
     {
      "op": "literal",
      "value": "on-invalid-response"
     },
     {
      "op": "literal",
      "value": "on-error"
     }
    ]
   },
   {
    "op": "rule",
    "value": "action"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "condition-statement": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "on"
   },
   {
    "op": "alt",
    "nodes": [
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "rule",
      "value": "pattern-list"
     },
     {
      "op": "seq",
      "nodes": [
       {
        "op": "rule",
        "value": "postfix"
       },
       {
        "op": "rule",
        "value": "pattern-list"
       }
      ]
     }
    ]
   },
   {
    "op": "maybe",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "when"
      },
      {
       "op": "rule",
       "value": "expression"
      }
     ]
    }
   },
   {
    "op": "rule",
    "value": "action"
   },
   {
    "op": "maybe",
    "node": {
     "op": "rule",
     "value": "before-order"
    }
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "present-statement": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "on-present"
   },
   {
    "op": "maybe",
    "node": {
     "op": "rule",
     "value": "postfix"
    }
   },
   {
    "op": "alt",
    "nodes": [
     {
      "op": "seq",
      "nodes": [
       {
        "op": "literal",
        "value": "require"
       },
       {
        "op": "rule",
        "value": "expression"
       },
       {
        "op": "literal",
        "value": "else"
       },
       {
        "op": "rule",
        "value": "action"
       },
       {
        "op": "rule",
        "value": "NEWLINE"
       }
      ]
     },
     {
      "op": "seq",
      "nodes": [
       {
        "op": "rule",
        "value": "action"
       },
       {
        "op": "maybe",
        "node": {
         "op": "rule",
         "value": "before-order"
        }
       },
       {
        "op": "rule",
        "value": "NEWLINE"
       }
      ]
     },
     {
      "op": "rule",
      "value": "transaction"
     }
    ]
   }
  ]
 },
 "when-statement": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "when"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "rule",
    "value": "operation-statements"
   },
   {
    "op": "rule",
    "value": "DEDENT"
   },
   {
    "op": "maybe",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "otherwise:"
      },
      {
       "op": "rule",
       "value": "NEWLINE"
      },
      {
       "op": "rule",
       "value": "INDENT"
      },
      {
       "op": "rule",
       "value": "operation-statements"
      },
      {
       "op": "rule",
       "value": "DEDENT"
      }
     ]
    }
   }
  ]
 },
 "before-order": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "before"
   },
   {
    "op": "rule",
    "value": "step-name"
   },
   {
    "op": "many",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": ","
      },
      {
       "op": "rule",
       "value": "step-name"
      }
     ]
    }
   }
  ]
 },
 "return-statement": {
  "op": "seq",
  "nodes": [
   {
    "op": "alt",
    "nodes": [
     {
      "op": "literal",
      "value": "return"
     },
     {
      "op": "literal",
      "value": "returns"
     }
    ]
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "failure-action": {
  "op": "seq",
  "nodes": [
   {
    "op": "alt",
    "nodes": [
     {
      "op": "literal",
      "value": "reject"
     },
     {
      "op": "literal",
      "value": "fail"
     }
    ]
   },
   {
    "op": "rule",
    "value": "step-name"
   }
  ]
 },
 "action": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "return"
     },
     {
      "op": "rule",
      "value": "expression"
     }
    ]
   },
   {
    "op": "rule",
    "value": "failure-action"
   }
  ]
 },
 "read-set": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "read-set"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "literal",
    "value": "for"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": "in"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "rule",
    "value": "operation-statements"
   },
   {
    "op": "literal",
    "value": "bind"
   },
   {
    "op": "rule",
    "value": "collected-bindings"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "DEDENT"
   },
   {
    "op": "literal",
    "value": "validate-all-before-writes"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "collected-bindings": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "collected-binding"
   },
   {
    "op": "many",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": ","
      },
      {
       "op": "rule",
       "value": "collected-binding"
      }
     ]
    }
   }
  ]
 },
 "collected-binding": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "maybe",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "="
      },
      {
       "op": "rule",
       "value": "expression"
      }
     ]
    }
   }
  ]
 },
 "transaction": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "transaction"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "literal",
    "value": "atomic-participants"
   },
   {
    "op": "rule",
    "value": "name-list"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "transaction-statement"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "transaction-statement"
    }
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "transaction-statement": {
  "op": "alt",
  "nodes": [
   {
    "op": "rule",
    "value": "enforce-statement"
   },
   {
    "op": "rule",
    "value": "mutation"
   },
   {
    "op": "rule",
    "value": "emit-statement"
   },
   {
    "op": "rule",
    "value": "transaction-loop"
   },
   {
    "op": "rule",
    "value": "transaction-condition"
   },
   {
    "op": "rule",
    "value": "let-statement"
   },
   {
    "op": "rule",
    "value": "transaction-guard"
   },
   {
    "op": "rule",
    "value": "transaction-handler"
   }
  ]
 },
 "transaction-guard": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "require-absent"
     },
     {
      "op": "rule",
      "value": "qualified-name"
     },
     {
      "op": "rule",
      "value": "bindings"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "require-retained-record-capacity"
     },
     {
      "op": "rule",
      "value": "natural"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "rule",
    "value": "guard"
   }
  ]
 },
 "mutation": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "create"
     },
     {
      "op": "rule",
      "value": "NAME"
     },
     {
      "op": "rule",
      "value": "qualified-name"
     },
     {
      "op": "literal",
      "value": ":"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     },
     {
      "op": "rule",
      "value": "INDENT"
     },
     {
      "op": "rule",
      "value": "assignments"
     },
     {
      "op": "rule",
      "value": "DEDENT"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "create"
     },
     {
      "op": "rule",
      "value": "NAME"
     },
     {
      "op": "rule",
      "value": "qualified-name"
     },
     {
      "op": "literal",
      "value": "from"
     },
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "update"
     },
     {
      "op": "rule",
      "value": "NAME"
     },
     {
      "op": "rule",
      "value": "qualified-name"
     },
     {
      "op": "literal",
      "value": "by"
     },
     {
      "op": "rule",
      "value": "bindings"
     },
     {
      "op": "literal",
      "value": "expected-version"
     },
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "literal",
      "value": ":"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     },
     {
      "op": "rule",
      "value": "INDENT"
     },
     {
      "op": "rule",
      "value": "assignments"
     },
     {
      "op": "rule",
      "value": "DEDENT"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "update"
     },
     {
      "op": "rule",
      "value": "NAME"
     },
     {
      "op": "rule",
      "value": "qualified-name"
     },
     {
      "op": "literal",
      "value": "from"
     },
     {
      "op": "rule",
      "value": "NAME"
     },
     {
      "op": "literal",
      "value": ":"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     },
     {
      "op": "rule",
      "value": "INDENT"
     },
     {
      "op": "rule",
      "value": "assignments"
     },
     {
      "op": "rule",
      "value": "DEDENT"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "record-event"
     },
     {
      "op": "rule",
      "value": "NAME"
     },
     {
      "op": "rule",
      "value": "qualified-name"
     },
     {
      "op": "literal",
      "value": ":"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     },
     {
      "op": "rule",
      "value": "INDENT"
     },
     {
      "op": "rule",
      "value": "assignments"
     },
     {
      "op": "rule",
      "value": "DEDENT"
     }
    ]
   }
  ]
 },
 "emit-statement": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "emit"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "literal",
    "value": "payload"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "assignments": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": "<-"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "many",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "rule",
       "value": "NAME"
      },
      {
       "op": "literal",
       "value": "<-"
      },
      {
       "op": "rule",
       "value": "expression"
      },
      {
       "op": "rule",
       "value": "NEWLINE"
      }
     ]
    }
   }
  ]
 },
 "transaction-loop": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "for"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": "in"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "rule",
    "value": "transaction-statement"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "transaction-statement"
    }
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "transaction-condition": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "when"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "rule",
    "value": "transaction-statement"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "transaction-statement"
    }
   },
   {
    "op": "rule",
    "value": "DEDENT"
   },
   {
    "op": "maybe",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "otherwise:"
      },
      {
       "op": "rule",
       "value": "NEWLINE"
      },
      {
       "op": "rule",
       "value": "INDENT"
      },
      {
       "op": "rule",
       "value": "transaction-statement"
      },
      {
       "op": "many",
       "node": {
        "op": "rule",
        "value": "transaction-statement"
       }
      },
      {
       "op": "rule",
       "value": "DEDENT"
      }
     ]
    }
   }
  ]
 },
 "transaction-handler": {
  "op": "seq",
  "nodes": [
   {
    "op": "alt",
    "nodes": [
     {
      "op": "literal",
      "value": "on-version-conflict"
     },
     {
      "op": "literal",
      "value": "on-unique-conflict"
     },
     {
      "op": "literal",
      "value": "on-proven-rollback"
     },
     {
      "op": "literal",
      "value": "on-unknown-commit"
     },
     {
      "op": "literal",
      "value": "on-arithmetic-error"
     },
     {
      "op": "literal",
      "value": "on-invariant-error"
     }
    ]
   },
   {
    "op": "rule",
    "value": "transaction-recovery"
   },
   {
    "op": "maybe",
    "node": {
     "op": "literal",
     "value": "retaining original scope, fingerprint"
    }
   },
   {
    "op": "maybe",
    "node": {
     "op": "literal",
     "value": "; do-not-ack"
    }
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "transaction-recovery": {
  "op": "alt",
  "nodes": [
   {
    "op": "rule",
    "value": "action"
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "rollback-all then"
     },
     {
      "op": "rule",
      "value": "action"
     }
    ]
   },
   {
    "op": "literal",
    "value": "resolve original replay-record; never create second order"
   },
   {
    "op": "literal",
    "value": "reread original inbox"
   },
   {
    "op": "literal",
    "value": "rollback-all then reread original inbox-or-shipment"
   }
  ]
 },
 "acknowledgement": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "acknowledge after committed"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "literal",
    "value": "receipt"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "query-declaration": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "query"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "many",
    "node": {
     "op": "alt",
     "nodes": [
      {
       "op": "rule",
       "value": "parameter"
      },
      {
       "op": "rule",
       "value": "context"
      }
     ]
    }
   },
   {
    "op": "alt",
    "nodes": [
     {
      "op": "rule",
      "value": "local-query"
     },
     {
      "op": "rule",
      "value": "delegated-query"
     },
     {
      "op": "rule",
      "value": "native-inspect-body"
     }
    ]
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "local-query": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "source"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "many",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "join"
      },
      {
       "op": "rule",
       "value": "NAME"
      },
      {
       "op": "rule",
       "value": "qualified-name"
      },
      {
       "op": "literal",
       "value": "on"
      },
      {
       "op": "rule",
       "value": "expression"
      }
     ]
    }
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "output"
   },
   {
    "op": "rule",
    "value": "type"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "where"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "query-clause"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "query-clause"
    }
   }
  ]
 },
 "query-clause": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "project"
     },
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "require"
     },
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "literal",
      "value": "else"
     },
     {
      "op": "rule",
      "value": "action"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "rule",
    "value": "read-handler"
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "effects none"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   }
  ]
 },
 "delegated-query": {
  "op": "seq",
  "nodes": [
   {
    "op": "alt",
    "nodes": [
     {
      "op": "seq",
      "nodes": [
       {
        "op": "literal",
        "value": "output"
       },
       {
        "op": "rule",
        "value": "type"
       },
       {
        "op": "rule",
        "value": "NEWLINE"
       },
       {
        "op": "literal",
        "value": "delegates"
       },
       {
        "op": "rule",
        "value": "invocation"
       },
       {
        "op": "rule",
        "value": "NEWLINE"
       }
      ]
     },
     {
      "op": "seq",
      "nodes": [
       {
        "op": "literal",
        "value": "delegates"
       },
       {
        "op": "rule",
        "value": "invocation"
       },
       {
        "op": "rule",
        "value": "NEWLINE"
       },
       {
        "op": "literal",
        "value": "output"
       },
       {
        "op": "rule",
        "value": "type"
       },
       {
        "op": "rule",
        "value": "NEWLINE"
       }
      ]
     }
    ]
   },
   {
    "op": "maybe",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "effects none"
      },
      {
       "op": "rule",
       "value": "NEWLINE"
      }
     ]
    }
   }
  ]
 },
 "entry-declaration": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "entry"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "literal",
    "value": "invokes"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "interaction"
   },
   {
    "op": "alt",
    "nodes": [
     {
      "op": "literal",
      "value": "request-response"
     },
     {
      "op": "seq",
      "nodes": [
       {
        "op": "literal",
        "value": "event"
       },
       {
        "op": "maybe",
        "node": {
         "op": "rule",
         "value": "qualified-name"
        }
       }
      ]
     }
    ]
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "maybe",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "bind"
      },
      {
       "op": "rule",
       "value": "NAME"
      },
      {
       "op": "literal",
       "value": "<-"
      },
      {
       "op": "rule",
       "value": "expression"
      },
      {
       "op": "rule",
       "value": "NEWLINE"
      }
     ]
    }
   },
   {
    "op": "literal",
    "value": "access:"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "rule",
    "value": "access-clause"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "access-clause"
    }
   },
   {
    "op": "rule",
    "value": "DEDENT"
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "access-clause": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "authenticated"
     },
     {
      "op": "alt",
      "nodes": [
       {
        "op": "literal",
        "value": "customer"
       },
       {
        "op": "literal",
        "value": "service"
       },
       {
        "op": "literal",
        "value": "operator"
       },
       {
        "op": "literal",
        "value": "relay"
       }
      ]
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "permission"
     },
     {
      "op": "rule",
      "value": "permission-name"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "alt",
      "nodes": [
       {
        "op": "literal",
        "value": "auth-resource"
       },
       {
        "op": "literal",
        "value": "auth-scope"
       },
       {
        "op": "literal",
        "value": "caller"
       },
       {
        "op": "literal",
        "value": "producer"
       }
      ]
     },
     {
      "op": "rule",
      "value": "step-name"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "auth-action"
     },
     {
      "op": "rule",
      "value": "permission-name"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "auth-route"
     },
     {
      "op": "rule",
      "value": "reference"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "context"
     },
     {
      "op": "rule",
      "value": "qualified-name"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "native-requires"
     },
     {
      "op": "rule",
      "value": "reference"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "current-action before replay-and-effects"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "resource-binding"
     },
     {
      "op": "rule",
      "value": "NAME"
     },
     {
      "op": "rule",
      "value": "qualified-name"
     },
     {
      "op": "literal",
      "value": "from"
     },
     {
      "op": "rule",
      "value": "reference"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "resource-condition"
     },
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "on-resource-false reject forbidden before effects"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "on-resource-missing-or-false missing resource-not-found before projection"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "principal-from registered authenticated subject, never request fields"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "worker-from original registered local lifecycle owner"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "invocation-decision fresh and separate from worker lifetime capability"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "occurrence-from original registered event ingress"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "acknowledge after committed inbox-and-result"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   }
  ]
 },
 "workflow-declaration": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "workflow"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "literal",
    "value": "owner"
   },
   {
    "op": "rule",
    "value": "step-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "scope cross-service"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "many",
    "node": {
     "op": "alt",
     "nodes": [
      {
       "op": "rule",
       "value": "parameter"
      },
      {
       "op": "rule",
       "value": "context"
      }
     ]
    }
   },
   {
    "op": "literal",
    "value": "correlation"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "input-entry"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "input-producer"
   },
   {
    "op": "rule",
    "value": "step-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "input-inbox identity"
   },
   {
    "op": "rule",
    "value": "name-list"
   },
   {
    "op": "literal",
    "value": "compare"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "durable-state"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "ownership compare-and-set"
   },
   {
    "op": "rule",
    "value": "name-list"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "recovery no-lease-steal; native quiescent-predecessor evidence required"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "input-ack after inbox-and-work-schedule commit"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "snapshot-driver"
   },
   {
    "op": "rule",
    "value": "claim-driver"
   },
   {
    "op": "rule",
    "value": "observation-driver"
   },
   {
    "op": "rule",
    "value": "resume-block"
   },
   {
    "op": "rule",
    "value": "workflow-step"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "workflow-step"
    }
   },
   {
    "op": "rule",
    "value": "workflow-terminal"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "workflow-terminal"
    }
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "driver-input": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "input"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": "<-"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "driver-result": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "result"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "rule",
    "value": "type"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "snapshot-driver": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "snapshot-operation"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "driver-input"
    }
   },
   {
    "op": "rule",
    "value": "driver-result"
   },
   {
    "op": "literal",
    "value": "require"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "immutable-inputs"
   },
   {
    "op": "rule",
    "value": "name-list"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "before-each-step reread current order/progress versions and ownership"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "on-missing"
   },
   {
    "op": "rule",
    "value": "failure-action"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "on-unavailable suspend same-state"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "claim-driver": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "claim-operation"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "driver-input"
    }
   },
   {
    "op": "rule",
    "value": "driver-result"
   },
   {
    "op": "literal",
    "value": "bind-native-claim worker to committed claim before dispatch"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "on-contention stop-this-worker"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "on-unknown suspend ownership-unresolved"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "observation-driver": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "observation-operation"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "driver-input"
    }
   },
   {
    "op": "rule",
    "value": "driver-result"
   },
   {
    "op": "literal",
    "value": "after-observation reread snapshot; then-target requires observed.fresh and matching current state, otherwise resume"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "on-contention reread snapshot then reapply original observation; never repeat remote call"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "on-unknown invokes"
   },
   {
    "op": "rule",
    "value": "invocation"
   },
   {
    "op": "literal",
    "value": "; no fresh continuation ticket or rollback inference"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "on-evidence-conflict persist EvidenceConflict using original step command"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "resume-block": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "resume:"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "rule",
    "value": "resume-case"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "resume-case"
    }
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "resume-case": {
  "op": "seq",
  "nodes": [
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "maybe",
    "node": {
     "op": "seq",
     "nodes": [
      {
       "op": "literal",
       "value": "when"
      },
      {
       "op": "rule",
       "value": "expression"
      }
     ]
    }
   },
   {
    "op": "literal",
    "value": "->"
   },
   {
    "op": "rule",
    "value": "workflow-action"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "workflow-action": {
  "op": "alt",
  "nodes": [
   {
    "op": "rule",
    "value": "step-name"
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "finish"
     },
     {
      "op": "rule",
      "value": "step-name"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "suspend"
     },
     {
      "op": "rule",
      "value": "qualified-name"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "suspend"
     },
     {
      "op": "rule",
      "value": "step-name"
     }
    ]
   },
   {
    "op": "literal",
    "value": "resume"
   },
   {
    "op": "literal",
    "value": "stop-this-worker"
   }
  ]
 },
 "workflow-step": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "step"
   },
   {
    "op": "rule",
    "value": "step-name"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "alt",
    "nodes": [
     {
      "op": "rule",
      "value": "remote-step"
     },
     {
      "op": "rule",
      "value": "local-step"
     },
     {
      "op": "rule",
      "value": "review-step"
     }
    ]
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "remote-step": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "invokes"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "driver-input"
    }
   },
   {
    "op": "rule",
    "value": "driver-result"
   },
   {
    "op": "rule",
    "value": "step-branch"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "step-branch"
    }
   }
  ]
 },
 "step-branch": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "on"
     },
     {
      "op": "rule",
      "value": "pattern-list"
     },
     {
      "op": "maybe",
      "node": {
       "op": "seq",
       "nodes": [
        {
         "op": "literal",
         "value": "when"
        },
        {
         "op": "rule",
         "value": "expression"
        }
       ]
      }
     },
     {
      "op": "rule",
      "value": "branch-action"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "on-success require"
     },
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "literal",
      "value": "then"
     },
     {
      "op": "rule",
      "value": "workflow-action"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "on-call-failure"
     },
     {
      "op": "rule",
      "value": "branch-action"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "on-contention reread snapshot then resume"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "on-unavailable"
     },
     {
      "op": "rule",
      "value": "workflow-action"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "on-evidence-conflict"
     },
     {
      "op": "rule",
      "value": "branch-action"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "on-unknown continue"
     },
     {
      "op": "rule",
      "value": "step-name"
     },
     {
      "op": "maybe",
      "node": {
       "op": "seq",
       "nodes": [
        {
         "op": "literal",
         "value": ";"
        },
        {
         "op": "alt",
         "nodes": [
          {
           "op": "literal",
           "value": "do-not-release"
          },
          {
           "op": "literal",
           "value": "do-not-assume-rollback"
          }
         ]
        }
       ]
      }
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   }
  ]
 },
 "branch-action": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "maybe",
      "node": {
       "op": "seq",
       "nodes": [
        {
         "op": "literal",
         "value": "require"
        },
        {
         "op": "rule",
         "value": "expression"
        },
        {
         "op": "literal",
         "value": "then"
        }
       ]
      }
     },
     {
      "op": "rule",
      "value": "workflow-action"
     },
     {
      "op": "maybe",
      "node": {
       "op": "seq",
       "nodes": [
        {
         "op": "literal",
         "value": "retaining original"
        },
        {
         "op": "alt",
         "nodes": [
          {
           "op": "literal",
           "value": "command"
          },
          {
           "op": "literal",
           "value": "attempt"
          }
         ]
        }
       ]
      }
     },
     {
      "op": "maybe",
      "node": {
       "op": "seq",
       "nodes": [
        {
         "op": "literal",
         "value": ";"
        },
        {
         "op": "alt",
         "nodes": [
          {
           "op": "literal",
           "value": "do-not-release"
          },
          {
           "op": "literal",
           "value": "do-not-assume-rollback"
          }
         ]
        }
       ]
      }
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "observe"
     },
     {
      "op": "rule",
      "value": "expression"
     },
     {
      "op": "literal",
      "value": "then"
     },
     {
      "op": "rule",
      "value": "workflow-action"
     }
    ]
   }
  ]
 },
 "local-step": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "local-observation"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "commit-before"
   },
   {
    "op": "rule",
    "value": "step-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "on-unknown inspect original observation before any provider dispatch"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "next"
   },
   {
    "op": "rule",
    "value": "step-name"
   },
   {
    "op": "literal",
    "value": "only after fresh acknowledged local commit or native never-dispatched journal evidence"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "review-step": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "requires persisted"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "suspend"
   },
   {
    "op": "rule",
    "value": "step-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "workflow-terminal": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "terminal"
   },
   {
    "op": "rule",
    "value": "step-name"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "literal",
    "value": "require persisted"
   },
   {
    "op": "rule",
    "value": "expression"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "effects none"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "generic-workflow-declaration": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "workflow"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "literal",
    "value": "owner"
   },
   {
    "op": "rule",
    "value": "step-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "scope generated-recoverable"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "profile"
   },
   {
    "op": "rule",
    "value": "reference"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "parameter"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "parameter"
    }
   },
   {
    "op": "literal",
    "value": "correlation"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "durable-state"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "start"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "generic-workflow-step"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "generic-workflow-step"
    }
   },
   {
    "op": "literal",
    "value": "recovery needed-compensations-only reverse-completion"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "generic-workflow-step": {
  "op": "alt",
  "nodes": [
   {
    "op": "rule",
    "value": "local-workflow-step"
   },
   {
    "op": "rule",
    "value": "provider-workflow-step"
   },
   {
    "op": "rule",
    "value": "event-workflow-step"
   },
   {
    "op": "rule",
    "value": "plain-workflow-step"
   }
  ]
 },
 "plain-workflow-step": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "step"
   },
   {
    "op": "rule",
    "value": "step-name"
   },
   {
    "op": "literal",
    "value": "invokes"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "local-workflow-step": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "step"
   },
   {
    "op": "rule",
    "value": "step-name"
   },
   {
    "op": "literal",
    "value": "invokes"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "literal",
    "value": "compensate-with"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "provider-workflow-step": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "step"
   },
   {
    "op": "rule",
    "value": "step-name"
   },
   {
    "op": "literal",
    "value": "invokes"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "literal",
    "value": "on-unknown resume-original-command"
   },
   {
    "op": "literal",
    "value": "on-definite-failure compensate"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "event-workflow-step": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "step"
   },
   {
    "op": "rule",
    "value": "step-name"
   },
   {
    "op": "literal",
    "value": "awaits"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "literal",
    "value": "delivered-to"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "interface-declaration": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "interface"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "literal",
    "value": "kind"
   },
   {
    "op": "rule",
    "value": "interface-kind"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "interface-clause"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "interface-clause"
    }
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "interface-kind": {
  "op": "alt",
  "nodes": [
   {
    "op": "literal",
    "value": "internal"
   },
   {
    "op": "literal",
    "value": "external"
   },
   {
    "op": "literal",
    "value": "bounded-schema"
   },
   {
    "op": "literal",
    "value": "native-producer"
   },
   {
    "op": "literal",
    "value": "trusted-context"
   },
   {
    "op": "literal",
    "value": "native-auth-owner"
   },
   {
    "op": "literal",
    "value": "technical-profile-family"
   },
   {
    "op": "literal",
    "value": "application-composition"
   }
  ]
 },
 "interface-clause": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "exposes"
     },
     {
      "op": "rule",
      "value": "name-list"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "visibility service-private owner"
     },
     {
      "op": "rule",
      "value": "step-name"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "alt",
      "nodes": [
       {
        "op": "literal",
        "value": "abi"
       },
       {
        "op": "literal",
        "value": "signatures"
       },
       {
        "op": "literal",
        "value": "fields"
       },
       {
        "op": "literal",
        "value": "methods"
       },
       {
        "op": "literal",
        "value": "variants"
       }
      ]
     },
     {
      "op": "rule",
      "value": "reference"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "custody"
     },
     {
      "op": "rule",
      "value": "custody-kind"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "serializable false"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "public-constructor forbidden"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "implementation required-later-native-asset"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "on-unresolved reject NativeImplementationUnavailable"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "admission auth-foundation-authorization-admission-service"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "decision auth-foundation-authorization-ready-decision.authorize"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "protocol"
     },
     {
      "op": "rule",
      "value": "PROTOCOL_NAME"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "alt",
      "nodes": [
       {
        "op": "literal",
        "value": "request"
       },
       {
        "op": "literal",
        "value": "result"
       }
      ]
     },
     {
      "op": "rule",
      "value": "type"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "alt",
      "nodes": [
       {
        "op": "literal",
        "value": "binding"
       },
       {
        "op": "literal",
        "value": "family-contract"
       },
       {
        "op": "literal",
        "value": "obligations"
       }
      ]
     },
     {
      "op": "rule",
      "value": "reference"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "input checked technical Craft model with original owner"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "output derived candidate package with actual resolved native basis"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "callbacks forbidden"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "unknown-primitive reject"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "missing-producer reject"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "rule",
    "value": "value-domain-clause"
   },
   {
    "op": "rule",
    "value": "application-clause"
   }
  ]
 },
 "custody-kind": {
  "op": "alt",
  "nodes": [
   {
    "op": "literal",
    "value": "private-registered-source-profile-callsite"
   },
   {
    "op": "literal",
    "value": "private-registered-entry-auth-owner"
   },
   {
    "op": "literal",
    "value": "private-registered-local-worker-owner"
   },
   {
    "op": "literal",
    "value": "private-registered-service-entry-owner"
   },
   {
    "op": "literal",
    "value": "private-registered-parent-call-store-worker-or-event-owner"
   }
  ]
 },
 "value-domain-clause": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "scalar UInt64 wire canonical-decimal-string native bigint range"
     },
     {
      "op": "rule",
      "value": "natural"
     },
     {
      "op": "literal",
      "value": ".."
     },
     {
      "op": "rule",
      "value": "natural"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "scalar Bool wire boolean native boolean"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "validates"
     },
     {
      "op": "rule",
      "value": "type"
     },
     {
      "op": "literal",
      "value": "using"
     },
     {
      "op": "alt",
      "nodes": [
       {
        "op": "rule",
        "value": "qualified-name"
       },
       {
        "op": "literal",
        "value": "declared-refinement"
       },
       {
        "op": "literal",
        "value": "closed-enum"
       },
       {
        "op": "literal",
        "value": "closed-fields-and-invariants"
       }
      ]
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "codec strict-utf8-duplicate-aware-json"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "optional wire null-or-value native tagged-none-or-some"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "on-invalid reject invalid-request before business invocation"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   }
  ]
 },
 "application-clause": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "source"
     },
     {
      "op": "rule",
      "value": "reference"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "service"
     },
     {
      "op": "rule",
      "value": "step-name"
     },
     {
      "op": "literal",
      "value": "module"
     },
     {
      "op": "rule",
      "value": "qualified-name"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "alt",
      "nodes": [
       {
        "op": "literal",
        "value": "entry-catalog"
       },
       {
        "op": "literal",
        "value": "implementation"
       }
      ]
     },
     {
      "op": "rule",
      "value": "qualified-name"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "rule",
      "value": "application-reference"
     },
     {
      "op": "rule",
      "value": "reference"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "coordination-records"
     },
     {
      "op": "rule",
      "value": "name-list"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "required-output"
     },
     {
      "op": "rule",
      "value": "output-kind"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "formal-claims optional"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "hosting deferred"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   }
  ]
 },
 "application-reference": {
  "op": "alt",
  "nodes": [
   {
    "op": "literal",
    "value": "parameters"
   },
   {
    "op": "literal",
    "value": "http-bindings"
   },
   {
    "op": "literal",
    "value": "external-bindings"
   },
   {
    "op": "literal",
    "value": "external-config"
   },
   {
    "op": "literal",
    "value": "value-domain"
   },
   {
    "op": "literal",
    "value": "computation-bounds"
   },
   {
    "op": "literal",
    "value": "provider-protocol"
   },
   {
    "op": "literal",
    "value": "authorization"
   },
   {
    "op": "literal",
    "value": "native-obligations"
   },
   {
    "op": "literal",
    "value": "profile-family"
   },
   {
    "op": "literal",
    "value": "coordination-contract"
   },
   {
    "op": "literal",
    "value": "source-identities"
   }
  ]
 },
 "output-kind": {
  "op": "alt",
  "nodes": [
   {
    "op": "literal",
    "value": "code"
   },
   {
    "op": "literal",
    "value": "api-contracts"
   },
   {
    "op": "literal",
    "value": "business-graph"
   },
   {
    "op": "literal",
    "value": "system-graph"
   },
   {
    "op": "literal",
    "value": "business-system-bridge"
   }
  ]
 },
 "claim-declaration": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "formal-claim"
   },
   {
    "op": "rule",
    "value": "NAME"
   },
   {
    "op": "literal",
    "value": ":"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "literal",
    "value": "language"
   },
   {
    "op": "alt",
    "nodes": [
     {
      "op": "literal",
      "value": "lean4"
     },
     {
      "op": "literal",
      "value": "smtlib2"
     },
     {
      "op": "literal",
      "value": "alloy"
     },
     {
      "op": "literal",
      "value": "tla-plus"
     },
     {
      "op": "literal",
      "value": "souffle"
     }
    ]
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "source"
   },
   {
    "op": "rule",
    "value": "reference"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "targets"
   },
   {
    "op": "rule",
    "value": "name-list"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "native-capture-body": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "native-protocol"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "intent immutable"
   },
   {
    "op": "rule",
    "value": "invocation"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "same-key same-request returns current original-attempt status; never another effect"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "same-key different-request fails ProviderRequestConflict without mutation"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "may-return"
   },
   {
    "op": "rule",
    "value": "name-list"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "on-malformed-request fails ProviderInputRejected"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "on-invalid-response fails ProviderProtocolRejected"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "on-transport-failure fails ProviderTransportUnknown"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "native-inspect-body": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "output"
   },
   {
    "op": "rule",
    "value": "type"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "native-protocol"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "compare original request using"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "on-existing returns current original-attempt status"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "on-missing returns UnknownKey with exact supplied identity and no reference"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "on-conflict fails ProviderRequestConflict"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "effects none"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   }
  ]
 },
 "replay-protocol": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "ordered-protocol:"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "literal",
    "value": "validate request-shape before replay-read"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "check current-action-access before replay-read"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "scope"
   },
   {
    "op": "rule",
    "value": "name-list"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "fingerprint"
   },
   {
    "op": "rule",
    "value": "reference"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "literal",
    "value": "fields"
   },
   {
    "op": "rule",
    "value": "name-list"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "encoding"
   },
   {
    "op": "rule",
    "value": "reference"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "digest sha256"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "normalization none"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "DEDENT"
   },
   {
    "op": "literal",
    "value": "read replay-record by scope"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "apply"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "replay-contract-case"
   },
   {
    "op": "many",
    "node": {
     "op": "rule",
     "value": "replay-contract-case"
    }
   },
   {
    "op": "rule",
    "value": "DEDENT"
   },
   {
    "op": "rule",
    "value": "replay-retention"
   },
   {
    "op": "rule",
    "value": "replay-reconciliation"
   }
  ]
 },
 "replay-contract-case": {
  "op": "alt",
  "nodes": [
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "on ReplayAccepted return stored"
     },
     {
      "op": "rule",
      "value": "qualified-name"
     },
     {
      "op": "rule",
      "value": "before-order"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "on ReplayPending retain original command; no second execution"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "on OutcomeUnknown retain original command; inspect authoritative record read-only"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "on FingerprintConflict retain original record; no new-effects"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "on CapacityUnavailable retain all existing records; no new-effects"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   },
   {
    "op": "seq",
    "nodes": [
     {
      "op": "literal",
      "value": "on EvaluateFreshQuote evaluate owned quote; atomically claim scope with local acceptance"
     },
     {
      "op": "rule",
      "value": "NEWLINE"
     }
    ]
   }
  ]
 },
 "replay-retention": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "retention:"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "literal",
    "value": "capacity"
   },
   {
    "op": "rule",
    "value": "natural"
   },
   {
    "op": "literal",
    "value": "per-orders-service"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "lifetime scratch-cell-lifetime"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "accepted never-evict"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "pending never-evict"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "indeterminate never-evict"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "full reject-new-work"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "key-reset forbidden"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "automatic-expiry forbidden"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 },
 "replay-reconciliation": {
  "op": "seq",
  "nodes": [
   {
    "op": "literal",
    "value": "reconciliation:"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "INDENT"
   },
   {
    "op": "literal",
    "value": "require current-action-access before authoritative-read"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "validate original request-shape before authoritative-read"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "read-only original scope, fingerprint"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "accepted return original"
   },
   {
    "op": "rule",
    "value": "qualified-name"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "pending remain ReplayPending"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "indeterminate remain OutcomeUnknown"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "absent-after-uncertainty remain OutcomeUnknown"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "proven-local-rollback retry original command with same scope, fingerprint"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "literal",
    "value": "unavailable remain OutcomeUnknown"
   },
   {
    "op": "rule",
    "value": "NEWLINE"
   },
   {
    "op": "rule",
    "value": "DEDENT"
   }
  ]
 }
};
