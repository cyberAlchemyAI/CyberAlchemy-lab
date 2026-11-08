import { defineEnum } from "../../runtime/enum/index.js";
const shared = { Active: "active" } as const;
export const OrderStatus = defineEnum({ ...shared, Closed: "closed", Draft: "draft" } as const);
