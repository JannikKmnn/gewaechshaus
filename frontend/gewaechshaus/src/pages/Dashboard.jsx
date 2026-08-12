import { useEffect, useState } from "react";
import BinaryWidget from "../components/BinaryWidget";
import MultipleTimeseriesChart from "../components/MultipleCharts";
import TimeseriesChart from "../components/TimeseriesChart";
import SingleValueWidget from "../components/SingleValueWidget";
import { getData } from "../api/data";
import { getWindowIntervals } from "../api/windows";
import { temperatureToColor } from "../utils/color";
import { formatDateTime, isoAgo, isoWayOff } from "../utils/time";
import { ChevronLeft, ChevronRight, X } from "lucide-react";

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

  const [fullScreenMode, setFullScreenMode] = useState(false);
  const [fullScreenSensor, setFullScreenSensor] = useState("");

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

  async function activateFullScreenMode(sensor) {
    setFullScreenSensor(sensor);
    setFullScreenMode(true);
  }

  function renderFullScreen() {
    switch (fullScreenSensor) {
      case "temperature":
        return (
          <div
            style={{ display: "flex", alignItems: "center", height: "100%" }}
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
              height="220"
            />
          </div>
        );

      case "humidity":
        return (
          <div
            style={{ display: "flex", alignItems: "center", height: "100%" }}
          >
            <TimeseriesChart
              data={upHumidityArray}
              label="Humidity"
              unit="%"
              yAxisLabel="Humidity"
              color="rgba(85, 88, 193, 0.92)"
              height="220"
            />
          </div>
        );

      case "airpressure":
        return (
          <div
            style={{ display: "flex", alignItems: "center", height: "100%" }}
          >
            <TimeseriesChart
              data={airPressureArray}
              label="Air Pressure"
              unit="hPa"
              yAxisLabel="Air Pressure"
              color="rgba(186, 84, 40, 0.92)"
              height="220"
            />
          </div>
        );

      default:
        return null;
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
    <>
      {fullScreenMode == true ? (
        <div>
          <div style={{ float: "right" }}>
            <button
              style={{
                backgroundColor: "transparent",
                fontSize: "22px",
                color: "white",
                borderRadius: "5px",
                borderColor: "#2e2f31",
                alignItems: "center",
              }}
              onClick={() => [
                setFullScreenMode(false),
                setFullScreenSensor(""),
              ]}
            >
              <X />
            </button>
          </div>
          <div>{renderFullScreen()}</div>
        </div>
      ) : (
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
                backgroundColor: "transparent",
                fontSize: "18px",
                color: "white",
                borderRadius: "5px",
                borderColor: "#2e2f31",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                padding: 0,
              }}
              onClick={() => moveTimeWindow("back")}
            >
              <ChevronLeft />
            </button>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "48% 4% 48%",
                backgroundColor: "transparent",
                width: "100%",
                height: "30px",
                fontSize: "18px",
                color: "#2e2f31",
                borderRadius: "5px",
                border: "1px solid #2e2f31",
                alignItems: "center",
              }}
            >
              <div style={{ textAlign: "center", color: "white" }}>
                {formatDateTime(displayStartTimeSeries)}
              </div>
              <div style={{ color: "white" }}>-</div>
              <div style={{ textAlign: "center", color: "white" }}>
                {formatDateTime(endTimeSeries)}
              </div>
            </div>

            <button
              style={{
                backgroundColor: "transparent",
                fontSize: "18px",
                color: "white",
                borderRadius: "5px",
                borderColor: "#2e2f31",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                padding: 0,
              }}
              onClick={() => moveTimeWindow("front")}
            >
              <ChevronRight />
            </button>

            <label>
              <select
                name="timeRange"
                style={{
                  backgroundColor: "transparent",
                  width: "80%",
                  height: "30px",
                  fontSize: "20px",
                  color: "white",
                  borderRadius: "5px",
                  borderColor: "#2e2f31",
                }}
                value={timeSeriesDiff}
                onChange={(e) => setTimeSeriesDiff(e.target.value)}
              >
                <option style={{ backgroundColor: "#8ba288" }} value="5m">
                  5 minutes
                </option>
                <option style={{ backgroundColor: "#8ba288" }} value="30m">
                  30 minutes
                </option>
                <option style={{ backgroundColor: "#8ba288" }} value="1h">
                  1 hour
                </option>
                <option style={{ backgroundColor: "#8ba288" }} value="3h">
                  3 hours
                </option>
                <option style={{ backgroundColor: "#8ba288" }} value="6h">
                  6 hours
                </option>
                <option style={{ backgroundColor: "#8ba288" }} value="12h">
                  12 hours
                </option>
                <option style={{ backgroundColor: "#8ba288" }} value="1d">
                  1 day
                </option>
                <option style={{ backgroundColor: "#8ba288" }} value="3d">
                  3 days
                </option>
                <option style={{ backgroundColor: "#8ba288" }} value="7d">
                  1 week
                </option>
                <option style={{ backgroundColor: "#8ba288" }} value="14d">
                  2 weeks
                </option>
                <option style={{ backgroundColor: "#8ba288" }} value="30d">
                  30 days
                </option>
                <option style={{ backgroundColor: "#8ba288" }} value="60d">
                  60 days
                </option>
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
              className="hovering-panel"
              style={{
                borderRadius: "8px",
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
              className="hovering-panel"
              style={{
                borderRadius: "8px",
              }}
              onClick={() => activateFullScreenMode("temperature")}
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
              className="hovering-panel"
              style={{
                borderRadius: "8px",
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
              className="hovering-panel"
              style={{
                borderRadius: "8px",
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
              className="hovering-panel"
              style={{
                borderRadius: "8px",
              }}
              onClick={() => activateFullScreenMode("humidity")}
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
              className="hovering-panel"
              style={{
                borderRadius: "8px",
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
              className="hovering-panel"
              style={{
                borderRadius: "8px",
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
              className="hovering-panel"
              style={{
                borderRadius: "8px",
              }}
              onClick={() => activateFullScreenMode("airpressure")}
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
      )}
    </>
  );
}
