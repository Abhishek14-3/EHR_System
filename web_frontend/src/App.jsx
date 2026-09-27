import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import LedgerTicker from "./components/LedgerTicker";
import AuthPage from "./pages/AuthPage";
import PatientDashboard from "./pages/PatientDashboard";
import DoctorDashboard from "./pages/DoctorDashboard";
import AdminDashboard from "./pages/AdminDashboard";

function ProtectedRoute({ children, allowedRoles }) {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to={user.role === "doctor" ? "/doctor" : user.role === "patient" ? "/patient" : "/admin"} replace />;
  }
  return children;
}

function RootRedirect() {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (user.role === "doctor") return <Navigate to="/doctor" replace />;
  if (user.role === "patient") return <Navigate to="/patient" replace />;
  return <Navigate to="/admin" replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
          <Navbar />
          <LedgerTicker />
          <main style={{ flex: 1 }}>
            <Routes>
              <Route path="/" element={<RootRedirect />} />
              <Route path="/login" element={<AuthPage />} />
              
              <Route
                path="/patient"
                element={
                  <ProtectedRoute allowedRoles={["patient", "admin"]}>
                    <PatientDashboard />
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/doctor"
                element={
                  <ProtectedRoute allowedRoles={["doctor", "admin"]}>
                    <DoctorDashboard />
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/admin"
                element={
                  <ProtectedRoute allowedRoles={["admin"]}>
                    <AdminDashboard />
                  </ProtectedRoute>
                }
              />

              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          
          <footer style={{
            padding: "1.5rem",
            textAlign: "center",
            borderTop: "1px solid var(--border)",
            fontSize: "0.8rem",
            color: "var(--text-muted)"
          }}>
            HealthChain AI Platform • Powered by Hyperledger Fabric, IPFS & Scikit-Learn • Sovereign Medical Records
          </footer>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}
