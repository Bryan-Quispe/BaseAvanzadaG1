import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import InputText from "./Components/InputText.jsx"


function Register() {
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    cliente_id: "",
    cliente_nombres: "",
    cliente_apellidos: "",
    cliente_correo: "",
    cliente_celular: "",
    cliente_direccion: "",
    cliente_provincia: "",
    cliente_ciudad: "",
    cliente_fchnacimiento: "",
  });

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch("https://baseavanzadag1.onrender.com/clientes/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Error al registrar:", errorData.detail || errorData);
        alert("Error al registrar cliente.");
        setLoading(false);
        return;
      }

      await response.json();

      setFormData({
        cliente_id: "",
        cliente_nombres: "",
        cliente_apellidos: "",
        cliente_correo: "",
        cliente_celular: "",
        cliente_direccion: "",
        cliente_provincia: "",
        cliente_ciudad: "",
        cliente_fchnacimiento: "",
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-white">
        <div className="flex flex-col items-center gap-4">
          <svg
            className="animate-spin h-10 w-10 text-yellow-400"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
            ></path>
          </svg>
          <span className="text-xl font-semibold text-yellow-400">Cargando...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex py-7 items-center justify-center bg-white">
      <div className="bg-white p-10 rounded-lg shadow-lg w-lg border border-gray-200">
        <form onSubmit={handleRegister}>
          <h2 className="text-3xl mb-8 text-center text-blue-900">
            ¡Empecemos! <br />
            Ingresa tus datos
          </h2>

          <InputText
            label="Cédula"
            name="cliente_id"
            value={formData.cliente_id}
            onChange={handleChange}
            placeholder="Ex: 1728851399"
            required
          />

          <InputText
            label="Nombres"
            name="cliente_nombres"
            value={formData.cliente_nombres}
            onChange={handleChange}
            placeholder="Ex: Juliana Andrea"
            required
          />

          <InputText
            label="Apellidos"
            name="cliente_apellidos"
            value={formData.cliente_apellidos}
            onChange={handleChange}
            placeholder="Ex: Osorio Rodriguez"
            required
          />

          <InputText
            label="Correo electrónico"
            name="cliente_correo"
            type="email"
            value={formData.cliente_correo}
            onChange={handleChange}
            placeholder="Ex: julia@gmail.com"
            required
          />

          <InputText
            label="Celular"
            name="cliente_celular"
            type="tel"
            value={formData.cliente_celular}
            onChange={handleChange}
            placeholder="Ex: 0967666697"
            required
            pattern="[0-9]{7,15}"
            title="Ingrese un número válido (7 a 15 dígitos)"
          />

          <InputText
            label="Dirección"
            name="cliente_direccion"
            value={formData.cliente_direccion}
            placeholder="Ex: Av. Casa Grande"
            onChange={handleChange}
            required
          />

          <InputText
            label="Provincia"
            name="cliente_provincia"
            value={formData.cliente_provincia}
            onChange={handleChange}
            placeholder="Ex: Pichincha"
            required
          />

          <InputText
            label="Ciudad"
            name="cliente_ciudad"
            value={formData.cliente_ciudad}
            onChange={handleChange}
            placeholder="Ex: Quito"
            required
          />

          <InputText
            label="Fecha de nacimiento"
            name="cliente_fchnacimiento"
            type="date"
            value={formData.cliente_fchnacimiento}
            onChange={handleChange}
            required
          />

          <button
            type="submit"
            disabled={loading}
            className={`w-full flex items-center justify-center gap-2 bg-yellow-400 text-blue-900 font-bold py-2 rounded-md transition cursor-pointer ${loading ? "opacity-70 cursor-not-allowed" : "hover:bg-yellow-500"
              }`}
          >
            {loading ? (
              <>
                <svg
                  className="animate-spin h-5 w-5 text-blue-900"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                  ></path>
                </svg>
                Cargando...
              </>
            ) : (
              "Continuar"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Register;
