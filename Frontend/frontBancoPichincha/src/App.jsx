import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Login from './pages/Login.jsx';
import { Menu } from './pages/Menu.jsx';
import Register from './pages/Register.jsx';
import { useAuth } from './context/AuthContext';
import RegisterConfirmation from  './pages/RegisterSuccesfull.jsx'
import Dashboard from './pages/Dashboard.jsx';
import CreateAccount from './pages/AccountCreate.jsx';

function App() {
  const { token } = useAuth();

  const isAuthenticated = token !== null;
  const isRegisterSuccesfull = sessionStorage.getItem("registerSuccesfull");

  return (
    <Routes>
      <Route path="/*" element={isAuthenticated ? <Menu /> : <Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/createAccount" element={isAuthenticated? <CreateAccount /> : <Login />} />
      <Route path="/dashboard" element={isAuthenticated? <Dashboard />: <Login/>} />
      <Route path="/registerSuccesfull" element={isRegisterSuccesfull?<RegisterConfirmation />:<Register/>} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;
