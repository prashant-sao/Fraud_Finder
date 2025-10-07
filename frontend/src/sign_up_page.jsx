import React, { useState } from "react";
import "./App.css";

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
    "Other"
];

const SignUpPage = ({ onBack }) => {
    const [form, setForm] = useState({
        name: "",
        email: "",
        password: "",
        profession: "",
        interest: ""
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        // Handle signup logic here
        alert("Sign up submitted!\n" + JSON.stringify(form, null, 2));
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
                <h2 style={{ fontFamily: 'JomolhariReg', textAlign: "center", marginBottom: "2rem", fontSize: 36, fontWeight: 500 }}>Sign Up</h2>
                <input
                    type="text"
                    name="name"
                    value={form.name}
                    onChange={handleChange}
                    required
                    placeholder="Enter your name"
                    style={{ width: "100%", maxWidth: 500, marginBottom: 24, padding: "1rem", borderRadius: 12, border: "1.5px solid #e0e0e0", fontSize: 20, background: "#f9f9f9", outline: "none" }}
                />
                <input
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    required
                    placeholder="Enter your email"
                    style={{ width: "100%", maxWidth: 500, marginBottom: 24, padding: "1rem", borderRadius: 12, border: "1.5px solid #e0e0e0", fontSize: 20, background: "#f9f9f9", outline: "none" }}
                />
                <input
                    type="password"
                    name="password"
                    value={form.password}
                    onChange={handleChange}
                    required
                    placeholder="Enter your password"
                    style={{ width: "100%", maxWidth: 500, marginBottom: 24, padding: "1rem", borderRadius: 12, border: "1.5px solid #e0e0e0", fontSize: 20, background: "#f9f9f9", outline: "none" }}
                />
                <select
                    name="profession"
                    value={form.profession}
                    onChange={handleChange}
                    required
                    style={{ width: "100%", maxWidth: 538, marginBottom: 24, padding: "1rem", borderRadius: 12, border: "1.5px solid #e0e0e0", fontSize: 20, background: "#f9f9f9", color: form.profession ? "#222" : "#7c7979ff", outline: "none" }}
                >
                    <option value="" disabled>Choose your profession</option>
                    {professions.map((prof) => (
                        <option key={prof} value={prof}>{prof}</option>
                    ))}
                </select>
                <select
                    name="interest"
                    value={form.interest || ""}
                    onChange={handleChange}
                    required
                    style={{ width: "100%", maxWidth: 538, marginBottom: 24, padding: "1rem", borderRadius: 12, border: "1.5px solid #e0e0e0", fontSize: 20, background: "#f9f9f9", color: form.interest ? "#222" : "#7c7979ff", outline: "none" }}
                >
                    <option value="" disabled>Choose your interest</option>
                    {interests.map((interest) => (
                        <option key={interest} value={interest}>{interest}</option>
                    ))}
                </select>
                <p style={{ marginBottom: 16, fontSize: 16 }}>
                    Already have an account?{" "}
                    <span
                        style={{ color: "#2ad0c4", textDecoration: "underline", fontWeight: 600, cursor: "pointer" }}
                        onClick={() => onBack("login")}
                    >
                        Log in here
                    </span>
                </p>
                <button type="submit" style={{
                    width: 220,
                    padding: "1rem",
                    borderRadius: 16,
                    border: "none",
                    background: "#2ad0c4",
                    color: "#fff",
                    fontWeight: 700,
                    fontSize: 18,
                    fontFamily: 'JomolhariReg',
                    cursor: "pointer",
                    marginTop: 16,
                    letterSpacing: 1
                }}>CONTINUE</button>
            </form>
        </div>
    );
};

export default SignUpPage;