import { defineEnum } from "../../runtime/enum/index.js";
export const OrderStatus = defineEnum({ Active: "active", AlsoActive: "active", Closed: "closed", Draft: "draft" } as const);
