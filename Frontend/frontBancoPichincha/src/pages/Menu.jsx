import  { useState, useRef } from 'react';
import { Routes,Route } from 'react-router-dom';

function Menu(token) {
    const botonRef = useRef(null);
    const menuRef = useRef(null);
    const [NombreUsuario, setNombre] = useState("");
    const [ApellidoUsuario, setApellido] = useState("");

    return (
    <div>
      <header >
        <div >
          <div >
            <div >
              <img  src="../img/Logo.png" alt="Logo" width="80" />
              <h1 >Banco Pichincha</h1>
            </div>


            {/* Perfil */}
            <div >
              <i ></i>
              <button
                type="button"
                id="PerfilDropdown"
                ref={botonRef}
              >
                <span id="usuario">{NombreUsuario + " " + ApellidoUsuario}</span>
                <i></i>
              </button>
              <ul
                ref={menuRef}
                aria-labelledby="PerfilDropdown"
              >
                <li><button ><i ></i> Mi Perfil</button></li>
                <li><hr  /></li>
                <li><button>Cerrar Sesión</button></li>
              </ul>
            </div>
          </div>
        </div>
      </header>

    <div >
      <div >
        {/* Botón hamburguesa para colapsar en móviles */}
        <div  id="menuNav">
          <ul>
                <li >
                    <button  onClick={() => navigate('/')}>
                      <i></i> Inicio
                    </button>
                </li>


                <li >
                    <button  onClick={() => navigate('/cuentas')}>
                      <i ></i> Cuentas
                    </button>
                </li>

                </ul>
              </div>
            </div>
          </div>

          <main >
            <Routes>
            <Route path="/" element={<div>Reports</div>} />
            <Route path="/cuentas" element={<div>Reports</div>} />
            </Routes>
          </main>
          
      </div>
      
  )
} 


export { Menu };
