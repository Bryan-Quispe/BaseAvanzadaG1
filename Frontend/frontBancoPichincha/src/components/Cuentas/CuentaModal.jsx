import TablaTransacciones from "../Transacciones/TablaTransacciones";
import { useEffect,useState } from "react";
function AccountModal({ cuenta, onClose }) {


  useEffect(()=>{

  }),[];

  if (!cuenta) return null;

  const handleOverlayClick = () => {
    onClose();
  };

  const handleModalClick = (e) => {
    e.stopPropagation(); 
  };

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={handleOverlayClick}
    >
      <div
        className="bg-white rounded-lg shadow-lg w-[70rem] max-w-[90vw] max-h-[90vh] overflow-y-auto p-8 relative"
        onClick={handleModalClick} 
      >
        <button
          className="absolute top-3 right-3 text-gray-500 hover:text-gray-800 text-lg"
          onClick={onClose}
        >
          <i className="bi bi-x-square"></i>
        </button>

        <h2 className="text-2xl font-bold text-blue-900 mb-6">Datos en la cuenta</h2>

        <TablaTransacciones Cuenta={cuenta}/>
      </div>
    </div>
  );
}

export default AccountModal;
