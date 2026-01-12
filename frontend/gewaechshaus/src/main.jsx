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
            display: "flex",
            width: "100vw",
            height: "100vh",
            margin: 0,
            padding: 0
        }}
        >
        <NavBar />
        <AppRoutes />
      </div>
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);