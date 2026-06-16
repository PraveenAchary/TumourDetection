# 🧠 Tumour Detection & Classification System

> AI-powered MRI brain scan analysis — classifies brain tumours into 4 categories with confidence scores.

🔗 **Live Demo:** [tumour-detection-two.vercel.app](https://tumour-detection-two.vercel.app/)

---

## 🚀 Key Features

- 🧠 **4-Class Tumour Classification** — Detects Glioma, Meningioma, Pituitary tumours, or No Tumour
- 📊 **Full Probability Breakdown** — Shows confidence scores for all 4 classes, not just the top prediction
- 🖼️ **MRI Preview** — Instantly previews the uploaded scan before submission
- ⚠️ **Smart Warnings** — Flags low-confidence results and shows medical disclaimers for tumour detections
- 🏥 **Professional UI** — Clean, responsive React interface built for clinical use
- ⚙️ **Decoupled Architecture** — Independent frontend and backend for scalability

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, CSS3 |
| Backend | Django, Django REST Framework |
| ML Model | PyTorch, Torchvision, ResNet-18, Pillow |
| Deployment | Vercel (Frontend), Render (Backend) |

---

## 🔬 Model Details

- **Architecture:** ResNet-18 (fine-tuned — layers 3 & 4 unfrozen)
- **Input size:** 128 × 128 RGB
- **Classes:** `glioma` · `meningioma` · `notumor` · `pituitary`
- **Output:** Top predicted class + confidence % + all 4 class probabilities

---

## 📋 Project Structure

```
TumourDetection/
├── backend/
│   └── TumourPrediction/
│       ├── ml/
│       │   ├── best_model.pth     # Trained ResNet-18 weights
│       │   └── predict.py         # Inference logic
│       ├── settings.py
│       ├── urls.py
│       ├── views.py
│       ├── wsgi.py
│       └── manage.py
└── frontend/
    └── TumourPrediction/
        ├── src/
│       │   ├── App.jsx            # Main UI component
│       │   └── App.css
        └── public/
```

---

## ⚙️ Local Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
python manage.py runserver
```

### Frontend

```bash
cd frontend/TumourPrediction
npm install
npm run dev
```

Make sure your `.env` or `App.jsx` URL points to `http://localhost:8000` for local dev.

---

## 🌐 Deployment

### Backend → Render
- **Root Directory:** `backend`
- **Start Command:** `gunicorn TumourPrediction.wsgi:application`
- **Environment:** Add `SECRET_KEY` as an environment variable
- In `settings.py`: set `CORS_ALLOW_ALL_ORIGINS = True` or add your Vercel URL to `CORS_ALLOWED_ORIGINS`

### Frontend → Vercel
- **Root Directory:** `frontend/TumourPrediction`
- **Framework Preset:** Vite
- **Output Directory:** `dist`
- Update the `URL` constant in `App.jsx` to your Render backend URL

---

## 📸 Usage

1. Open [tumour-detection-two.vercel.app](https://tumour-detection-two.vercel.app/)
2. Enter patient name
3. Upload an MRI brain scan (PNG or JPG)
4. Click **Analyze Scan**
5. View the predicted tumour class, confidence score, and full probability breakdown

---

## ⚕️ Disclaimer

This tool is intended for **research and educational purposes only**. It is not a substitute for professional medical diagnosis. Always consult a qualified neurologist or radiologist for clinical decisions.
