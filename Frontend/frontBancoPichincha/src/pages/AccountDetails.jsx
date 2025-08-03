import { useEffect, useState } from "react";
import React from "react";
import { useNavigate } from "react-router-dom";

function AccountDetails(accountId) {

    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const timer = setTimeout(() => {
            setLoading(false);
        }, 500);

        return () => clearTimeout(timer);
    }, []);

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
        <div className="flex py-7 items-center justify-center bg-white">
            <div className="w-[60%]">
                <div className="bg-white pt-6 pb-6 rounded-lg shadow-lg mb-6  border border-gray-200">
                    <div className="mb-6">
                        <h2 className="text-3xl text-center text-blue-900">
                            $366.15
                        </h2>
                        <p className="text-center mb-6">Saldo contable: $366.15</p>
                    </div>
                    <hr className="text-gray-400"></hr>
                    <div className="flex mt-6 mb-6 px-10 justify-center">
                        <div className="w-[30%]">
                            <p className="font-bold text-gray-700">AHO4305 <i className="text-yellow-500 font-semibold bi bi-star-fill text-xl"></i></p>
                            <p>Cuenta Transaccional</p>
                            <p>Nro. 100000000000001</p>
                        </div>
                        <div className="w-[30%] items-center">
                            <p className="text-blue-700"><i class="bi bi-share-fill"></i> Compartir nro.cuenta</p>
                        </div>
                    </div>
                </div>
                <hr className="text-gray-300 mb-8"></hr>
                <div>
                    <h2 className="font-bold text-gray-700">Movimientos</h2>
                </div>
                <div className="bg-white pt-6 pb-6 mb-6">
                    {/* Fecha 1 */}
                    <p className="text-sm text-gray-500 mb-2 ml-2">Viernes, 1 ago. 2025</p>

                    {/* Bloque de movimientos para esta fecha */}
                    <div className="pt-4 pb-4 shadow-lg  mb-6 border border-gray-200 px-4">

                        {/* Movimiento 1 */}
                        <div className="border-b border-gray-200 py-3">
                            <p className="text-gray-800 text-sm mb-1">
                                Consumo Visa in Amazon web Services Aws.amazon.c
                            </p>
                            <div className="flex justify-between items-center">
                                <span className="text-red-500 font-bold">-$1.84</span>
                                <span className="text-sm text-gray-500">$366.15</span>
                            </div>
                        </div>

                        {/* Movimiento 2 */}
                        <div className="border-b border-gray-200 py-3">
                            <p className="text-gray-800 text-sm mb-1">
                                Impuesto isd Amazon we
                            </p>
                            <div className="flex justify-between items-center">
                                <span className="text-red-500 font-bold">-$0.09</span>
                                <span className="text-sm text-gray-500">$367.99</span>
                            </div>
                        </div>

                        {/* Movimiento 3 */}
                        <div className="py-3">
                            <p className="text-gray-800 text-sm mb-1">
                                Retencion Ivasd Amazon we
                            </p>
                            <div className="flex justify-between items-center">
                                <span className="text-red-500 font-bold">-$0.28</span>
                                <span className="text-sm text-gray-500">$368.08</span>
                            </div>
                        </div>

                    </div>

                </div>
            </div>

        </div>
    );
}

export default AccountDetails;
