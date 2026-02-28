import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { roomService } from "../services/roomService";


interface Room {
    id: number;
    name: string;
}

export default function Rooms() {
    const [rooms, setRooms] = useState<Room[]>([]);

    useEffect(() => {
      roomService.getMyRooms().then(setRooms);
    }, []);

    return (
    <div>
      <h2>My Rooms</h2>
      {rooms.map((room) => (
        <div key={room.id}>
          <Link to={`/rooms/${room.id}`}>{room.name}</Link>
        </div>
      ))}
    </div>
  );
}