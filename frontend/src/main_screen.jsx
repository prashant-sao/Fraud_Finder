import React from "react";
import "./App.css";

const MainScreen = () => {
    return (
        <div className="main-screen-container" style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
            <header style={{ background: "#DDDCDC", color: "#000000ff", padding: "1rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <img src="src/assets/logo.png" alt="Fraud Finder Logo" style={{ height: "40px" }} />
                <h2 style={{ fontFamily: 'JomolhariReg' }}>Spot fake job postings before you apply</h2>
                <div>
                    <button style={{ fontFamily: 'JomolhariReg', marginRight: "1rem", padding: "0.5rem 1.2rem", borderRadius: "5px", border: "none", background: "#5c5c5cff", color: "#fff", fontWeight: 600, cursor: "pointer"}}>Sign In</button>
                    <button style={{ fontFamily: 'JomolhariReg', padding: "0.5rem 1.2rem", borderRadius: "5px", border: "none", background: "#5c5c5cff", color: "#fff", fontWeight: 600, cursor: "pointer"}}>Sign Up</button>
                </div>
            </header>

            <main style={{ flex: 1, padding: "3rem 2rem", background: "#f7f9fb" }}>
                <div style={{ maxWidth: 900, margin: "0 auto", textAlign: "center" }}>
                    <h2 style={{ fontFamily: 'JomolhariReg', fontSize: "2rem", fontWeight: 600, marginBottom: "1.5rem" }}>Welcome to Fraud Finder</h2>
                    <p style={{ fontFamily: 'JomolhariReg', fontSize: "1.2rem", color: "#444", marginBottom: "2rem" }}>
                        Your trusted platform for detecting and preventing fraudulent activities. Analyze suspicious contacts, get instant scam checks, and stay protected with our advanced AI-powered tools.
                    </p>
                </div>
            </main>

            <footer style={{ background: "#2C3E50", color: "#ffffffff", padding: "2rem 2rem 1rem 2rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", maxWidth: 1400, margin: "0 auto", flexWrap: "wrap" }}>
                    <div style={{ flex: "1 1 230px", margin: "0 1rem" }}>
                        <img src="src/assets/logo.png" alt="Fraud Finder Logo" style={{ height: "40px" }} />
                        <ul style={{ listStyle: "none", padding: 0, color: "#fff" }}>
                            <p style={{ fontFamily: 'JomolhariReg' }}>Our tool analyses job postings and identifies potential red flags. We check for inconsistencies, unrealistic promises, and other indicators of fraud.</p>
                        </ul>
                    </div>
                    <div style={{ flex: "1 1 230px", margin: "0 1rem" }}>
                        <h3 style={{ fontFamily: 'JomolhariReg', color: "#fff" }}>How It Works</h3>
                        <ul style={{ listStyle: "none", padding: 0, color: "#fff" }}>
                            <p style={{ fontFamily: 'JomolhariReg' }}>Machine Learning : Our algorithms learn from vast amounts of data to identify patterns and anomalies associated with fraudulent activities.</p>
                        </ul>
                    </div>
                    <div style={{ flex: "1 1 230px", margin: "0 1rem" }}>
                        <h3 style={{ fontFamily: 'JomolhariReg', color: "#fff" }}>Advanced Analysis</h3>
                        <ul style={{ listStyle: "none", padding: 0, color: "#fff" }}>
                            <p style={{ fontFamily: 'JomolhariReg' }}>Real-time Detection : We analyze new posting as they appear, providing you with up-to-the-minute protections against scams.</p>
                        </ul>
                    </div>
                    <div style={{ flex: "1 1 230px", margin: "0 1rem" }}>
                        <h3 style={{ fontFamily: 'JomolhariReg', color: "#fff" }}>Contact Us</h3>
                        <ul style={{ listStyle: "none", padding: 0, color: "#fff" }}>
                            <li style={{ fontFamily: 'JomolhariReg' }}>Email : support@fraudfinder.com</li>
                            <li style={{ fontFamily: 'JomolhariReg' }}>Phone : +91 1234567890</li>
                        </ul>
                    </div>
                </div>
                <div style={{ fontFamily: 'JomolhariReg', textAlign: "center", color: "#888", fontSize: "0.95rem" }}>
                    &copy; {new Date().getFullYear()} Fraud Finder. All rights reserved.
                </div>
            </footer>
        </div>
    );
};

export default MainScreen;