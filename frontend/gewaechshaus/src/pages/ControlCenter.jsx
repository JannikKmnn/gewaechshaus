import { useEffect, useState } from "react";
import BinaryWidget from "../components/BinaryWidget";
import { getWindowStatus } from "../api/windows";

export default function ControlCenter() {
  const [windowStatusLeft, setwindowStatusLeft] = useState(null);
  const [windowStatusRight, setwindowStatusRight] = useState(null);

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
        setwindowStatusLeft(results[0].status);
        setwindowStatusRight(results[1].status);
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
    
    </div>
  )
}