import { Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import ControlCenter from "./pages/ControlCenter";

export default function AppRoutes() {
  return (
    <div style={{
      width: "100%",
      height: "100%",
      padding: "10px",
      paddingLeft: "80px",
      boxSizing: "border-box"
    }}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/control" element={<ControlCenter />} />
      </Routes>
    </div>
  );
}
