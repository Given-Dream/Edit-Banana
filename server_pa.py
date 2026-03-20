#!/usr/bin/env python3
"""
FastAPI Backend Server — web service entry for Edit Banana.

Run with:
    python server_pa.py
"""

import os
import sys
import re
import html
import shutil
import hashlib
import unicodedata
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI(
    title="Edit Banana API",
    description="Image to editable DrawIO bundle",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    index_path = os.path.join(PROJECT_ROOT, "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "service": "Edit Banana",
        "docs": "/docs",
        "endpoint": "/convert",
    }


def safe_stem(filename: str) -> str:
    stem = Path(filename).stem or "upload"

    normalized = unicodedata.normalize("NFKD", stem)
    ascii_stem = normalized.encode("ascii", "ignore").decode("ascii")

    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", ascii_stem)
    cleaned = re.sub(r"_+", "_", cleaned).strip("._")

    if cleaned:
        return cleaned[:80]

    short_hash = hashlib.md5(stem.encode("utf-8")).hexdigest()[:8]
    return f"upload_{short_hash}"


def resolve_output_dir(config_output_dir: str) -> str:
    if os.path.isabs(config_output_dir):
        return config_output_dir
    return os.path.normpath(os.path.join(PROJECT_ROOT, config_output_dir))


def extract_text_from_drawio(drawio_path: str, txt_path: str):
    texts = []

    if os.path.exists(drawio_path):
        tree = ET.parse(drawio_path)
        root = tree.getroot()

        for elem in root.iter():
            value = elem.attrib.get("value")
            if not value:
                continue

            text = html.unescape(value)
            text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
            text = re.sub(r"<[^>]+>", "", text)
            text = text.replace("\xa0", " ").strip()

            if text:
                texts.append(text)

    seen = set()
    clean_texts = []
    for t in texts:
        if t not in seen:
            seen.add(t)
            clean_texts.append(t)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(clean_texts))

    return txt_path


def copy_if_exists(src: str, dst: str):
    if os.path.exists(src):
        shutil.copy2(src, dst)
        return dst
    return None


@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    name = file.filename or ""
    ext = Path(name).suffix.lower()
    allowed = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}

    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Use one of: {', '.join(sorted(allowed))}."
        )

    config_path = os.path.join(PROJECT_ROOT, "config", "config.yaml")
    if not os.path.exists(config_path):
        raise HTTPException(
            status_code=503,
            detail="Server not configured. Missing config/config.yaml"
        )

    upload_dir = None
    with_text_dir = None
    no_text_dir = None

    try:
        from main import load_config, Pipeline

        config = load_config()
        output_root = resolve_output_dir(
            config.get("paths", {}).get("output_dir", "./output")
        )
        os.makedirs(output_root, exist_ok=True)

        original_name = file.filename or f"upload{ext}"
        base_name = safe_stem(original_name)
        time_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_name = f"{base_name}_{time_tag}"

        upload_dir = os.path.join(PROJECT_ROOT, "input", job_name)
        os.makedirs(upload_dir, exist_ok=True)

        original_input_path = os.path.join(upload_dir, f"{job_name}{ext}")
        with open(original_input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        with_text_input = os.path.join(upload_dir, f"{job_name}_with_text{ext}")
        no_text_input = os.path.join(upload_dir, f"{job_name}_no_text{ext}")
        shutil.copy2(original_input_path, with_text_input)
        shutil.copy2(original_input_path, no_text_input)

        pipeline = Pipeline(config)

        result_with_text = pipeline.process_image(
            with_text_input,
            output_dir=output_root,
            with_refinement=False,
            with_text=True,
        )
        if not result_with_text or not os.path.exists(result_with_text):
            raise HTTPException(status_code=500, detail="Conversion failed for with_text version")

        result_no_text = pipeline.process_image(
            no_text_input,
            output_dir=output_root,
            with_refinement=False,
            with_text=False,
        )
        if not result_no_text or not os.path.exists(result_no_text):
            raise HTTPException(status_code=500, detail="Conversion failed for no_text version")

        with_text_dir = os.path.dirname(result_with_text)
        no_text_dir = os.path.dirname(result_no_text)

        text_drawio_path = os.path.join(with_text_dir, "text_only.drawio")
        recognized_txt_path = os.path.join(with_text_dir, "recognized_text.txt")
        extract_text_from_drawio(text_drawio_path, recognized_txt_path)

        bundle_dir = os.path.join(output_root, job_name)
        os.makedirs(bundle_dir, exist_ok=True)

        final_with_text = os.path.join(bundle_dir, f"{job_name}_with_text.drawio.xml")
        final_no_text = os.path.join(bundle_dir, f"{job_name}_no_text.drawio.xml")
        final_txt = os.path.join(bundle_dir, f"{job_name}_recognized_text.txt")

        copy_if_exists(result_with_text, final_with_text)
        copy_if_exists(result_no_text, final_no_text)
        copy_if_exists(recognized_txt_path, final_txt)

        return {
            "success": True,
            "job_name": job_name,
            "output_dir": bundle_dir,
            "with_text_file": final_with_text if os.path.exists(final_with_text) else None,
            "no_text_file": final_no_text if os.path.exists(final_no_text) else None,
            "text_txt_file": final_txt if os.path.exists(final_txt) else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        try:
            if upload_dir and os.path.isdir(upload_dir):
                shutil.rmtree(upload_dir, ignore_errors=True)
        except Exception:
            pass

        try:
            if with_text_dir and os.path.isdir(with_text_dir):
                shutil.rmtree(with_text_dir, ignore_errors=True)
        except Exception:
            pass

        try:
            if no_text_dir and os.path.isdir(no_text_dir):
                shutil.rmtree(no_text_dir, ignore_errors=True)
        except Exception:
            pass


def main():
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()