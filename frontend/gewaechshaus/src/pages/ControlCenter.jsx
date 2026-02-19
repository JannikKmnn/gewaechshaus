import { useEffect, useState } from "react";
import BinaryWidget from "../components/BinaryWidget";
import DoubleValueWidget from "../components/DoubleValueWidget";
import { getWindowStatus, callWindowActuators } from "../api/windows";
import { formatDateTime, windowOpenTime } from "../utils/time";

export default function ControlCenter() {
  const [windowStatusLeft, setWindowStatusLeft] = useState(null);
  const [windowStatusRight, setWindowStatusRight] = useState(null);

  const [windowOpeningLeft, setWindowOpeningLeft] = useState(null);
  const [windowOpeningRight, setWindowOpeningRight] = useState(null);

  const [windowClosingLeft, setWindowClosingLeft] = useState(null);
  const [windowClosingRight, setWindowClosingRight] = useState(null);

  async function actOnWindows(movement, position=null) {
    const results = await callWindowActuators({
      operation: movement,
      window_position: position
    });
    if (position == "left") {
      setWindowStatusLeft(movement == "open" ? "open" : "close")
    }
    else if (position == "right") {
      setWindowStatusRight(movement == "open" ? "open" : "close")
    }
    else {
      setWindowStatusLeft(movement == "open" ? "open" : "close")
      setWindowStatusRight(movement == "open" ? "open" : "close")
    }
    return results
  };

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
  }, [windowStatusLeft, windowStatusRight]);

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
          gridTemplateColumns: "1fr 1fr 1fr 1fr",
          gap: "20px",
          marginBottom: "10px"
        }}
      >

        <DoubleValueWidget
          label={windowStatusLeft == "closed" ? "Last open time" : "Open for"}
          value1={windowOpenTime(windowOpeningLeft, windowClosingLeft)[Object.keys(windowOpenTime(windowOpeningLeft, windowClosingLeft))[0]]}
          value2={windowOpenTime(windowOpeningLeft, windowClosingLeft)[Object.keys(windowOpenTime(windowOpeningLeft, windowClosingLeft))[1]]}
          unit1={Object.keys(windowOpenTime(windowOpeningLeft, windowClosingLeft))[0] == "diffDays" ? "Days" 
            : Object.keys(windowOpenTime(windowOpeningLeft, windowClosingLeft))[0] == "diffHours" ? "Hours"
            : "Minutes"
          }
          unit2={Object.keys(windowOpenTime(windowOpeningLeft, windowClosingLeft))[1] == "diffHours" ? "Hours" 
            : Object.keys(windowOpenTime(windowOpeningLeft, windowClosingLeft))[1] == "diffMinutes" ? "Minutes"
            : "Seconds"
          }
          color="rgba(212, 44, 10, 0.95)"
        />

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr / 1fr",
            gap: "20px",
            marginBottom: "10px"
          }}
        >

          <div>
            <div>Last Opening: {formatDateTime(windowOpeningLeft)}</div>
            <div>Last Closing: {formatDateTime(windowClosingLeft)}</div>
          </div>

          <button style={{
            backgroundColor: "rgba(146, 204, 159, 0.92)",
            fontSize: "18px",
            color: "white",
            boxShadow: "0 4px 20px #3a3f3c",
            borderRadius: "5px",
            alignItems: "center"
          }}
          onClick={() => {windowStatusLeft == "closed" ? actOnWindows("open", "left")
            : actOnWindows("close", "left")
          }}>
            {windowStatusLeft == "closed" ? "Open Window" : "Close Window"}
          </button>

        </div>

        <DoubleValueWidget
          label={windowStatusRight == "closed" ? "Last open time" : "Open for"}
          value1={windowOpenTime(windowOpeningRight, windowClosingRight)[Object.keys(windowOpenTime(windowOpeningRight, windowClosingRight))[0]]}
          value2={windowOpenTime(windowOpeningRight, windowClosingRight)[Object.keys(windowOpenTime(windowOpeningRight, windowClosingRight))[1]]}
          unit1={Object.keys(windowOpenTime(windowOpeningRight, windowClosingRight))[0] == "diffDays" ? "Days" 
            : Object.keys(windowOpenTime(windowOpeningRight, windowClosingRight))[0] == "diffHours" ? "Hours"
            : "Minutes"
          }
          unit2={Object.keys(windowOpenTime(windowOpeningRight, windowClosingRight))[1] == "diffHours" ? "Hours" 
            : Object.keys(windowOpenTime(windowOpeningRight, windowClosingRight))[1] == "diffMinutes" ? "Minutes"
            : "Seconds"
          }
          color="rgba(212, 44, 10, 0.95)"
        />

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr / 1fr",
            gap: "20px",
            marginBottom: "10px"
          }}
        >

          <div>
            <div>Last Opening: {formatDateTime(windowOpeningRight)}</div>
            <div>Last Closing: {formatDateTime(windowClosingRight)}</div>
          </div>

          <button style={{
            backgroundColor: "rgba(146, 204, 159, 0.92)",
            fontSize: "18px",
            color: "white",
            boxShadow: "0 4px 20px #3a3f3c",
            borderRadius: "5px",
            alignItems: "center"
          }}
          onClick={() => {windowStatusRight == "closed" ? actOnWindows("open", "right")
            : actOnWindows("close", "right")
          }}>
            {windowStatusRight == "closed" ? "Open Window" : "Close Window"}
          </button>

        </div>

      </div>
    
    </div>
  )
}