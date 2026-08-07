export default function CustomTooltip({ active, payload, label, unit }) {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  // sort descending by value
  const sorted = [...payload].sort((a, b) => b.value - a.value);

  return (
    <div
      style={{
        background: "#0b1220",
        borderRadius: "8px",
        padding: "10px 12px",
        boxShadow: "0 4px 20px rgba(0,0,0,0.35)",
        color: "#e5e7eb",
        fontSize: "12px",
      }}
    >
      {/* timestamp */}
      <div
        style={{
          marginBottom: "6px",
          color: "#9ca3af",
          fontSize: "11px",
        }}
      >
        {new Date(label).toLocaleString([], {
          day: "2-digit",
          month: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
        })}
      </div>

      {/* values */}
      {sorted.map((entry) => (
        <div
          key={entry.dataKey}
          style={{
            display: "flex",
            justifyContent: "space-between",
            gap: "12px",
            color: entry.color,
          }}
        >
          <span>{entry.dataKey}</span>
          <span>
            {entry.value} {unit}
          </span>
        </div>
      ))}
    </div>
  );
}
