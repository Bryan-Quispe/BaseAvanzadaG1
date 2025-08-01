import { Routes, Route } from "react-router-dom";

function MainContent() {
  return (
    <main className="flex-1 p-6">
      <Routes>
        <Route path="/" element={<div className="text-xl">Bienvenido al panel de inicio</div>} />
        <Route path="/cuentas" element={<div className="text-xl">Sección de cuentas</div>} />
      </Routes>
    </main>
  );
}

export default MainContent;
