  function TransactionCard({ fecha, costo, monto, descripcion }) {
  const costoNum = Number(costo) || 0;
  const montoNum = Number(monto) || 0;
  const valor = montoNum + costoNum;
  const esPositivo = valor > 0;

    return (
      <div className="py-4 px-4 shadow-md border border-gray-200 rounded-lg bg-white flex flex-col gap-2">
        <p className="text-gray-800 text-sm">{new Date(fecha).toLocaleDateString()}</p>
        <div className="flex justify-between items-center">
          <p className="font-bold text-blue-400">{descripcion} <br/></p>
          <span className={`${esPositivo ? "text-green-500" : "text-red-500"} font-bold`}>
            {esPositivo ? `+$${valor.toFixed(2)}` : `-$${Math.abs(valor).toFixed(2)}`}
          </span>
        </div>
      </div>
    );
  }

  export default TransactionCard;
