import api from "./client";

export async function getLastWatering() {
    const route = `watering/events/latest`;
    const result = await api.get(route);

    return result?.data ?? null;
}