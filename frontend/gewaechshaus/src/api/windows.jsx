import api from "./client";

export async function getWindowStatus({
    window_position,
}) {
    const route = `window/status/${window_position}`;
    const result = await api.get(route);

    return result?.data ?? null;
}

export async function getWindowConfigs({
    window_position,
}) {
    const route = `window/config/${window_position}`;
    const result = await api.get(route);

    return result?.data ?? null;
}

export async function callWindowActuators({
    operation,
    window_position = null,
}) {
    let route = `/window/${operation}`

    if (window_position !== null) {
        route = `/window/${operation}/${window_position}`
    }

    const result = await api.post(route);

    return result?.data ?? null;
}