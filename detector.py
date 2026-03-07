import cv2
import os
import time
from ultralytics import YOLO

class DroneDetector:
    def __init__(self, model_path='models/best.pt'):
        self.model = YOLO(model_path)
        
    def detect_drones(self, frame):
        # Run YOLOv11 detection
        results = self.model(frame, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Extract class name, confidence, and bounding box
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Only consider drone detections with high confidence
                    if conf > 0.5:
                        detections.append({
                            'class': self.model.names[cls],
                            'confidence': conf,
                            'bbox': [x1, y1, x2, y2]
                        })
                        
                        # Draw bounding box and label
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        label = f"{self.model.names[cls]}: {conf:.2f}"
                        cv2.putText(frame, label, (x1, y1 - 10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame, detections
    
    def process_image(self, image_path):
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            return None, []
        
        # Resize image
        img = cv2.resize(img, (800, 600))
        
        # Detect drones
        processed_img, detections = self.detect_drones(img)
        
        # Save processed image to static/processed directory
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_processed{ext}"
        output_path = os.path.join('static', 'processed', output_filename)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the processed image
        cv2.imwrite(output_path, processed_img)
        
        # Return the full path and detections
        return output_path, detections
    
    def process_video(self, video_path):
        # Open video file
        cap = cv2.VideoCapture(video_path)
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Create output video writer
        filename = os.path.basename(video_path)
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_processed.mp4"
        output_path = os.path.join('static', 'processed', output_filename)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (800, 600))
        
        frame_count = 0
        drone_detected = False
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process every 2nd frame
            if frame_count % 2 == 0:
                # Resize frame
                frame = cv2.resize(frame, (800, 600))
                
                # Detect drones
                processed_frame, detections = self.detect_drones(frame)
                
                # Check if drone was detected
                if detections:
                    drone_detected = True
                
                # Write processed frame
                out.write(processed_frame)
            
            frame_count += 1
        
        # Release resources
        cap.release()
        out.release()
        
        return output_path