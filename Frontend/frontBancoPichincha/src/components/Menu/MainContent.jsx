import { Routes, Route } from "react-router-dom";
import CuentasContent from "../Cuentas/CuentasContent";
import Dashboard from "../../pages/Dashboard";
import ProfileDetails from "../../pages/ProfileDetails";

function MainContent() {
  return (
    <main className="flex-1 p-6">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/cuentas" element={<CuentasContent />} />
        <Route path="/perfil" element={<ProfileDetails />} />
      </Routes>
    </main>
  );
}

export default MainContent;
