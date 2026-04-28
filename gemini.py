import cv2
import numpy as np

# Load your 'Green Forest' image
data= r"D:\Vish\AI_agent\Forest\data\raw\drone\normal_forest\forest1.jfif"
img = cv2.imread(data)

# 1. Simulate a logging road (Brown line)
cv2.line(img, (0, 10000), (4000, 3000), (42, 62, 85), 10) # BGR for brown-ish soil

# 2. Simulate a clear-cut patch
overlay = img.copy()
cv2.circle(overlay, (25, 25), 50, (3, 5, 7), -1) 
cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)

cv2.imwrite('forest_after_2.jpg', img)