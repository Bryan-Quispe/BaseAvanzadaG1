import { useMemo } from "react";
import { useState } from "react";

export  function useRetiroSinTarjeta(token) {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const generarRetiro = async (cuentaId, formData) => {
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const res = await fetch(
        `https://baseavanzadag1.onrender.com/cuentas/${cuentaId}/retiro-sin-tarjeta`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            cuenta_id: cuentaId,
            monto: Number(formData.monto), 
            descripcion: formData.descripcion || "", 
            celular_beneficiario: formData.celular, 
          }),
        }
      );

      if (!res.ok) throw new Error("Error en el servidor");

      const json = await res.json();
      setData(json);
      return json;
    } catch (err) {
      setError(err.message || "Error desconocido");
      throw err;
    } finally {
      setLoading(false);
    }
  };


  return { generarRetiro, loading, data, error };
}

export const agruparPorMes = (datos) => {
  return datos.reduce((acc, transaccion) => {
    const fecha = new Date(transaccion.transaccion_fecha);
    const mes = fecha.toLocaleString("es-ES", { month: "long", year: "numeric" });

    if (!acc[mes]) acc[mes] = [];
    acc[mes].push(transaccion);
    return acc;
  }, {});
};


export function useTransaccionesNegativas(transacciones) {
  return useMemo(() => {
    return transacciones.map((t) => {
      const costo = Number(t.transaccion_costo ?? 0);
      const monto = Number(t.transaccion_monto ?? 0);
      const esRetiro = t.transaccion_descripcion?.toLowerCase() === "retiro";

      return {
        ...t,
        costo: esRetiro ? -Math.abs(costo) : costo,
        monto: esRetiro ? -Math.abs(monto) : monto,
      };
    });
  }, [transacciones]);
}

export const getTransactions = async (cuenta_id, token) => {
  try {
    const transactionResponse = await fetch(
      `https://baseavanzadag1.onrender.com/cuentas/${cuenta_id}/transacciones`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "Authorization": `Bearer ${token}`
        }
      }
    );

    if (!transactionResponse.ok) {
      throw new Error("No se pudo obtener las cuentas");
    }
    return await transactionResponse.json();
  } catch (error) {
    console.error("Fallo la obtención de Transacciones", error);
    return [];
  }
};
