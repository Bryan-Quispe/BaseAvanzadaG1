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
    sessionStorage.setItem("clienteId", newClienteId);
    setToken(newToken);
    setClienteId(newClienteId);
  };

  const logout = () => {
    sessionStorage.removeItem("token");
    sessionStorage.removeItemItem("clienteId");
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, login, logout, clienteId }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
