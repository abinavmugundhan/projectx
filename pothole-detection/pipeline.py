"""CLI pothole pipeline. Bounding boxes are normalized to image width and height."""
import argparse
import bisect
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Point:
    seconds: float
    lat: float
    lon: float


def read_gps(path):
    with open(path, newline='', encoding='utf8') as file:
        rows = csv.DictReader(file)
        points = [Point(float(r['seconds']), float(r['lat']), float(r['lon'])) for r in rows]
    points.sort(key=lambda p: p.seconds)
    if not points or len({p.seconds for p in points}) != len(points):
        raise ValueError('GPS log needs unique timestamps in seconds')
    return points


def interpolate(points, seconds):
    times = [p.seconds for p in points]
    if seconds < times[0] or seconds > times[-1]:
        return None
    i = bisect.bisect_left(times, seconds)
    if i == 0 or times[i] == seconds:
        return points[i]
    a, b = points[i - 1], points[i]
    f = (seconds - a.seconds) / (b.seconds - a.seconds)
    return Point(seconds, a.lat + f * (b.lat - a.lat), a.lon + f * (b.lon - a.lon))


def severity(box):
    """Area heuristic only; physical depth requires another sensor."""
    x1, y1, x2, y2 = box
    area = max(0, x2 - x1) * max(0, y2 - y1)
    return 'high' if area >= .12 else 'medium' if area >= .04 else 'low'


def detect(video, gps, weights, output, sample_fps=2, threshold=.45):
    try:
        import cv2
        from ultralytics import YOLO
    except ImportError as error:
        raise SystemExit('Install requirements.txt to process video') from error
    points = read_gps(gps)
    model = YOLO(weights)
    capture = cv2.VideoCapture(str(video))
    source_fps = capture.get(cv2.CAP_PROP_FPS)
    if not capture.isOpened() or source_fps <= 0 or sample_fps <= 0:
        raise ValueError('Cannot read video or invalid FPS')
    results, next_sample = [], 0.0
    frame_id = 0
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            seconds = frame_id / source_fps
            frame_id += 1
            if seconds + 1e-9 < next_sample:
                continue
            next_sample = seconds + 1 / sample_fps
            location = interpolate(points, seconds)
            if location is None:
                continue
            height, width = frame.shape[:2]
            for prediction in model.predict(frame, conf=threshold, verbose=False):
                for box in prediction.boxes:
                    x1, y1, x2, y2 = (float(v) for v in box.xyxy[0])
                    normalized = [max(0, min(1, v)) for v in (x1/width, y1/height, x2/width, y2/height)]
                    results.append({'seconds': round(seconds, 3), 'lat': location.lat, 'lon': location.lon,
                                    'confidence': round(float(box.conf[0]), 3), 'box': normalized,
                                    'severity_estimate': severity(normalized)})
    finally:
        capture.release()
    # Collapse detections within ~15 m and five seconds to avoid repeated reports.
    import math
    unique = []
    for item in results:
        if any(abs(item['seconds'] - old['seconds']) <= 5 and
               math.hypot(item['lat'] - old['lat'], (item['lon'] - old['lon']) * math.cos(math.radians(item['lat']))) * 111_000 < 15
               for old in unique):
            continue
        unique.append(item)
    Path(output).write_text(json.dumps({'video': str(video), 'detections': unique}, indent=2), encoding='utf8')
    return unique


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for flag in ('video', 'gps', 'weights', 'output'):
        parser.add_argument('--' + flag, required=True)
    parser.add_argument('--sample-fps', type=float, default=2)
    parser.add_argument('--threshold', type=float, default=.45)
    args = parser.parse_args()
    print(f'{len(detect(args.video, args.gps, args.weights, args.output, args.sample_fps, args.threshold))} unique detections')
