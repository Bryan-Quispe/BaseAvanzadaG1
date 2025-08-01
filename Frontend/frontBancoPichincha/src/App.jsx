import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Login from './pages/Login.jsx';
import { Menu } from './pages/Menu.jsx';
import Register from './pages/Register.jsx';
import { useAuth } from './context/AuthContext';

function App() {
  const { token } = useAuth();

  const isAuthenticated = token !== null;

  return (
    <Routes>
      <Route path="/*" element={isAuthenticated ? <Menu /> : <Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;
