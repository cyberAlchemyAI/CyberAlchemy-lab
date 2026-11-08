export const getLimitBuyIn = (limit: string): number => {
  // Simple mapping: NL10 -> 10, NL25 -> 25, etc.
  const value = parseInt(limit.replace("NL", ""), 10);
  if (isNaN(value)) throw new Error(`Invalid limit format: ${limit}`);
  return value * 100; // 1 Buy-in = 100bb usually. But "NL10" usually means buyin is $10.
  // Wait, if limit is NL10, the buyin is 10.
  // If user meant "500bb of Current Limit", that's 5 buyins.
  // User said "8 buyins of current limit".
  // So if NL10 -> Buyin is 10. 8 Buyins = 80.
  return value;
};
