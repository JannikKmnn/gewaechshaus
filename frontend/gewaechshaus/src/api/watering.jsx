import api from "./client";

export async function getLastWatering() {
  const route = `watering/events/latest`;
  const result = await api.get(route);

  return result?.data ?? null;
}

export async function getWateringEvents({
  start_datetime,
  end_datetime = null,
}) {
  const data = {
    start_datetime,
    end_datetime,
  };

  let route = `watering/events`;

  const result = await api.post(route, data);

  return result?.data ?? null;
}
