import { useEffect, useState } from "react";
import TimeseriesChart from "../components/TimeseriesChart";
import SingleValueWidget from "../components/SingleValueWidget";
import { getData } from "../api/data";
import { temperatureToColor } from "../utils/color";

export default function Dashboard() {
  const [outsideTemp, setOutsideTemp] = useState(null);
  const [insideTemp, setInsideTemp] = useState(null);
  const [upTemp, setUpTemp] = useState(null);
  const [upHumidity, setUpHumidity] = useState(null);
  const [airPressure, setAirPressure] = useState(null);

  const [upHumidityArray, setUpHumidityArray] = useState([]);

  const endTime = new Date().toISOString();
  const startTimeSingle = new Date(Date.now() - 60 * 60 * 1000).toISOString();

  const roundToTwo = (num) => Math.round(num * 100) / 100;

  useEffect(() => {
    async function fetchMeasurements() {
      const results = await Promise.all([
        getData({
          measurement: "Temperature",
          start_time: startTimeSingle,
          end_time: endTime,
        }),
        getData({
          measurement: "Humidity",
          start_time: startTimeSingle,
          end_time: endTime,
        }),
        getData({
          measurement: "AirPressure",
          start_time: startTimeSingle,
          end_time: endTime,
        }),
    ])

      // Temperature Measurements
      if (Array.isArray(results[0]) && results[0].length > 0) {

        const outside_temps = results[0].filter((measurement) => measurement.field === "temperature_outside")
        const inside_temps = results[0].filter((measurement) => measurement.field === "temperature_inside")
        const up_temps = results[0].filter((measurement) => measurement.field === "temperature_up")

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

      // Humidity Measurements
      if (Array.isArray(results[1]) && results[1].length > 0) {

        const humidityMeasurements = results[1]
        setUpHumidityArray(humidityMeasurements)

        const latest_humidity = humidityMeasurements[humidityMeasurements.length - 1];
        setUpHumidity(roundToTwo(latest_humidity.value));

      } else {
        setUpHumidity(null);
      }

      // Air Pressure Measurements
      if (Array.isArray(results[2]) && results[2].length > 0) {

        const latest_air_pressure = results[2][results[2].length - 1];
        setAirPressure(Math.round(latest_air_pressure.value));

      } else {
        setAirPressure(null);
      }
    }

    fetchMeasurements();
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
          gridTemplateColumns: "220px 1fr 220px",
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
            label="Humidity"
            value={upHumidity}
            unit="%"
            color="rgba(85, 88, 193, 0.92)"
          />
        </div>

        <div
          style={{
            width: "100%"
          }}
        >
          <TimeseriesChart
            data={upHumidityArray}
            label="Humidity"
            unit="%"
            yAxisLabel="Humidity"
            color="rgba(85, 88, 193, 0.92)"
          />
        </div>

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
            width: "80px",
          }}
        >
          <SingleValueWidget
            label="AirPressure"
            value={airPressure}
            unit="hPa"
            color="rgba(212, 44, 10, 0.95)"
          />
        </div>
      </div>
    </div>
  );
}