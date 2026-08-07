import { useEffect, useState } from "react";
import BinaryWidget from "../components/BinaryWidget";
import MultipleTimeseriesChart from "../components/MultipleCharts";
import TimeseriesChart from "../components/TimeseriesChart";
import SingleValueWidget from "../components/SingleValueWidget";
import { getData } from "../api/data";
import { getWindowIntervals } from "../api/windows";
import { temperatureToColor } from "../utils/color";
import { formatDateTime, isoAgo, isoWayOff } from "../utils/time";

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

  const [windowOpeningIntervals, setWindowOpeningIntervals] = useState([]);

  const endTimeSingle = new Date().toISOString();
  const startTimeSingle = isoAgo("2m");

  const [timeSeriesDiff, setTimeSeriesDiff] = useState("1d");

  const [endTimeSeries, setEndTimeSeries] = useState(new Date().toISOString());
  const displayStartTimeSeries = isoAgo(timeSeriesDiff, endTimeSeries);

  const roundToTwo = (num) => Math.round(num * 100) / 100;

  async function moveTimeWindow(direction) {
    if (direction == "back") {
      setEndTimeSeries((prev) => isoAgo(timeSeriesDiff, prev));
    } else if (direction == "front") {
      setEndTimeSeries((prev) => {
        const now = new Date().toISOString();
        const next = isoWayOff(timeSeriesDiff, prev);

        if (new Date(next) > new Date(now)) {
          return prev;
        }
        return next;
      });
    }
  }

  useEffect(() => {
    const startTimeSeries = isoAgo(timeSeriesDiff, endTimeSeries);

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
      ]);

      // Temperature Measurements
      if (Array.isArray(results[0]) && results[0].length > 0) {
        const temperatureMeasurements = results[0];

        const outside_temps = temperatureMeasurements.filter(
          (measurement) => measurement.field === "temperature_outside",
        );
        const inside_temps = temperatureMeasurements.filter(
          (measurement) => measurement.field === "temperature_inside",
        );
        const up_temps = temperatureMeasurements.filter(
          (measurement) => measurement.field === "temperature_up",
        );

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
        const soilMoistureMeasurements = results[3];

        const back_sm = soilMoistureMeasurements.filter(
          (measurement) => measurement.field === "soil_moisture_back",
        );
        const front_sm = soilMoistureMeasurements.filter(
          (measurement) => measurement.field === "soil_moisture_front",
        );

        const latest_back = back_sm[back_sm.length - 1];
        setSoilMoistureBack(latest_back.value);

        const latest_front = front_sm[front_sm.length - 1];
        setSoilMoistureFront(latest_front.value);
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
        getWindowIntervals({
          start_time: startTimeSeries,
          end_time: endTimeSeries,
        }),
      ]);

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

      // Window Opening Intervals
      if (Array.isArray(results[3]) && results[3].length > 0) {
        setWindowOpeningIntervals(results[3]);
      } else {
        setWindowOpeningIntervals([]);
      }
    }

    fetchMeasurementsSingle();
    fetchMeasurementsSeries();
  }, [timeSeriesDiff, endTimeSeries]);

  return (
    <div>
      <h1>Sensor Measurements</h1>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "36% 2% 40% 2% 20%",
          gap: "10px",
          marginBottom: "15px",
        }}
      >
        <div></div>

        <button
          style={{
            backgroundColor: "rgba(146, 204, 159, 0.92)",
            fontSize: "18px",
            color: "white",
            boxShadow: "0 4px 20px #3a3f3c",
            borderRadius: "5px",
            alignItems: "center",
          }}
          onClick={() => moveTimeWindow("back")}
        >
          {"<"}
        </button>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "48% 4% 48%",
            backgroundColor: "rgba(146, 204, 159, 0.92)",
            width: "100%",
            height: "30px",
            fontSize: "18px",
            color: "white",
            boxShadow: "0 4px 20px #3a3f3c",
            borderRadius: "5px",
            alignItems: "center",
          }}
        >
          <div style={{ textAlign: "center" }}>
            {formatDateTime(displayStartTimeSeries)}
          </div>
          <div>-</div>
          <div style={{ textAlign: "center" }}>
            {formatDateTime(endTimeSeries)}
          </div>
        </div>

        <button
          style={{
            backgroundColor: "rgba(146, 204, 159, 0.92)",
            fontSize: "18px",
            color: "white",
            boxShadow: "0 4px 20px #3a3f3c",
            borderRadius: "5px",
            alignItems: "center",
          }}
          onClick={() => moveTimeWindow("front")}
        >
          {">"}
        </button>

        <label>
          <select
            name="timeRange"
            style={{
              backgroundColor: "rgba(146, 204, 159, 0.92)",
              width: "80%",
              height: "30px",
              fontSize: "20px",
              color: "white",
              boxShadow: "0 4px 20px #3a3f3c",
              borderRadius: "5px",
            }}
            value={timeSeriesDiff}
            onChange={(e) => setTimeSeriesDiff(e.target.value)}
          >
            <option value="5m">5 minutes</option>
            <option value="30m">30 minutes</option>
            <option value="1h">1 hour</option>
            <option value="3h">3 hours</option>
            <option value="6h">6 hours</option>
            <option value="12h">12 hours</option>
            <option value="1d">1 day</option>
            <option value="3d">3 days</option>
            <option value="7d">1 week</option>
            <option value="14d">2 weeks</option>
            <option value="30d">30 days</option>
            <option value="60d">60 days</option>
          </select>
        </label>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "220px 1fr 220px",
          gap: "20px",
          marginBottom: "10px",
        }}
      >
        <div
          style={{
            width: "80px",
          }}
        >
          <SingleValueWidget
            label="Outside (Current)"
            value={outsideTemp}
            unit="°C"
            color={temperatureToColor(outsideTemp)}
          />
        </div>

        <div
          style={{
            width: "100%",
          }}
        >
          <MultipleTimeseriesChart
            data={temperatureArray}
            intervals={windowOpeningIntervals}
            startTime={displayStartTimeSeries}
            endTime={endTimeSeries}
            exclude="temperature_cpu"
            label="Temperature"
            unit="°C"
            yAxisLabel="Temperature"
            color="rgba(85, 88, 193, 0.92)"
          />
        </div>

        <div
          style={{
            justifySelf: "end",
          }}
        >
          <SingleValueWidget
            label="Inside Up (Current)"
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
          marginBottom: "10px",
        }}
      >
        <div
          style={{
            width: "80px",
          }}
        >
          <SingleValueWidget
            label="Humidity (Current)"
            value={upHumidity}
            unit="%"
            color="rgba(85, 88, 193, 0.92)"
          />
        </div>

        <div
          style={{
            width: "100%",
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
            label="Inside (Current)"
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
          marginBottom: "10px",
        }}
      >
        <div
          style={{
            width: "80px",
          }}
        >
          <SingleValueWidget
            label="Air Pressure (Current)"
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
            marginBottom: "10px",
          }}
        >
          <div
            style={{
              width: "100%",
              height: "50%",
            }}
          >
            <BinaryWidget
              label="Soil Moisture Back (Current)"
              value={soilMoistureBack}
              binary_value={soilMoistureBack == "wet" ? 1 : 0}
              height="70px"
              fontsize="15px"
              fontsizelabel="12px"
            />
          </div>

          <div
            style={{
              width: "100%",
              height: "50%",
            }}
          >
            <BinaryWidget
              label="Soil Moisture Front (Current)"
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
