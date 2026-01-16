import api from "./client";

export async function getData({
    measurement,
    start_time,
    sensor_identifier = null,
    end_time = null
}) {
    const data = {
        start_time,
        measurement,
        end_time
    }

    const route = `/data`

    if (sensor_identifier !== null) {
        route = `/data/${sensor_identifier}`
    }

    const result = await api.post(route, data);

    return result?.data ?? null;
}