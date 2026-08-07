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
        background: "#3a3f3c",
        borderRadius: "12px",
        padding: "20px",
        width: "100%",
        height: "100%",
        boxShadow: "0 4px 20px #3a3f3c",
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
          />
          <YAxis
            label={{
              value: yAxisLabel,
              fontSize: 12,
              angle: -90,
              position: "Left",
              offset: 32,
              dx: -20,
            }}
            unit={unit}
            tick={{
              fontSize: 10,
            }}
          />
          <Tooltip
            formatter={(value) => [
              `${formatDuration(value).minutes} min, ${formatDuration(value).seconds} s`,
              "Watering Duration",
            ]}
          />
          <Bar
            dataKey={dataKeybar}
            fill="#8884d8"
            activeBar={{ fill: "pink", stroke: "blue" }}
            radius={[10, 10, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
