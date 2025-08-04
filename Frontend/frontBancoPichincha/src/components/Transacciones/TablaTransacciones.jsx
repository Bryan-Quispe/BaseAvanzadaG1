import { useEffect, useState } from "react";
import TransactionCard from "./ContenedorTransaccion";
import { maskAccountId } from "../../hooks/CuentasHooks";
import { useAuth } from "../../context/AuthContext";
import {getTransactions} from "../../hooks/TransaccionesHooks"

import { useTransaccionesNegativas, agruparPorMes } from "../../hooks/TransaccionesHooks";

function TablaTransacciones({ Cuenta }) {
  const { token, clienteId } = useAuth();
  const [transaccionesRetiro,setTransacciones]= useState([]);
  const [loading, setLoading] = useState(true);

  const maskId = maskAccountId(Cuenta.cuenta_id);
  useEffect(() => {
      const fetchAccounts = async () => {
        setLoading(true);
        const data = await getTransactions(Cuenta.cuenta_id, token);
        await setTransacciones(Array.isArray(data) ? [...data] : []);
        setLoading(false);
      };

      if (clienteId && token) fetchAccounts();
    }, [Cuenta.cuenta_id, token]);

  const transaccionesNegativas = useTransaccionesNegativas(transaccionesRetiro);

  const transaccionesPorMes = agruparPorMes(transaccionesNegativas);


  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 500);
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 bg-white">
        <span className="text-xl font-semibold text-yellow-400">Cargando...</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center bg-white py-7 gap-6">
      {/* Cabecera */}
      <div className="w-full max-w-5xl bg-white pt-6 pb-6 rounded-lg shadow-lg border border-gray-200">
        <div className="mb-6">
          <h2 className="text-3xl text-center text-blue-900">
            {Cuenta.cuenta_nombre}{" "}
            <i className="text-yellow-500 font-semibold bi bi-star-fill text-xl"></i>
          </h2>
        </div>
        <hr className="text-gray-400" />
        <div className="flex mt-6 mb-6 px-10 justify-center gap-10">
          <div>
            <h2 className="font-bold text-xl text-blue-700">Cuenta Id: {maskId} </h2>
            <p className="font-bold text-gray-700 text-2xl">Saldo contable:</p>
            <p className="font-bold text-green-700 text-xl">
              ${Number(Cuenta.cuenta_saldo).toFixed(2)}
            </p>
          </div>
          <div className="flex items-center">
            <p className="text-blue-700 cursor-pointer">
              <i className="bi bi-share-fill"></i> Compartir Nro.cuenta
            </p>
          </div>
        </div>
        <div className="flex mt-6 mb-6 px-10 justify-center gap-10">
        </div>
        <hr className="text-gray-400" />
      </div>

      {/* Bloques de transacciones por mes */}
      <div className="w-full max-w-5xl">
        <h2 className="font-bold text-gray-700 mb-4">Movimientos</h2>

        {Object.entries(transaccionesPorMes).map(([mes, lista], idx) => (
          <div key={idx} className="mb-8">
            <h3 className="text-lg font-semibold text-gray-600 mb-4 capitalize">{mes}</h3>
            <div className="flex flex-col gap-4">
              {lista.map((t, i) => (
                <TransactionCard
                  key={i}
                  fecha={t.transaccion_fecha}
                  costo={t.costo}           
                  monto={t.monto}    
                  descripcion={t.transaccion_descripcion}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TablaTransacciones;
