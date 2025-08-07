import { useEffect, useState } from "react";

export default function ProfileDetails() {
  const [tab, setTab] = useState("detalle");
  const [loading, setLoading] = useState(true);
  const [cliente, setCliente] = useState({});
  const [editingField, setEditingField] = useState(null);
  const [tempValue, setTempValue] = useState("");
  const [currentPass, setCurrentPass] = useState("");
  const [newPass, setNewPass] = useState("");
  const [repeatNewPass, setRepeatNewPass] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [passwordSuccess, setPasswordSuccess] = useState("");
  const [passwordLoading, setPasswordLoading] = useState(false);

  const user = JSON.parse(sessionStorage.getItem('user')) || {
    cliente_nombre: 'Usuario',
  };

  const getProfile = async () => {
    setLoading(true);
    try {
      const profileResponse = await fetch(
        `https://baseavanzadag1.onrender.com/clientes/${user.cliente_id}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            Authorization: `Bearer ${sessionStorage.getItem('token')}`,
          },
        }
      );

      if (!profileResponse.ok) {
        throw new Error('No se pudo obtener los datos del perfil');
      }

      const profileFound = await profileResponse.json();
      setCliente(profileFound);
    } catch (error) {
      console.error('Fallo la obtención del perfil: ', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    getProfile();
  }, []);

  const startEditing = (field) => {
    setEditingField(field);
    setTempValue(cliente[field] || "");
  };

  const saveField = async () => {
    const updatedCliente = { ...cliente, [editingField]: tempValue };
    setLoading(true);
    try {
      const response = await fetch(`https://baseavanzadag1.onrender.com/clientes/${user.cliente_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${sessionStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          cliente_nombres: updatedCliente.cliente_nombres,
          cliente_apellidos: updatedCliente.cliente_apellidos,
          cliente_correo: updatedCliente.cliente_correo,
          cliente_celular: updatedCliente.cliente_celular,
          cliente_direccion: updatedCliente.cliente_direccion,
          cliente_provincia: updatedCliente.cliente_provincia,
          cliente_ciudad: updatedCliente.cliente_ciudad,
          cliente_fchnacimiento: updatedCliente.cliente_fchnacimiento,
        }),
      });

      if (!response.ok) {
        throw new Error('Error al actualizar el perfil');
      }

      const data = await response.json();
      setCliente(data);
      setEditingField(null);
      setTempValue("");
    } catch (error) {
      console.error('Fallo al guardar datos: ', error);
      alert('No se pudo guardar el cambio, inténtalo nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  const changePassword = async (currentPassword, newPassword) => {
    try {
      const response = await fetch(
        "https://baseavanzadag1.onrender.com/clientes/change-password/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${sessionStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Error al cambiar la contraseña");
      }

      const data = await response.json();
      return data;
    } catch (error) {
      throw error;
    }
  };

  const onSubmitChangePassword = async () => {
    setPasswordError("");
    setPasswordSuccess("");

    if (!currentPass || !newPass || !repeatNewPass) {
      setPasswordError("Por favor, completa todos los campos.");
      return;
    }

    if (newPass !== repeatNewPass) {
      setPasswordError("Las nuevas contraseñas no coinciden.");
      return;
    }

    setPasswordLoading(true);
    try {
      await changePassword(currentPass, newPass);
      setPasswordSuccess("Contraseña cambiada con éxito.");
      setCurrentPass("");
      setNewPass("");
      setRepeatNewPass("");
    } catch (error) {
      setPasswordError(error.message || "Error al cambiar la contraseña.");
    } finally {
      setPasswordLoading(false);
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
    <div className="min-h-screen bg-gray-100 flex justify-center items-start py-10 font-sans">
      <div className="w-full max-w-3xl">
        {/* Header */}
        <div className="border-gray-700 px-6 py-4 bg-white shadow-md rounded-md">
          <div className="flex items-center space-x-4">
            <div className="bg-gray-200 w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold text-gray-600">
              JP
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-700">
                {cliente.cliente_nombres?.toUpperCase()}{" "}
                {cliente.cliente_apellidos?.toUpperCase()}
              </h2>
              <p className="text-sm text-gray-500">
                Último ingreso 16/05/2019 a las 12:00
              </p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mt-4 flex space-x-6 mb-7">
          <button
            className={`pb-2 text-sm cursor-pointer ${tab === "detalle"
              ? "border-b-2 border-blue-600 text-blue-600 font-medium"
              : "text-gray-600"
              }`}
            onClick={() => setTab("detalle")}
          >
            Detalle
          </button>
          <button
            className={`pb-2 text-sm cursor-pointer ${tab === "contrasena"
              ? "border-b-2 border-blue-600 text-blue-600 font-medium"
              : "text-gray-600"
              }`}
            onClick={() => setTab("contrasena")}
          >
            Cambio de contraseña
          </button>
        </div>

        {/* Detalle */}
        {tab === "detalle" && (
          <div className="px-6 py-6 space-y-4 border-gray-700 bg-white shadow-md rounded-md">
            <div>
              <p className="text-sm text-gray-500 flex items-center justify-between">
                Fecha de nacimiento
                {editingField !== "cliente_fchnacimiento" && (
                  <button
                    className="text-blue-600 text-xs underline hover:text-blue-800"
                    onClick={() => startEditing("cliente_fchnacimiento")}
                  >
                    Editar
                  </button>
                )}
              </p>
              {editingField === "cliente_fchnacimiento" ? (
                <input
                  type="date"
                  value={tempValue}
                  onChange={(e) => setTempValue(e.target.value)}
                  className="border border-gray-300 rounded px-2 py-1 mt-1 w-full max-w-xs"
                />
              ) : (
                <p className="text-gray-800">{cliente.cliente_fchnacimiento}</p>
              )}
            </div>

            <div>
              <p className="text-sm text-gray-500 flex items-center justify-between">
                Dirección
                {editingField !== "cliente_direccion" && (
                  <button
                    className="text-blue-600 text-xs underline hover:text-blue-800"
                    onClick={() => startEditing("cliente_direccion")}
                  >
                    Editar
                  </button>
                )}
              </p>
              {editingField === "cliente_direccion" ? (
                <input
                  type="text"
                  value={tempValue}
                  onChange={(e) => setTempValue(e.target.value)}
                  className="border border-gray-300 rounded px-2 py-1 mt-1 w-full"
                />
              ) : (
                <p className="text-gray-800">{cliente.cliente_direccion}</p>
              )}
            </div>

            <div>
              <p className="text-sm text-gray-500 flex items-center justify-between">
                Ciudad
                {editingField !== "cliente_ciudad" && (
                  <button
                    className="text-blue-600 text-xs underline hover:text-blue-800"
                    onClick={() => startEditing("cliente_ciudad")}
                  >
                    Editar
                  </button>
                )}
              </p>
              {editingField === "cliente_ciudad" ? (
                <input
                  type="text"
                  value={tempValue}
                  onChange={(e) => setTempValue(e.target.value)}
                  className="border border-gray-300 rounded px-2 py-1 mt-1 w-full"
                />
              ) : (
                <p className="text-gray-800">{cliente.cliente_ciudad}</p>
              )}
            </div>

            <div>
              <p className="text-sm text-gray-500 flex items-center justify-between">
                Provincia
                {editingField !== "cliente_provincia" && (
                  <button
                    className="text-blue-600 text-xs underline hover:text-blue-800"
                    onClick={() => startEditing("cliente_provincia")}
                  >
                    Editar
                  </button>
                )}
              </p>
              {editingField === "cliente_provincia" ? (
                <input
                  type="text"
                  value={tempValue}
                  onChange={(e) => setTempValue(e.target.value)}
                  className="border border-gray-300 rounded px-2 py-1 mt-1 w-full"
                />
              ) : (
                <p className="text-gray-800">{cliente.cliente_provincia}</p>
              )}
            </div>

            <div>
              <p className="text-sm text-gray-500 flex items-center justify-between">
                Correo electrónico
                {editingField !== "cliente_correo" && (
                  <button
                    className="text-blue-600 text-xs underline hover:text-blue-800"
                    onClick={() => startEditing("cliente_correo")}
                  >
                    Editar
                  </button>
                )}
              </p>
              {editingField === "cliente_correo" ? (
                <input
                  type="email"
                  value={tempValue}
                  onChange={(e) => setTempValue(e.target.value)}
                  className="border border-gray-300 rounded px-2 py-1 mt-1 w-full"
                />
              ) : (
                <p className="text-gray-800">{cliente.cliente_correo}</p>
              )}
            </div>

            <div>
              <p className="text-sm text-gray-500 flex items-center justify-between">
                Número de teléfono
                {editingField !== "cliente_celular" && (
                  <button
                    className="text-blue-600 text-xs underline hover:text-blue-800"
                    onClick={() => startEditing("cliente_celular")}
                  >
                    Editar
                  </button>
                )}
              </p>
              {editingField === "cliente_celular" ? (
                <input
                  type="tel"
                  value={tempValue}
                  onChange={(e) => setTempValue(e.target.value)}
                  className="border border-gray-300 rounded px-2 py-1 mt-1 w-full"
                />
              ) : (
                <p className="text-gray-800">{cliente.cliente_celular}</p>
              )}
            </div>

            <div>
              <p className="text-sm text-gray-500">Cuentas</p>
              <ul className="list-disc pl-6 text-gray-800">
                {cliente.cuentas?.map((cuenta, index) => (
                  <li key={index}>{cuenta}</li>
                )) || <li>No hay cuentas</li>}
              </ul>
            </div>

            {/* Botón Guardar general para el campo en edición */}
            {editingField && (
              <div className="text-right mt-4 space-x-2">
                <button
                  className="bg-yellow-400 text-blue-950 font-bold px-6 py-2 rounded shadow hover:bg-yellow-300"
                  onClick={saveField}
                >
                  Guardar
                </button>
                <button
                  className="bg-gray-300 text-gray-700 font-bold px-6 py-2 rounded shadow hover:bg-gray-400"
                  onClick={() => {
                    setEditingField(null);
                    setTempValue("");
                  }}
                >
                  Cancelar
                </button>
              </div>
            )}

          </div>
        )}

        {/* Cambio de contraseña */}
        {tab === "contrasena" && (
          <div className="px-6 py-6 space-y-4 border-gray-700 bg-white shadow-md rounded-md">
            <div>
              <label className="text-sm text-gray-700 block mb-1">
                Contraseña actual
              </label>
              <input
                type="password"
                className="w-full border border-gray-300 rounded px-3 py-2"
                value={currentPass}
                onChange={(e) => setCurrentPass(e.target.value)}
                disabled={passwordLoading}
              />
            </div>
            <hr />
            <div>
              <label className="text-sm text-gray-700 block mb-1">
                Nueva contraseña
              </label>
              <input
                type="password"
                className="w-full border border-gray-300 rounded px-3 py-2"
                value={newPass}
                onChange={(e) => setNewPass(e.target.value)}
                disabled={passwordLoading}
              />
            </div>
            <div>
              <label className="text-sm text-gray-700 block mb-1">
                Repetir nueva contraseña
              </label>
              <input
                type="password"
                className="w-full border border-gray-300 rounded px-3 py-2"
                value={repeatNewPass}
                onChange={(e) => setRepeatNewPass(e.target.value)}
                disabled={passwordLoading}
              />
            </div>

            <div className="text-sm text-gray-600 space-y-1">
              <p>✔ 12 a 16 caracteres.</p>
              <p>✔ Incluir mínimo 1 mayúscula, minúscula y número.</p>
              <p>✖ Sin caracteres especiales (tildes, Ññ*/#.=)</p>
            </div>

            {passwordError && (
              <p className="text-red-600 font-semibold">{passwordError}</p>
            )}
            {passwordSuccess && (
              <p className="text-green-600 font-semibold">{passwordSuccess}</p>
            )}

            <div className="text-right">
              <button
                className={`bg-yellow-400 text-blue-950 font-bold px-6 py-2 rounded shadow hover:bg-yellow-300 ${passwordLoading ? "opacity-50 cursor-not-allowed" : ""
                  }`}
                onClick={onSubmitChangePassword}
                disabled={passwordLoading}
              >
                {passwordLoading ? "Guardando..." : "Guardar"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
