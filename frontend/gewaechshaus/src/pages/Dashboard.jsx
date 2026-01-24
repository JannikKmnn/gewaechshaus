import { useEffect, useState } from "react";
import BinaryWidget from "../components/BinaryWidget";
import MultipleTimeseriesChart from "../components/MultipleCharts";
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
  const [soilMoistureFront, setSoilMoistureFront] = useState(null);
  const [soilMoistureBack, setSoilMoistureBack] = useState(null);

  const [temperatureArray, setTemperatureArray] = useState([]);
  const [upHumidityArray, setUpHumidityArray] = useState([]);
  const [airPressureArray, setAirPressureArray] = useState([]);

  const endTimeSingle = new Date().toISOString();
  const startTimeSingle = new Date(Date.now() - 2 * 60 * 1000).toISOString();

  const endTimeSeries =new Date().toISOString();
  const startTimeSeries = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

  const roundToTwo = (num) => Math.round(num * 100) / 100;

  useEffect(() => {
    async function fetchMeasurementsSingle() {
      const results = await Promise.all([
        getData({
          measurement: "Temperature",
          start_time: startTimeSingle,
          end_time: endTimeSingle,
        }),
        getData({
          measurement: "Humidity",
          start_time: startTimeSingle,
          end_time: endTimeSingle,
        }),
        getData({
          measurement: "AirPressure",
          start_time: startTimeSingle,
          end_time: endTimeSingle,
        }),
        getData({
          measurement: "SoilMoisture",
          start_time: startTimeSingle,
          end_time: endTimeSingle,
        }),
      ])

      // Temperature Measurements
      if (Array.isArray(results[0]) && results[0].length > 0) {

        const temperatureMeasurements = results[0]

        const outside_temps = temperatureMeasurements.filter((measurement) => measurement.field === "temperature_outside")
        const inside_temps = temperatureMeasurements.filter((measurement) => measurement.field === "temperature_inside")
        const up_temps = temperatureMeasurements.filter((measurement) => measurement.field === "temperature_up")

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

        const latest_humidity = results[1][results[1].length - 1];
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

      // Soil Moisture Measurements
      if (Array.isArray(results[3]) && results[3].length > 0) {

        const soilMoistureMeasurements = results[3]

        const back_sm = soilMoistureMeasurements.filter((measurement) => measurement.field === "soil_moisture_back")
        const front_sm = soilMoistureMeasurements.filter((measurement) => measurement.field === "soil_moisture_front")

        const latest_back = back_sm[back_sm.length - 1]
        setSoilMoistureBack(latest_back.value)

        const latest_front = front_sm[front_sm.length - 1]
        setSoilMoistureFront(latest_front.value)

      } else {
        setSoilMoistureBack(null);
        setSoilMoistureFront(null);
      }
    }

    async function fetchMeasurementsSeries() {
      const results = await Promise.all([
        getData({
          measurement: "Temperature",
          start_time: startTimeSeries,
          end_time: endTimeSeries,
        }),
        getData({
          measurement: "Humidity",
          start_time: startTimeSeries,
          end_time: endTimeSeries,
        }),
        getData({
          measurement: "AirPressure",
          start_time: startTimeSeries,
          end_time: endTimeSeries,
        }),
      ])

      // Temperature Measurements
      if (Array.isArray(results[0]) && results[0].length > 0) {
        setTemperatureArray(results[0]);
      } else {
        setTemperatureArray([]);
      }

      // Humidity Measurements
      if (Array.isArray(results[1]) && results[1].length > 0) {
        setUpHumidityArray(results[1]);
      } else {
        setUpHumidityArray([]);
      }

      // Air Pressure Measurements
      if (Array.isArray(results[2]) && results[2].length > 0) {
        setAirPressureArray(results[2]);
      } else {
        setAirPressureArray([]);
      }
    }

    fetchMeasurementsSingle();
    fetchMeasurementsSeries();
  }, []);

  return (
    <div>
      <h1 style={{ marginBottom: "20px" }}>Sensor Measurements</h1>

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
            label="Outside"
            value={outsideTemp}
            unit="°C"
            color={temperatureToColor(outsideTemp)}
          />
        </div>

        <div
          style={{
            width: "100%"
          }}
        >
          <MultipleTimeseriesChart
            data={temperatureArray}
            exclude="temperature_cpu"
            label="Temperature"
            unit="°C"
            yAxisLabel="Temperature"
            color="rgba(85, 88, 193, 0.92)"
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
          gridTemplateColumns: "220px 1fr 220px",
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
            label="Air Pressure"
            value={airPressure}
            unit="hPa"
            color="rgba(212, 44, 10, 0.95)"
          />
        </div>

        <div
          style={{
            width: "100%",
          }}
        >
          <TimeseriesChart
            data={airPressureArray}
            label="Air Pressure"
            unit="hPa"
            yAxisLabel="Air Pressure"
            color="rgba(186, 84, 40, 0.92)"
          />
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr / 1fr",
            gap: "10px",
            marginBottom: "10px"
          }}
        >
            <div style={{
              width: "100%",
              height: "50%"
            }}>
              <BinaryWidget
                label="Soil Moisture Back"
                value={soilMoistureBack}
                binary_value={soilMoistureBack == "wet" ? 1 : 0}
                height="70px"
                fontsize="15px"
                fontsizelabel="12px"
              />
            </div>

            <div style={{
              width: "100%",
              height: "50%"
            }}>

              <BinaryWidget
                label="Soil Moisture Front"
                value={soilMoistureFront}
                binary_value={soilMoistureFront == "wet" ? 1 : 0}
                height="70px"
                fontsize="15px"
                fontsizelabel="12px"
              />
            </div>
        </div>
      </div>
    </div>
  );
}