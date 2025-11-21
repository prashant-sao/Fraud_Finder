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

    // ML Recommendation state
    const [recommendation, setRecommendation] = useState(null);
    const [loadingRecommendation, setLoadingRecommendation] = useState(false);
    const [userId, setUserId] = useState("");
    const [visibleCount, setVisibleCount] = useState(1);


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

    const handleMLRecommend = async () => {
        setRecommendation(null);
        setLoadingRecommendation(true);
        try {
            // Use the current input as job data, or provide defaults
            const job = {
                title: input || 'Sample Job',
                company: 'Sample Company',
                url: '',
                source: 'User',
            };
            const response = await fetch("/api/ml_recommend", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(job)
            });
            const data = await response.json();
            if (!response.ok || data.error) {
                setRecommendation({
                    error: data.error || "Failed to load recommendation."
                });
            } else {
                setRecommendation(data);
            }
        } catch (err) {
            setRecommendation({ error: err.message });
        } finally {
            setLoadingRecommendation(false);
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
                                        {/* <label style={{ fontFamily: 'JomolhariReg', fontSize: "1rem", display: "flex", alignItems: "center", cursor: userName ? "pointer" : "not-allowed", opacity: userName ? 1 : 0.5 }}>
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
                                        </label> */}
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
                                    <span style={{ fontWeight: 600 }}>Failed to analyze -</span> {result.error}
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
                                            Risk Score -{result.fraud_score} ({result.risk_level})
                                        </span>
                                        <div style={{
                                            marginTop: '0.7rem',
                                            marginBottom: '0.5rem',
                                            width: '100%',
                                            maxWidth: 900,
                                            height: 22,
                                            background: 'linear-gradient(90deg, #43a047 0%, #fbc02d 50%, #e53935 100%)',
                                            borderRadius: 12,
                                            position: 'relative',
                                            boxShadow: '0 2px 8px rgba(44,62,80,0.07)'
                                        }}>
                                            <div style={{
                                                position: 'absolute',
                                                left: 0,
                                                top: 0,
                                                height: '100%',
                                                width: `${Math.max(0, Math.min(100, result.fraud_score))}%`,
                                                borderRadius: 12,
                                                background: 'rgba(255,255,255,0.15)',
                                                boxSizing: 'border-box',
                                                transition: 'width 0.5s cubic-bezier(.4,2,.6,1)'
                                            }} />
                                            <div style={{
                                                position: 'absolute',
                                                left: `${Math.max(0, Math.min(100, result.fraud_score))}%`,
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
                                                {result.fraud_score}
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
                                                <span style={{ fontWeight: 600 }}>Red Flags -</span>
                                                <div style={{
                                                    display: 'grid',
                                                    gridTemplateColumns: '1fr 1fr',
                                                    gap: '1rem',
                                                    marginTop: '0.7rem',
                                                    marginBottom: '0.5rem',
                                                    minHeight: 120
                                                }}>
                                                    {(() => {
                                                        const flagMessages = {
                                                            'vague_description': 'Vague Job Description',
                                                            'unrealistic_salary': 'Unrealistic Salary/Benefits',
                                                            'no_company_info': 'No Company Information',
                                                            'requests_personal_details': 'Request for Personal Details',
                                                            'poor_grammar': 'Poor Grammar/Spelling',
                                                            'suspicious_contact': 'Suspicious Contact Methods',
                                                            'no_linkedin': 'No LinkedIn Presence',
                                                            'no_company_website': 'No Company Website'
                                                        };

                                                        const flagImages = {
                                                            vague_description: "/src/assets/vague_jd.png",
                                                            unrealistic_salary: "/src/assets/unreal_salary.png",
                                                            no_company_info: "/src/assets/no_comp_info.png",
                                                            requests_personal_details: "/src/assets/personal_info.png",
                                                            poor_grammar: "/src/assets/poor_grammar.png",
                                                            suspicious_contact: "/src/assets/sus_contact.png",
                                                            no_linkedin: "/src/assets/no_linkedin.png",
                                                            no_company_website: "/src/assets/no_website.png"
                                                        };

                                                        const flags = result.analysis.red_flags;

                                                        const activeFlags = Object.entries(flags)
                                                            .filter(([key, value]) => value === true)
                                                            .map(([key]) => [key, flagMessages[key]]);


                                                        return activeFlags.map(([key, label], idx) => (
                                                            <div
                                                                key={idx}
                                                                style={{
                                                                    background: '#c0c0c0',
                                                                    border: '2px solid #c0c0c0',
                                                                    borderRadius: 25,
                                                                    width: 295,
                                                                    height: 120,
                                                                    display: 'flex',
                                                                    flexDirection: 'column',
                                                                    alignItems: 'center',
                                                                    justifyContent: 'center',
                                                                    fontWeight: 500,
                                                                    fontSize: 18,
                                                                    color: '#000000',
                                                                    boxShadow: '0 2px 8px rgba(44,62,80,0.2)',
                                                                    padding: 10,
                                                                    textAlign: 'center',
                                                                    transition: 'transform 0.2s',
                                                                }}
                                                            >
                                                                <img
                                                                    src={flagImages[key]}
                                                                    alt={label}
                                                                    style={{
                                                                        width: 50,
                                                                        height: 50,
                                                                        objectFit: "contain",
                                                                        marginBottom: 8
                                                                    }}
                                                                />
                                                                <div>{label}</div>
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

                    {/* ML Recommendation Panel */}
                    <div style={{
                        width: "350px",
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "flex-start",
                        top: "20px",
                    }}>

                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem', gap: '1rem' }}>
                            <h2 style={{
                                fontFamily: 'JomolhariReg',
                                fontSize: "1.7rem",
                                margin: 0
                            }}>
                                Job Recommendations
                            </h2>
                        </div>

                        <button
                            onClick={handleMLRecommend}
                            style={{
                                fontFamily: 'JomolhariReg',
                                padding: '0.5rem 1.2rem',
                                borderRadius: '25px',
                                border: 'none',
                                background: '#32BCAE',
                                color: '#fff',
                                fontWeight: 600,
                                fontSize: '1rem',
                                cursor: 'pointer',
                                marginLeft: '0.5rem'
                            }}
                            disabled={loadingRecommendation}
                        >
                            {loadingRecommendation ? 'Loading...' : 'Get Recommendation'}
                        </button>

                        {/* LOADING */}
                        {loadingRecommendation && (
                            <div style={{
                                background: "#e0f7fa",
                                borderRadius: "20px",
                                padding: "1.8rem 1.2rem",
                                marginTop: "12px",
                                width: "90%",
                                color: "#00796b",
                                fontFamily: 'JomolhariReg',
                                textAlign: "center",
                                boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
                                border: "1px solid #b2ebf2",
                                fontSize: "1.1rem"
                            }}>
                                Fetching job recommendations...
                                <div style={{ marginTop: "10px", fontSize: "0.9rem", opacity: 0.8 }}>
                                    Please wait while we analyze safe & risky jobs
                                </div>
                            </div>
                        )}

                        {/* ERROR */}
                        {recommendation && recommendation.error && (
                            <div style={{
                                marginTop: "1rem",
                                background: "#ffebee",
                                borderRadius: "20px",
                                padding: "1.4rem 1.5rem",
                                width: "90%",
                                color: "#c62828",
                                fontFamily: 'JomolhariReg',
                                border: "1px solid #ffcdd2",
                                boxShadow: "0 4px 12px rgba(0,0,0,0.12)",
                                fontSize: "1.05rem"
                            }}>
                                <strong style={{ fontWeight: 700 }}>❌ Error:</strong> {recommendation.error}
                                <div style={{ marginTop: "8px", fontSize: "0.95rem", opacity: 0.8 }}>
                                    Please try again or check your internet connection.
                                </div>
                            </div>
                        )}

                        {/* SUCCESS RECOMMENDATION */}
                        {recommendation && !recommendation.error && (
                            <div style={{
                                marginTop: "1rem",
                                borderRadius: "25px",
                                padding: "1rem 1rem",
                                width: "90%",
                                boxShadow: "0 10px 10px rgba(44,62,80,0.2)",
                                fontFamily: 'JomolhariReg',
                                border: "1px solid #32BCAE",
                                background: "#f0fffd"
                            }}>

                                {/* SUMMARY */}
                                <h3 style={{
                                    margin: 0,
                                    fontSize: "1.45rem",
                                    marginBottom: "0.6rem"
                                }}>
                                    Recommended Jobs Summary
                                </h3>

                                <div style={{ fontSize: "1.05rem", marginBottom: "1rem", lineHeight: "1.5" }}>
                                    <div><strong>Total Recommendations:</strong> {recommendation.total_recommendations}</div>
                                    <div><strong>Safe Jobs:</strong> {recommendation.safe_jobs_count}</div>
                                    <div><strong>Risky Jobs:</strong> {recommendation.risky_jobs_count}</div>
                                </div>

                                <hr style={{ borderTop: "1px solid #ccc", margin: "1rem 0" }} />

                                <h3 style={{ marginBottom: "0.6rem", marginTop: "0" }}>Job Recommendations</h3>

                                {/* JOB LIST WITH LOAD MORE */}
                                {recommendation.recommendations &&
                                    recommendation.recommendations
                                        .slice(0, visibleCount)
                                        .map((job, index) => (
                                            <div key={index} style={{
                                                background: "#ffffff",
                                                borderRadius: "20px",
                                                padding: "1rem",
                                                marginBottom: "1.1rem",
                                                border: "1px solid #d0f0eb",
                                                boxShadow: "0 4px 10px rgba(0,0,0,0.08)"
                                            }}>

                                                <h4 style={{
                                                    margin: "0 0 0.3rem 0",
                                                    fontSize: "1.25rem"
                                                }}>
                                                    {job.title}
                                                </h4>

                                                <div style={{ fontSize: "1rem", marginBottom: "0.3rem" }}>
                                                    <strong>Company:</strong> {job.company}
                                                </div>

                                                <div style={{ fontSize: "1rem", marginBottom: "0.3rem" }}>
                                                    <strong>Fraud Score:</strong> {job.fraud_score}
                                                </div>

                                                {/* HTML DESCRIPTION */}
                                                <div
                                                    style={{ marginTop: "0.4rem", fontSize: "1rem", lineHeight: "1.4" }}
                                                    dangerouslySetInnerHTML={{ __html: job.description }}
                                                />

                                                <a
                                                    href={job.link}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    style={{
                                                        display: "inline-block",
                                                        marginTop: "0.8rem",
                                                        padding: "0.5rem 1.1rem",
                                                        background: "#1976d2",
                                                        color: "white",
                                                        borderRadius: "12px",
                                                        textDecoration: "none",
                                                        fontFamily: 'JomolhariReg',
                                                        fontWeight: 600
                                                    }}
                                                >
                                                    View Job →
                                                </a>
                                            </div>
                                        ))
                                }

                                {/* LOAD MORE BUTTON */}
                                {recommendation.recommendations &&
                                    visibleCount < recommendation.recommendations.length && (
                                        <button
                                            onClick={() => setVisibleCount(prev => prev + 3)}
                                            style={{
                                                padding: "0.6rem 1rem",
                                                background: "#32BCAE",
                                                color: "white",
                                                borderRadius: "12px",
                                                border: "none",
                                                cursor: "pointer",
                                                fontFamily: 'JomolhariReg',
                                                fontWeight: 600,
                                                display: "block",
                                                margin: "10px auto"
                                            }}
                                        >
                                            Load More ↓
                                        </button>
                                    )}

                                {/* SHOW LESS BUTTON */}
                                {visibleCount > 1 && (
                                    <button
                                        onClick={() => setVisibleCount(1)}
                                        style={{
                                            padding: "0.6rem 1rem",
                                            background: "#b0bec5",
                                            color: "white",
                                            borderRadius: "12px",
                                            border: "none",
                                            cursor: "pointer",
                                            fontFamily: 'JomolhariReg',
                                            fontWeight: 600,
                                            display: "block",
                                            margin: "10px auto"
                                        }}
                                    >
                                        Show Less ↑
                                    </button>
                                )}

                            </div>
                        )}
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