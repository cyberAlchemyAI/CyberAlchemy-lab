/** Fixed native ABI adapter over the actual source-generated codec component.
 * Open Questions: docs/COMMERCE-SDK-V5.md#open-questions. */
import {createCommerceValueCodecs} from './values-and-codecs.js';
const original=createCommerceValueCodecs();
export const checkCommerceSchema=original.checkCommerceSchema;
export const decodeCommerceValue=original.decodeCommerceValue;
export const encodeCommerceValue=original.encodeCommerceValue;
export const copyCommerceValue=original.copyCommerceValue;
export const schemaForCommerceType=original.schemaForType;
export const schemaForCommerceArguments=original.schemaForCallableArguments;
export const encodeCommerceComputationParameters=original.encodeComputationParameters;
export const decodeCommerceComputationValue=original.decodeComputationValue;
export const inspectCommerceSchema=original.inspectSchema;
