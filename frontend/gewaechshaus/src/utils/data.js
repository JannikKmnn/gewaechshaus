export function reshapeTimeseries(data, exclude = null) {
  const byTimestamp = {};

  for (const point of data) {
    if (point.field == exclude) {
      continue;
    }

    const { timestamp, field, value } = point;

    if (!byTimestamp[timestamp]) {
      byTimestamp[timestamp] = { timestamp };
    }

    byTimestamp[timestamp][field] = value;
  }

  return Object.values(byTimestamp);
}
