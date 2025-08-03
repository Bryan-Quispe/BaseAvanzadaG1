import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(null);
  const [clienteId, setClienteId] = useState(null); 

  useEffect(() => {
    const savedToken = sessionStorage.getItem("token");
    if (savedToken) {
      setToken(savedToken);
    }
  }, []);

  const login = (newToken, newClienteId) => {
    sessionStorage.setItem("token", newToken); 
    setToken(newToken);
    setClienteId(newClienteId);
  };

  const logout = () => {
    sessionStorage.removeItem("token");
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
