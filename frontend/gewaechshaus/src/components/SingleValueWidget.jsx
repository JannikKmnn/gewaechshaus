export default function SingleValueWidget({
  label,
  value,
  unit,
  color
}) {
  return (
    <div
      style={{
        background: "#0b1220",
        borderRadius: "12px",
        padding: "20px",
        minWidth: "220px",
        minHeight: "150px",
        boxShadow: "0 4px 20px rgba(0,0,0,0.25)"
      }}
    >
      <div
        style={{
          fontSize: "14px",
          opacity: 0.7,
          marginBottom: "10px"
        }}
      >
        {label}
      </div>

      <div
        style={{
          fontSize: "42px",
          fontWeight: 500,
          color
        }}
      >
        {value !== null ? value : "—"}
        <span style={{ fontSize: "20px", marginLeft: "4px" }}>
          {unit}
        </span>
      </div>
    </div>
  );
}