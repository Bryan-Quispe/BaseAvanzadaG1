import { useState,useEffect, use } from "react";
import Header from "../components/Menu/Header";
import MainContent from "../components/Menu/MainContent";
import Sidebar from "../components/Menu/Sidebar";

function Cuentas() {
  const [NombreUsuario, setNombre] = useState("");
  const [ApellidoUsuario, setApellido] = useState("");
  return (
    <div className="min-h-screen bg-gray-100 text-gray-800">
      <Header />
      <div className="flex">
        <Sidebar /> 
        <MainContent/>
      </div>
    </div>
  );
}

export default Cuentas;
