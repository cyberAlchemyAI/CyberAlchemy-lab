import type { TypeOnlyMarker } from "./type-only.js";
import { second } from "./second.js";
export { barrel } from "./barrel.js";

export const root: TypeOnlyMarker = second;
export const loadDynamicLiteral = () => import("./dynamic-literal.js");
