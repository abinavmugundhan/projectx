# Pothole Detection

A CLI for dashcam video and synchronized GPS. The detector requires **pothole trained** YOLO weights; generic COCO weights cannot detect potholes. Outputs a deduplicated JSON report with confidence, coordinates and apparent image area severity. Image area does not measure real world depth.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r pothole-detection/requirements.txt
python pothole-detection/pipeline.py --video trip.mp4 --gps trip.csv --weights pothole-best.pt --output outputs/report.json
```

`trip.csv` columns: `seconds,lat,lon`. `seconds` is elapsed time from the start of the video; align GPS clock and video clock before running. Train weights separately with a licensed, annotated pothole dataset, hold out a test split, and report mAP/latency only after measurement. No model or measured benchmark is included here. There is no automatic authority assignment or complaint submission.

Optional HTTP inference (local trusted users only):

```bash
cd pothole-detection
POTHOLE_WEIGHTS=/absolute/path/to/pothole-best.pt uvicorn server:app
curl -F video=@trip.mp4 -F gps=@trip.csv http://localhost:8000/detect
```
