"""Optional HTTP inference; configure pothole weights via POTHOLE_WEIGHTS."""
import os
import tempfile
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from pipeline import detect

app = FastAPI(title='Pothole detection')


@app.post('/detect')
async def infer(video: UploadFile = File(...), gps: UploadFile = File(...)):
    weights = os.getenv('POTHOLE_WEIGHTS')
    if not weights or not Path(weights).is_file():
        raise HTTPException(503, 'Configure POTHOLE_WEIGHTS with pothole trained weights')
    if not video.filename.lower().endswith(('.mp4', '.mov')) or not gps.filename.lower().endswith('.csv'):
        raise HTTPException(400, 'Expected video MP4/MOV and GPS CSV')
    with tempfile.TemporaryDirectory() as folder:
        paths = [Path(folder) / 'video.mp4', Path(folder) / 'gps.csv', Path(folder) / 'report.json']
        for upload, dest in ((video, paths[0]), (gps, paths[1])):
            contents = await upload.read(100 * 1024 * 1024 + 1)
            if len(contents) > 100 * 1024 * 1024:
                raise HTTPException(413, 'Max upload size is 100 MB per file')
            dest.write_bytes(contents)
        try:
            found = detect(paths[0], paths[1], weights, paths[2])
        except ValueError as error:
            raise HTTPException(400, str(error)) from error
    return {'detections': found}
