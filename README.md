# WAVE Drone Detection Web System (Yolov11)

Cyber‑military themed web app that spots drones in live camera feeds, uploaded images, or videos using a YOLOv11 model trained on a custom Roboflow dataset (~150 labeled images). Even with a short 15‑epoch training budget, the model delivers strong accuracy and clean bounding‑box overlays.

## What’s inside
- **Live detection:** Start/stop camera feed; real‑time boxes and labels on detected drones.
- **Media uploads:** Drop in images or videos, get processed outputs and downloadable results.
- **Responsive UI:** Dark neon “operations center” look that adapts to desktop, tablet, and mobile.
- **Extensible training assets:** Jupyter notebook and current model weights so you can resume or extend training.

## Quick start
```bash
# 1) Clone and enter
git clone https://github.com/<your-username>/<your-repo>.git
cd Drone-detection-by-yolov11-web-system

# 2) (Recommended) create venv
python -m venv .venv
.\.venv\Scripts\activate   # Windows

# 3) Install deps
pip install -r requirements.txt

# 4) Run the app
python app.py
# Visit http://127.0.0.1:5000
```

## How it works
1) **Front end (Flask + HTML/CSS/JS):** Serves the cyber‑styled UI, captures uploads, and displays live MJPEG stream from `/video_feed`.
2) **Detection pipeline:** `app.py` routes requests to `detector.py`, which wraps a YOLOv11 model (`models/best.pt`). Detections are drawn on frames and returned to the browser.
3) **Alarm logic:** `alarm.py` can trigger an audible alarm when drones are found (configurable).
4) **Assets:** Processed outputs are saved under `static/processed/`; uploads land in `uploads/`.

## Training notes (why 15 epochs)
- Goal was to reach a usable model fast; GPU budget was limited, so training stopped at 15 epochs instead of the planned 50.
- Dataset: Roboflow‑hosted custom drone dataset (~150 labeled images). Balanced enough for a solid first model; easy to extend with more samples.
- Outcome: High precision/recall on test images despite the shorter run.

### Continue training yourself
1) Open the provided Jupyter notebook (`The_NN_THURSDAY (2).ipynb` / `webcame.ipynb`) in a GPU environment (Colab/Kaggle/Gradient).
2) Point it to your Roboflow dataset export and the current `models/best.pt`.
3) Increase epochs (e.g., to 50), tune `imgsz`, `lr0`, `lrf`, and augmentation to push accuracy further.
4) Replace the weight file in `models/` and restart the app.

## Folder map
- `app.py` – Flask app routes, camera stream, upload handlers.
- `detector.py` – YOLOv11 wrapper (load, detect, annotate).
- `alarm.py` – Alarm trigger/stop helper.
- `static/` – CSS/JS/assets; processed outputs saved under `static/processed/`.
- `templates/` – HTML (main UI).
- `uploads/` – Incoming user files (ignored by Git).
- `models/best.pt` – Current trained weights.
- `snapshots/` – Optional saved frames (ignored by Git).

## Usage
- **Live:** Click “Start Camera” to stream, “Stop Camera” to end. Bounding boxes/labels render on the feed.
- **Image/Video:** Use the upload buttons; processed media and detection status appear below with download buttons.
- **Alarm:** Toggle via the “Stop Alarm” control if enabled.

## Requirements
- Python 3.10+ recommended.
- OpenCV + ultralytics YOLO (installed via `requirements.txt`).
- GPU optional; CPU runs but is slower for real‑time video.

## Roadmap ideas
- Longer training run (50+ epochs) with more data.
- Add auth/logging for detections.
- Optional lightweight history/timeline panel when performance budget allows.
