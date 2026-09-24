import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import AdminApp from "./AdminApp";
import App from "./App";
import "./styles.css";

const RootApp = window.location.pathname.startsWith("/admin") ? AdminApp : App;

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RootApp />
  </StrictMode>,
);

if ("serviceWorker" in navigator && import.meta.env.PROD) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {
      // The app remains usable online even if service-worker registration fails.
    });
  });
}
