import { useEffect, useState } from "react";
import SingleValueWidget from "../components/SingleValueWidget";
import { getData } from "../api/data";

export default function Dashboard() {
  const [outsideTemp, setOutsideTemp] = useState(null);

  const endTime = new Date().toISOString();
  const startTimeSingle = new Date(Date.now() - 2 * 60 * 1000).toISOString();

  useEffect(() => {
    async function fetchOutsideTemp() {
      const result = await getData({
        sensor_identifier: "temperature_outside",
        measurement: "Temperature",
        start_time: startTimeSingle,
        end_time: endTime,
      });

      if (Array.isArray(result) && result.length > 0) {
        const latest = result[result.length - 1];
        setOutsideTemp(latest.value);
      } else {
        setOutsideTemp(null);
      }
    }

    fetchOutsideTemp();
  }, []);

  return (
    <div>
      <h1 style={{ marginBottom: "20px" }}>Sensor Measurements</h1>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "20px"
        }}
      >
        <SingleValueWidget
          label="Outside"
          value={outsideTemp}
          unit="°C"
          color="#7aa2ff"
        />
      </div>
    </div>
  );
}