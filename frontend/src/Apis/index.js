import axios from "axios";

const api = axios.create({
    baseURL: process.env.REACT_APP_BACKEND_URL
});


export const getResponse = async (query) => {
    try {
        const response = await api.post("/get_response", {
            query: query
        });
        return response.data;
    } catch (error) {
        console.error("Error fetching response:", error);
        return { error: "An error occurred while fetching the response." };
    }
};
