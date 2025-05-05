from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import os
import subprocess
import shutil
import tempfile
import zipfile
import uuid

app = FastAPI()

@app.post("/extract/")
async def extract_figures(file: UploadFile = File(...)):
    input_dir = "/app/input"
    output_dir = "/app/output"
    input_path = os.path.join(input_dir, file.filename)

    # Save uploaded file
    with open(input_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Validate PDF
    if not os.path.exists(input_path) or os.path.getsize(input_path) < 100:
        return {"error": "Uploaded file is invalid or empty."}

    # Run pdffigures2
    result = subprocess.run([
        "sbt", 
        f"runMain org.allenai.pdffigures2.FigureExtractorBatchCli {input_path} -m {output_dir}/mmd -d {output_dir}/figures"
    ], cwd="/app/pdffigures2", capture_output=True, text=True)

    if result.returncode != 0:
        return {"error": result.stderr}

    # Collect output files
    files = []
    for prefix in ["figures", "mmd"]:
        files += [
            os.path.join(output_dir, f) 
            for f in os.listdir(output_dir) 
            if f.startswith(prefix) and os.path.isfile(os.path.join(output_dir, f))
        ]

    if not files:
        return {"error": "No output files were generated."}

    # Create a zip archive of results
    zip_filename = f"/app/output/extracted_{uuid.uuid4().hex[:8]}.zip"
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for file_path in files:
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname=arcname)

    return FileResponse(zip_filename, media_type="application/zip", filename=os.path.basename(zip_filename))