export default function BinaryWidget({
  label,
  value,
  binary_value,
  color_true = "#269e24",
  color_false = "#cc923a",
  height,
  fontsize,
  fontsizelabel
}) {
  return (
    <div
      style={{
        background: binary_value? color_true : color_false,
        borderRadius: "12px",
        padding: "20px",
        minWidth: "220px",
        minHeight: height || "150px",
        boxShadow: "0 4px 20px rgba(0,0,0,0.25)"
      }}
    >
      <div
        style={{
          fontSize: fontsizelabel || "14px",
          opacity: 0.7,
        }}
      >
        {label}
      </div>

      <div
        style={{
          fontSize: fontsize || "42px",
          fontWeight: 500,
          textAlign: "center",
        }}
      >
        {value !== null ? value : "—"}
      </div>
    </div>
  );
}