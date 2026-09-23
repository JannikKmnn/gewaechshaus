import api from "./client";

export async function getData({
  measurement,
  start_time,
  sensor_identifier = null,
  end_time = null,
}) {
  const data = {
    start_time,
    measurement,
    end_time,
  };

  let route = `/data`;

  if (sensor_identifier !== null) {
    route = `/data/${sensor_identifier}`;
  }

  const result = await api.post(route, data);

  return result?.data ?? null;
}

export async function getSoilMoistureIntervals({
  start_time,
  end_time,
  sensor_identifier,
}) {
  const data = {
    start_time,
    end_time,
    sensor_identifier,
  };

  let route = `data/soil_moisture_intervals`;

  const result = await api.post(route, data);

  return result?.data ?? null;
}
