export default function MensajeModal({ show, onClose, title, message }) {
  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg w-[400px] max-w-[90vw] p-6 relative">
        <button
          className="absolute top-3 right-3 text-gray-500 hover:text-gray-800 text-lg"
          onClick={onClose}
        >
          <i className="bi bi-x-square"></i>
        </button>

        <h2 className="text-xl font-bold text-blue-900 mb-4">{title}</h2>

        {/* Soporta texto o JSX */}
        <div className="text-center">{message}</div>
      </div>
    </div>
  );
}
