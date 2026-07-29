import { useEffect, useState } from "react";
import { getLastWatering } from "../api/watering";
import DoubleValueWidget from "../components/DoubleValueWidget";
import { formatDateTime } from "../utils/time";

export default function WateringControl() {
  const [lastWateringDatetime, setlastWateringDatetime] = useState(null);
  const [lastWateringDurationSeconds, setlastWateringDurationSeconds] = useState(null);

  async function getLatestWatering() {
    const result = await getLastWatering();

    console.log(result)

    setlastWateringDatetime(result.last_watering);
    setlastWateringDurationSeconds(result.last_watering_duration);

  }

  useEffect(() => {
    getLatestWatering();
  }, []);

  return (
      <div>
        <h1 style={{ marginBottom: "20px" }}>Control Center Watering</h1>

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
              value2={lastWateringDurationSeconds}
              unit1={""}
              unit2={"Seconds"}
              color="rgba(10, 138, 212, 0.95)"
            />
          </div>
        
      </div>
    )
}