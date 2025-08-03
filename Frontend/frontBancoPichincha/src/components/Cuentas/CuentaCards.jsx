import {maskAccountId} from '../../hooks/CuentasHooks'

function AccountCard({ cuenta }) {
    const maskedId =maskAccountId(cuenta.cuenta_id);
  return (
    <div className="min-w-[250px] bg-white rounded-xl shadow-md p-4 flex flex-col items-start border border-gray-200 hover:shadow-lg transition">
      <h3 className="text-lg font-bold text-blue-900">{cuenta.cuenta_nombre}</h3>
      <p className="text-gray-600 text-sm">ID: {maskedId}</p>
      <p className="mt-2 text-xl font-semibold text-green-600">
        ${cuenta.cuenta_saldo.toFixed(2)}
      </p>
      <p className="text-gray-500 text-xs mt-1">
        Apertura: {new Date(cuenta.cuenta_apertura).toLocaleDateString()}
      </p>
      <span className="mt-2 px-3 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800 font-medium">
        {cuenta.cuenta_estado}
      </span>
    </div>
  );
}

export default AccountCard;
