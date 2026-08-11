import { useEffect, useState } from "react";
import { Check, Pencil } from "lucide-react";
import BinaryWidget from "../components/BinaryWidget";
import DoubleValueWidget from "../components/DoubleValueWidget";
import {
  getWindowConfigs,
  getWindowStatus,
  callWindowActuators,
  updateWindowConfig,
} from "../api/windows";
import { formatDateTime, windowOpenTime } from "../utils/time";

export default function WindowControl() {
  const [windowStatusLeft, setWindowStatusLeft] = useState(null);
  const [windowStatusRight, setWindowStatusRight] = useState(null);

  const [windowOpeningLeft, setWindowOpeningLeft] = useState(null);
  const [windowOpeningRight, setWindowOpeningRight] = useState(null);

  const [windowClosingLeft, setWindowClosingLeft] = useState(null);
  const [windowClosingRight, setWindowClosingRight] = useState(null);

  const [editingThresholdLeft, setEditingThresholdLeft] = useState(false);
  const [editedThresholdLeft, setEditedThresholdLeft] = useState(null);
  const [windowTempThresholdLeft, setWindowTempThresholdLeft] = useState(null);

  const [editingThresholdRight, setEditingThresholdRight] = useState(false);
  const [editedThresholdRight, setEditedThresholdRight] = useState(null);
  const [windowTempThresholdRight, setWindowTempThresholdRight] =
    useState(null);

  const [loadingLeft, setLoadingLeft] = useState(false);
  const [loadingRight, setLoadingRight] = useState(false);

  async function actOnWindows(movement, position = null) {
    if (position === "left") setLoadingLeft(true);
    if (position === "right") setLoadingRight(true);

    if (position == null) {
      setLoadingLeft(true);
      setLoadingRight(true);
    }

    await callWindowActuators({
      operation: movement,
      window_position: position,
    });

    await getWindowsStatus();

    setLoadingLeft(false);
    setLoadingRight(false);
  }

  async function getWindowsStatus() {
    const results = await Promise.all([
      getWindowStatus({
        window_position: "left",
      }),
      getWindowStatus({
        window_position: "right",
      }),
    ]);

    if (results.length === 2) {
      setWindowStatusLeft(results[0].status);
      setWindowStatusRight(results[1].status);
      setWindowOpeningLeft(results[0].last_opening);
      setWindowOpeningRight(results[1].last_opening);
      setWindowClosingLeft(results[0].last_closing);
      setWindowClosingRight(results[1].last_closing);
    }
  }

  async function getWindowsConfig() {
    const results = await Promise.all([
      getWindowConfigs({
        window_position: "left",
      }),
      getWindowConfigs({
        window_position: "right",
      }),
    ]);

    if (results.length === 2) {
      setWindowTempThresholdLeft(
        results[0].inside_temperature_opening_threshold,
      );
      setEditedThresholdLeft(results[0].inside_temperature_opening_threshold);
      setEditingThresholdLeft(false);
      setWindowTempThresholdRight(
        results[1].inside_temperature_opening_threshold,
      );
      setEditedThresholdRight(results[1].inside_temperature_opening_threshold);
      setEditingThresholdRight(false);
    }
  }

  async function handleSaveThresholdLeft() {
    const threshold = Number(editedThresholdLeft);

    if (!Number.isInteger(threshold)) {
      return;
    }

    try {
      await updateWindowConfig({
        window_position: "left",
        config: {
          window_position: "left",
          inside_temperature_opening_threshold: threshold,
        },
      });

      setWindowTempThresholdLeft(threshold);
      setEditingThresholdLeft(false);
    } catch (error) {
      console.error("Failed to update left window configuration:", error);
    }
  }

  async function handleSaveThresholdRight() {
    const threshold = Number(editedThresholdRight);

    if (!Number.isInteger(threshold)) {
      return;
    }

    try {
      await updateWindowConfig({
        window_position: "right",
        config: {
          window_position: "right",
          inside_temperature_opening_threshold: threshold,
        },
      });

      setWindowTempThresholdRight(threshold);
      setEditingThresholdRight(false);
    } catch (error) {
      console.error("Failed to update right window configuration:", error);
    }
  }

  useEffect(() => {
    getWindowsStatus();
    getWindowsConfig();
  }, []);

  return (
    <div>
      <div
        style={{
          position: "relative",
        }}
      >
        <h1 style={{ marginBottom: "20px" }}>Control Center Windows</h1>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "20px",
            marginBottom: "10px",
          }}
        >
          <BinaryWidget
            label="Window Left"
            value={windowStatusLeft}
            binary_value={windowStatusLeft == "closed" ? 1 : 0}
            color_false="#3737d3"
            height="70px"
            fontsize="15px"
            fontsizelabel="12px"
          />

          <BinaryWidget
            label="Window Right"
            value={windowStatusRight}
            binary_value={windowStatusRight == "closed" ? 1 : 0}
            color_false="#3737d3"
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
            marginBottom: "10px",
          }}
        >
          <DoubleValueWidget
            label={windowStatusLeft == "closed" ? "Last open time" : "Open for"}
            value1={
              windowOpenTime(windowOpeningLeft, windowClosingLeft)[
                Object.keys(
                  windowOpenTime(windowOpeningLeft, windowClosingLeft),
                )[0]
              ]
            }
            value2={
              windowOpenTime(windowOpeningLeft, windowClosingLeft)[
                Object.keys(
                  windowOpenTime(windowOpeningLeft, windowClosingLeft),
                )[1]
              ]
            }
            unit1={
              Object.keys(
                windowOpenTime(windowOpeningLeft, windowClosingLeft),
              )[0] == "diffDays"
                ? "Days"
                : Object.keys(
                      windowOpenTime(windowOpeningLeft, windowClosingLeft),
                    )[0] == "diffHours"
                  ? "Hours"
                  : "Minutes"
            }
            unit2={
              Object.keys(
                windowOpenTime(windowOpeningLeft, windowClosingLeft),
              )[1] == "diffHours"
                ? "Hours"
                : Object.keys(
                      windowOpenTime(windowOpeningLeft, windowClosingLeft),
                    )[1] == "diffMinutes"
                  ? "Minutes"
                  : "Seconds"
            }
            color="rgba(212, 44, 10, 0.95)"
          />

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr / 1fr / 1fr",
              gap: "20px",
              marginBottom: "10px",
            }}
          >
            <div>
              <div style={{ color: "#2e2f31" }}>
                Last Opening: {formatDateTime(windowOpeningLeft)}
              </div>
              <div style={{ color: "#2e2f31" }}>
                Last Closing: {formatDateTime(windowClosingLeft)}
              </div>
            </div>

            <div>
              Opens when temperature inside exceeds{" "}
              <span style={{ color: "yellow" }}>
                {windowTempThresholdLeft}°C
              </span>
              <button
                onClick={() => {
                  setEditedThresholdLeft(windowTempThresholdLeft);
                  setEditingThresholdLeft(true);
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
              for 15 minutes.
              {editingThresholdLeft && (
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

                    background: "#8ba288",
                    padding: "8px 10px",
                    borderRadius: "8px",
                    boxShadow: "0 4px 15px rgba(0, 0, 0, 0.25)",
                  }}
                >
                  <input
                    type="number"
                    step="1"
                    value={editedThresholdLeft}
                    onChange={(e) => {
                      const value = e.target.value;

                      if (/^\d*$/.test(value)) {
                        setEditedThresholdLeft(value);
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
                    °C
                  </div>

                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                    }}
                  >
                    <button
                      onClick={() =>
                        setEditedThresholdLeft((value) => Number(value) + 1)
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
                        setEditedThresholdLeft((value) =>
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
                    onClick={handleSaveThresholdLeft}
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
                color: "#2e2f31",
                boxShadow: "0 4px 20px #3a3f3c",
                borderRadius: "5px",
                alignItems: "center",
                opacity: loadingRight ? 0.6 : 1,
              }}
              onClick={() => {
                windowStatusLeft == "closed"
                  ? actOnWindows("open", "left")
                  : actOnWindows("close", "left");
              }}
              disabled={loadingLeft}
            >
              {loadingLeft
                ? "Moving..."
                : windowStatusLeft == "closed"
                  ? "Open Window"
                  : "Close Window"}
            </button>
          </div>

          <DoubleValueWidget
            label={
              windowStatusRight == "closed" ? "Last open time" : "Open for"
            }
            value1={
              windowOpenTime(windowOpeningRight, windowClosingRight)[
                Object.keys(
                  windowOpenTime(windowOpeningRight, windowClosingRight),
                )[0]
              ]
            }
            value2={
              windowOpenTime(windowOpeningRight, windowClosingRight)[
                Object.keys(
                  windowOpenTime(windowOpeningRight, windowClosingRight),
                )[1]
              ]
            }
            unit1={
              Object.keys(
                windowOpenTime(windowOpeningRight, windowClosingRight),
              )[0] == "diffDays"
                ? "Days"
                : Object.keys(
                      windowOpenTime(windowOpeningRight, windowClosingRight),
                    )[0] == "diffHours"
                  ? "Hours"
                  : "Minutes"
            }
            unit2={
              Object.keys(
                windowOpenTime(windowOpeningRight, windowClosingRight),
              )[1] == "diffHours"
                ? "Hours"
                : Object.keys(
                      windowOpenTime(windowOpeningRight, windowClosingRight),
                    )[1] == "diffMinutes"
                  ? "Minutes"
                  : "Seconds"
            }
            color="rgba(212, 44, 10, 0.95)"
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
              <div style={{ color: "#2e2f31" }}>
                Last Opening: {formatDateTime(windowOpeningRight)}
              </div>
              <div style={{ color: "#2e2f31" }}>
                Last Closing: {formatDateTime(windowClosingRight)}
              </div>
            </div>

            <div>
              Opens when temperature inside exceeds{" "}
              <span style={{ color: "yellow" }}>
                {windowTempThresholdRight}°C
              </span>
              <button
                onClick={() => {
                  setEditedThresholdRight(windowTempThresholdRight);
                  setEditingThresholdRight(true);
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
              for 15 minutes.
              {editingThresholdRight && (
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
                    value={editedThresholdRight}
                    onChange={(e) => {
                      const value = e.target.value;

                      if (/^\d*$/.test(value)) {
                        setEditedThresholdRight(value);
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
                    °C
                  </div>

                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                    }}
                  >
                    <button
                      onClick={() =>
                        setEditedThresholdRight((value) => Number(value) + 1)
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
                        setEditedThresholdRight((value) =>
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
                    onClick={handleSaveThresholdRight}
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
                color: "#2e2f31",
                boxShadow: "0 4px 20px #3a3f3c",
                borderRadius: "5px",
                alignItems: "center",
                opacity: loadingRight ? 0.6 : 1,
              }}
              onClick={() => {
                windowStatusRight == "closed"
                  ? actOnWindows("open", "right")
                  : actOnWindows("close", "right");
              }}
              disabled={loadingRight}
            >
              {loadingRight
                ? "Moving..."
                : windowStatusRight === "closed"
                  ? "Open Window"
                  : "Close Window"}
            </button>
          </div>
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <button
            style={{
              backgroundColor: "transparent",
              fontSize: "18px",
              color: "#2e2f31",
              boxShadow: "0 4px 20px #3a3f3c",
              borderRadius: "5px",
              alignItems: "center",
              minWidth: "220px",
              minHeight: "90px",
              opacity: loadingRight && loadingLeft ? 0.6 : 1,
            }}
            onClick={() => {
              windowStatusRight == "closed" && windowStatusLeft == "closed"
                ? actOnWindows("open")
                : windowStatusRight == "open" && windowStatusLeft == "open"
                  ? actOnWindows("close")
                  : null;
            }}
            disabled={loadingRight || loadingLeft}
          >
            {loadingRight && loadingLeft
              ? "Moving..."
              : windowStatusRight === "closed" && windowStatusLeft == "closed"
                ? "Open Both Windows"
                : windowStatusRight === "open" && windowStatusLeft == "open"
                  ? "Close Both Windows"
                  : "Both windows not in the same state"}
          </button>
        </div>
      </div>
      {(editingThresholdLeft || editingThresholdRight) && (
        <div
          onClick={() => {
            setEditingThresholdLeft(false);
            setEditingThresholdRight(false);
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
