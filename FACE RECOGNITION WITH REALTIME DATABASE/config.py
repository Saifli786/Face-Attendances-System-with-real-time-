import logging

# Firebase Configuration
SERVICE_ACCOUNT_KEY = "serviceAccountKey.json"
FIREBASE_CONFIG = {
    'databaseURL': "https://face-attendance-realtime-6b86f-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket': "face-attendance-realtime-6b86f.appspot.com"
}

# Face Recognition Settings
FRAME_SKIP = 2  # Process every 2nd frame to reduce CPU load
FACE_DETECTION_SCALE = 0.25  # Scale down image for faster processing
MIN_FACE_CONFIDENCE = 0.6  # Minimum confidence threshold for face matches
FACE_DETECTION_MODEL = 'cnn'  # Use CNN model for better accuracy ('hog' for faster processing)

# GPU Acceleration Settings
USE_GPU = False  # Set to True if you have GPU support

# Logging Configuration
def get_log_level():
    """Get the logging level"""
    return logging.INFO

def check_gpu_support():
    """Check if GPU acceleration is available"""
    # This is a placeholder - in a real implementation, you would check for GPU availability
    # For face_recognition library, GPU support depends on dlib compilation with CUDA
    return False

# Application Settings
MAX_FRAME_WIDTH = 640
MAX_FRAME_HEIGHT = 480
ATTENDANCE_COOLDOWN = 300  # 5 minutes cooldown between attendance records

# Debug Settings
DEBUG_MODE = False
SAVE_FRAMES = False  # Save processed frames for debugging
