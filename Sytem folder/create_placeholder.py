import cv2
import numpy as np
import os

# Create directories if they don't exist
os.makedirs('static/img', exist_ok=True)

# Create a black image with text
img = np.zeros((600, 800, 3), np.uint8)
cv2.putText(img, 'CAMERA FEED INACTIVE', (250, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
cv2.putText(img, 'Click "START CAMERA" to begin', (230, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

# Save the image
cv2.imwrite('static/img/placeholder.jpg', img)
print("Placeholder image created successfully!")