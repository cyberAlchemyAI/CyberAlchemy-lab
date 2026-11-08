import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import { installReviewMode } from "./review";
import "../../../../../../../../cyberalchemy-exchange/knowledge-exchange-protocol/capabilities/hosted-devnet-exchange/v1/implementation/static/assets/design-system.css";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);

installReviewMode();
