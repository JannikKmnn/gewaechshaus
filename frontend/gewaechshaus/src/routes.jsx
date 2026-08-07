import { Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import WateringControl from "./pages/WateringControl";
import WindowControl from "./pages/WindowControl";

export default function AppRoutes() {
  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        padding: "10px",
        paddingLeft: "80px",
        boxSizing: "border-box",
      }}
    >
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/control/windows" element={<WindowControl />} />
        <Route path="/control/watering" element={<WateringControl />} />
      </Routes>
    </div>
  );
}
