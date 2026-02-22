# This is the stream receiver. It reads the video stream from the raspberry pi.

import cv2
import streamlink
from ultralytics import YOLO

url = "https://www.youtube.com/live/oJBrDcMnGx4"  # live stream[web:12]
streams = streamlink.streams(
    url, options={"hls-live-edge": 1, "hls-segment-threads": 1}
)
stream = streams["best"]  # or "360p", etc.
cap = cv2.VideoCapture(stream.url)


model = YOLO("best.pt")

i = 0
frame_num = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model.predict(frame)

    for result in results:
        boxes = result.boxes

        # Draw bounding boxes
        if boxes is not None:
            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Get confidence and class
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = model.names[class_id]

                # Draw rectangle
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Draw label with confidence
                label = f"{class_name} {confidence:.2f}"
                cv2.putText(
                    frame,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2,
                )

    i += 1

    if i == 100:
        i = 0

        success = cv2.imwrite(f"images/frame_{frame_num}.jpg", frame)
        print(f"Writing frame {frame_num}")
        if not success:
            #raise RuntimeError("Failed to save image")
            frame_num += 1

    cv2.imshow("Live", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
