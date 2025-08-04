import { useEffect, useState } from 'react';
import React from 'react';
import { useNavigate } from 'react-router-dom';
import MapaCajeros from './Components/MapaCajeros.jsx';

function Dashboard() {
  const user = JSON.parse(sessionStorage.getItem('user')) || {
    cliente_nombre: 'Usuario',
  };
  const [cuentas, setCuentas] = useState([]);
  const [tarjetas, setTarjetas] = useState({});
  const [showBalances, setShowBalances] = useState([true, true, true]);
  const [loading, setLoading] = useState(true);
  let tarjetaIndex = cuentas.length;

  const getAccounts = async () => {
    setLoading(true);
    try {
      const accountsResponse = await fetch(
        `https://baseavanzadag1.onrender.com/clientes/${user.cliente_id}/cuentas`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            Authorization: `Bearer ${sessionStorage.getItem('token')}`,
          },
        }
      );

      if (!accountsResponse.ok) {
        throw new Error('No se pudo obtener las cuentas');
      }

      const accounts = await accountsResponse.json();
      setCuentas(accounts);

      const tarjetasPorCuenta = {};
      let totalTarjetas = 0;
      for (const cuenta of accounts) {
        const tarjetasCuenta = await getTarjetasPorCuenta(cuenta.cuenta_id);
        tarjetasPorCuenta[cuenta.cuenta_id] = tarjetasCuenta;
        totalTarjetas += tarjetasCuenta.length;
      }
      setTarjetas(tarjetasPorCuenta);
      setShowBalances(Array(accounts.length + totalTarjetas).fill(true));
    } catch (error) {
      console.error('Fallo la obtención de cuentas y tarjetas:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTarjetasPorCuenta = async (cuenta_id) => {
    const token = sessionStorage.getItem('token');
    const headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      Authorization: `Bearer ${token}`,
    };

    try {
      const [creditoRes, debitoRes] = await Promise.all([
        fetch(
          `https://baseavanzadag1.onrender.com/cuentas/${cuenta_id}/tarjetas-credito`,
          { method: 'GET', headers }
        ),
        fetch(
          `https://baseavanzadag1.onrender.com/cuentas/${cuenta_id}/tarjetas-debito`,
          { method: 'GET', headers }
        ),
      ]);

      const tarjetasCredito = await (creditoRes.ok ? creditoRes.json() : []);
      const tarjetasDebito = await (debitoRes.ok ? debitoRes.json() : []);

      return [
        ...tarjetasCredito.map((t) => ({ ...t, tipo: 'Crédito' })),
        ...tarjetasDebito.map((t) => ({ ...t, tipo: 'Débito' })),
      ];
    } catch (error) {
      console.error(
        `Error obteniendo tarjetas de la cuenta ${cuenta_id}:`,
        error
      );
      return [];
    }
  };

  useEffect(() => {
    getAccounts();
  }, []);

  useEffect(() => {
    const totalTarjetas = Object.values(tarjetas).reduce(
      (acc, arr) => acc + arr.length,
      0
    );
    setShowBalances(Array(cuentas.length + totalTarjetas).fill(true));
  }, [cuentas, tarjetas]);

  const toggleBalance = (index) => {
    setShowBalances((prev) => {
      const newShow = [...prev];
      newShow[index] = !newShow[index];
      return newShow;
    });
  };

  const ocultarSaldo = (saldo) => {
    const saldoStr = saldo.toString();
    const [parteEntera, parteDecimal] = saldoStr.split('.');
    const ocultoEntera = '*'.repeat(parteEntera.length);
    const ocultoDecimal = parteDecimal ? '*'.repeat(parteDecimal.length) : '';
    return `${ocultoEntera}.${ocultoDecimal}`;
  };

  const formatearNumeroCuenta = (numero) => {
    if (!numero) return '**** **** **** ****';
    const strNumero = String(numero);
    const ultimos4 = strNumero.slice(-4);
    return '**** **** **** ' + ultimos4;
  };

  const formatearNumeroTarjeta = (numero) => {
    if (!numero) return '*** **** ***';
    const str = String(numero);
    if (str.length <= 6) return str;

    const primeros3 = str.slice(0, 3);
    const ultimos3 = str.slice(-3);
    const ocultos = '*'.repeat(str.length - 6);

    return `${primeros3}${ocultos}${ultimos3}`;
  };

  return (
    <div className="flex min-h-screen bg-gray-100">
      {/* Main content */}
      <main className="flex-1 p-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-blue-900">Mis Productos</h1>
          <span className="text-gray-500">
            Bienvenido, {user.cliente_nombres}
          </span>
        </div>

        {/* Cuentas y tarjetas */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
            <div className="col-span-full flex items-center justify-center text-blue-900 text-lg space-x-2">
              <svg
                className="animate-spin h-6 w-6 text-blue-900"
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
              <span>Cargando productos...</span>
            </div>
          ) : (
            <>
              {cuentas.map((cuenta, indexCuenta) => {
                const tarjetasCuenta = tarjetas[cuenta.cuenta_id] || [];
                return (
                  <React.Fragment key={cuenta.cuenta_id}>
                    {/* Cuenta */}
                    {/* ... Tu bloque actual de cuenta y tarjetas ... */}

                    {/* Tarjetas asociadas */}
                    {tarjetasCuenta.map((tarjeta, idx) => {
                      const indexGlobal = tarjetaIndex++;
                      return (
                        <div
                          key={tarjeta.tarjeta_id}
                          className="relative p-6 rounded-lg shadow border border-purple-400"
                          style={{
                            backgroundImage: `linear-gradient(rgba(255,255,255,0), rgba(255,255,255,0)), url('${
                              tarjeta.tarjeta_estilo == 'VISA'
                                ? '/fondoGris.svg'
                                : '/fondoDorado.svg'
                            }')`,
                            backgroundSize: 'cover',
                            backgroundPosition: 'center',
                          }}
                        >
                          {/* ... contenido de la tarjeta ... */}
                        </div>
                      );
                    })}
                  </React.Fragment>
                );
              })}
            </>
          )}
        </div>

        {/* Aquí va el mapa al final de la página */}
        <MapaCajeros />
      </main>
    </div>
  );
}
export default Dashboard;
