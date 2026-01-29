export default function SingleValueWidget({
  label,
  value,
  unit,
  color,
  height,
  fontsize,
  fontsizelabel
}) {
  return (
    <div
      style={{
        background: "#3a3f3c",
        borderRadius: "12px",
        padding: "20px",
        minWidth: "220px",
        minHeight: height || "150px",
        boxShadow: "0 4px 20px #3a3f3c"
      }}
    >
      <div
        style={{
          fontSize: fontsizelabel || "14px",
          opacity: 0.7,
          marginBottom: "10px"
        }}
      >
        {label}
      </div>

      <div
        style={{
          fontSize: fontsize || "42px",
          fontWeight: 500,
          color
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