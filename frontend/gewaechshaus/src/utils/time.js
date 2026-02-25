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

export function windowOpenTime(lastOpening, lastClosing) {

  const lastOpeningDate = new Date(lastOpening);
  let lastClosingDate = new Date(lastClosing);

  if (lastOpeningDate > lastClosingDate) {
    // window is still open
    lastClosingDate = Date.now();
  }

  const timeDiff = Math.abs(lastClosingDate - lastOpeningDate);

  const diffDays = Math.floor((timeDiff / (1000 * 60 * 60 * 24))); 
  const diffHours = Math.floor((timeDiff / (1000 * 60 * 60) % 24)); 
  const diffMinutes = Math.floor((timeDiff / (1000 * 60)) % 60);
  const diffSeconds = Math.floor((timeDiff / 1000) % 60);

  if (diffDays > 0) {
    return {
      "diffDays": diffDays,
      "diffHours": diffHours,
    }
  }
  else if (diffHours > 0) {
    return {
      "diffHours": diffHours,
      "diffMinutes": diffMinutes,
    }
  }
  else {
    return {
      "diffMinutes": diffMinutes,
      "diffSeconds": diffSeconds,
    }
  }
}

export function isoAgo(
  str,
  base = Date.now(),
) {
  const value = parseInt(str);
  const unit = str.replace(value, "");

  const multipliers = {
    m: 60 * 1000,
    h: 60 * 60 * 1000,
    d: 24 * 60 * 60 * 1000,
  };

  const baseMs = Math.floor(new Date(base).getTime() / 1000) * 1000;

  return new Date(baseMs - value * multipliers[unit]).toISOString();
}

export function isoWayOff(
  str,
  base,
) {
  const value = parseInt(str);
  const unit = str.replace(value, "");

  const multipliers = {
    m: 60 * 1000,
    h: 60 * 60 * 1000,
    d: 24 * 60 * 60 * 1000,
  };

  const baseMs = Math.floor(new Date(base).getTime() / 1000) * 1000;

  return new Date(baseMs + value * multipliers[unit]).toISOString();
}