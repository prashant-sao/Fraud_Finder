import React, { useState } from "react";

const ProfilePage = ({ userName, onBack }) => {
    const [selected, setSelected] = useState("history");

    // Accept onLogout from parent (main_screen)
    const handleLogout = async () => {
        try {
            await fetch("/api/logout", { method: "POST", credentials: "include" });
        } catch (err) {
            // Optionally handle error, but still clear state
        }
        localStorage.removeItem("user");
        localStorage.removeItem("token");
        localStorage.clear();
        sessionStorage.clear();
        if (typeof onLogout === "function") onLogout();
        else if (typeof onBack === "function") onBack();
    };


    const analysisHistory = [
        { id: 1, date: "2023-10-01", title: "Job Posting 1", result: "No issues detected" },
        { id: 2, date: "2023-10-05", title: "Job Posting 2", result: "Potential fraud detected: High salary promise" },
        { id: 3, date: "2023-10-10", title: "Job Posting 3", result: "No issues detected" },
        { id: 4, date: "2023-10-12", title: "Job Posting 4", result: "Potential fraud detected: Lack of company details" }
    ];

    const downloadHistory = [
        { id: 1, date: "2023-10-01", title: "Senior Software Engineer", result: "High Risk" },
        { id: 2, date: "2023-10-05", title: "Product Manager", result: "Medium Risk" },
        { id: 3, date: "2023-10-10", title: "Marketing Coordinator", result: "Low Risk" }
    ];

    return (
        <div style={{ minHeight: "100vh", background: "#f7f9fb", display: "flex", flexDirection: "column" }}>
            <header style={{ background: "#DDDCDC", color: "#000000ff", padding: "1rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <img src="src/assets/logo.png" alt="Fraud Finder Logo" style={{ height: "40px" }} />
                <h2 style={{ fontFamily: 'JomolhariReg' }}>User Profile</h2>
            </header>

            <main style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", position: "relative", padding: "2rem" }}>
                <div style={{ position: "absolute", top: 32, left: 32, cursor: "pointer", fontSize: 28 }} onClick={onBack}>
                    <span style={{ fontWeight: 600 }}>&larr;</span>
                </div>
                <div style={{ display: "flex", background: "#fff", borderRadius: "25px", boxShadow: "0 10px 25px rgba(44, 62, 80, 0.10)", minWidth: 700, minHeight: 400, width: "70%", maxWidth: 900 }}>
                    <Sidebar userName={userName} onLogout={handleLogout} setSelected={setSelected} selected={selected} />
                    <MainContent selected={selected} analysisHistory={analysisHistory} downloadHistory={downloadHistory} />
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

// Sidebar Component
function Sidebar({ userName, onLogout, setSelected, selected }) {
    const options = [
        { key: "history", label: "Analysis History", icon: "src/assets/history.png" },
        { key: "downloads", label: "Downloads", icon: "src/assets/downloads.png" },
        { key: "edit", label: "Edit Profile", icon: "src/assets/edit_profile.png" },
        { key: "logout", label: "Logout", icon: "src/assets/logout.png" }
    ];

    return (
        <div style={{ width: 220, borderRight: "1.5px solid #e0e0e0", padding: "2rem 1rem", display: "flex", flexDirection: "column", alignItems: "flex-start", background: "#f7f9fb", borderRadius: "25px 0 0 25px" }}>
            <div style={{ fontSize: 20, fontWeight: 600, color: "#32BCAE", marginBottom: 32, fontFamily: 'JomolhariReg' }}>
                {userName ? `Welcome, ${userName}` : "User info unavailable"}
            </div>
            {options.map(opt => (
                <button
                    key={opt.key}
                    onClick={() => {
                        if (opt.key === "logout") {
                            onLogout();
                        } else {
                            setSelected(opt.key);
                        }
                    }}
                    style={{
                        width: "100%",
                        padding: "0.8rem 1rem",
                        marginBottom: 18,
                        borderRadius: 12,
                        border: "none",
                        background: selected === opt.key ? "#32BCAE" : "#fff",
                        color: selected === opt.key ? "#fff" : "#222",
                        fontWeight: 600,
                        fontSize: 18,
                        fontFamily: 'JomolhariReg',
                        cursor: "pointer",
                        boxShadow: selected === opt.key ? "0 2px 8px rgba(44,62,80,0.10)" : "none",
                        display: "flex",
                        alignItems: "center"
                    }}
                >
                    <img src={opt.icon} alt="" style={{ marginRight: "0.7rem", height: 24, width: 24, verticalAlign: "middle" }} />
                    {opt.label}
                </button>
            ))}
        </div>
    );
}

// MainContent Component
function MainContent({ selected, analysisHistory, downloadHistory }) {
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
    const [form, setForm] = React.useState({
        email: "",
        profession: professions[0],
        interest: interests[0]
    });
    let content;
    switch (selected) {
        case "history":
            content = (
                <div style={{ padding: "2rem" }}>
                    <h3>Analysis History</h3>
                    <div style={{ maxHeight: "300px", overflowY: "auto" }}>
                        {analysisHistory.map((analysis) => (
                            <div key={analysis.id} style={{ marginBottom: "16px", padding: "12px", backgroundColor: "#f1f1f1", borderRadius: "25px" }}>
                                <h4>{analysis.title}</h4>
                                <p><strong>Date : </strong> {analysis.date}</p>
                                <p><strong>Result : </strong> {analysis.result}</p>
                            </div>
                        ))}
                    </div>
                </div>
            );
            break;
        case "downloads":
            content = (
                <div style={{ padding: "2rem" }}>
                    <h3>Downloads</h3>
                    <div style={{ maxHeight: "300px", overflowY: "auto" }}>
                        {downloadHistory.map((analysis) => (
                            <div key={analysis.id} style={{ marginBottom: "16px", padding: "12px", backgroundColor: "#f1f1f1", borderRadius: "25px" }}>
                                <h4>{analysis.title}</h4>
                                <p><strong>Date : </strong> {analysis.date}</p>
                                <p><strong>Result : </strong> {analysis.result}</p>
                            </div>
                        ))}
                    </div>
                </div>
            );
            break;
        case "edit":
            content = (
                <div style={{ padding: "2rem", maxWidth: 400, margin: "0 auto" }}>
                    <h3>Edit Profile</h3>
                    <form onSubmit={e => { e.preventDefault(); alert("Profile updated!\n" + JSON.stringify(form, null, 2)); }}>
                        <label style={{ display: "block", marginBottom: 12, fontWeight: 500 }}>Email:</label>
                        <input
                            type="email"
                            value={form.email}
                            onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                            placeholder="Enter your email"
                            style={{ width: "100%", padding: "0.8rem", borderRadius: 12, border: "1.5px solid #e0e0e0", marginBottom: 18, fontSize: 18 }}
                            required
                        />
                        <label style={{ display: "block", marginBottom: 12, fontWeight: 500 }}>Profession:</label>
                        <select
                            value={form.profession}
                            onChange={e => setForm(f => ({ ...f, profession: e.target.value }))}
                            style={{ width: "100%", padding: "0.8rem", borderRadius: 12, border: "1.5px solid #e0e0e0", marginBottom: 18, fontSize: 18 }}
                        >
                            {professions.map(prof => (
                                <option key={prof} value={prof}>{prof}</option>
                            ))}
                        </select>
                        <label style={{ display: "block", marginBottom: 12, fontWeight: 500 }}>Interest:</label>
                        <select
                            value={form.interest}
                            onChange={e => setForm(f => ({ ...f, interest: e.target.value }))}
                            style={{ width: "100%", padding: "0.8rem", borderRadius: 12, border: "1.5px solid #e0e0e0", marginBottom: 18, fontSize: 18 }}
                        >
                            {interests.map(interest => (
                                <option key={interest} value={interest}>{interest}</option>
                            ))}
                        </select>
                        <button type="submit" style={{ width: "100%", padding: "1rem", borderRadius: 16, border: "none", background: "#32BCAE", color: "#fff", fontWeight: 700, fontSize: 18, cursor: "pointer", marginTop: 16 }}>Save Changes</button>
                    </form>
                </div>
            );
            break;
        case "logout":
            content = (
                <button
                    key={opt.key}
                    onClick={() => {
                        setSelected(opt.key); // Set the selected section
                        if (opt.key === "logout") handleLogout(); // Use handleLogout
                    }}
                    style={{
                        width: "100%",
                        padding: "0.8rem 1rem",
                        marginBottom: 18,
                        borderRadius: 12,
                        border: "none",
                        background: selected === opt.key ? "#32BCAE" : "#fff",
                        color: selected === opt.key ? "#fff" : "#222",
                        fontWeight: 600,
                        fontSize: 18,
                        fontFamily: 'JomolhariReg',
                        cursor: "pointer",
                        boxShadow: selected === opt.key ? "0 2px 8px rgba(44,62,80,0.10)" : "none",
                        display: "flex",
                        alignItems: "center"
                    }}
                >
                    <img src={opt.icon} alt="" style={{ marginRight: "0.7rem", height: 24, width: 24, verticalAlign: "middle" }} />
                    {opt.label}
                </button>

            );
            break;
        default:
            content = <div style={{ padding: "2rem" }}><h3>Welcome</h3></div>;
    }
    return (
        <div style={{ flex: 1, minHeight: 400, borderRadius: "0 25px 25px 0", background: "#fff", display: "flex", alignItems: "center", justifyContent: "center" }}>
            {content}
        </div>
    );
}

export default ProfilePage;