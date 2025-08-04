import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { useRetiroSinTarjeta } from "../../hooks/TransaccionesHooks";
import {getAccounts} from "../../hooks/CuentasHooks"
import RetiroForm from "../Formularios/FormRetiroSintTarjeta";
import MensajeModal from "../MensajeInfo/mensaje";

export default function ActionRetiroSinTarjeta() {
  const [Cuentas, setCuentas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAccount, setSelectedAccount] = useState(""); 
  const [showModal, setShowModal] = useState(false);
  const [modalMessage, setModalMessage] = useState("");

  const { clienteId, token } = useAuth();
  const { generarRetiro, loading: loadingRetiro } = useRetiroSinTarjeta(token);

  useEffect(() => {
    const fetchAccounts = async () => {
      setLoading(true);
      const data = await getAccounts(clienteId, token);
      setCuentas(Array.isArray(data) ? [...data] : []);
      setLoading(false);
    };
    if (clienteId && token) fetchAccounts();
  }, [clienteId, token]);

  const handleRetiro = async (formData) => {
  try {
    const data = await generarRetiro(selectedAccount, formData);

    setModalMessage(
      <p className="text-green-600 text-3xl font-bold">
        Código de verificación: {data.codigo_verificacion}
      </p>
    );
  } catch (error) {
    setModalMessage(
      <p className="text-red-600 text-xl font-bold">
        ❌ Error al generar el retiro. Inténtalo nuevamente.
      </p>
    );
  } finally {
    setShowModal(true);
  }
};

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-2xl font-bold text-blue-900 mb-6">
        Acciones en la cuenta
      </h2>

      {loading ? (
        <p className="text-gray-500">Cargando cuentas...</p>
      ) : (
        <>
          <label className="font-semibold text-gray-700">
            Selecciona una cuenta:
          </label>
          <select
            className="border border-gray-300 rounded-lg p-2 w-full"
            value={selectedAccount}
            onChange={(e) => setSelectedAccount(e.target.value)}
          >
            <option value="">-- Selecciona --</option>
            {Cuentas.map((cuenta) => (
              <option key={cuenta.cuenta_id} value={cuenta.cuenta_id}>
                {cuenta.cuenta_nombre} - Saldo $
                {Number(cuenta.cuenta_saldo).toFixed(2)}
              </option>
            ))}
          </select>

          {selectedAccount && (
            <RetiroForm onSubmit={handleRetiro} />
          )}

          {loadingRetiro && <p className="text-blue-500 mt-2">Procesando retiro...</p>}
        </>
      )}

      <MensajeModal
        show={showModal}
        onClose={() => setShowModal(false)}
        title="Resultado del Retiro"
        message={modalMessage}
      />
    </div>
  );
}
