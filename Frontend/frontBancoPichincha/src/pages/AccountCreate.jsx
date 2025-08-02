import { useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom';
import InputText from "./Components/InputText.jsx"

function CreateAccount() {

    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        cliente_id: "",
        cuenta_nombre: "",
        cuenta_saldo: "",
        cuenta_apertura: new Date().toISOString(),
        cuenta_estado: "ACTIVA",
        cuenta_limite_trans_web: "",
        cuenta_limite_trans_movil: "",
    });

    useEffect(() => {
        const storedUser = JSON.parse(sessionStorage.getItem("user"));
        if (storedUser?.cliente_id) {
            setFormData(prev => ({
                ...prev,
                cliente_id: storedUser.cliente_id
            }));
        }
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleCreateAccount = async (e) => {
        e.preventDefault();
        setLoading(true);

        console.log(formData);

        try {
            const response = await fetch("https://baseavanzadag1.onrender.com/cuentas/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${sessionStorage.getItem("token")}`
                },
                body: JSON.stringify(formData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error("Error al crear:", errorData.detail || errorData);
                alert("Error al crear una cuenta.");
                setLoading(false);
                return;
            }

            await response.json();

            setFormData({
                cliente_id: "",
                cuenta_nombre: "",
                cuenta_saldo: "",
                cuenta_apertura: "",
                cuenta_estado: "ACTIVA",
                cuenta_limite_trans_web: "",
                cuenta_limite_trans_movil: "",
            });

            sessionStorage.setItem("registerSuccesfull", true);
            navigate("/registerSuccesfull");
        } catch (error) {
            sessionStorage.setItem("registerSuccesfull", false);
            console.error("Error en el registro:", error);
            alert("Hubo un error al registrar el cliente.");
            setLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center h-screen " style={{ backgroundImage: "url('/fondoAmarillo.svg')" }}>
            <div className="bg-white p-10 rounded-lg shadow-lg w-[40%] border border-gray-200">
                <form onSubmit={handleCreateAccount}>
                    <h2 className="text-3xl mb-4 text-blue-900">
                        Por favor, ingresa tus datos
                    </h2>
                    <p className="mb-6">Sea cuidadoso con los datos ingresados</p>
                    <p className="font-bold text-gray-700 mb-4">Datos Personales</p>
                    <div className="mb-4">
                        <label htmlFor="cliente_id" className="block text-sm font-semibold text-blue-900 mb-1">
                            ID del Cliente
                        </label>
                        <input
                            id="cliente_id"
                            name="cliente_id"
                            type="text"
                            value={formData.cliente_id}
                            onChange={handleChange}
                            readOnly
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400"
                        />
                    </div>

                    <p className="font-bold text-gray-700 mb-4">Datos de la Cuenta</p>

                    <InputText
                        label="Nombre de la Cuenta"
                        name="cuenta_nombre"
                        value={formData.cuenta_nombre}
                        onChange={handleChange}
                        placeholder="Ex: Cuenta de Ahorros Para el Negocio"
                        required
                    />

                    <InputText
                        label="Saldo de Apertura"
                        name="cuenta_saldo"
                        value={formData.cuenta_saldo}
                        onChange={handleChange}
                        placeholder="Ex: 500"
                        required
                    />

                    <p className="font-bold text-gray-700 mb-4">Configuración de la Cuenta</p>

                    <InputText
                        label="Límite de transferencia web"
                        name="cuenta_limite_trans_web"
                        value={formData.cuenta_limite_trans_web}
                        onChange={handleChange}
                        placeholder="Ex: 1500"
                        required
                    />

                    <InputText
                        label="Límite de transferencia movil"
                        name="cuenta_limite_trans_movil"
                        value={formData.cuenta_limite_trans_movil}
                        onChange={handleChange}
                        placeholder="Ex: 1500"
                        required
                    />
                    <br></br>
                    <hr></hr>
                    <br></br>
                    <button
                        type="submit"
                        className="w-full bg-yellow-400 text-blue-900 font-bold py-2 rounded-md hover:bg-yellow-500 transition cursor-pointer"
                    >
                        Abrir Cuenta
                    </button>
                </form>
                <br></br>
            </div>

            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-sm text-gray-500">
                © 2023 Banco Pichicha  | Todos los derechos reservados
            </div>

        </div>
    );

}

export default CreateAccount;
