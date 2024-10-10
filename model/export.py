from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO("logo_license_detection_yolo.pt")

# Export the model to TensorRT format
model.export(format="engine", device=0)  # creates 'yolov8n.engine'

# Load the exported TensorRT model
tensorrt_model = YOLO("logo_license_detection_yolo.engine")

# Run inference
results = tensorrt_model("bus.jpg")

print(results)