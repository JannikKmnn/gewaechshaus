import { XAxis, ReferenceArea, ResponsiveContainer } from "recharts";
import { formatTime } from "../utils/time";

export default function TimeSectionsChart({
  intervals,
  startTime,
  endTime,
  height = 110,
}) {
  const chartIntervals = intervals.map((i) => ({
    ...i,
    from: new Date(i.from).getTime(),
    to: new Date(i.to).getTime(),
  }));

  function stateColor(state) {
    switch (state) {
      case "wet":
        return "#8ecae6";
      case "dry":
        return "#ffb703";
      default:
        return "#8ecae6";
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
      <ResponsiveContainer width="100%" height={height}>
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
            fill: "white",
            fontSize: 10,
            angle: -20,
            dy: 10,
          }}
          domain={[new Date(startTime).getTime(), new Date(endTime).getTime()]}
          tickFormatter={(value) => formatTime(new Date(value).toISOString())}
        />
      </ResponsiveContainer>
    </div>
  );
}
