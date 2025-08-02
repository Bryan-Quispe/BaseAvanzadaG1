import { useState,useEffect, use } from "react";
import Header from "../components/Menu/Header";
import MainContent from "../components/Menu/MainContent";
import Sidebar from "../components/Menu/Sidebar";

function Cuentas(token) {
  const [NombreUsuario, setNombre] = useState("");
  const [ApellidoUsuario, setApellido] = useState("");
    useEffect(()=>{
      setNombre("Juan");
      setApellido("Perez")
    })
  return (
    <div className="min-h-screen bg-gray-100 text-gray-800">
      <Header NombreUsuario={NombreUsuario} ApellidoUsuario={ApellidoUsuario} />
      <div className="flex">
        <Sidebar />
        <MainContent />
      </div>
    </div>
  );
}

export default Cuentas;
