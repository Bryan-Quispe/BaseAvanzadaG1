import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function Dashboard() {
  const user = JSON.parse(sessionStorage.getItem("user")) || { cliente_nombre: "Usuario" };
  const [cuentas, setCuentas] = useState([]);
  const [showBalances, setShowBalances] = useState([true, true, true]);
  const [loading, setLoading] = useState(true);

  const getAccounts = async () => {
    setLoading(true);
    try {
      const accountsResponse = await fetch(`https://baseavanzadag1.onrender.com/clientes/${user.cliente_id}/cuentas`, {
        method: "GET",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "Authorization": `Bearer ${sessionStorage.getItem("token")}`
        }
      });

      if (!accountsResponse.ok) {
        throw new Error("No se pudo obtener las cuentas");
      }

      const accounts = await accountsResponse.json();
      setCuentas(accounts);

    } catch (error) {
      console.error("Fallo la obtención de cuentas:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    getAccounts();
  }, []);

  useEffect(() => {
    setShowBalances(Array(cuentas.length).fill(true));
  }, [cuentas]);

  const toggleBalance = (index) => {
    setShowBalances((prev) => {
      const newShow = [...prev];
      newShow[index] = !newShow[index];
      return newShow;
    });
  };

  const ocultarSaldo = (saldo) => {
    const saldoStr = saldo.toString();
    const [parteEntera, parteDecimal] = saldoStr.split(".");
    const ocultoEntera = "*".repeat(parteEntera.length);
    const ocultoDecimal = parteDecimal ? "*".repeat(parteDecimal.length) : "";
    return `${ocultoEntera}.${ocultoDecimal}`;
  };


  const formatearNumeroCuenta = (numero) => {
    return "**** **** **** " + numero.slice(-4);
  };

  return (
    <div className="flex min-h-screen bg-gray-100">
      {/* Main content */}
      <main className="flex-1 p-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-blue-900">Mis Productos</h1>
          <span className="text-gray-500">Bienvenido, {user.cliente_nombres}</span>
        </div>

        {/* Cuentas */}
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
              <span>Cargando cuentas...</span>
            </div>
          ) : (
            cuentas.map((cuenta, index) => (
              <div
                key={cuenta.cuenta_id}
                className="relative bg-white p-6 rounded-lg shadow border border-yellow-400"
              >
                {/* Estrella y cuenta favorita */}
                <div className="absolute top-4 right-4 flex items-center space-x-1 text-yellow-500 text-sm font-semibold">
                  <i className={`bi ${true ? "bi-star-fill" : "bi-star"} text-xl`}></i>
                  <span>Cuenta favorita</span>
                </div>

                {/* Código de cuenta */}
                <div className="text-blue-900 text-lg font-bold mb-1">{cuenta.cuenta_nombre}</div>

                {/* Número de cuenta */}
                <div className="text-gray-600 mb-4">{formatearNumeroCuenta(cuenta.cuenta_id)}</div>

                {/* Saldo disponible */}
                <div className="mb-6">
                  <p className="text-sm text-gray-600 mb-1">Saldo disponible</p>
                  <div className="flex items-center space-x-2">
                    <p className="text-xl font-bold text-green-600">
                      {showBalances[index] ? cuenta.cuenta_saldo : ocultarSaldo(cuenta.cuenta_saldo)} USD
                    </p>
                    <button onClick={() => toggleBalance(index)} className="transform transition-transform duration-200 hover:scale-110">
                      <i className={`bi ${showBalances[index] ? "bi-eye-slash text-gray-600" : "bi-eye text-blue-900"}  cursor-pointer text-2xl`}></i>
                    </button>


                  </div>
                </div>

                {/* Tipo de cuenta */}
                <div className="absolute bottom-4 right-4 text-gray-500 text-sm">
                  Cuenta de Ahorro
                </div>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  );
}

export default Dashboard;
