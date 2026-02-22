import argparse
import pickle
from collections import Counter
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import cv2
import face_recognition

DEFAULT_ENCODINGS_PATH = Path("output/encodings.pkl")

Path("training").mkdir(exist_ok=True)
Path("output").mkdir(exist_ok=True)
Path("validation").mkdir(exist_ok=True)


def encode_known_faces(
    model: str = "hog", encodings_location: Path = DEFAULT_ENCODINGS_PATH
) -> None:
    names = []
    encodings = []
    for filepath in Path("training").glob("*/*"):
        name = filepath.parent.name
        image = face_recognition.load_image_file(filepath)

        face_locations = face_recognition.face_locations(image, model=model)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        for encoding in face_encodings:
            names.append(name)
            encodings.append(encoding)
    name_encodings = {"names": names, "encodings": encodings}
    with encodings_location.open(mode="wb") as f:
        pickle.dump(name_encodings, f)


def load_known_faces(encodings_location: Path = DEFAULT_ENCODINGS_PATH) -> dict:
    if not encodings_location.exists():
        raise FileNotFoundError(
            f"Encodings not found at {encodings_location}. Run --encode first."
        )
    with encodings_location.open(mode="rb") as f:
        return pickle.load(f)


def recognize_faces_in_image(
    image_location: str,
    model: str = "hog",
    encodings_location: Path = DEFAULT_ENCODINGS_PATH,
    tolerance: float = 0.6,
) -> List[Tuple[str, Tuple[int, int, int, int]]]:
    loaded_encodings = load_known_faces(encodings_location)
    input_image = face_recognition.load_image_file(image_location)
    input_face_locations = face_recognition.face_locations(input_image, model=model)
    input_face_encodings = face_recognition.face_encodings(
        input_image, input_face_locations
    )

    results: List[Tuple[str, Tuple[int, int, int, int]]] = []
    for bounding_box, unknown_encoding in zip(
        input_face_locations, input_face_encodings
    ):
        name = _recognize_face(unknown_encoding, loaded_encodings, tolerance)
        results.append((name or "Unknown", bounding_box))
    return results


def _recognize_face(unknown_encoding, loaded_encodings, tolerance: float = 0.6):
    boolean_matches = face_recognition.compare_faces(
        loaded_encodings["encodings"], unknown_encoding, tolerance=tolerance
    )
    votes = Counter(
        name for match, name in zip(boolean_matches, loaded_encodings["names"]) if match
    )

    if votes:
        return votes.most_common(1)[0][0]


BOUNDING_BOX_COLOR = "blue"
TEXT_COLOR = "white"


def _scale_location(
    bounding_box: Tuple[int, int, int, int], scale_factor: float
) -> Tuple[int, int, int, int]:
    top, right, bottom, left = bounding_box
    return (
        int(top * scale_factor),
        int(right * scale_factor),
        int(bottom * scale_factor),
        int(left * scale_factor),
    )


def _draw_labels(
    frame,
    face_locations: Iterable[Tuple[int, int, int, int]],
    face_names: Iterable[str],
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


def _detect_faces(frame, model: str, frame_scale: float):
    resized = cv2.resize(frame, (0, 0), fx=frame_scale, fy=frame_scale)
    rgb_small = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(rgb_small, model=model)
    encodings = face_recognition.face_encodings(rgb_small, locations)
    return locations, encodings


def run_camera(
    model: str = "hog",
    encodings_location: Path = DEFAULT_ENCODINGS_PATH,
    camera_index: int = 0,
    frame_scale: float = 0.25,
    tolerance: float = 0.6,
) -> None:
    loaded_encodings = load_known_faces(encodings_location)
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open camera index {camera_index}.")

    scale_factor = 1.0 / frame_scale
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            locations, encodings = _detect_faces(frame, model, frame_scale)
            names: List[str] = []
            for encoding in encodings:
                name = _recognize_face(encoding, loaded_encodings, tolerance)
                names.append(name or "Unknown")

            scaled_locations = [_scale_location(loc, scale_factor) for loc in locations]
            _draw_labels(frame, scaled_locations, names)

            cv2.imshow("CrimsonCode Face Recognition", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Live face recognition camera app")
    parser.add_argument("--encode", action="store_true", help="Rebuild face encodings")
    parser.add_argument("--camera", type=int, default=0, help="Camera index to open")
    parser.add_argument(
        "--model", default="hog", choices=["hog", "cnn"], help="Detection model"
    )
    parser.add_argument(
        "--scale", type=float, default=0.25, help="Resize scale for speed"
    )
    parser.add_argument("--tolerance", type=float, default=0.6, help="Match tolerance")
    return parser.parse_args()


def main() -> None:
    # encode_known_faces()

    args = _parse_args()
    if args.encode:
        encode_known_faces(model=args.model)
        return
    run_camera(
        model=args.model,
        camera_index=args.camera,
        frame_scale=args.scale,
        tolerance=args.tolerance,
    )


if __name__ == "__main__":
    main()
