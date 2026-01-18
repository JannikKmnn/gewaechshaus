export function temperatureToColor(temp) {
  if (temp === null || temp === undefined) return "#ffffff";

  const minTemp = 0;
  const maxTemp = 35;

  // clamp
  const t = Math.max(minTemp, Math.min(maxTemp, temp));
  const ratio = (t - minTemp) / (maxTemp - minTemp);

  let r, g, b;

  if (ratio < 0.5) {
    // blue → green
    const local = ratio / 0.5;
    r = 0;
    g = Math.round(255 * local);
    b = Math.round(255 * (1 - local));
  } else {
    // green → red (via yellow/orange)
    const local = (ratio - 0.5) / 0.5;
    r = Math.round(255 * local);
    g = Math.round(255 * (1 - local));
    b = 0;
  }

  return `rgb(${r}, ${g}, ${b})`;
}
