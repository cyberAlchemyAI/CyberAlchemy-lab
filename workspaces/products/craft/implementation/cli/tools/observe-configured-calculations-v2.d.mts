import type {ExactCalculationContract} from '../src/typed-backend/calculation-exact.js';
import type {planConfiguredCalculationsV2} from '../src/generation/configured-calculations-v2.js';
import type {CalculationObservation} from './observe-configured-calculations.mjs';

type ExpectedBinding=Pick<ReturnType<typeof planConfiguredCalculationsV2>['modules'][number],'provider_import'|'callable'|'descriptor'>;
export function observeCalculationV2(source:string,contract:ExactCalculationContract):CalculationObservation;
export function observeCalculationV2Binding(provider:string,wrapper:string,expected:ExpectedBinding,contract:ExactCalculationContract):CalculationObservation;
