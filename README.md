# FormFlow – Online Forms & Survey Platform

A full-stack web application for creating, sharing, and analyzing forms and surveys.
Built with HTML/CSS/JS (frontend), Flask (backend), MongoDB (database),
Decision Tree classifier (response analysis), and Gemini API (question & insight generation).

---

## Project Structure

```
FormFlow/
├── Frontend/          ← All HTML, CSS, JS files
│   ├── index.html     ← Landing page
│   ├── login.html     ← Login
│   ├── register.html  ← Register
│   ├── dashboard.html ← My Forms
│   ├── create-form.html ← Form builder
│   ├── form.html      ← Public form (for respondents)
│   ├── share.html     ← Share link page
│   ├── analytics.html ← Response analytics & predictions
│   ├── question-gen.html ← Question idea generator
│   ├── style.css      ← All styles
│   └── app.js         ← Shared utilities + demo data
│
├── Backend/
│   ├── app.py         ← Flask REST API
│   └── requirements.txt
│
└── ML/
    ├── train_model.py          ← Model training script
    ├── FormFlow_ML_Notebook.ipynb ← Jupyter notebook
    ├── model.pkl               ← Saved trained model (generated)
    └── survey_dataset.csv      ← Dataset (generated)
```

---

## Setup Instructions

### 1. Run Frontend (no server needed)

Open `Frontend/index.html` in your browser.
The app uses `localStorage` as a fallback when the backend is not running,
so you can demo all features without any setup.

---

### 2. Run Backend (optional, for full features)

**Requirements:** Python 3.9+, MongoDB running locally

```bash
cd Backend
pip install -r requirements.txt
python app.py
```

Server starts at: `http://localhost:5000`

**Environment variables (optional):**

```
MONGO_URI=mongodb://localhost:27017/
GEMINI_API_KEY=your_key_here
```

Get a free Gemini API key from: https://aistudio.google.com/

---

### 3. Train the ML Model

```bash
cd ML
python train_model.py
```

This generates:
- `model.pkl` – the trained Decision Tree model
- `survey_dataset.csv` – the dataset used for training

Or open `FormFlow_ML_Notebook.ipynb` in Jupyter Notebook for a step-by-step walkthrough.

---

## Demo Login

Without a backend, use the demo account:
- Email: `demo@formflow.com`
- Password: `demo123`

Or register a new account (stored in localStorage).

---

## Features

- User registration and login
- Create custom forms (text, MCQ, rating questions)
- Share forms via unique link
- Collect and store responses
- Response analytics with bar charts
- Feedback category prediction (Positive / Neutral / Negative)
- Response likelihood prediction (High / Moderate / Low)
- Survey question idea generator
- Plain-English response summary (Gemini-powered)

---

## Tech Stack

| Layer        | Technology          |
|--------------|---------------------|
| Frontend     | HTML, CSS, JavaScript |
| Backend      | Python (Flask)      |
| Database     | MongoDB             |
| Prediction   | scikit-learn (Decision Tree) |
| Text Generation | Google Gemini API |

---

## Author

Student Project – 3rd Year, Computer Science
