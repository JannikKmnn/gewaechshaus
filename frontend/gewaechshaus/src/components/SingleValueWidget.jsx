export default function SingleValueWidget({
  label,
  value,
  unit,
  color,
  height,
  fontsize,
  fontsizelabel,
  background_color = "transparent",
}) {
  return (
    <div
      style={{
        background: background_color,
        padding: "20px",
        minWidth: "220px",
        minHeight: height || "150px",
      }}
    >
      <div
        style={{
          fontSize: fontsizelabel || "14px",
          marginBottom: "10px",
          color: "#2e2f31",
        }}
      >
        {label}
      </div>

      <div
        style={{
          fontSize: fontsize || "42px",
          fontWeight: 500,
          color,
        }}
      >
        {value !== null ? value : "—"}
        <span style={{ fontSize: fontsize || "20px", marginLeft: "4px" }}>
          {unit}
        </span>
      </div>
    </div>
  );
}
