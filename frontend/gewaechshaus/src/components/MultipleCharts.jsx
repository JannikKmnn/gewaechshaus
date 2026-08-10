import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceArea,
  ResponsiveContainer,
} from "recharts";
import CustomTooltip from "./ChartTooltip";
import { temperatureToColor } from "../utils/color";
import { reshapeTimeseries } from "../utils/data";
import { formatTime } from "../utils/time";

export default function MultipleTimeseriesChart({
  data,
  intervals,
  startTime,
  endTime,
  exclude,
  label,
  unit,
  yAxisLabel,
  color,
  yAxisMax,
  yAxisMin,
}) {
  const wideData = reshapeTimeseries(data, exclude).map((d) => ({
    ...d,
    timestamp: new Date(d.timestamp).getTime(),
  }));

  const chartIntervals = intervals.map((i) => ({
    ...i,
    from: new Date(i.from).getTime(),
    to: new Date(i.to).getTime(),
  }));

  const seriesKeys = Array.from(new Set(data.map((d) => d.field)));
  const filteredKeys = seriesKeys.filter((val) => val !== exclude);

  function stateColor(state) {
    switch (state) {
      case "closed":
        return "#8ecae6";
      case "left":
        return "#ffb703";
      case "both":
        return "#fb6f6f";
      default:
        return "#9ca3af";
    }
  }

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
        <LineChart data={wideData}>
          {chartIntervals.map((interval, i) => {
            return (
              <ReferenceArea
                key={i}
                x1={interval.from}
                x2={interval.to}
                fill={stateColor(interval.state)}
                fillOpacity={0.25}
              />
            );
          })}
          <XAxis
            dataKey="timestamp"
            type="number"
            scale="time"
            tick={{
              fill: "#2e2f31",
              fontSize: 10,
              angle: -20,
              dy: 10,
            }}
            domain={[
              new Date(startTime).getTime(),
              new Date(endTime).getTime(),
            ]}
            tickFormatter={(value) => formatTime(new Date(value).toISOString())}
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
              fill: "#2e2f31",
            }}
            tickFormatter={(value) => Number(value).toFixed(1)}
            domain={[yAxisMin, yAxisMax]}
          />
          <Tooltip content={<CustomTooltip unit={unit} />} />
          {filteredKeys.map((key) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={color}
              dot={false}
              strokeWidth={2}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
