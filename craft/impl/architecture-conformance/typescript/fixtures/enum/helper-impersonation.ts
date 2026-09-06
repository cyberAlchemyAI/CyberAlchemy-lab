import { defineEnum } from "./fake-provider.js";
export const OrderStatus = defineEnum({ Active: "active", Closed: "closed", Draft: "draft" } as const);
