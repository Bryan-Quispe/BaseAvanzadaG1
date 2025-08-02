import { useState } from "react";
import { useNavigate } from 'react-router-dom';

function InputText({ label, name, type = "text", value, onChange, required = false, pattern, title, placeholder }) {
  return (
    <div className="mb-4">
      <label className="block text-sm font-semibold text-blue-900 mb-1" htmlFor={name}>
        {label} {required && "*"}
      </label>
      <input id={name} name={name} type={type} value={value} onChange={onChange} required={required} pattern={pattern} title={title} placeholder={placeholder}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400"
      />
    </div>
  );
}

function Register() {
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

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleRegister = async (e) => {
    e.preventDefault();

    console.log("registro");

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
        return;
      }

      const data = await response.json();
      console.log("Cliente registrado con éxito:", data);
      alert("Cliente registrado con éxito.");

      setFormData({
        cliente_id: "",
        cliente_nombres: "",
        cliente_apellidos: "",
        cliente_correo: "",
        cliente_celular: "",
        cliente_direccion: "",
        cliente_provincia: "",
        cliente_ciudad: "",
        cliente_fchnacimiento: ""
      });

      sessionStorage.setItem("registerSuccesfull",true);
      navigate('/registerSuccesfull');
    } catch (error) {
      sessionStorage.setItem("registerSuccesfull",false);
      console.error("Error en el registro:", error);
      alert("Hubo un error al registrar el cliente.");
    }
  };


  return (
    <div className="flex py-7 items-center justify-center bg-white">
      <div className="bg-white p-10 rounded-lg shadow-lg w-lg border border-gray-200">
        <form onSubmit={handleRegister}>
          <h2 className="text-3xl mb-8 text-center text-blue-900">
            ¡Empecemos! <br />Ingresa tus datos
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

          <button type="submit" className="w-full bg-yellow-400 text-blue-900 font-bold py-2 rounded-md hover:bg-yellow-500 transition cursor-pointer">
            Continuar
          </button>
        </form>
      </div>
    </div>
  );
}

export default Register;
