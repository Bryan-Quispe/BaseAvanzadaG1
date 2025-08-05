import { useState } from "react";

export default function RetiroForm({ onSubmit }) {
  const [monto, setMonto] = useState("");
  const [celular, setCelular] = useState("");
  const [descripcion, setDescripcion] = useState("Retiro");
  const [errores, setErrores] = useState({});

  const validarCampos = () => {
    const nuevosErrores = {};

    if (!monto || Number(monto) <= 0) {
      nuevosErrores.monto = "El monto debe ser mayor a 0.";
    }

    if (!celular || !/^\d{10,}$/.test(celular)) {
      nuevosErrores.celular = "Ingresa un número válido de al menos 10 dígitos.";
    }

    setErrores(nuevosErrores);
    return Object.keys(nuevosErrores).length === 0;
  };

  const handleSubmit = () => {
    if (!validarCampos()) return;

    onSubmit({
      monto: Number(monto),
      celular,
      descripcion,
    });

    setMonto("");
    setCelular("");
    setDescripcion("");
    setErrores({});
  };

  return (
    <div className="flex flex-col gap-4 mt-4">
      {/* Campo monto */}
      <div className="flex flex-col gap-2">
        <label className="font-semibold text-gray-700">Coloca el monto:</label>
        <input type="number" className={`border rounded-lg p-2 w-full ${ errores.monto ? "border-red-500" : "border-gray-300"
          }`}
          value={monto} onChange={(e) => setMonto(e.target.value)} placeholder="Ej: 50.00" />
        {errores.monto && (
          <span className="text-red-500 text-sm">{errores.monto}</span>
        )}
      </div>

      {/* Campo celular */}
      <div className="flex flex-col gap-2">
        <label className="font-semibold text-gray-700">Número de celular:</label>
        <input type="tel" className={`border rounded-lg p-2 w-full ${errores.celular ? "border-red-500" : "border-gray-300"
          }`}
          value={celular} onChange={(e) => setCelular(e.target.value)} placeholder="Ej: 0991234567"
        />
        {errores.celular && (
          <span className="text-red-500 text-sm">{errores.celular}</span>
        )}
      </div>

      {/* Botón generar */}
      <button
        onClick={handleSubmit}
        className="mt-4 px-4 py-2 rounded-lg font-bold text-black bg-yellow-400 hover:bg-yellow-600 transition"
      >
        Generar Retiro
      </button>
    </div>
  );
}
