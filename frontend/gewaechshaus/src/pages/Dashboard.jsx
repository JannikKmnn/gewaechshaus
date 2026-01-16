import { useEffect, useState } from "react";
import SingleValueWidget from "../components/SingleValueWidget";
import { getData } from "../api/data";
import { temperatureToColor } from "../utils/color";

export default function Dashboard() {
  const [outsideTemp, setOutsideTemp] = useState(null);
  const [insideTemp, setInsideTemp] = useState(null);
  const [upTemp, setUpTemp] = useState(null);

  const endTime = new Date().toISOString();
  const startTimeSingle = new Date(Date.now() - 2 * 60 * 1000).toISOString();

  const roundToTwo = (num) => Math.round(num * 100) / 100;

  useEffect(() => {
    async function fetchTemp() {
      const result = await getData({
        measurement: "Temperature",
        start_time: startTimeSingle,
        end_time: endTime,
      });

      const outside_temps = result.filter((measurement) => measurement.field === "temperature_outside")
      const inside_temps = result.filter((measurement) => measurement.field === "temperature_inside")
      const up_temps = result.filter((measurement) => measurement.field === "temperature_up")

      if (Array.isArray(result) && result.length > 0) {

        const latest_outside = outside_temps[outside_temps.length - 1];
        setOutsideTemp(roundToTwo(latest_outside.value));

        const latest_inside = inside_temps[inside_temps.length - 1];
        setInsideTemp(roundToTwo(latest_inside.value));

        const latest_up = up_temps[up_temps.length - 1];
        setUpTemp(roundToTwo(latest_up.value));

      } else {
        setOutsideTemp(null);
        setInsideTemp(null);
        setUpTemp(null);
      }
    }

    fetchTemp();
  }, []);

  return (
    <div>
      <h1 style={{ marginBottom: "20px" }}>Sensor Measurements</h1>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "20px",
          marginBottom: "10px"
        }}
      >

        <div
          style={{
            width: "80px"
          }}
        >
          <SingleValueWidget
            label="Outside"
            value={outsideTemp}
            unit="°C"
            color={temperatureToColor(outsideTemp)}
          />
        </div>
        
        <div
          style={{
            justifySelf: "end"
          }}
        >
          <SingleValueWidget
            label="Inside Up"
            value={upTemp}
            unit="°C"
            color={temperatureToColor(upTemp)}
          />
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "20px",
          marginBottom: "10px"
        }}
      >
        <div
          style={{
            justifySelf: "end",
          }}
        >
          <SingleValueWidget
            label="Inside"
            value={insideTemp}
            unit="°C"
            color={temperatureToColor(insideTemp)}
          />
        </div>
      </div>
    </div>
  );
}