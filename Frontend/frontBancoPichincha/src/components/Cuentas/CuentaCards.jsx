import { useState } from "react";
import { maskAccountId } from "../../hooks/CuentasHooks";

function AccountCard({ cuenta, onClick }) {
  const [showBalance, setShowBalance] = useState(true); 
  const maskedId = maskAccountId(cuenta.cuenta_id);
  return (
    <div
      className="min-w-[280px] bg-white rounded-2xl shadow-lg p-6 flex flex-col items-start border border-gray-200 hover:shadow-xl transition cursor-pointer relative"
      onClick={() => onClick(cuenta)}
    >
      <h3 className="text-xl font-bold text-blue-900">{cuenta.cuenta_nombre}</h3>
      <p className="text-gray-600 text-sm">ID: {maskedId}</p>

      <div className="mt-3 flex items-center space-x-3">
        <p className="text-2xl font-semibold text-green-600">
          {showBalance ? Number(cuenta.cuenta_saldo).toFixed(2) : "••••••"}
        </p>
        <button
          type="button"
          className="text-gray-400 hover:text-yellow-500 transition text-2xl"
          onClick={(e) => {
            e.stopPropagation();
            setShowBalance(!showBalance);
          }}
        >
          <i className={`bi ${showBalance ? "bi-eye-slash" : "bi-eye"}`} />
        </button>
      </div>

      <p className="text-gray-500 text-xs mt-2">
        Apertura: {new Date(cuenta.cuenta_apertura).toLocaleDateString()}
      </p>

      <span className="mt-3 px-4 py-1 text-sm rounded-full bg-yellow-100 text-yellow-800 font-medium">
        {cuenta.cuenta_estado}
      </span>
    </div>
  );
}

export default AccountCard;
