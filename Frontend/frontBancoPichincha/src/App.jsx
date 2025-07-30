<<<<<<< HEAD
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Login from './pages/Login.jsx';
=======
import { useState } from 'react'
import './App.css'
import Login from  './pages/Login.jsx';
import { Menu } from './pages/Menu.jsx';
>>>>>>> 38fd49dafd7ff18aafa59fa2401f4cc3146b7192

function App() {
  return (
<<<<<<< HEAD
      <Routes>
        <Route path="/" element={<Login />} />
      </Routes>
  );
=======
    <>
    <Menu />
    <h1>Hola mundo</h1>
    </>
  )
>>>>>>> 38fd49dafd7ff18aafa59fa2401f4cc3146b7192
}

export default App;
