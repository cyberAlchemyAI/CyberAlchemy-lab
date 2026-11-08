import { getLimitBuyIn } from "../limit/limit.service";

export type DealSplit = {
  team: number;
  player: number;
};

export const getDealSplit = (limit: string): DealSplit => {
  // NL100 buyin is 100 * 100 = 10000 cents?
  // Let's assume NL100 is the threshold.
  // NL100 string -> 100.
  const value = parseInt(limit.replace("NL", ""), 10);
  
  if (value >= 100) {
    return { team: 0.5, player: 0.5 };
  }
  return { team: 0.6, player: 0.4 };
};
