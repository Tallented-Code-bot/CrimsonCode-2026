"""
Background thread: reads the live stream, runs best.pt on every Nth frame,
tracks how many people are in view, and writes an event to the DB whenever
that count changes. When people are detected, facial recognition is used to
identify them.
"""

import os
import pickle
import threading
import time
from collections import Counter
from pathlib import Path
from typing import List

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
    face_model_type: str = "hog"
    prev_count = None
    frame_scale: float = 0.25
    tolerance: float = 0.6
    avg_conf = 0

    scale_factor = 1.0 / frame_scale

    loaded_encodings = load_known_faces(DEFAULT_ENCODINGS_PATH)

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

                # Only run facial recognition if people are detected by YOLO
                person_names = []
                if count > 0:
                    locations, encodings = _detect_faces(
                        frame, face_model_type, frame_scale
                    )
                    for encoding in encodings:
                        name = _recognize_face(encoding, loaded_encodings, tolerance)
                        person_names.append(name or "Unknown")

                if prev_count is not None and count != prev_count:
                    diff = count - prev_count
                    if diff > 0:
                        # Person(s) entered - use identified names if available
                        if person_names:
                            person_name = ", ".join(person_names[:diff])
                        else:
                            person_name = (
                                f"{diff} person{'s' if diff > 1 else ''} entered"
                            )
                        label = f"{person_name} ({count} in view)"
                        event_type = "entered"
                    else:
                        gone = abs(diff)
                        label = (
                            f"{gone} person{'s' if gone > 1 else ''} left "
                            f"({count} in view)"
                        )
                        event_type = "left"
                        person_name = "Unknown"

                    insert_event(
                        person_name=person_name if diff > 0 else "Unknown",
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


def _recognize_face(unknown_encoding, loaded_encodings, tolerance: float = 0.6):
    boolean_matches = face_recognition.compare_faces(
        loaded_encodings["encodings"], unknown_encoding, tolerance=tolerance
    )
    votes = Counter(
        name for match, name in zip(boolean_matches, loaded_encodings["names"]) if match
    )

    if votes:
        return votes.most_common(1)[0][0]


def _scale_location(
    bounding_box: tuple[int, int, int, int], scale_factor: float
) -> tuple[int, int, int, int]:
    top, right, bottom, left = bounding_box
    return (
        int(top * scale_factor),
        int(right * scale_factor),
        int(bottom * scale_factor),
        int(left * scale_factor),
    )


def _draw_labels(
    frame,
    face_locations,
    face_names,
) -> None:
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
        cv2.rectangle(
            frame, (left, bottom - 20), (right, bottom), (255, 0, 0), cv2.FILLED
        )
        cv2.putText(
            frame,
            name,
            (left + 4, bottom - 6),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )


def start(stream_url: str):
    """Launch the detector as a daemon thread."""
    t = threading.Thread(target=_run, args=(stream_url,), daemon=True)
    t.start()
    print(f"[detector] started (stream={stream_url})")
