import { defineEnum } from "../../runtime/enum/index.js";
export const OrderStatus = defineEnum({ Active: "active", Archived: "archived", Closed: "closed", Draft: "draft" } as const);
