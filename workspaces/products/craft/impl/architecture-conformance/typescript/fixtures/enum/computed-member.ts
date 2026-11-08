import { defineEnum } from "../../runtime/enum/index.js";
const active = "Active";
export const OrderStatus = defineEnum({ [active]: "active", Closed: "closed", Draft: "draft" } as const);
