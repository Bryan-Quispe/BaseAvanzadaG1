import { useNavigate } from "react-router-dom";

function Sidebar() {
  const navigate = useNavigate();

  return (
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
  );
}

export default Sidebar;
