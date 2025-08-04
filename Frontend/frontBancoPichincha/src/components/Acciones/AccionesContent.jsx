import AccionesModal from "./AccionesModal";
import { useState } from "react";

export default function ActionsContent() {
  const [showModal, setShowModal] = useState(false);
  const [modalTipo, setModalTipo] = useState(null);

  const abrirModal = (tipo) => {
    setModalTipo(tipo);
    setShowModal(true);
  };

  return (
    <div className="flex items-center gap-8">
      {/* Botón Retiro sin tarjeta */}
      <span className="flex flex-col items-center gap-2">
        <button
          className="border border-black hover:bg-blue-300 text-black font-bold w-12 h-12 rounded-full flex items-center justify-center"
          onClick={() => abrirModal("ST")}
        >
          <i className="bi bi-credit-card"></i>
        </button>
        <p>Generar Retiro sin Tarjeta</p>
      </span>


      {/* Modal */}
      {showModal && (
        <AccionesModal
          tipo={modalTipo}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
}
