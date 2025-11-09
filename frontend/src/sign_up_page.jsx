import React, { useState } from "react";
import "./App.css";
import api from "./services/api";

const professions = [
    "Student",
    "Recent Graduate",
    "Working Professional",
    "Job Seeking Professional",
];

const interests = [
    "Technology",
    "Finance",
    "Healthcare",
    "Education",
    "Other",
];

const SignUpPage = ({ onBack, onAuthSuccess }) => {
    const [form, setForm] = useState({
        username: "",
        email: "",
        password: "",
        qualification: "",
        fields_of_interest: "",
    });

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((prev) => ({ ...prev, [name]: value }));
        if (error) setError("");
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (loading) return;  // Prevent double submission
        
        setLoading(true);
        setError("");

        try {
            const response = await api.register({
                username: form.username,
                email: form.email,
                password: form.password,
                qualification: form.qualification,
                fields_of_interest: form.fields_of_interest,
            });
            
            // Success!
            console.log('Registration successful:', response);
            
            // Show success message
            alert('Registration successful! Please log in with your credentials.');
            
            // Navigate to login screen
            onBack("login");
            
        } catch (err) {
            console.error("Registration error:", err);
            setError(err.message || "Registration failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ minHeight: "100vh", background: "#2ad0c4", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <div style={{ position: "absolute", top: 32, left: 32, cursor: "pointer", fontSize: 28 }} onClick={() => onBack()}>
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
                <h2 style={{ fontFamily: 'JomolhariReg', textAlign: "center", marginBottom: "2rem", fontSize: 36, fontWeight: 500 }}>Sign Up</h2>

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
                    type="text"
                    name="username"
                    value={form.username}
                    onChange={handleChange}
                    required
                    placeholder="Enter your username"
                    disabled={loading}
                    style={inputStyle(loading)}
                />

                <input
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    required
                    placeholder="Enter your email"
                    disabled={loading}
                    style={inputStyle(loading)}
                />

                <input
                    type="password"
                    name="password"
                    value={form.password}
                    onChange={handleChange}
                    required
                    placeholder="Enter your password"
                    minLength={6}
                    disabled={loading}
                    style={inputStyle(loading)}
                />

                <select
                    name="qualification"
                    value={form.qualification}
                    onChange={handleChange}
                    required
                    disabled={loading}
                    style={selectStyle(loading, form.qualification)}
                >
                    <option value="" disabled>Choose your profession</option>
                    {professions.map((prof) => (
                        <option key={prof} value={prof}>{prof}</option>
                    ))}
                </select>

                <select
                    name="fields_of_interest"
                    value={form.fields_of_interest}
                    onChange={handleChange}
                    required
                    disabled={loading}
                    style={selectStyle(loading, form.fields_of_interest)}
                >
                    <option value="" disabled>Choose your interest</option>
                    {interests.map((interest) => (
                        <option key={interest} value={interest}>{interest}</option>
                    ))}
                </select>

                <p style={{ marginBottom: 16, fontSize: 16, fontFamily: 'JomolhariReg' }}>
                    Already have an account?{" "}
                    <span
                        style={{ color: "#2ad0c4", textDecoration: "underline", fontWeight: 600, cursor: loading ? "not-allowed" : "pointer" }}
                        onClick={() => !loading && onBack("login")}
                    >
                        Log in here
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
                    {loading ? "CREATING ACCOUNT..." : "CONTINUE"}
                </button>
            </form>
        </div>
    );
};

// Reusable styles
const inputStyle = (loading) => ({
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
});

const selectStyle = (loading, hasValue) => ({
    width: "100%",
    maxWidth: 538,
    marginBottom: 24,
    padding: "1rem",
    borderRadius: 12,
    border: "1.5px solid #e0e0e0",
    fontSize: 20,
    background: loading ? "#e0e0e0" : "#f9f9f9",
    color: hasValue ? "#222" : "#7c7979ff",
    outline: "none",
    cursor: loading ? "not-allowed" : "pointer"
});

export default SignUpPage;