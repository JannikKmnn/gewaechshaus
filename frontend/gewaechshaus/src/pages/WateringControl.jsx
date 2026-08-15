import { useEffect, useState } from "react";
import { Check, Pencil } from "lucide-react";
import {
  getLastWatering,
  getWateringEvents,
  runWatering,
} from "../api/watering";
import DoubleValueWidget from "../components/DoubleValueWidget";
import TimeBarChart from "../components/TimeBarChart";
import { formatDateTime, formatDuration, isoAgo } from "../utils/time";

export default function WateringControl() {
  const [lastWateringDatetime, setlastWateringDatetime] = useState(null);
  const [lastWateringDurationSeconds, setlastWateringDurationSeconds] =
    useState(null);

  const [wateringDays, setWateringDays] = useState([]);

  const [wateringCallMinutes, setWateringCallMinutes] = useState(15);
  const [wateringCallSeconds, setWateringCallSeconds] = useState(0);

  const [wateringRunning, setWateringRunning] = useState(false);

  const [editingDuration, setEditingDuration] = useState(false);
  const [editedDurationMinutes, setEditedDurationMinutes] = useState(15);
  const [editedDurationSeconds, setEditedDurationSeconds] = useState(0);

  const [dateTimeDiff, setDateTimeDiff] = useState("14d");
  const [endDateTime, setEndDateTime] = useState(new Date().toISOString());
  const startDateTime = isoAgo(dateTimeDiff, endDateTime);
  const lastWateringDuration = formatDuration(lastWateringDurationSeconds);

  async function getLatestWatering() {
    const result = await getLastWatering();

    setlastWateringDatetime(result.last_watering);
    setlastWateringDurationSeconds(result.last_watering_duration);
  }

  async function getWateringDates() {
    const wateringEvents = await getWateringEvents({
      start_datetime: startDateTime,
      end_datetime: endDateTime,
    });

    const aggregated = Object.entries(
      wateringEvents.reduce((acc, [timestamp, value]) => {
        const day = timestamp.slice(0, 10);

        acc[day] = (acc[day] || 0) + value;
        return acc;
      }, {}),
    ).map(([date, duration_seconds]) => ({
      date,
      duration_seconds,
    }));

    setWateringDays(aggregated);
  }

  async function handleSaveDuration() {
    const minutes = Number(editedDurationMinutes);
    const seconds = Number(editedDurationSeconds);

    setWateringCallMinutes(minutes);
    setWateringCallSeconds(seconds);
    setEditingDuration(false);
  }

  async function handleRunWatering() {
    setWateringRunning(true);

    try {
      const watering_time_seconds =
        Number(wateringCallMinutes) * 60 + Number(wateringCallSeconds);

      await runWatering({ watering_time_seconds });

      await getLatestWatering();
    } catch (error) {
      console.error("Watering failed:", error);
    } finally {
      setWateringRunning(false);
    }
  }

  useEffect(() => {
    getLatestWatering();
    getWateringDates();
  }, []);

  return (
    <div>
      <div
        style={{
          position: "relative",
        }}
      >
        <h1 style={{ marginBottom: "20px" }}>Control Center Watering</h1>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr / 1fr",
            gap: "20px",
            marginBottom: "10px",
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "20px",
              marginBottom: "10px",
            }}
          >
            <DoubleValueWidget
              label={"Last Watering"}
              value1={formatDateTime(lastWateringDatetime)}
              value2={
                lastWateringDuration.minutes +
                " Minutes, " +
                lastWateringDuration.seconds +
                " Seconds"
              }
              unit1={""}
              unit2={""}
              color="rgba(17, 84, 123, 0.95)"
            />

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr / 1fr",
                gap: "20px",
                marginBottom: "10px",
              }}
            >
              <div>
                Run watering for {wateringCallMinutes} minutes and{" "}
                {wateringCallSeconds} seconds.{" "}
                <button
                  onClick={() => {
                    setEditedDurationMinutes(wateringCallMinutes);
                    setEditedDurationSeconds(wateringCallSeconds);
                    setEditingDuration(true);
                  }}
                  style={{
                    background: "none",
                    border: "none",
                    padding: 0,
                    marginLeft: "6px",
                    color: "white",
                    cursor: "pointer",
                    display: "inline-flex",
                    verticalAlign: "middle",
                  }}
                >
                  <Pencil size={14} />
                </button>{" "}
                {editingDuration && (
                  <div
                    style={{
                      position: "relative",
                      top: "-10px",
                      left: "0",
                      zIndex: 20,
                      whiteSpace: "nowrap",
                      width: "fit-content",

                      display: "flex",
                      alignItems: "center",
                      gap: "8px",

                      background: "#",
                      padding: "8px 10px",
                      borderRadius: "8px",
                      boxShadow: "0 4px 15px rgba(0, 0, 0, 0.25)",
                    }}
                  >
                    <input
                      type="number"
                      step="1"
                      value={editedDurationMinutes}
                      onChange={(e) => {
                        const value = e.target.value;

                        if (/^\d*$/.test(value)) {
                          setEditedDurationMinutes(value);
                        }
                      }}
                      style={{
                        width: "50px",
                        height: "30px",
                        textAlign: "center",
                        fontSize: "16px",
                        border: "1px solid #2e2f31",
                        borderRadius: "4px",
                      }}
                    />

                    <div
                      style={{
                        textAlign: "center",
                        fontSize: "16px",
                      }}
                    >
                      Minutes
                    </div>

                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                      }}
                    >
                      <button
                        onClick={() =>
                          setEditedDurationMinutes((value) => Number(value) + 1)
                        }
                        style={{
                          background: "none",
                          border: "none",
                          padding: 0,
                          height: "15px",
                          cursor: "pointer",
                          fontSize: "10px",
                        }}
                      >
                        ▲
                      </button>

                      <button
                        onClick={() =>
                          setEditedDurationMinutes((value) =>
                            Math.max(0, Number(value) - 1),
                          )
                        }
                        style={{
                          background: "none",
                          border: "none",
                          padding: 0,
                          height: "15px",
                          cursor: "pointer",
                          fontSize: "10px",
                        }}
                      >
                        ▼
                      </button>
                    </div>

                    <input
                      type="number"
                      step="1"
                      value={editedDurationSeconds}
                      onChange={(e) => {
                        const value = e.target.value;

                        if (/^\d*$/.test(value)) {
                          setEditedDurationSeconds(value);
                        }
                      }}
                      style={{
                        width: "50px",
                        height: "30px",
                        textAlign: "center",
                        fontSize: "16px",
                        border: "1px solid #2e2f31",
                        borderRadius: "4px",
                      }}
                    />

                    <div
                      style={{
                        textAlign: "center",
                        fontSize: "16px",
                      }}
                    >
                      Seconds
                    </div>

                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                      }}
                    >
                      <button
                        onClick={() =>
                          setEditedDurationSeconds((value) => Number(value) + 1)
                        }
                        style={{
                          background: "none",
                          border: "none",
                          padding: 0,
                          height: "15px",
                          cursor: "pointer",
                          fontSize: "10px",
                        }}
                      >
                        ▲
                      </button>

                      <button
                        onClick={() =>
                          setEditedDurationSeconds((value) =>
                            Math.max(0, Number(value) - 1),
                          )
                        }
                        style={{
                          background: "none",
                          border: "none",
                          padding: 0,
                          height: "15px",
                          cursor: "pointer",
                          fontSize: "10px",
                        }}
                      >
                        ▼
                      </button>
                    </div>

                    <button
                      onClick={handleSaveDuration}
                      style={{
                        background: "none",
                        border: "none",
                        padding: 0,
                        color: "#2e2f31",
                        cursor: "pointer",
                      }}
                    >
                      <Check size={18} />
                    </button>
                  </div>
                )}
              </div>
              <button
                style={{
                  backgroundColor: "transparent",
                  fontSize: "18px",
                  color: "rgba(17, 84, 123, 0.95)",
                  boxShadow: "0 4px 20px #3a3f3c",
                  borderRadius: "5px",
                  alignItems: "center",
                  opacity: wateringRunning ? 0.6 : 1,
                }}
                onClick={() => {
                  handleRunWatering();
                }}
                disabled={wateringRunning}
              >
                {wateringRunning ? "Watering in progress..." : "Run Watering"}
              </button>
            </div>
          </div>

          <div>
            <TimeBarChart
              data={wateringDays}
              dataKeyxAxis={"date"}
              dataKeybar={"duration_seconds"}
              unit={"s"}
              yAxisLabel={"Duration"}
            />
          </div>
        </div>
      </div>
      {editingDuration && (
        <div
          onClick={() => {
            setEditingDuration(false);
          }}
          style={{
            position: "absolute",
            inset: 0,
            backgroundColor: "rgba(0, 0, 0, 0.15)",
            zIndex: 10,
            pointerEvents: "auto",
          }}
        />
      )}
    </div>
  );
}
