import React, { useState } from "react";
import "./App.css";
import api from "./services/api";

const LoginScreen = ({ onBack, onAuthSuccess }) => {
  const [form, setForm] = useState({
    email: "",
    password: ""
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (error) setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;  // Prevent double submission

    setLoading(true);
    setError(""); // Clear any previous error

    try {
        const response = await api.login({
            email: form.email,
            password: form.password
        });

        // Success!
        console.log('Login successful:', response);

        // Store user data in localStorage
        localStorage.setItem('user', JSON.stringify(response.user));
        localStorage.setItem('isLoggedIn', 'true');

        // Show success message
        alert('Login successful! Welcome back, ' + response.user.username);

        // Call onAuthSuccess callback and pass the username
        if (onAuthSuccess) {
            onAuthSuccess(response.user.username);
        }

        // Navigate back to main screen
        onBack();

    } catch (err) {
        console.error('Login error:', err);
        setError(err.message || 'Invalid email or password. Please try again.');
    } finally {
        setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: "#2ad0c4", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ position: "absolute", top: 32, left: 32, cursor: "pointer", fontSize: 28 }} onClick={onBack}>
        <span style={{ fontWeight: 600 }}>&larr;</span>
      </div>
      <img src="src/assets/logo.png" alt="Fraud Finder Logo" style={{ position: "absolute", top: 32, right: 32, height: "40px" }} />
      <form onSubmit={handleSubmit} style={{
        background: "#f7f7f7",
        borderRadius: "25px",
        boxShadow: "0 10px 25px rgba(44, 62, 80, 0.10)",
        padding: "1rem 1rem 1rem 1rem",
        width: "100%",
        maxWidth: "600px",
        border: "none",
        display: "flex",
        flexDirection: "column",
        alignItems: "center"
      }}>
        <h2 style={{ fontFamily: 'JomolhariReg', textAlign: "center", marginBottom: "2rem", fontSize: 36, fontWeight: 500 }}>Log In</h2>

        {/* Error Message */}
        {error && (
          <div style={{
            width: "100%",
            maxWidth: 500,
            padding: "1rem",
            marginBottom: 16,
            background: "#ffebee",
            color: "#c62828",
            borderRadius: 12,
            fontSize: 16,
            textAlign: "center",
            fontFamily: 'JomolhariReg'
          }}>
            {error}
          </div>
        )}

        <input
          type="email"
          name="email"
          value={form.email}
          onChange={handleChange}
          required
          placeholder="Enter your email"
          disabled={loading}
          style={{
            width: "100%",
            maxWidth: 500,
            marginBottom: 24,
            padding: "1rem",
            borderRadius: 12,
            border: "1.5px solid #e0e0e0",
            fontSize: 20,
            background: loading ? "#e0e0e0" : "#f9f9f9",
            outline: "none",
            cursor: loading ? "not-allowed" : "text"
          }}
        />
        <input
          type="password"
          name="password"
          value={form.password}
          onChange={handleChange}
          required
          placeholder="Enter your password"
          disabled={loading}
          style={{
            width: "100%",
            maxWidth: 500,
            marginBottom: 24,
            padding: "1rem",
            borderRadius: 12,
            border: "1.5px solid #e0e0e0",
            fontSize: 20,
            background: loading ? "#e0e0e0" : "#f9f9f9",
            outline: "none",
            cursor: loading ? "not-allowed" : "text"
          }}
        />
        <p style={{ marginBottom: 16, fontSize: 16, fontFamily: 'JomolhariReg' }}>
          Don't have an account?{" "}
          <span
            style={{ color: "#2ad0c4", textDecoration: "underline", fontWeight: 600, cursor: "pointer" }}
            onClick={() => onBack("signup")}
          >
            Sign up here
          </span>
        </p>
        <button
          type="submit"
          disabled={loading}
          style={{
            width: 220,
            padding: "1rem",
            borderRadius: 16,
            border: "none",
            background: loading ? "#b0b0b0" : "#2ad0c4",
            color: "#fff",
            fontWeight: 700,
            fontSize: 18,
            fontFamily: 'JomolhariReg',
            cursor: loading ? "not-allowed" : "pointer",
            marginTop: 16,
            letterSpacing: 1,
            opacity: loading ? 0.7 : 1
          }}
        >
          {loading ? "LOGGING IN..." : "LOG IN"}
        </button>
      </form>
    </div>
  );
};

export default LoginScreen;