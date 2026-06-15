import React, { useState } from "react";
import "./App.css";

export default function HomePage() {
    const URL = "https://tumourdetection.onrender.com";
    const [image, setImage] = useState(null);
    const [name, setName] = useState("");
    // New state for storing the result
    const [prediction, setPrediction] = useState(null); 
    const [loading, setLoading] = useState(false);

    const handleFileChange = (e) => {
        setImage(e.target.files[0]);
    };

    async function submitForm(e) {
        e.preventDefault();
        if (!image || !name) return alert("Please fill all fields");

        setLoading(true);
        const formData = new FormData();
        formData.append("username", name);
        formData.append("image", image);

        try {
            const response = await fetch(`${URL}/api/Predict-Tumour/`, {
                method: 'POST',
                body: formData,
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error);
            
            // Set the result to state instead of alerting
            setPrediction(result.prediction); 
        } catch (error) {
            alert(error.message);
        } finally {
            setLoading(false);
        }
    }
    
    return (
        <div className="container">
            <div className="card">
                <h1>Tumour Detection System</h1>
                <form onSubmit={submitForm}>
                    <div className="input-group">
                        <label>Your Name</label>
                        <input type="text" value={name} onChange={(e) => setName(e.target.value)} required />
                    </div>
                    <div className="input-group">
                        <label>Upload Medical Scan</label>
                        <input type="file" accept="image/*" onChange={handleFileChange} />
                    </div>
                    <button type="submit" disabled={loading}>
                        {loading ? "Analyzing..." : "Analyze Scan"}
                    </button>
                </form>

                {/* Meaningful result display */}
                {prediction && (
                    <div className="result-box">
                        <h3>Analysis Complete</h3>
                        <p>Hello <strong>{name}</strong>,</p>
                        <p>Based on our AI analysis, the scan is classified as: 
                           <span className="highlight"> {prediction.class}</span>.</p>
                        <p>Confidence Level: {prediction.confidence}%</p>
                    </div>
                )}
            </div>
        </div>
    );
}
