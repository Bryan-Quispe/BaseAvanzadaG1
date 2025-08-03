import { useState } from "react";
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const { login } = useAuth();

  const registro = () => {
    navigate('/register');
  }

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const response = await fetch("https://baseavanzadag1.onrender.com/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: formData.toString()
      });

      const data = await response.json();
      
      const userResponse = await fetch(`https://baseavanzadag1.onrender.com/clientes/${username}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "Authorization": `Bearer ${data.access_token}`
        }
      });

      if (!userResponse.ok) {
        throw new Error("No se pudo obtener el usuario");
      }

      const user = await userResponse.json();

      sessionStorage.setItem("user", JSON.stringify(user));
      console.log(user)
      login(data.access_token,user.cliente_id);

    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  return (
    <div className="flex items-center justify-center h-screen bg-white">
      <div className="bg-white p-10 rounded-lg shadow-lg w-96 border border-gray-200">
        <form onSubmit={handleLogin}>
          <h2 className="text-3xl font-bold mb-8 text-center text-blue-900">
            Banco Pichicha
          </h2>
          <div className="mb-4">
            <label className="block text-sm font-semibold text-blue-900 mb-1">
              Usuario
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="mb-6">
            <label className="block text-sm font-semibold text-blue-900 mb-1">
              Contraseña
            </label>
            <input
              type="password"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-yellow-400 text-blue-900 font-bold py-2 rounded-md hover:bg-yellow-500 transition cursor-pointer"
          >
            Ingresar
          </button>
        </form>
        <br></br>
        <hr></hr>
        <br></br>
        <p>No tienes cuenta? <button onClick={registro}><span className="text-blue-800 cursor-pointer">Crea una Ahora</span></button></p>
      </div>

      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-sm text-gray-500">
        © 2023 Banco Pichicha  | Todos los derechos reservados
      </div>

    </div>
  );
}

export default Login;
