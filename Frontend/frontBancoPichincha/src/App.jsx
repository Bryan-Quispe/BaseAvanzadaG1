import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Login from './pages/Login.jsx';
import { useState } from 'react'
import './App.css'
import Login from  './pages/Login.jsx';
import { Menu } from './pages/Menu.jsx';

function App() {
  return (

      <Routes>
        <Route path="/" element={<Login />} />
      </Routes>
  );

}

export default App;
