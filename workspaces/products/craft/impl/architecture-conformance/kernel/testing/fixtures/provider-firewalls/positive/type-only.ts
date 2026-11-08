import type { TargetProvider } from "../../targets/typescript/index.js";
import { type RealizationProvider } from "../../realizations/rule/index.js";
export type { OtherFamilyContract } from "../beta/contracts.js";

export type FamilyContract = TargetProvider & RealizationProvider;
