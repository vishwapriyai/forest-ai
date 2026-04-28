# from ultralytics import YOLO
# import cv2

# model = YOLO("yolov8n.pt")  # pre-trained

# def detect_drone_activity(image_path):
#     img = cv2.imread(image_path)

#     results = model(img)

#     detections = []

#     for r in results:
#         for box in r.boxes:
#             cls = int(box.cls[0])
#             label = model.names[cls]

#             if label in ["person", "truck", "car"]:
#                 detections.append(label)

#     return detections




from ultralytics import YOLO
import cv2

# Load model once
model = YOLO("yolov8n.pt")

def detect_drone_activity(image_path):
    img = cv2.imread(image_path)

    results = model(img)

    detections = []

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            label = model.names[cls]

            print(f"Detected: {label} | Confidence: {conf:.2f}")

            # ✅ Lower threshold for demo
            if conf > 0.25:

                # 🔥 Group all vehicles
                if label in ["car", "truck", "bus", "motorbike"]:
                    detections.append("vehicle")

                elif label == "person":
                    detections.append("person")

    print("Final detections:", detections)

    return detections