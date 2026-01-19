export const formatTime = (isoString) => {
  const date = new Date(isoString);
  return date.toLocaleTimeString([], {
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};