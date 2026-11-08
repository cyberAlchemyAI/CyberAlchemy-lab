import "../../families/finite-vocabulary/index.js";
export { evaluator } from "../../realization/evaluator/index.js";
const loadRealization = () => import("../../realizations/rule/index.js");
const acceptance = require("../../acceptance/rule/index.js");
import "../../families/outcome-function/obligations/index.js";
import "./fixtures/semantic-results.js";

export { acceptance, loadRealization };
