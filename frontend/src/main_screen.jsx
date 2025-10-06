import React, { useState } from "react";
import "./App.css";
import LoginScreen from "./login_screen";
import SignUpPage from "./sign_up_page";


const MainScreen = () => {
    const [showSignUp, setShowSignUp] = useState(false);
    const [showLogin, setShowLogin] = useState(false);


    if (showSignUp) {
        return <SignUpPage onBack={() => setShowSignUp(false)} />;
    }
    if (showLogin) {
        return <LoginScreen onBack={() => setShowLogin(false)} />;
    }

    return (
        <div className="main-screen-container" style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
            <header style={{ background: "#DDDCDC", color: "#000000ff", padding: "1rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <img src="src/assets/logo.png" alt="Fraud Finder Logo" style={{ height: "40px" }} />
                <h2 style={{ fontFamily: 'JomolhariReg' }}>Spot fake job postings before you apply</h2>
                <div>
                    <button
                        style={{ fontFamily: 'JomolhariReg', marginRight: "1rem", padding: "0.5rem 1.2rem", borderRadius: "5px", border: "none", background: "#5c5c5cff", color: "#fff", fontWeight: 600, cursor: "pointer" }}
                        onClick={() => setShowSignUp(true)}
                    >
                        Sign Up
                    </button>
                    <button
                        style={{ fontFamily: 'JomolhariReg', padding: "0.5rem 1.2rem", borderRadius: "5px", border: "none", background: "#5c5c5cff", color: "#fff", fontWeight: 600, cursor: "pointer" }}
                        onClick={() => setShowLogin(true)}
                    >
                        Log In
                    </button>
                </div>
            </header>

            <main style={{ flex: 1, padding: "3rem 2rem", background: "#f7f9fb" }}>
                <div style={{
                    maxWidth: 1200,
                    margin: "0 auto",
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "flex-start",
                    height: "100%",
                    gap: "2rem"
                }}>
                    <div style={{
                        background: "#fff",
                        borderRadius: "25px",
                        boxShadow: "0 10px 25px rgba(44, 62, 80, 0.10)",
                        width: "100%",
                        maxWidth: "800px",
                        textAlign: "center",
                        border: "2px solid #e0e0e0",
                        overflow: "hidden"
                    }}>
                        <div style={{
                            background: "#DDDCDC",
                            padding: "1rem"
                        }}>
                            <h1 style={{ fontFamily: 'JomolhariReg', fontSize: "2.3rem", fontWeight: 600, marginBottom: "1.2rem" }}>Is The Job Offer Legit?</h1>
                            <p style={{ fontFamily: 'JomolhariReg', fontSize: "1rem", marginBottom: "1.2rem" }}>Paste a job posting url or its description below. Our AI will analyze if for signs of fraud, helping you stay safe in your job search.</p>
                        </div>

                        <hr style={{
                            border: 0,
                            height: "1px",
                            background: "#DDDCDC",
                            margin: 0
                        }} />

                        <div style={{
                            background: "#fffde7",
                            padding: "1.5rem 2.5rem 2rem 2.5rem"
                        }}>
                            <div style={{
                                background: "#fff",
                                borderRadius: "25px",
                                width: "700px",
                                height: "150px",
                                textAlign: "center",
                                border: "2px solid #e0e0e0",
                                overflow: "hidden"
                            }}>
                                <textarea
                                    style={{
                                        width: "95%",
                                        height: "90%",
                                        border: "none",
                                        outline: "none",
                                        resize: "none",
                                        fontSize: "1.1rem",
                                        fontFamily: 'JomolhariReg',
                                        padding: "1rem",
                                        background: "transparent"
                                    }}
                                    placeholder="Paste the job posting URL or the full text here"
                                />
                            </div>
                            <div>
                                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", margin: "1.5rem 0" }}>
                                    <div style={{ fontFamily: 'JomolhariReg', fontSize: "1.1rem", color: "#333", textAlign: "left" }}>
                                        Choose analysis type -
                                    </div>
                                    <div style={{ display: "flex", gap: "2rem", alignItems: "center" }}>
                                        <label style={{ fontFamily: 'JomolhariReg', fontSize: "1rem", display: "flex", alignItems: "center", cursor: "pointer" }}>
                                            <input type="radio" name="inputType" value="url" style={{ marginRight: "0.5rem" }} defaultChecked />
                                            Quick
                                        </label>
                                        <label style={{ fontFamily: 'JomolhariReg', fontSize: "1rem", display: "flex", alignItems: "center", cursor: "pointer" }}>
                                            <input type="radio" name="inputType" value="description" style={{ marginRight: "0.5rem" }} />
                                            Detailed
                                        </label>
                                    </div>
                                </div>
                            </div>
                            <button style={{
                                fontSize: "1rem",
                                fontFamily: 'JomolhariReg',
                                marginTop: "1.5rem",
                                padding: "0.7rem 1.5rem",
                                borderRadius: "25px",
                                border: "none",
                                background: "#32BCAE",
                                color: "#fff",
                                fontWeight: 600,
                                cursor: "pointer"
                            }}>Analyze Job Posting</button>

                        </div>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", height: "100%" }}>
                        <img src="src/assets/sample.png" alt="sample" style={{ maxWidth: "350px", borderRadius: "15px", boxShadow: "0 10px 15px rgba(44,62,80,0.10)" }} />
                    </div>
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