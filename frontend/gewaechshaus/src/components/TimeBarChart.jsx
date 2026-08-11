import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { formatDuration } from "../utils/time";

export default function TimeBarChart({
  data,
  dataKeyxAxis,
  dataKeybar,
  unit,
  yAxisLabel,
}) {
  return (
    <div
      style={{
        background: "transparent",
        padding: "20px",
        width: "100%",
        height: "100%",
      }}
    >
      <ResponsiveContainer width="100%" height={110}>
        <BarChart data={data}>
          <XAxis
            dataKey={dataKeyxAxis}
            tickFormatter={(d) =>
              new Date(d).toLocaleDateString("de-DE", {
                day: "2-digit",
                month: "2-digit",
              })
            }
            tick={{
              fill: "white",
            }}
          />
          <YAxis
            label={{
              value: yAxisLabel,
              fontSize: 12,
              angle: -90,
              position: "Left",
              offset: 32,
              dx: -20,
              fill: "#2e2f31",
            }}
            unit={unit}
            tick={{
              fontSize: 10,
              fill: "white",
            }}
          />
          <Tooltip
            cursor={false}
            formatter={(value) => [
              `${formatDuration(value).minutes} min, ${formatDuration(value).seconds} s`,
              "Watering Duration",
            ]}
            contentStyle={{
              backgroundColor: "#0b1220",
              border: "none",
              borderRadius: "8px",
              color: "#e5e7eb",
              boxShadow: "0 4px 20px rgba(0,0,0,0.35)",
            }}
          />
          <Bar
            dataKey={dataKeybar}
            fill="rgba(17, 84, 123, 0.95)"
            activeBar={{ fill: "rgba(66, 142, 186, 0.95)", stroke: "blue" }}
            radius={[10, 10, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
