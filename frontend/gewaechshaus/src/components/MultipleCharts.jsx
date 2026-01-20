import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from "recharts";
import { formatTime } from "../utils/time";

export default function MultipleTimeseriesChart({
  data,
  label,
  unit,
  yAxisLabel,
  color,
  yAxisMax,
  yAxisMin,
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
                tick={{ 
                  fill: "#9ca3af", 
                  fontSize: 10, 
                  angle: -20, 
                  dy: 10 
                }}
            />
            <YAxis
                label={{ 
                  value: yAxisLabel, 
                  fontSize: 12, 
                  angle: -90, 
                  position: "Left",
                  offset: 32,
                  dx: -20
                }}
                unit={unit}
                tick={{
                  fontSize: 10,
                }}
                domain={[yAxisMin, yAxisMax]}
            />
            <Tooltip 
              labelFormatter={(label) =>
                new Date(label).toLocaleString([], {
                  day: "2-digit",
                  month: "2-digit",
                  hour: "2-digit",
                  minute: "2-digit",
                })
              }
              formatter={(value) => [`${value} ${unit}`, label]}
              contentStyle={{
                backgroundColor: "#0b1220",
                border: "none",
                borderRadius: "8px",
                color: "#e5e7eb",
                boxShadow: "0 4px 20px rgba(0,0,0,0.35)"
              }}
              itemStyle={{ color }}
              labelStyle={{ color: "#9ca3af" }}
            />
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