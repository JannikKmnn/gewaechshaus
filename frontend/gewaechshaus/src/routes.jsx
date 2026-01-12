import { Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import ControlCenter from "./pages/ControlCenter";

export default function AppRoutes() {
  return (
    <div style={{ flex: 1, padding: "20px" }}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/control" element={<ControlCenter />} />
      </Routes>
    </div>
  );
}
