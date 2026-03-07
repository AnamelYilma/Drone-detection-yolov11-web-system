document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const videoFeed = document.getElementById('video-feed');
    const startCameraBtn = document.getElementById('start-camera-btn');
    const stopCameraBtn = document.getElementById('stop-camera-btn');
    const stopAlarmBtn = document.getElementById('stop-alarm-btn');
    const imageUpload = document.getElementById('image-upload');
    const videoUpload = document.getElementById('video-upload');
    const detectionOverlay = document.getElementById('detection-overlay');
    const detectionIndicator = document.getElementById('detection-indicator');
    const detectionCount = document.getElementById('detection-count');
    const cameraStatus = document.getElementById('camera-status');
    const alarmStatus = document.getElementById('alarm-status');
    const threatLevel = document.getElementById('threat-level');
    const currentTimeElement = document.getElementById('current-time');
    const uptimeElement = document.getElementById('uptime');
    
    // Image result elements
    const imageResult = document.getElementById('image-result');
    const imageResultPlaceholder = document.getElementById('image-result-placeholder');
    const imageDetectionStatus = document.getElementById('image-detection-status');
    const downloadImageBtn = document.getElementById('download-image-btn');
    
    // Video result elements
    const videoResult = document.getElementById('video-result');
    const videoResultPlaceholder = document.getElementById('video-result-placeholder');
    const videoDetectionStatus = document.getElementById('video-detection-status');
    const downloadVideoBtn = document.getElementById('download-video-btn');
    
    // State
    let cameraActive = false;
    let alarmActive = false;
    let detectionCountValue = 0;
    let startTime = new Date();
    let currentImageFile = null;
    let currentVideoFile = null;
    
    // Update current time
    function updateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        currentTimeElement.textContent = timeString;
        
        // Update uptime
        const uptime = new Date(now - startTime);
        const uptimeString = `${uptime.getUTCHours().toString().padStart(2, '0')}:${uptime.getUTCMinutes().toString().padStart(2, '0')}:${uptime.getUTCSeconds().toString().padStart(2, '0')}`;
        uptimeElement.textContent = uptimeString;
    }
    
    setInterval(updateTime, 1000);
    updateTime();
    
    // Start camera
    startCameraBtn.addEventListener('click', function() {
        fetch('/start_camera', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'Camera started') {
                // Set video feed source to the streaming endpoint
                videoFeed.src = '/video_feed';
                cameraActive = true;
                cameraStatus.textContent = 'ACTIVE';
                addLogEntry('Camera feed activated');
                
                // Hide detection overlay when camera is active
                detectionOverlay.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error starting camera:', error);
            addLogEntry('Error: Failed to start camera');
        });
    });
    
    // Stop camera
    stopCameraBtn.addEventListener('click', function() {
        fetch('/stop_camera', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'Camera stopping') {
                cameraActive = false;
                cameraStatus.textContent = 'OFFLINE';
                addLogEntry('Camera feed deactivated');
                
                // Reset to placeholder image
                videoFeed.src = "/static/img/placeholder.jpg";
                detectionOverlay.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error stopping camera:', error);
            addLogEntry('Error: Failed to stop camera');
        });
    });
    
    // Stop alarm
    stopAlarmBtn.addEventListener('click', function() {
        fetch('/stop_alarm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'Alarm stopped') {
                alarmActive = false;
                alarmStatus.textContent = 'STANDBY';
                detectionIndicator.classList.remove('drone-detected');
                detectionIndicator.classList.add('no-drone');
                detectionIndicator.innerHTML = '<i class="fas fa-exclamation-triangle"></i><span>NO DRONE DETECTED</span>';
                detectionOverlay.style.display = 'none';
                threatLevel.textContent = 'LOW';
                threatLevel.style.color = '';
                addLogEntry('Alarm deactivated by user');
            }
        })
        .catch(error => {
            console.error('Error stopping alarm:', error);
            addLogEntry('Error: Failed to stop alarm');
        });
    });
    
    // Image upload
    imageUpload.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const formData = new FormData();
            formData.append('file', this.files[0]);
            
            fetch('/upload_image', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.result_path) {
                    // Display the processed image in the image result section
                    imageResult.src = data.result_path;
                    imageResult.style.display = 'block';
                    imageResultPlaceholder.style.display = 'none';
                    
                    // Update detection status
                    if (data.detection_status) {
                        imageDetectionStatus.classList.remove('no-detection');
                        imageDetectionStatus.classList.add('detection');
                        imageDetectionStatus.innerHTML = '<i class="fas fa-check-circle"></i><span>DRONE DETECTED</span>';
                    } else {
                        imageDetectionStatus.classList.remove('detection');
                        imageDetectionStatus.classList.add('no-detection');
                        imageDetectionStatus.innerHTML = '<i class="fas fa-times-circle"></i><span>NO DRONE DETECTED</span>';
                    }
                    
                    // Show download button
                    downloadImageBtn.style.display = 'block';
                    currentImageFile = data.filename;
                    
                    addLogEntry(`Image processed: ${data.detection_status ? 'Drone detected' : 'No drone detected'}`);
                } else if (data.error) {
                    addLogEntry(`Error: ${data.error}`);
                }
            })
            .catch(error => {
                console.error('Error uploading image:', error);
                addLogEntry('Error: Failed to process image');
            });
        }
    });
    
    // Video upload
    videoUpload.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const formData = new FormData();
            formData.append('file', this.files[0]);
            
            fetch('/upload_video', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.result_path) {
                    // Display the processed video in the video result section
                    videoResult.src = data.result_path;
                    videoResult.style.display = 'block';
                    videoResultPlaceholder.style.display = 'none';
                    
                    // Update detection status
                    if (data.detection_status) {
                        videoDetectionStatus.classList.remove('no-detection');
                        videoDetectionStatus.classList.add('detection');
                        videoDetectionStatus.innerHTML = '<i class="fas fa-check-circle"></i><span>DRONE DETECTED</span>';
                    } else {
                        videoDetectionStatus.classList.remove('detection');
                        videoDetectionStatus.classList.add('no-detection');
                        videoDetectionStatus.innerHTML = '<i class="fas fa-times-circle"></i><span>NO DRONE DETECTED</span>';
                    }
                    
                    // Show download button
                    downloadVideoBtn.style.display = 'block';
                    currentVideoFile = data.filename;
                    
                    addLogEntry(`Video processed: ${data.detection_status ? 'Drone detected' : 'No drone detected'}`);
                } else if (data.error) {
                    addLogEntry(`Error: ${data.error}`);
                }
            })
            .catch(error => {
                console.error('Error uploading video:', error);
                addLogEntry('Error: Failed to process video');
            });
        }
    });
    
    // Download image result
    downloadImageBtn.addEventListener('click', function() {
        if (currentImageFile) {
            window.location.href = `/download/${currentImageFile}`;
            addLogEntry(`Downloaded image result: ${currentImageFile}`);
        }
    });
    
    // Download video result
    downloadVideoBtn.addEventListener('click', function() {
        if (currentVideoFile) {
            window.location.href = `/download/${currentVideoFile}`;
            addLogEntry(`Downloaded video result: ${currentVideoFile}`);
        }
    });
    
    // Trigger alarm
    function triggerAlarm() {
        alarmActive = true;
        alarmStatus.textContent = 'ACTIVE';
        detectionIndicator.classList.remove('no-drone');
        detectionIndicator.classList.add('drone-detected');
        detectionIndicator.innerHTML = '<i class="fas fa-exclamation-triangle"></i><span>DRONE DETECTED</span>';
        detectionOverlay.style.display = 'flex';
        threatLevel.textContent = 'HIGH';
        threatLevel.style.color = 'var(--danger-color)';
        addLogEntry('ALARM: Drone detected');
    }
    
    // Update detection count
    function updateDetectionCount(count) {
        detectionCountValue += count;
        detectionCount.textContent = detectionCountValue;
    }
    
    // Add log entry
    function addLogEntry(message) {
        const logContainer = document.querySelector('.log-container');
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        logEntry.innerHTML = `
            <div class="log-time">${timeString}</div>
            <div class="log-message">${message}</div>
        `;
        
        logContainer.insertBefore(logEntry, logContainer.firstChild);
        
        // Keep only the last 10 log entries
        while (logContainer.children.length > 10) {
            logContainer.removeChild(logContainer.lastChild);
        }
    }
    
    // Simulate periodic system checks
    setInterval(() => {
        if (cameraActive && Math.random() > 0.8) {
            addLogEntry(`Scanning sector ${Math.floor(Math.random() * 10)}`);
        }
    }, 5000);
});
