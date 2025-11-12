import React, { useState } from "react";
import "./App.css";

import LoginScreen from "./login_screen";
import SignUpPage from "./sign_up_page";
import ProfilePage from "./profile_page";

const MainScreen = () => {
    const [showSignUp, setShowSignUp] = useState(false);
    const [showLogin, setShowLogin] = useState(false);
    const [userName, setUserName] = useState("");
    const [showProfile, setShowProfile] = useState(false);
    // Analysis state
    const [input, setInput] = useState("");
    const [analysisType, setAnalysisType] = useState("quick");
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    // Handler for successful login/sign
    const handleAuthSuccess = (name) => {
        setUserName(name);
        setShowSignUp(false);
        setShowLogin(false);
    };

    if (showSignUp) {
        return <SignUpPage onBack={() => setShowSignUp(false)} onAuthSuccess={handleAuthSuccess} />;
    }
    if (showLogin) {
        return <LoginScreen onBack={() => setShowLogin(false)} onAuthSuccess={handleAuthSuccess} />;
    }
    if (showProfile) {
        return <ProfilePage userName={userName} onBack={() => setShowProfile(false)} />;
    }

    // Analysis logic (from AnalysisPage)
    const handleAnalyze = async (e) => {
        e.preventDefault();
        setResult(null);
        if (!input.trim()) {
            setResult({ error: "Please enter a job posting URL or description." });
            return;
        }
        // Detect if input is a URL
        const isUrl = /^https?:\/\//i.test(input.trim());
        const payload = {
            job_text: isUrl ? "" : input.trim(),
            job_url: isUrl ? input.trim() : "",
            company_name: "",
            analysis_type: analysisType,
            job_title: ""
        };
        setLoading(true);
        try {
            const response = await fetch("/api/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            if (!response.ok || data.error) {
                setResult({ error: data.error || "Failed to analyze. Please try again." });
            } else {
                setResult(data);
            }
        } catch (err) {
            setResult({ error: err.message });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="main-screen-container" style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
            <header style={{ background: "#DDDCDC", color: "#000000ff", padding: "1rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <img src="src/assets/logo.png" alt="Fraud Finder Logo" style={{ height: "40px" }} />
                <h2 style={{ fontFamily: 'JomolhariReg' }}>Spot fake job postings before you apply</h2>
                <div>
                    {userName ? (
                        <span
                            style={{ fontFamily: 'JomolhariReg', fontWeight: 600, fontSize: 20, color: "#32BCAE", marginRight: "1rem", cursor: "pointer", textDecoration: "underline" }}
                            onClick={() => setShowProfile(true)}
                        >
                            Welcome, {userName}
                        </span>
                    ) : (
                        <>
                            <button
                                style={{ fontFamily: 'JomolhariReg', marginRight: "1rem", padding: "0.5rem 1.2rem", borderRadius: "25px", border: "none", background: "#5c5c5cff", color: "#fff", fontWeight: 600, cursor: "pointer" }}
                                onClick={() => setShowSignUp(true)}
                            >
                                Sign Up
                            </button>
                            <button
                                style={{ fontFamily: 'JomolhariReg', marginRight: "1rem", padding: "0.5rem 1.2rem", borderRadius: "25px", border: "none", background: "#5c5c5cff", color: "#fff", fontWeight: 600, cursor: "pointer" }}
                                onClick={() => setShowLogin(true)}
                            >
                                Log In
                            </button>
                        </>
                    )}
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
                    gap: "2rem",
                    marginRight: "1rem"
                }}>
                    <div style={{
                        background: "#fff",
                        borderRadius: "25px",
                        boxShadow: "0 10px 25px rgba(44, 62, 80, 0.10)",
                        width: "100%",
                        maxWidth: "800px",
                        textAlign: "center",
                        border: "2px solid #e0e0e0",
                        overflow: "hidden",
                        marginRight: "1rem"
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
                                    placeholder={userName ? "Paste the job posting URL or the full text here" : "Log in to analyze job postings"}
                                    value={input}
                                    onChange={e => setInput(e.target.value)}
                                    disabled={!userName}
                                />
                            </div>
                            <div>
                                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", margin: "1.5rem 0" }}>
                                    <div style={{ fontFamily: 'JomolhariReg', fontSize: "1.1rem", color: "#333", textAlign: "left" }}>
                                        Choose analysis type -
                                    </div>
                                    <div style={{ display: "flex", gap: "2rem", alignItems: "center" }}>
                                        <label style={{ fontFamily: 'JomolhariReg', fontSize: "1rem", display: "flex", alignItems: "center", cursor: userName ? "pointer" : "not-allowed", opacity: userName ? 1 : 0.5 }}>
                                            <input
                                                type="radio"
                                                name="analysisType"
                                                value="quick"
                                                checked={analysisType === "quick"}
                                                onChange={() => userName && setAnalysisType("quick")}
                                                style={{ marginRight: "0.5rem" }}
                                                disabled={!userName}
                                            />
                                            Quick
                                        </label>
                                        <label style={{ fontFamily: 'JomolhariReg', fontSize: "1rem", display: "flex", alignItems: "center", cursor: userName ? "pointer" : "not-allowed", opacity: userName ? 1 : 0.5 }}>
                                            <input
                                                type="radio"
                                                name="analysisType"
                                                value="detailed"
                                                checked={analysisType === "detailed"}
                                                onChange={() => userName && setAnalysisType("detailed")}
                                                style={{ marginRight: "0.5rem" }}
                                                disabled={!userName}
                                            />
                                            Detailed
                                        </label>
                                    </div>
                                </div>
                            </div>
                            <form onSubmit={handleAnalyze}>
                                <button
                                    type="submit"
                                    style={{
                                        fontSize: "1rem",
                                        fontFamily: 'JomolhariReg',
                                        marginTop: "1.5rem",
                                        padding: "0.7rem 1.5rem",
                                        borderRadius: "25px",
                                        border: "none",
                                        background: !userName ? "#bdbdbd" : (loading ? "#b2dfdb" : "#32BCAE"),
                                        color: "#fff",
                                        fontWeight: 600,
                                        cursor: !userName ? "not-allowed" : (loading ? "not-allowed" : "pointer")
                                    }}
                                    disabled={loading || !userName}
                                >
                                    {loading ? "Analyzing..." : "Analyze Job Posting"}
                                </button>
                            </form>
                            {!userName && (
                                <div style={{
                                    marginTop: "1.2rem",
                                    color: "#b71c1c",
                                    fontFamily: 'JomolhariReg',
                                    fontSize: "1.1rem",
                                    textAlign: "center"
                                }}>
                                    Please log in to analyze job postings.
                                </div>
                            )}
                            {result && result.error ? (
                                <div style={{
                                    marginTop: "2rem",
                                    background: "#ffebee",
                                    borderRadius: "15px",
                                    padding: "1.2rem 2rem",
                                    color: "#b71c1c",
                                    fontFamily: 'JomolhariReg',
                                    fontSize: "1.1rem",
                                    textAlign: "left",
                                    border: "1px solid #e57373"
                                }}>
                                    <span style={{ fontWeight: 600 }}>Failed to analyze:</span> {result.error}
                                </div>
                            ) : result && typeof result === 'object' ? (
                                <div style={{
                                    marginTop: "2rem",
                                    background: "#f0f4c3",
                                    borderRadius: "15px",
                                    padding: "1.5rem 2rem",
                                    color: "#333",
                                    fontFamily: 'JomolhariReg',
                                    fontSize: "1.1rem",
                                    textAlign: "left"
                                }}>
                                    <div style={{ marginBottom: '1rem' }}>
                                        <span style={{ fontWeight: 700, fontSize: '1.3rem', color: result.risk_color || '#333' }}>
                                            Risk Score - {result.risk_score} ({result.risk_level})
                                        </span>
                                        <div style={{
                                            marginTop: '0.7rem',
                                            marginBottom: '0.5rem',
                                            width: '100%',
                                            maxWidth: 400,
                                            height: 22,
                                            background: 'linear-gradient(90deg, #e53935 0%, #fbc02d 50%, #43a047 100%)',
                                            borderRadius: 12,
                                            position: 'relative',
                                            boxShadow: '0 2px 8px rgba(44,62,80,0.07)'
                                        }}>
                                            <div style={{
                                                position: 'absolute',
                                                left: 0,
                                                top: 0,
                                                height: '100%',
                                                width: `${Math.max(0, Math.min(100, result.risk_score))}%`,
                                                borderRadius: 12,
                                                background: 'rgba(255,255,255,0.15)',
                                                border: '2px solid #fff',
                                                boxSizing: 'border-box',
                                                transition: 'width 0.5s cubic-bezier(.4,2,.6,1)'
                                            }} />
                                            <div style={{
                                                position: 'absolute',
                                                left: `${Math.max(0, Math.min(100, result.risk_score))}%`,
                                                top: 0,
                                                transform: 'translateX(-50%)',
                                                color: '#222',
                                                fontWeight: 700,
                                                fontSize: 14,
                                                lineHeight: '22px',
                                                padding: '0 6px',
                                                background: 'rgba(255,255,255,0.85)',
                                                borderRadius: 8,
                                                boxShadow: '0 1px 4px rgba(44,62,80,0.08)'
                                            }}>
                                                {result.risk_score}
                                            </div>
                                        </div>
                                    </div>
                                    <div style={{ marginBottom: '1rem' }}>
                                        <span style={{ fontWeight: 600 }}>Verdict -</span> {result.verdict}
                                    </div>
                                    <div style={{ marginBottom: '1rem' }}>
                                        <span style={{ fontWeight: 600 }}>Is Scam -</span> {result.is_scam ? 'Yes' : 'No'}
                                    </div>
                                    {result.analysis && (
                                        <>
                                            <div style={{ marginBottom: '1rem' }}>
                                                <span style={{ fontWeight: 600 }}>Red Flags:</span>
                                                <div style={{
                                                    display: 'grid',
                                                    gridTemplateColumns: '1fr 1fr',
                                                    gap: '1rem',
                                                    marginTop: '0.7rem',
                                                    marginBottom: '0.5rem',
                                                    minHeight: 120
                                                }}>
                                                    {(() => {
                                                        const flags = Array.isArray(result.analysis.red_flags) ? result.analysis.red_flags.slice(0, 8) : [];
                                                        while (flags.length < 8) flags.push('No flag');
                                                        return flags.map((flag, idx) => (
                                                            <div key={idx} style={{
                                                                background: '#fff',
                                                                border: '2px solid #e57373',
                                                                borderRadius: 12,
                                                                width: 100,
                                                                height: 100,
                                                                minWidth: 100,
                                                                minHeight: 100,
                                                                maxWidth: 100,
                                                                maxHeight: 100,
                                                                display: 'flex',
                                                                alignItems: 'center',
                                                                justifyContent: 'center',
                                                                fontWeight: 500,
                                                                fontSize: 13,
                                                                color: '#b71c1c',
                                                                boxShadow: '0 2px 8px rgba(44,62,80,0.07)',
                                                                padding: 0,
                                                                textAlign: 'center',
                                                                transition: 'background 0.3s',
                                                                overflow: 'hidden',
                                                                wordBreak: 'break-word'
                                                            }}>
                                                                {flag}
                                                            </div>
                                                        ));
                                                    })()}
                                                </div>
                                            </div>
                                            <div style={{ marginBottom: '1rem' }}>
                                                <div style={{ marginLeft: '1em' }}>{result.analysis.llm_analysis}</div>
                                            </div>
                                        </>
                                    )}
                                    {result.auto_reply && (
                                        <div style={{ marginTop: '1.5rem', background: '#e0f7fa', borderRadius: '10px', padding: '1rem' }}>
                                            <span style={{ fontWeight: 600 }}>Auto Reply Suggestion -</span>
                                        </div>
                                    )}
                                </div>
                            ) : result && (
                                <div style={{
                                    marginTop: "2rem",
                                    background: "#f0f4c3",
                                    borderRadius: "15px",
                                    padding: "1rem",
                                    color: "#333",
                                    fontFamily: 'JomolhariReg',
                                    fontSize: "1.1rem"
                                }}>
                                    {typeof result === 'string' ? result : JSON.stringify(result)}
                                </div>
                            )}
                        </div>
                    </div>
                    <div style={{ display: "flex", alignItems: "right", height: "100%" }}>
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