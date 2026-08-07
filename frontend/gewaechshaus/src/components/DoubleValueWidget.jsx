export default function DoubleValueWidget({
  label,
  value1,
  value2,
  unit1,
  unit2,
  color,
  height,
  fontsize,
  fontsizelabel,
  background_color = "#3a3f3c",
}) {
  return (
    <div
      style={{
        background: background_color,
        borderRadius: "12px",
        padding: "20px",
        minWidth: "220px",
        minHeight: height || "150px",
        boxShadow: "0 4px 20px #3a3f3c",
      }}
    >
      <div
        style={{
          fontSize: fontsizelabel || "14px",
          opacity: 0.7,
          marginBottom: "10px",
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
        {value1 !== null ? value1 : "—"}
        <span style={{ fontSize: fontsize || "20px", marginLeft: "4px" }}>
          {unit1}
        </span>
      </div>

      <div
        style={{
          fontSize: fontsize || "42px",
          fontWeight: 500,
          color,
        }}
      >
        {value2 !== null ? value2 : "—"}
        <span style={{ fontSize: fontsize || "20px", marginLeft: "4px" }}>
          {unit2}
        </span>
      </div>
    </div>
  );
}
