from fastapi import FastAPI, File, UploadFile
import os
import subprocess
import shutil

app = FastAPI()

@app.post("/extract/")
async def extract_figures(file: UploadFile = File(...)):
    input_path = f"./input/{file.filename}"
    output_path = "./output"

    # Save uploaded PDF
    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Run pdffigures2 using sbt
    result = subprocess.run([
        "sbt", 
        f"""runMain org.allenai.pdffigures2.FigureExtractorBatchCli {input_path} -m {output_path}/mmd -d {output_path}/figures"""
    ], cwd="/app/pdffigures2", capture_output=True, text=True)

    if result.returncode != 0:
        return {"error": result.stderr}

    return {
        "message": "Extraction complete",
        "mmd_dir": "/output/mmd",
        "figures_dir": "/output/figures"
    }