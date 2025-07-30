import  { useState, useRef } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';

function Menu(token) {
    const botonRef = useRef(null);
    const menuRef = useRef(null);
    const [NombreUsuario, setNombre] = useState("");
    const [ApellidoUsuario, setApellido] = useState("");
    const navigate = useNavigate();

    return (
    <div className="min-h-screen bg-gray-100 text-gray-800">
      {/* Header */}
      <header className="bg-white shadow-md px-6 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <img src="./BancoPichinchaLogo.png" alt="Logo" className="w-16" />
          <h1 className="text-2xl font-bold text-yellow-600">Banco Pichincha</h1>
        </div>

        {/* Perfil */}
        <div className="relative">
          <button
            type="button"
            id="PerfilDropdown"
            ref={botonRef}
            className="flex items-center space-x-2 text-sm font-medium bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600"
          >
            <span>{NombreUsuario} {ApellidoUsuario}</span>
            <i className="bi bi-chevron-down"></i>
          </button>

          {/* Menú desplegable */}
          <ul
            ref={menuRef}
            className="absolute right-0 mt-2 w-40 bg-white rounded-md shadow-md overflow-hidden z-50"
          >
            <li>
              <button className="w-full text-left px-4 py-2 hover:bg-gray-100">
                <i className="bi bi-person"></i> Mi Perfil
              </button>
            </li>
            <li><hr className="my-1" /></li>
            <li>
              <button className="w-full text-left px-4 py-2 hover:bg-gray-100 text-red-500">
                Cerrar Sesión
              </button>
            </li>
          </ul>
        </div>
      </header>

      {/* Sidebar */}
      <div className="flex">
        <nav className="w-60 bg-white p-6 shadow-lg min-h-screen">
          <ul className="space-y-4">
            <li>
              <button
                onClick={() => navigate('/')}
                className="flex items-center space-x-2 text-left w-full px-4 py-2 rounded hover:bg-yellow-100"
              >
                <i className="bi bi-house-door"></i>
                <span>Inicio</span>
              </button>
            </li>
            <li>
              <button
                onClick={() => navigate('/cuentas')}
                className="flex items-center space-x-2 text-left w-full px-4 py-2 rounded hover:bg-yellow-100"
              >
                <i className="bi bi-wallet2"></i>
                <span>Cuentas</span>
              </button>
            </li>
          </ul>
        </nav>

        {/* Main Content */}
        <main className="flex-1 p-6">
          <Routes>
            <Route path="/" element={<div className="text-xl">Bienvenido al panel de inicio</div>} />
            <Route path="/cuentas" element={<div className="text-xl">Sección de cuentas</div>} />
          </Routes>
        </main>
      </div>
    </div>
  );
} 


export { Menu };
