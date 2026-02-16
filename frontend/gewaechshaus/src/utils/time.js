export const formatTime = (isoString) => {
  const date = new Date(isoString);
  return date.toLocaleTimeString([], {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

export function formatDateTime(isoString) {
  if (!isoString) return "—";

  const date = new Date(isoString);

  return date
    .toLocaleString("de-DE", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    })
    .replace(",", "");
}