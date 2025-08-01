import { useRef } from "react";
import DropdownMenu from "./DropdownMenu";

function Header({ NombreUsuario, ApellidoUsuario }) {
  const botonRef = useRef(null);
  const menuRef = useRef(null);

  return (
    <header className="bg-white shadow-md px-6 py-4 flex justify-between items-center">
      <div className="flex items-center space-x-4">
        <img src="./BancoPichinchaLogo.png" alt="Logo" className="w-16" />
        <h1 className="text-2xl font-bold text-yellow-600">Banco Pichincha</h1>
      </div>

      <DropdownMenu
        botonRef={botonRef}
        menuRef={menuRef}
        NombreUsuario={NombreUsuario}
        ApellidoUsuario={ApellidoUsuario}
      />
    </header>
  );
}

export default Header;
