import { useState, useEffect, useRef, useDebugValue } from 'react';
import { Logout } from '../../hooks/Logout';
import { useAuth } from '../../context/AuthContext';
import {getAccount} from '../../hooks/MenuHooks'
import 'bootstrap-icons/font/bootstrap-icons.css';

function DropdownMenu() {
  const [open, setOpen] = useState(false);
  const [usuario,setUsuario]= useState([]);
  const menuRef = useRef(null);
  const botonRef = useRef(null);
  const {logout, clienteId, token} = useAuth();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target) &&
        !botonRef.current.contains(event.target)
      ) {
        setOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
      const fetchAccounts = async () => {
        const data = await getAccount(clienteId, token);
        setUsuario(data);
      };
  
      fetchAccounts();
    }, [clienteId, token]); 

    const handleLogout = () => {
    
    Logout();       
    logout();
    setOpen(false); 
    };
  return (
    <div className="flex items-center space-x-3 relative">
      <p>{usuario.cliente_nombres} {usuario.cliente_apellidos}</p>

      <div className="relative">
        <button
          type="button"
          ref={botonRef}
          onClick={() => setOpen(!open)}
          className="flex items-center space-x-2 text-sm font-medium bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600"
        >
          <span className="flex items-center space-x-2">
            <i className="bi bi-person-circle"></i>
          </span>
          Sesión <i className="bi bi-chevron-down"></i>
        </button>

        {open && (
          <ul
            ref={menuRef}
            className="absolute top-full mt-2 right-0 w-40 bg-white rounded-md shadow-md overflow-hidden z-50"
          >
            <li>
              <button className="w-full text-left px-4 py-2 hover:bg-gray-100">
                <i className="bi bi-person"></i> Mi Perfil
              </button>
            </li>
            <li><hr className="my-1" /></li>
            <li>
              <button className="w-full text-left px-4 py-2 hover:bg-gray-100 text-red-500" onClick={handleLogout}>
                Cerrar Sesión
              </button>
            </li>
          </ul>
        )}
      </div>
    </div>
  );
}

export default DropdownMenu;
