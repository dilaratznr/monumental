import cv2
import numpy as np
from core.config import Config

def segment_brick(rgb_image, depth_image):
    gray = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [largest_contour], -1, 255, -1)
        segmented_depth = cv2.bitwise_and(depth_image, depth_image, mask=mask)
        return segmented_depth, largest_contour
    
    return None, None

def create_point_cloud(rgb_image, depth_image):
    points = []
    colors = []
    h, w = depth_image.shape
    
    for v in range(h):
        for u in range(w):
            Z = depth_image[v, u]
            if Z == 0: continue
            X = (u - Config.CX) * Z / Config.FX
            Y = (v - Config.CY) * Z / Config.FY
            points.append([X, Y, Z])
            colors.append(rgb_image[v, u] / 255.0)
    
    points = np.array(points)
    colors = np.array(colors)
    
    return points, colors
