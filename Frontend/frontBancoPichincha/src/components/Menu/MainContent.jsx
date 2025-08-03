import { Routes, Route } from "react-router-dom";
import CuentasContent from "../Cuentas/CuentasContent";
import Dashboard from "../../pages/Dashboard";

function MainContent() {
  return (
    <main className="flex-1 p-6">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/cuentas" element={<CuentasContent />} />
      </Routes>
    </main>
  );
}

export default MainContent;
