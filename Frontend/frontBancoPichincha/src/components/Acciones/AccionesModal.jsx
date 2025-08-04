import ActionRetiroSinTarjeta from "./AccionRetiroSinTarjeta";

export default function AccionesModal({ onClose, tipo }) {
  const handleOverlayClick = () => onClose();
  const handleModalClick = (e) => e.stopPropagation();

  let contenido = null;
  if (tipo === "ST") {
    contenido = <ActionRetiroSinTarjeta />;
  } else {
    contenido = <br/>;
  }

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

        {contenido}
      </div>
    </div>
  );
}
