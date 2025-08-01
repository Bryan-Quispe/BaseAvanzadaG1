import 'bootstrap-icons/font/bootstrap-icons.css';

function DropdownMenu({ botonRef, menuRef, NombreUsuario, ApellidoUsuario }) {
  return (
    <div className="flex items-center space-x-3">
        <p>{NombreUsuario} {ApellidoUsuario}</p>
      <button
        type="button"
        id="PerfilDropdown"
        ref={botonRef}
        className="flex items-center space-x-2 text-sm font-medium bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600"
      >
        <span className="flex items-center space-x-2"><i className="bi bi-person-circle"></i></span>
        Sesión <i className="bi bi-chevron-down"></i>
      </button>

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
  );
}

export default DropdownMenu;
