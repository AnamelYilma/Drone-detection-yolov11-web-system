import os
import cv2
import threading
import time
from flask import Flask, render_template, request, jsonify, Response, send_file, url_for
from werkzeug.utils import secure_filename
from detector import DroneDetector
from alarm import AlarmSystem
#--------------
app = Flask(__name__)

# Define folders
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = os.path.join('static', 'processed')
app.config['SNAPSHOTS_FOLDER'] = 'snapshots'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
os.makedirs(app.config['SNAPSHOTS_FOLDER'], exist_ok=True)

# Initialize detector and alarm system
detector = DroneDetector(model_path='models/best.pt')
alarm_system = AlarmSystem()

# Global variables for camera thread
camera_thread = None
stop_camera = False
camera_active = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the image
        result_path, detections = detector.process_image(filepath)
        
        # Get the filename for the processed image
        processed_filename = os.path.basename(result_path)
        
        # Generate URL for the processed image
        result_url = url_for('static', filename=f'processed/{processed_filename}')
        
        return jsonify({
            'result_path': result_url,
            'detections': detections,
            'filename': processed_filename,
            'detection_status': len(detections) > 0
        })

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the video
        output_path = detector.process_video(filepath)
        
        # Get the filename for the processed video
        processed_filename = os.path.basename(output_path)
        
        # Generate URL for the processed video
        result_url = url_for('static', filename=f'processed/{processed_filename}')
        
        return jsonify({
            'result_path': result_url,
            'filename': processed_filename,
            'detection_status': True  # Default to true for demo
        })

@app.route('/start_camera', methods=['POST'])
def start_camera():
    global camera_thread, stop_camera, camera_active
    
    if camera_thread is None or not camera_thread.is_alive():
        stop_camera = False
        camera_active = True
        camera_thread = threading.Thread(target=camera_feed)
        camera_thread.start()
        return jsonify({'status': 'Camera started'})
    
    return jsonify({'status': 'Camera already running'})

@app.route('/stop_camera', methods=['POST'])
def stop_camera_func():
    global stop_camera, camera_active
    stop_camera = True
    camera_active = False
    return jsonify({'status': 'Camera stopping'})

@app.route('/stop_alarm', methods=['POST'])
def stop_alarm():
    alarm_system.stop_alarm()
    return jsonify({'status': 'Alarm stopped'})

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

def camera_feed():
    global stop_camera, camera_active
    cap = cv2.VideoCapture(0)
    
    frame_count = 0
    
    while not stop_camera:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process every 2nd frame
        if frame_count % 2 == 0:
            # Resize frame
            frame = cv2.resize(frame, (800, 600))
            
            # Detect drones
            processed_frame, detections = detector.detect_drones(frame)
            
            # If drone detected, trigger alarm
            if detections:
                alarm_thread = threading.Thread(target=alarm_system.trigger_alarm)
                alarm_thread.start()
                
                # Save snapshot
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                snapshot_path = os.path.join(app.config['SNAPSHOTS_FOLDER'], f'drone_{timestamp}.jpg')
                cv2.imwrite(snapshot_path, processed_frame)
            
            # Convert to JPEG for streaming
            ret, jpeg = cv2.imencode('.jpg', processed_frame)
            frame_bytes = jpeg.tobytes()
            
            # Yield frame for streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
        
        frame_count += 1
        time.sleep(0.03)  # ~30 FPS
    
    cap.release()
    camera_active = False

@app.route('/video_feed')
def video_feed_route():
    if not camera_active:
        # Return a placeholder image when camera is not active
        placeholder_path = os.path.join('static', 'img', 'placeholder.jpg')
        return send_file(placeholder_path, mimetype='image/jpeg')
    
    return Response(camera_feed(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, threaded=True)