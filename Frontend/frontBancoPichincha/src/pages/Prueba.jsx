import { useState } from "react";
import { useNavigate } from 'react-router-dom';

function Dashboard() {
 
  return (
    <div className="flex items-center justify-center h-screen bg-white">
      <div className="bg-white p-10 rounded-lg shadow-lg w-[70%] border border-gray-200">
        <form >
          <h2 className="text-3xl mb-4 text-blue-900">
            Por favor, ingresa tus datos
          </h2>
          <p className="mb-6">Los datos que se ingresen deben ser personales para poder verificar la identidad</p>
          <p className="font-bold text-gray-700">Datos Personales</p>
          <div className="mb-4">
            <label className="block text-sm font-semibold text-blue-900 mb-1">
              
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400"
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
      </div>

      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-sm text-gray-500">
        © 2023 Banco Pichicha  | Todos los derechos reservados
      </div>

    </div>
  );
}

export default Dashboard;
