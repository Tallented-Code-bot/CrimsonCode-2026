# Basic program to get training data

import cv2
from ultralytics import YOLO

model = YOLO("best.pt")

i = 0
frame_num = 0

cap = cv2.VideoCapture(0)


name = input("Enter your name please...")


path = f"training/{name}"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # results = model.predict(frame)

    # for result in results:
    #     boxes = result.boxes

    #     # Draw bounding boxes
    #     if boxes is not None:
    #         for box in boxes:
    #             # Get box coordinates
    #             x1, y1, x2, y2 = map(int, box.xyxy[0])

    #             # Get confidence and class
    #             confidence = float(box.conf[0])
    #             class_id = int(box.cls[0])
    #             class_name = model.names[class_id]

    #             # Draw rectangle
    #             cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    #             # Draw label with confidence
    #             label = f"{class_name} {confidence:.2f}"
    #             cv2.putText(
    #                 frame,
    #                 label,
    #                 (x1, y1 - 10),
    #                 cv2.FONT_HERSHEY_SIMPLEX,
    #                 0.5,
    #                 (0, 255, 0),
    #                 2,
    #             )

    i += 1

    if i == 25:
        i = 0

        success = cv2.imwrite(f"{path}/frame_{frame_num}.jpg", frame)
        print(f"Writing frame {frame_num}")
        if not success:
            raise RuntimeError("Failed to save image")
        frame_num += 1

        if frame_num >= 200:
            break
            # if path == "verification":
            #     break

            # path = "verification"
            # frame_num = 0

    cv2.imshow("Live", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
