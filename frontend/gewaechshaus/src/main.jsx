import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import NavBar from "./components/NavBar";
import AppRoutes from "./routes";

import "./index.css";

function App() {
  return (
    <BrowserRouter>
      <div
        style={{
          position: "relative",
          width: "100vw",
          minHeight: "100vh",
        }}
      >
        <NavBar />
        <AppRoutes />
      </div>
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
