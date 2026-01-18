import { Link, useLocation } from "react-router-dom";
import { useState } from "react";
import { LayoutDashboard, ServerCog } from "lucide-react";

export default function NavBar() {
  const [expanded, setExpanded] = useState(false);
  const location = useLocation();

  const navWidth = expanded ? "200px" : "60px";

  const itemStyle = (path) => ({
    display: "flex",
    alignItems: "center",
    gap: "14px",
    padding: "16px",
    width: "100%",
    boxSizing: "border-box",
    color: "white",
    textDecoration: "none",
    background: location.pathname === path ? "#32cd32" : "transparent",
    transition: "background 0.2s",
    cursor: "pointer"
  });

  const labelStyle = {
    whiteSpace: "nowrap",
    opacity: expanded ? 1 : 0,
    transition: "opacity 0.2s",
    fontSize: "14px",
    fontWeight: 500,
    letterSpacing: "0.02em"
  };

  const iconStyle = {
    minWidth: "24px"
  };

  return (
    <div
      onMouseEnter={() => setExpanded(true)}
      onMouseLeave={() => setExpanded(false)}
      style={{
        width: navWidth,
        height: "100vh",
        background: "#54b754",
        display: "flex",
        flexDirection: "column",
        transition: "width 0.25s ease",
        overflow: "hidden",
        boxShadow: "2px 0 10px rgba(0,0,0,0.15)",
        position: "fixed",
        left: 0,
        top: 0,
        zIndex: 1000
      }}
    >
      <Link to="/" style={itemStyle("/")}>
        <LayoutDashboard style={iconStyle} />
        <span style={labelStyle}>Dashboard</span>
      </Link>

      <Link to="/control" style={itemStyle("/control")}>
        <ServerCog style={iconStyle} />
        <span style={labelStyle}>Control Center</span>
      </Link>
    </div>
  );
}
