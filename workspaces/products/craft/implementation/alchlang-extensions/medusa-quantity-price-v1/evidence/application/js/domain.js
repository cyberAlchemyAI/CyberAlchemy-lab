"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.evaluateMapping = evaluateMapping;
exports.selectPolicy = selectPolicy;
exports.evaluateCalculation = evaluateCalculation;
exports.evaluateQuery = evaluateQuery;
const fn0 = __importStar(require("./generated/src/domainspec/typescript/quantity-price/eligible-prices.js"));
const fn1 = __importStar(require("./generated/src/domainspec/typescript/quantity-price/line-subtotal.js"));
function implementation(module) { const exported = Object.values(module).filter((value) => typeof value === "function"); if (exported.length !== 1)
    throw new Error("ALCH_GENERATED_EXPORT_CONTRACT"); return exported[0]; }
const implementations = { "EligiblePrices": implementation(fn0), "LineSubtotal": implementation(fn1) };
const mappings = {};
const policies = {};
const queries = { "EligiblePrices": { "fields": [{ "id": "priceId", "target": "price_id", "type": "identifier" }, { "id": "currency", "target": "currency", "type": "string" }, { "id": "amountMinor", "target": "amount_minor", "type": "integer" }, { "id": "minQuantity", "target": "min_quantity", "type": "integer" }, { "id": "maxQuantity", "target": "max_quantity", "type": "integer" }], "inputs": [{ "id": "requestedCurrency", "target": "requested_currency", "type": "string" }, { "id": "requestedQuantity", "target": "requested_quantity", "type": "integer" }], "outputs": [{ "id": "priceId", "target": "price_id" }, { "id": "currency", "target": "currency" }, { "id": "amountMinor", "target": "amount_minor" }] } };
const calculations = { "LineSubtotal": { "inputs": [{ "id": "amountMinor", "target": "amount_minor", "type": "integer" }, { "id": "requestedQuantity", "target": "requested_quantity", "type": "integer" }] } };
function input(value, fields, required, numericStrings = false) {
    if (!value || typeof value !== "object" || Array.isArray(value) || ![Object.prototype, null].includes(Object.getPrototypeOf(value)))
        throw new Error("ALCH_INPUT_RECORD");
    const out = Object.create(null);
    for (const f of fields) {
        const desc = Object.getOwnPropertyDescriptor(value, f.id);
        if (!desc) {
            if (required)
                throw new Error("ALCH_MISSING_INPUT:" + f.id);
            continue;
        }
        if (!("value" in desc))
            throw new Error("ALCH_INPUT_TYPE:" + f.id);
        if (f.type === "integer") {
            const value = desc.value;
            const valid = typeof value === "bigint" || typeof value === "number" && Number.isSafeInteger(value) || numericStrings && typeof value === "string" && /^(0|[1-9][0-9]*)$/.test(value);
            if (!valid)
                throw new Error(numericStrings ? "CALCULATION_INPUT_TYPE" : "ALCH_INPUT_TYPE:" + f.id);
            if (BigInt(value) < 0n || BigInt(value) > 18446744073709551615n)
                throw new Error(numericStrings ? "CALCULATION_RANGE" : "ALCH_INPUT_RANGE:" + f.id);
        }
        else if (typeof desc.value !== (f.type === "boolean" ? "boolean" : "string"))
            throw new Error("ALCH_INPUT_TYPE:" + f.id);
        out[f.target] = desc.value;
    }
    return out;
}
function evaluateMapping(id, value) {
    if (!Object.hasOwn(mappings, id))
        throw new Error("ALCH_UNKNOWN_MAPPING:" + id);
    const m = mappings[id];
    const result = implementations[id](input(value, m.fields, false));
    const out = {};
    for (const f of m.outputs)
        if (Object.hasOwn(result, f.target))
            Object.defineProperty(out, f.id, { value: result[f.target], enumerable: true });
    return Object.freeze(out);
}
function selectPolicy(id, value) {
    if (!Object.hasOwn(policies, id))
        throw new Error("ALCH_UNKNOWN_POLICY:" + id);
    const p = policies[id];
    const result = implementations[id](input(value, p.fields, false));
    if (!Object.hasOwn(p.targets, result))
        throw new Error("ALCH_UNKNOWN_TARGET");
    return p.targets[result];
}
function evaluateCalculation(id, value) {
    if (!Object.hasOwn(calculations, id))
        throw new Error("ALCH_UNKNOWN_CALCULATION:" + id);
    return implementations[id](input(value, calculations[id].inputs, false, true));
}
function evaluateQuery(id, rows, parameters = {}) {
    if (!Object.hasOwn(queries, id))
        throw new Error("ALCH_UNKNOWN_QUERY:" + id);
    if (!Array.isArray(rows))
        throw new Error("ALCH_QUERY_ROWS");
    const q = queries[id], args = input(parameters, q.inputs, false);
    const results = implementations[id](rows.map(row => input(row, q.fields, false)), args);
    return Object.freeze(results.map((result) => Object.freeze(Object.fromEntries(q.outputs.map((f) => [f.id, result[f.target]])))));
}
