# 👗 Virtual Try-On Studio

A full-stack web application that lets users upload a person photo and a clothing image, then generates a virtual try-on result using AI (or a built-in mock renderer).

---

## Tech Stack

| Layer     | Technology              |
|-----------|-------------------------|
| Backend   | Python · FastAPI        |
| Frontend  | React 18 · Vite         |
| AI (real) | Google Gemini API       |
| AI (mock) | Pillow image compositing|

---

## Project Structure

```
virtual-tryon/
├── backend/
│   ├── main.py          ← FastAPI app (all API logic)
│   ├── requirements.txt
│   └── uploads/         ← temp storage (auto-created)
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx      ← main page
│       ├── index.css    ← all styles
│       └── components/
│           ├── ImageUploadZone.jsx
│           └── ResultPanel.jsx
└── README.md
```

---

## How to Run

### 1 — Backend (FastAPI)

```bash
cd backend

# Create & activate virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```

API will be live at **http://localhost:8000**
Interactive docs at **http://localhost:8000/docs**

---

### 2 — Frontend (React)

```bash
cd frontend

npm install
npm run dev
```

App will open at **http://localhost:5173**

---

## Where to Add the API Key

Open `backend/main.py` and find:

```python
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
```

You can either:
- Set an environment variable: `export GEMINI_API_KEY=your_key_here`
- Or paste the key directly: `GEMINI_API_KEY = "your_key_here"`

Also uncomment `google-generativeai` in `requirements.txt` and re-install.

> **Without a key** the app runs in **Mock mode** — it uses Pillow to overlay the clothing on the person image locally. No API calls are made.

---

## How the System Works

```
User uploads two images
        │
        ▼
React frontend (port 5173)
   — previews both images
   — on "Try On" click: sends FormData to backend
        │
        ▼
FastAPI backend (port 8000)  POST /tryon
   — validates file types
   — saves uploads temporarily
   — if GEMINI_API_KEY set → calls Gemini Vision API
   — else → runs Pillow mock compositor
   — deletes temp files
   — returns { result_image: <base64>, mime, mode }
        │
        ▼
React frontend
   — decodes base64
   — displays result image
   — offers Download button
```

---

## API Reference

### `POST /tryon`

| Field          | Type   | Description             |
|----------------|--------|-------------------------|
| `person_image` | file   | Photo of the person     |
| `cloth_image`  | file   | Photo of clothing item  |

**Response:**
```json
{
  "result_image": "<base64 string>",
  "mime": "image/jpeg",
  "mode": "mock"
}
```

---

## Notes

- Accepted image formats: JPEG, PNG, WEBP
- Uploaded files are deleted from disk immediately after processing
- CORS is pre-configured for `localhost:5173` and `localhost:3000`
