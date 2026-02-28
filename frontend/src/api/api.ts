import axios from "axios"

export const api = axios.create(
    {
        baseURL: "http://localhost:8000",
    }

);

export const setAuthToken = (token: string | null) => {
    if (token){
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
    else{
        delete api.defaults.headers.common["Authorization"]
    }
};


api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status == 401){
            localStorage.removeItem("token");
            window.location.href = "/";
        }
        
        return Promise.reject(error)
    }

)