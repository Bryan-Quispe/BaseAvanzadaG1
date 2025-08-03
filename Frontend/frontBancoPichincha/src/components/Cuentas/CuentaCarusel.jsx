
import AccountCard from "./CuentaCards";
import { useState,useEffect } from "react";
import { useAuth} from '../../context/AuthContext'
import { getAccounts } from "../../hooks/CuentasHooks";
function AccountSlider() {

    const [Cuentas,setCuentas]= useState([]);
    const {clienteId,token} = useAuth()
    const [loading, setLoading] = useState(true);
     useEffect(() => {
    const fetchAccounts = async () => {
      setLoading(true); 
      const data = await getAccounts(clienteId, token);
      setCuentas(Array.isArray(data) ? [...data] : []);
      setLoading(false); 
    };

    if (clienteId && token) fetchAccounts();
  }, [clienteId, token]);

  if (loading) {
    return (
      <div className="col-span-full flex items-center justify-center text-blue-900 text-lg space-x-2 p-6">
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
        <span>Cargando Cuentas...</span>
      </div>
    );
  }; 

  return (
    <div className="w-full overflow-x-auto scrollbar-hide">
      <div className="flex space-x-4 p-4">
        {Cuentas.length > 0 ? (
          Cuentas.map((cuenta) => (
            <AccountCard key={cuenta.cuenta_id} cuenta={cuenta} />
          ))
        ) : (
          <p className="text-gray-500">No tienes cuentas registradas.</p>
        )}
      </div>
    </div>
  );
}

export default AccountSlider;
