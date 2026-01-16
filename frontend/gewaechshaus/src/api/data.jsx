import api from "./client";

export async function getData({
    sensor_identifier,
    measurement,
    start_time,
    end_time = null
}) {
    const data = {
        start_time,
        measurement,
        end_time
    }

    const result = await api.post(`/data/${sensor_identifier}`, data)

    return result?.data ?? null;
}