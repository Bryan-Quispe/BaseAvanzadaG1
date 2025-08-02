import { useState } from "react";
import { useNavigate } from 'react-router-dom';

function RegisterConfirmation() {
    const navigate = useNavigate();

    const login = () => {
        navigate('/');
    }

    return (
        <div
            className="flex items-center justify-center h-screen bg-cover bg-center"
            style={{ backgroundImage: "url('/fondoAmarillo.svg')" }}
        >
            <div className="bg-white p-10 rounded-lg shadow-lg text-center w-96 border border-gray-200">
                <h1 className="text-3xl text-center text-blue-900">¡Proceso Completado Exitosamente!</h1>
                <i className="bi bi-check-square text-[50px] text-green-700 font-bold"></i>
                <button onClick={login} className="w-full bg-yellow-400 text-blue-900 font-bold py-2 rounded-md hover:bg-yellow-500 transition cursor-pointer">Continuar</button>
            </div>

            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-sm text-gray-500">
                © 2023 Banco Pichicha | Todos los derechos reservados
            </div>
        </div>
    );
}


export default RegisterConfirmation;