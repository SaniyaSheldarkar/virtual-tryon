# Virtual Try-On Studio

A full-stack web application that allows users to upload a person photo and a clothing image and receive an AI-generated virtual try-on result.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Plain CSS |
| Backend | Python, FastAPI, Uvicorn |
| AI Model | IDM-VTON on Replicate |
| Fallback | Pillow image compositor |

---

## AI Model

**IDM-VTON** (Improving Diffusion Models for Authentic Virtual Try-on in the Wild)
- Hosted on Replicate.com
- Model ID: `cuuupid/idm-vton`
- Type: Diffusion Model
- Input: Person image + Clothing image
- Output: AI-generated try-on image

---

## Project Structure

```
virtual-tryon/
├── backend/
│   ├── main.py              ← FastAPI app (all backend logic)
│   ├── requirements.txt
│   └── uploads/             ← temporary image storage (auto-created)
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── index.css
        └── components/
            ├── ImageUploadZone.jsx
            └── ResultPanel.jsx
```

---

## How to Run

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend runs at: http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:5173

---

## Where to Add the API Key

Open `backend/main.py` and find this line:

```python
REPLICATE_API_TOKEN = ""  # paste your r8_... token here
```

To get a free token:
1. Go to replicate.com
2. Sign up with GitHub
3. Go to Account then API Tokens
4. Copy your token and paste it above

---

## How It Works

1. User uploads a person image and a clothing image
2. Frontend sends both images to the backend via POST /tryon
3. Backend sends images to Replicate IDM-VTON model
4. Model generates a realistic try-on result (30-40 seconds)
5. Backend returns the result as base64 to the frontend
6. Frontend displays the result image with a download option

If the Replicate API is unavailable or the token is missing, the app automatically falls back to a Pillow-based image compositor locally.

---

## Accepted Image Formats

JPEG, JPG, PNG, WEBP

---

## Requirements

### Backend
- Python 3.10 or higher
- See requirements.txt for all packages

### Frontend
- Node.js 18 or higher
- npm
