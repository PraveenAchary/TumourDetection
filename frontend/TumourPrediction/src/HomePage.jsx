import React, { useState } from "react";

const TUMOUR_INFO = {
  notumor: {
    label: "No Tumour Detected",
    emoji: "✅",
    color: "#16a34a",
    bg: "#f0fdf4",
    border: "#bbf7d0",
    description: "The scan shows no signs of a brain tumour.",
  },
  glioma: {
    label: "Glioma",
    emoji: "⚠️",
    color: "#b45309",
    bg: "#fffbeb",
    border: "#fde68a",
    description:
      "Gliomas arise from glial cells and can be benign or malignant. Further evaluation is essential.",
  },
  meningioma: {
    label: "Meningioma",
    emoji: "⚠️",
    color: "#b45309",
    bg: "#fffbeb",
    border: "#fde68a",
    description:
      "Meningiomas grow in the membranes surrounding the brain. Most are benign but require medical assessment.",
  },
  pituitary: {
    label: "Pituitary Tumour",
    emoji: "⚠️",
    color: "#b45309",
    bg: "#fffbeb",
    border: "#fde68a",
    description:
      "Pituitary tumours affect the pituitary gland and can impact hormone levels. Specialist review is advised.",
  },
};

export default function HomePage() {
  const URL = "https://tumourdetection.onrender.com";
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [name, setName] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setImage(file);
    if (file) setPreview(URL.createObjectURL(file));
  };

  async function submitForm(e) {
    e.preventDefault();
    if (!image || !name) return alert("Please fill all fields");
    setLoading(true);
    setPrediction(null);
    const formData = new FormData();
    formData.append("username", name);
    formData.append("image", image);
    try {
      const response = await fetch(`${URL}/api/Predict-Tumour/`, {
        method: "POST",
        body: formData,
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error);
      setPrediction(result.prediction);
    } catch (error) {
      alert("Error: " + error.message);
    } finally {
      setLoading(false);
    }
  }

  const info = prediction ? TUMOUR_INFO[prediction.class] || TUMOUR_INFO["notumor"] : null;
  const confidence = prediction ? parseFloat(prediction.confidence) : 0;
  const isTumour = prediction && prediction.class !== "notumor";

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        {/* Header */}
        <div style={styles.header}>
          <div style={styles.brainIcon}>🧠</div>
          <h1 style={styles.title}>Tumour Detection System</h1>
          <p style={styles.subtitle}>AI-powered MRI brain scan analysis</p>
        </div>

        {/* Form */}
        <form onSubmit={submitForm} style={styles.form}>
          <div style={styles.field}>
            <label style={styles.label}>Patient Name</label>
            <input
              type="text"
              value={name}
              placeholder="Enter your name"
              onChange={(e) => setName(e.target.value)}
              required
              style={styles.input}
            />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Upload MRI Scan</label>
            <label style={styles.fileLabel}>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                style={{ display: "none" }}
              />
              {preview ? (
                <img src={preview} alt="MRI preview" style={styles.preview} />
              ) : (
                <div style={styles.filePlaceholder}>
                  <span style={{ fontSize: 32 }}>🖼️</span>
                  <span style={styles.fileText}>Click to upload MRI scan</span>
                  <span style={styles.fileHint}>PNG, JPG supported</span>
                </div>
              )}
            </label>
          </div>

          <button type="submit" disabled={loading} style={{
            ...styles.button,
            ...(loading ? styles.buttonDisabled : {}),
          }}>
            {loading ? (
              <span>
                <span style={styles.spinner}>⏳</span> Analyzing...
              </span>
            ) : (
              "Analyze Scan"
            )}
          </button>
        </form>

        {/* Result */}
        {prediction && info && (
          <div style={{ ...styles.resultBox, background: info.bg, borderColor: info.border }}>
            <div style={styles.resultHeader}>
              <span style={styles.resultEmoji}>{info.emoji}</span>
              <div>
                <h3 style={{ ...styles.resultTitle, color: info.color }}>{info.label}</h3>
                <p style={styles.resultName}>Patient: <strong>{name}</strong></p>
              </div>
            </div>

            <p style={styles.resultDesc}>{info.description}</p>

            {/* Confidence bar */}
            <div style={styles.confSection}>
              <div style={styles.confRow}>
                <span style={styles.confLabel}>Confidence</span>
                <span style={{ ...styles.confValue, color: info.color }}>{confidence}%</span>
              </div>
              <div style={styles.barTrack}>
                <div style={{
                  ...styles.barFill,
                  width: `${confidence}%`,
                  background: info.color,
                }} />
              </div>
              {confidence < 70 && (
                <p style={styles.lowConf}>
                  ⚡ Confidence is below 70% — image quality may affect accuracy.
                </p>
              )}
            </div>

            {/* Tumour type info */}
            {isTumour && (
              <div style={styles.disclaimer}>
                <strong>⚕️ Medical Disclaimer:</strong> This is an AI-assisted result only.
                Please consult a qualified neurologist or radiologist for diagnosis and treatment.
              </div>
            )}

            {/* Classes reference */}
            <div style={styles.classGrid}>
              <p style={styles.classGridTitle}>Tumour Types Screened</p>
              <div style={styles.classRow}>
                {Object.entries(TUMOUR_INFO).map(([key, val]) => (
                  <div key={key} style={{
                    ...styles.classBadge,
                    background: prediction.class === key ? info.color : "#e5e7eb",
                    color: prediction.class === key ? "#fff" : "#374151",
                    fontWeight: prediction.class === key ? 700 : 400,
                  }}>
                    {val.label}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "24px 16px",
    fontFamily: "'Segoe UI', system-ui, sans-serif",
  },
  card: {
    background: "#ffffff",
    borderRadius: 20,
    padding: "36px 32px",
    width: "100%",
    maxWidth: 520,
    boxShadow: "0 25px 60px rgba(0,0,0,0.4)",
  },
  header: {
    textAlign: "center",
    marginBottom: 28,
  },
  brainIcon: {
    fontSize: 48,
    marginBottom: 8,
  },
  title: {
    fontSize: 24,
    fontWeight: 700,
    color: "#0f172a",
    margin: "0 0 6px",
  },
  subtitle: {
    fontSize: 14,
    color: "#64748b",
    margin: 0,
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: 18,
  },
  field: {
    display: "flex",
    flexDirection: "column",
    gap: 6,
  },
  label: {
    fontSize: 13,
    fontWeight: 600,
    color: "#374151",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },
  input: {
    padding: "10px 14px",
    borderRadius: 10,
    border: "1.5px solid #d1d5db",
    fontSize: 15,
    outline: "none",
    transition: "border 0.2s",
    color: "#111",
  },
  fileLabel: {
    cursor: "pointer",
    display: "block",
    borderRadius: 12,
    border: "2px dashed #cbd5e1",
    overflow: "hidden",
  },
  filePlaceholder: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 6,
    padding: "28px 16px",
    background: "#f8fafc",
  },
  fileText: {
    fontSize: 14,
    color: "#475569",
    fontWeight: 500,
  },
  fileHint: {
    fontSize: 12,
    color: "#94a3b8",
  },
  preview: {
    width: "100%",
    maxHeight: 200,
    objectFit: "cover",
    display: "block",
  },
  button: {
    padding: "13px",
    borderRadius: 12,
    border: "none",
    background: "linear-gradient(135deg, #1e40af, #3b82f6)",
    color: "#fff",
    fontSize: 16,
    fontWeight: 600,
    cursor: "pointer",
    marginTop: 4,
    transition: "opacity 0.2s",
  },
  buttonDisabled: {
    opacity: 0.6,
    cursor: "not-allowed",
  },
  spinner: {
    marginRight: 6,
  },
  resultBox: {
    marginTop: 24,
    borderRadius: 14,
    border: "1.5px solid",
    padding: "20px 18px",
    display: "flex",
    flexDirection: "column",
    gap: 14,
  },
  resultHeader: {
    display: "flex",
    alignItems: "center",
    gap: 14,
  },
  resultEmoji: {
    fontSize: 40,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: 700,
    margin: "0 0 2px",
  },
  resultName: {
    fontSize: 13,
    color: "#6b7280",
    margin: 0,
  },
  resultDesc: {
    fontSize: 14,
    color: "#374151",
    margin: 0,
    lineHeight: 1.6,
  },
  confSection: {
    display: "flex",
    flexDirection: "column",
    gap: 6,
  },
  confRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  confLabel: {
    fontSize: 13,
    color: "#6b7280",
    fontWeight: 500,
  },
  confValue: {
    fontSize: 15,
    fontWeight: 700,
  },
  barTrack: {
    height: 8,
    background: "#e5e7eb",
    borderRadius: 99,
    overflow: "hidden",
  },
  barFill: {
    height: "100%",
    borderRadius: 99,
    transition: "width 0.8s ease",
  },
  lowConf: {
    fontSize: 12,
    color: "#92400e",
    margin: 0,
  },
  disclaimer: {
    fontSize: 13,
    background: "#fef3c7",
    border: "1px solid #fcd34d",
    borderRadius: 8,
    padding: "10px 14px",
    color: "#78350f",
    lineHeight: 1.5,
  },
  classGrid: {
    borderTop: "1px solid #e5e7eb",
    paddingTop: 12,
  },
  classGridTitle: {
    fontSize: 12,
    color: "#9ca3af",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
    margin: "0 0 8px",
  },
  classRow: {
    display: "flex",
    flexWrap: "wrap",
    gap: 6,
  },
  classBadge: {
    fontSize: 12,
    padding: "4px 10px",
    borderRadius: 99,
    transition: "all 0.2s",
  },
};
