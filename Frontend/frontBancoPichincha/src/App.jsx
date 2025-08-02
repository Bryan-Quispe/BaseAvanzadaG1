import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Login from './pages/Login.jsx';
import { useState } from 'react'
import  Cuentas  from './pages/Cuentas.jsx';
import Register from './pages/Register.jsx';

function App() {
  return (

      <Routes>
        <Route path="/" element={localStorage.getItem("token") === null ? <Login /> : <Cuentas />} />
        <Route path="/register" element={<Register />} />
      </Routes>
  );

}

export default App;
