import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

export const runScript = async () => {
    try {
        const response = await axios.post(`${API_URL}/run-script/`);
        return response.data;
    } catch (error) {
        console.error('Error running script:', error);
        throw error;
    }
};
