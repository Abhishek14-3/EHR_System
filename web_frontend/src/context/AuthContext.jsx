import React, { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const token = localStorage.getItem("healthchain_token");
    const role = localStorage.getItem("healthchain_role");
    const username = localStorage.getItem("healthchain_username");
    return token ? { token, role, username } : null;
  });

  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("healthchain_theme") || "dark";
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("healthchain_theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  const loginUser = (token, role, username) => {
    localStorage.setItem("healthchain_token", token);
    localStorage.setItem("healthchain_role", role);
    localStorage.setItem("healthchain_username", username);
    setUser({ token, role, username });
  };

  const logoutUser = () => {
    localStorage.removeItem("healthchain_token");
    localStorage.removeItem("healthchain_role");
    localStorage.removeItem("healthchain_username");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, theme, toggleTheme, loginUser, logoutUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
