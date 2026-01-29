import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from "recharts";
import CustomTooltip from "./ChartTooltip";
import { temperatureToColor } from "../utils/color";
import { reshapeTimeseries } from "../utils/data";
import { formatTime } from "../utils/time";

export default function MultipleTimeseriesChart({
  data,
  exclude,
  label,
  unit,
  yAxisLabel,
  color,
  yAxisMax,
  yAxisMin,
}) {

  const wideData = reshapeTimeseries(data, exclude);

  const seriesKeys = Array.from(
    new Set(data.map(d => d.field))
  );
  const filteredKeys = seriesKeys.filter(val => val !== exclude);

  return (
    <div
      style={{
        background: "#3a3f3c",
        borderRadius: "12px",
        padding: "20px",
        width: "100%",
        height: "100%",
        boxShadow: "0 4px 20px #3a3f3c"
      }}
    >
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={wideData}>
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
              content={<CustomTooltip unit={unit} />}
            />
            {
              filteredKeys.map((key) => (
                <Line 
                  key={key}
                  type="monotone" 
                  dataKey={key}
                  stroke={color} 
                  dot={false}
                  strokeWidth={2}
                />
              ))
            }
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}