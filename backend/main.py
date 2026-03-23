"""
Virtual Try-On Backend — FastAPI + Replicate IDM-VTON
======================================================
Uses IDM-VTON model on Replicate for perfect virtual try-on results.
Get free API token at: https://replicate.com/account/api-tokens

Run with: uvicorn main:app --reload --port 8000
"""

import os, uuid, base64, shutil, io, httpx, time
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="Virtual Try-On API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ── Paste your Replicate API token here ──────────────────────────────────────
REPLICATE_API_TOKEN = ""  # ← paste your r8_... token here
# ─────────────────────────────────────────────────────────────────────────────

# IDM-VTON model on Replicate
REPLICATE_MODEL = "cuuupid/idm-vton:906425dbca90663ff5427624839572cc56ea7d380343d13e2a4c4b09d3f0c30f"

def save_upload(file: UploadFile) -> Path:
    ext = Path(file.filename).suffix or ".jpg"
    dest = UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
    with dest.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)
    return dest

def get_mime(path: Path) -> str:
    return {".jpg":"image/jpeg",".jpeg":"image/jpeg",
            ".png":"image/png",".webp":"image/webp"}.get(path.suffix.lower(),"image/jpeg")

def path_to_data_uri(path: Path) -> str:
    """Convert image file to base64 data URI for Replicate."""
    b64 = base64.b64encode(path.read_bytes()).decode()
    mime = get_mime(path)
    return f"data:{mime};base64,{b64}"

# ─── Smart Pillow Fallback ────────────────────────────────────────────────────

def smart_tryon_mock(person_path: Path, cloth_path: Path) -> str:
    from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
    person_img = Image.open(person_path).convert("RGBA")
    cloth_img  = Image.open(cloth_path).convert("RGBA")
    pw, ph = person_img.size

    new_data = []
    for r, g, b, a in cloth_img.getdata():
        if a < 30 or (r > 210 and g > 210 and b > 210):
            new_data.append((r, g, b, 0))
        elif r < 80 and g < 80 and b < 80 and abs(r-g) < 15:
            new_data.append((r, g, b, 0))
        else:
            new_data.append((r, g, b, a))
    cloth_img.putdata(new_data)

    cw = int(pw * 0.55)
    ch = int(cw * cloth_img.height / cloth_img.width)
    if ch > int(ph * 0.55):
        ch = int(ph * 0.55)
        cw = int(ch * cloth_img.width / cloth_img.height)

    cloth_r = cloth_img.resize((cw, ch), Image.LANCZOS).filter(ImageFilter.SMOOTH)
    composite = person_img.copy()
    composite.paste(cloth_r, ((pw-cw)//2, int(ph*0.20)), cloth_r)
    rgb = ImageEnhance.Color(composite.convert("RGB")).enhance(1.05)
    buf = io.BytesIO()
    rgb.save(buf, format="JPEG", quality=92)
    return base64.b64encode(buf.getvalue()).decode()

# ─── Replicate IDM-VTON ───────────────────────────────────────────────────────

async def replicate_tryon(person_path: Path, cloth_path: Path) -> str:
    """
    Calls IDM-VTON on Replicate API.
    1. Sends both images as base64 data URIs
    2. Polls for result (Replicate runs async)
    3. Downloads and returns result image as base64
    """
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    # Convert images to data URIs
    person_uri = path_to_data_uri(person_path)
    cloth_uri  = path_to_data_uri(cloth_path)

    payload = {
        "version": REPLICATE_MODEL.split(":")[1],
        "input": {
            "human_img":    person_uri,
            "garm_img":     cloth_uri,
            "garment_des":  "clothing item",
            "is_checked":   True,
            "is_checked_crop": False,
            "denoise_steps": 30,
            "seed": 42,
        }
    }

    async with httpx.AsyncClient(timeout=120) as client:
        # Step 1: Start the prediction
        res = await client.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=payload,
        )
        if res.status_code != 201:
            raise Exception(f"Replicate error: {res.text}")

        prediction = res.json()
        prediction_id = prediction["id"]
        poll_url = prediction["urls"]["get"]

        # Step 2: Poll until done (max 120 seconds)
        for _ in range(40):
            await asyncio.sleep(3)
            poll_res = await client.get(poll_url, headers=headers)
            data = poll_res.json()
            status = data.get("status")

            if status == "succeeded":
                output = data.get("output")
                # output is a list of image URLs
                image_url = output[0] if isinstance(output, list) else output
                # Download the result image
                img_res = await client.get(image_url)
                return base64.b64encode(img_res.content).decode()

            elif status == "failed":
                raise Exception(f"Replicate prediction failed: {data.get('error')}")

        raise Exception("Replicate timed out after 120 seconds")

# ─── Endpoint ─────────────────────────────────────────────────────────────────

@app.post("/tryon")
async def virtual_tryon(
    person_image: UploadFile = File(...),
    cloth_image:  UploadFile = File(...),
):
    import asyncio

    allowed = {"image/jpeg","image/jpg","image/png","image/webp"}
    for u in (person_image, cloth_image):
        if u.content_type not in allowed:
            raise HTTPException(400, detail=f"Unsupported: {u.content_type}")

    person_path = cloth_path = None
    try:
        person_path = save_upload(person_image)
        cloth_path  = save_upload(cloth_image)

        if not REPLICATE_API_TOKEN:
            # No token — use smart mock
            result_b64 = smart_tryon_mock(person_path, cloth_path)
            mode = "smart-mock"
        else:
            try:
                result_b64 = await replicate_tryon(person_path, cloth_path)
                mode = "idm-vton"
            except Exception as e:
                print(f"Replicate failed: {e} — using fallback")
                result_b64 = smart_tryon_mock(person_path, cloth_path)
                mode = "smart-mock-fallback"

        return JSONResponse({
            "result_image": result_b64,
            "mime": "image/jpeg",
            "mode": mode,
        })

    finally:
        for p in (person_path, cloth_path):
            if p and p.exists():
                p.unlink(missing_ok=True)

@app.get("/")
def root():
    return {
        "status": "ok",
        "model": "IDM-VTON on Replicate" if REPLICATE_API_TOKEN else "Smart Mock"
    }
