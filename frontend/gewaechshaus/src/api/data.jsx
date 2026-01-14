import axios from "axios";

async function getData({
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

    const result = await axios.post(`/data/${sensor_identifier}`, data)

    return result || null;
}