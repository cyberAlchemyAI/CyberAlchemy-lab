export const UINT64_MAX = 18446744073709551615n;
export const QUANTITY_MAX = 2147483647;
function fail(code) { throw new Error(code); }
function record(value, allowed) {
  if (!value || typeof value !== 'object' || Array.isArray(value) ||
      ![Object.prototype, null].includes(Object.getPrototypeOf(value))) fail('QUOTE_RECORD');
  for (const key of Reflect.ownKeys(value)) {
    if (!allowed.includes(key) || !('value' in Object.getOwnPropertyDescriptor(value, key))) fail('QUOTE_FIELD');
  }
  return value;
}
function identity(value) {
  if (typeof value !== 'string' || !value.trim()) fail('QUOTE_ID');
  return value;
}
function currency(value) {
  if (typeof value !== 'string' || !/^[A-Za-z]{3}$/.test(value)) fail('QUOTE_CURRENCY_REQUIRED');
  return value.toLowerCase();
}
function quantity(value, nullable = false) {
  if (nullable && (value === null || value === undefined)) return null;
  if (!Number.isSafeInteger(value) || value < 1 || value > QUANTITY_MAX) fail('QUOTE_QUANTITY');
  return value;
}
export function usdToMinor(value) {
  if (typeof value !== 'string' || !/^(0|[1-9][0-9]*)(\.[0-9]{1,2})?$/.test(value)) fail('QUOTE_USD_DECIMAL');
  const [whole, fraction = ''] = value.split('.');
  const result = BigInt(whole) * 100n + BigInt(fraction.padEnd(2, '0'));
  if (result > UINT64_MAX) fail('QUOTE_MONEY_RANGE');
  return result;
}
export function minorToUsd(value) {
  if (typeof value !== 'bigint' || value < 0n || value > UINT64_MAX) fail('QUOTE_MONEY_RANGE');
  return `${value / 100n}.${(value % 100n).toString().padStart(2, '0')}`;
}
export function prepareQuote(snapshot, request) {
  record(snapshot, ['variant_id', 'price_set_id', 'prices']);
  record(request, ['request_id', 'variant_id', 'currency_code', 'quantity']);
  identity(request.request_id);
  if (identity(request.variant_id) !== identity(snapshot.variant_id)) fail('QUOTE_VARIANT_MISMATCH');
  const priceSetId = identity(snapshot.price_set_id);
  const requestedCurrency = currency(request.currency_code);
  if (requestedCurrency !== 'usd') fail('QUOTE_UNSUPPORTED_CURRENCY');
  const requestedQuantity = BigInt(quantity(request.quantity));
  if (!Array.isArray(snapshot.prices)) fail('QUOTE_PRICES');
  const seen = new Set();
  const rows = [];
  for (const price of snapshot.prices) {
    record(price, ['id', 'price_set_id', 'currency_code', 'raw_amount', 'min_quantity', 'max_quantity', 'price_list_id', 'rules_count', 'deleted_at']);
    const priceId = identity(price.id);
    if (seen.has(priceId)) fail('QUOTE_DUPLICATE_PRICE');
    seen.add(priceId);
    if (identity(price.price_set_id) !== priceSetId) fail('QUOTE_PRICE_SET_MISMATCH');
    // This DTO deliberately admits only base prices with no contextual rules.
    if (price.price_list_id != null || price.rules_count !== 0) fail('QUOTE_UNSUPPORTED_RULES');
    const code = currency(price.currency_code);
    if (price.currency_code !== code) fail('QUOTE_STORED_CURRENCY');
    if (price.deleted_at != null && (typeof price.deleted_at !== 'string' || Number.isNaN(Date.parse(price.deleted_at)))) fail('QUOTE_DELETED_AT');
    const min = quantity(price.min_quantity, true), max = quantity(price.max_quantity, true);
    if (min !== null && max !== null && min > max) fail('QUOTE_TIER_RANGE');
    if (price.deleted_at != null || code !== requestedCurrency) continue;
    record(price.raw_amount, ['value', 'precision']);
    if (price.raw_amount.precision !== 20) fail('QUOTE_RAW_PRECISION');
    rows.push(Object.freeze({priceId, currency: code, amountMinor: usdToMinor(price.raw_amount.value),
      minQuantity: min === null ? 0n : BigInt(min), maxQuantity: max === null ? UINT64_MAX : BigInt(max)}));
  }
  return { rows, parameters: { requestedCurrency, requestedQuantity } };
}
export function quotePrice(api, snapshot, request) {
  const {rows, parameters} = prepareQuote(snapshot, request);
  const matches = api.evaluateQuery('EligiblePrices', rows, parameters);
  const base = {request_id: request.request_id, variant_id: request.variant_id, price_set_id: snapshot.price_set_id, currency_code: 'usd'};
  if (!matches.length) return Object.freeze({...base, status: 'no_price'});
  const best = matches[0];
  const ties = matches.filter(row => row.amountMinor === best.amountMinor);
  if (ties.length > 1) return Object.freeze({...base, status: 'ambiguous_price',
    price_ids: Object.freeze(ties.map(row => row.priceId).sort()), unit_amount: minorToUsd(best.amountMinor)});
  const subtotal = api.evaluateCalculation('LineSubtotal', {amountMinor: best.amountMinor, requestedQuantity: parameters.requestedQuantity});
  return Object.freeze({...base, status: 'quoted', price_id: best.priceId,
    unit_amount: minorToUsd(best.amountMinor), unit_amount_minor: best.amountMinor.toString(),
    quantity: request.quantity, subtotal: minorToUsd(subtotal), subtotal_minor: subtotal.toString()});
}
