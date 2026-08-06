import { useEffect, useState } from "react";
import { getLastWatering, getWateringEvents } from "../api/watering";
import DoubleValueWidget from "../components/DoubleValueWidget";
import TimeBarChart from "../components/TimeBarChart";
import { formatDateTime, formatDuration, isoAgo } from "../utils/time";

export default function WateringControl() {
  const [lastWateringDatetime, setlastWateringDatetime] = useState(null);
  const [lastWateringDurationSeconds, setlastWateringDurationSeconds] = useState(null);

  const [wateringDays, setWateringDays] = useState([]);

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
      end_datetime: endDateTime
    });

    const aggregated = Object.entries(
      wateringEvents.reduce((acc, [timestamp, value]) => {
        const day = timestamp.slice(0, 10);

        acc[day] = (acc[day] || 0) + value;
        return acc;
      }, {})
    ).map(([date, duration_seconds]) => ({
      date,
      duration_seconds,
    }));

    console.log(aggregated);

    setWateringDays(aggregated);
  }

  useEffect(() => {
    getLatestWatering();
    getWateringDates();
  }, []);

  return (
      <div>
        <h1 style={{ marginBottom: "20px" }}>Control Center Watering</h1>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr / 1fr",
              gap: "20px",
              marginBottom: "10px"
            }}
          >

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "20px",
                marginBottom: "10px"
              }}
            >
              <DoubleValueWidget
                label={"Last Watering"}
                value1={formatDateTime(lastWateringDatetime)}
                value2={lastWateringDuration.minutes + " Minutes, " + lastWateringDuration.seconds + " Seconds"}
                unit1={""}
                unit2={""}
                color="rgba(10, 138, 212, 0.95)"
              />
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
    )
}
