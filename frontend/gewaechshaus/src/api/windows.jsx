import api from "./client";

export async function getWindowStatus({
    window_position,
}) {
    const route = `window/status/${window_position}`;
    const result = await api.get(url=route);

    return result?.data ?? null;
}