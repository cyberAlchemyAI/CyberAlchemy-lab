import "../families/finite-vocabulary/index.js";
export { target } from "../targets/typescript/index.js";
const loadRealization = () => import("../realization/evaluator/index.js");
const pluralRealization = require("../realizations/rule/index.js");
import "../acceptance/rule/index.js";
import "../factory/registry/factory-node-registry-v1.js";

export { loadRealization, pluralRealization };
