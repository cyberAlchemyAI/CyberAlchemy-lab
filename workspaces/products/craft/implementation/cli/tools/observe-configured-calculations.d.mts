import type {TypedCalculationContract} from '../src/typed-backend/contracts.js';
import type {planConfiguredCalculations} from '../src/generation/configured-calculations.js';

export type CalculationObservation={result:'pass';source_sha256:string;instructions:number;return_kind:'bigint';authority_effect:'none'};
type ExpectedBinding=Pick<ReturnType<typeof planConfiguredCalculations>['modules'][number],'provider_import'|'callable'|'descriptor'>;
export function observeCalculation(source:string,contract:TypedCalculationContract):CalculationObservation;
export function observeCalculationBinding(provider:string,wrapper:string,expected:ExpectedBinding,contract:TypedCalculationContract):CalculationObservation;
