"""
Background thread: reads the live stream, runs best.pt on every Nth frame,
tracks how many people are in view, and writes an event to the DB whenever
that count changes.
"""

import os
import pickle
import threading
import time

import cv2
import face_recognition
import streamlink
from ultralytics import YOLO

DEFAULT_ENCODINGS_PATH = Path("output/encodings.pkl")

from .db import insert_event

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "best.pt")
_FRAME_SKIP = 10  # process every Nth frame to keep CPU reasonable


def _run(stream_url: str):
    model = YOLO(_MODEL_PATH)
    prev_count = None
    avg_conf = 0

    while True:
        try:
            print(f"[detector] connecting to {stream_url}")
            streams = streamlink.streams(
                stream_url,
                options={"hls-live-edge": 1, "hls-segment-threads": 1},
            )
            cap = cv2.VideoCapture(streams["best"].url)

            frame_n = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("[detector] stream ended, reconnecting…")
                    break

                frame_n += 1
                if frame_n % _FRAME_SKIP != 0:
                    continue

                results = model.predict(frame, verbose=False)
                count = sum(1 for box in results[0].boxes if float(box.conf[0]) >= 0.80)

                if prev_count is not None and count != prev_count:
                    diff = count - prev_count
                    if diff > 0:
                        label = (
                            f"{diff} person{'s' if diff > 1 else ''} entered "
                            f"({count} in view)"
                        )
                        event_type = "entered"
                    else:
                        gone = abs(diff)
                        label = (
                            f"{gone} person{'s' if gone > 1 else ''} left "
                            f"({count} in view)"
                        )
                        event_type = "left"

                    insert_event(
                        person_name=label,
                        person_count=count,
                        event_type=event_type,
                    )
                    print(f"[detector] event: {label}")

                prev_count = count

            cap.release()

        except Exception as e:
            print(f"[detector] error: {e} — retrying in 10s")
            time.sleep(10)


def _detect_faces(frame, model: str, frame_scale: float):
    resized = cv2.resize(frame, (0, 0), fx=frame_scale, fy=frame_scale)
    rgb_small = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(rgb_small, model=model)
    encodings = face_recognition.face_encodings(rgb_small, locations)
    return locations, encodings


def load_known_faces(encodings_location: Path = DEFAULT_ENCODINGS_PATH) -> dict:
    if not encodings_location.exists():
        raise FileNotFoundError(
            f"Encodings not found at {encodings_location}. Run --encode first."
        )
    with encodings_location.open(mode="rb") as f:
        return pickle.load(f)


def start(stream_url: str):
    """Launch the detector as a daemon thread."""
    t = threading.Thread(target=_run, args=(stream_url,), daemon=True)
    t.start()
    print(f"[detector] started (stream={stream_url})")
