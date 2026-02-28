import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Rooms from "./pages/Rooms";
import Chat from "./pages/Chat";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route
            path="/rooms"
            element={
              <ProtectedRoute>
                <Rooms />
              </ProtectedRoute>
            }
          />

          <Route
            path="/rooms/:id"
            element={
              <ProtectedRoute>
                <Chat />
              </ProtectedRoute>
            }
          />
                  </Routes>
                </BrowserRouter>
              </AuthProvider>
            );
}

export default App;