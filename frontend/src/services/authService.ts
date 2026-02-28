import { api } from "../api/api";

export const authService = {
    login: async (username: string, password: string) => {
        const res = await api.post("/auth/login", {
            username,
            password
        });

        return res.data
    },
};