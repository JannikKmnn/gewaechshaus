import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from "recharts";
import { formatTime } from "../utils/time";

export default function TimeseriesChart({
  data,
  label,
  unit,
  yAxisLabel,
  color
}) {
  return (
    <div
      style={{
        background: "#0b1220",
        borderRadius: "12px",
        padding: "20px",
        width: "100%",
        height: "100%",
        boxShadow: "0 4px 20px rgba(0,0,0,0.25)"
      }}
    >
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
            <XAxis
                dataKey="timestamp"
                tickFormatter={formatTime}
                tick={{ fill: "#9ca3af", fontSize: 12 }}
            />
            <YAxis
                label={{ 
                  value: yAxisLabel, 
                  angle: -90, 
                  position: "Left",
                  offset: 32,
                  dx: -30
                }}
                unit={unit}
            />
            <Tooltip />
            <Line
                type="monotone"
                dataKey="value"
                stroke={color}
                dot={false}
                strokeWidth={2}
            />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
