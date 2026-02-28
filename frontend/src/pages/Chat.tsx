import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { roomService } from "../services/roomService";
import { useWebSocket } from "../hooks/WebSocket";

interface Message {
  id: number;
  content: string;
  username: string;
}

export default function Chat() {
  const { id } = useParams();
  const { token } = useAuth();

  const [messages, setMessages] = useState<Message[]>([]);

  const url =
    id && token
      ? `ws://localhost:8000/ws/${id}?token=${token}`
      : null

    const {status, send } = useWebSocket({
      url,
      onMessage: (data) => {
        if (data.event == "message") {
          setMessages((prev) => [...prev, data.message]);
        }
      },
    });

    useEffect(() => {
      if (!id) return;
      roomService.getRoomMessages(id).then(setMessages);
    }, [id]);


  return (
    <div>
      <h2>Room {id}</h2>
      <p>Status: {status}</p>

      <div style={{ height: 300, overflowY: "auto" }}>
        {messages.map((msg) => (
          <div key={msg.id}>
            <strong>{msg.username}:</strong> {msg.content}
          </div>
        ))}
      </div>

      <button
        onClick={() =>
          send({
            action: "send_message",
            content: "Hello",
          })
        }
      >
        Send Test
      </button>
    </div>
  );
}