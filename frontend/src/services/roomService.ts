import { api } from "../api/api";

export const roomService = {
    getMyRooms: async () => {
        const res = await api.get("/rooms/my");
        return res.data.rooms;
    },

    getRoomMessages: async (roomId: string) => {
    const res = await api.get(`/rooms/${roomId}/messages`);
    return res.data.messages;
  },
};