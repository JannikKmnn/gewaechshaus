import { useEffect, useState } from "react";
import BinaryWidget from "../components/BinaryWidget";
import { getWindowStatus } from "../api/windows";
import { formatDateTime } from "../utils/time";

export default function ControlCenter() {
  const [windowStatusLeft, setWindowStatusLeft] = useState(null);
  const [windowStatusRight, setWindowStatusRight] = useState(null);

  const [windowOpeningLeft, setWindowOpeningLeft] = useState(null);
  const [windowOpeningRight, setWindowOpeningRight] = useState(null);

  const [windowClosingLeft, setWindowClosingLeft] = useState(null);
  const [windowClosingRight, setWindowClosingRight] = useState(null);

  useEffect(() => {
    async function getWindowsStatus() {
      const results = await Promise.all([
        getWindowStatus({
          window_position: "left",
        }),
        getWindowStatus({
          window_position: "right",
        }),
      ])

      if (results.length === 2) {
        setWindowStatusLeft(results[0].status);
        setWindowStatusRight(results[1].status);
        setWindowOpeningLeft(results[0].last_opening);
        setWindowOpeningRight(results[1].last_opening);
        setWindowClosingLeft(results[0].last_closing);
        setWindowClosingRight(results[1].last_closing);
      }
      
    }

    getWindowsStatus();
  }, []);

  return (
    <div>
      <h1 style={{ marginBottom: "20px" }}>Control Center</h1>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "20px",
          marginBottom: "10px"
        }}
      >

        <BinaryWidget
          label="Window Left"
          value={windowStatusLeft}
          binary_value={windowStatusLeft == "closed" ? 1 : 0}
          color_false = "#3737d3"
          height="70px"
          fontsize="15px"
          fontsizelabel="12px"
        />

        <BinaryWidget
          label="Window Right"
          value={windowStatusRight}
          binary_value={windowStatusRight == "closed" ? 1 : 0}
          color_false = "#3737d3"
          height="70px"
          fontsize="15px"
          fontsizelabel="12px"
        />

      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "20px",
          marginBottom: "10px"
        }}
      >

        <div>
          <div>Last Opening: {formatDateTime(windowOpeningLeft)}</div>
          <div>Last Closing: {formatDateTime(windowClosingLeft)}</div>
        </div>

        <div>
          <div>Last Opening: {formatDateTime(windowOpeningRight)}</div>
          <div>Last Closing: {formatDateTime(windowClosingRight)}</div>
        </div>
      </div>
    
    </div>
  )
}