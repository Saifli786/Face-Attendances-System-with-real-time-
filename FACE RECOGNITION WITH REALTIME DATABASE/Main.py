import os
import pickle
import cvzone
import cv2
import numpy as np
import face_recognition
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
import threading
import time
import logging

# Import configuration
try:
    import config
    logger = logging.getLogger(__name__)
    
    # Setup logging
    logging.basicConfig(
        level=config.get_log_level(),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('face_recognition.log'),
            logging.StreamHandler()
        ]
    )
    
    # Check GPU support
    if config.USE_GPU and config.check_gpu_support():
        logger.info("GPU acceleration enabled (OpenCL/AMD)")
    elif config.USE_GPU:
        logger.warning("GPU acceleration requested but not available. Using CPU.")
    
except Exception as e:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.warning(f"Config import failed: {e}. Using default settings.")

# Initialize Firebase
try:
    cred = credentials.Certificate(getattr(config, 'SERVICE_ACCOUNT_KEY', 'serviceAccountKey.json'))
    firebase_admin.initialize_app(cred, getattr(config, 'FIREBASE_CONFIG', {
        'databaseURL': "https://face-attendance-realtime-6b86f-default-rtdb.asia-southeast1.firebasedatabase.app/",
        'storageBucket': "face-attendance-realtime-6b86f.appspot.com"
    }))
    bucket = storage.bucket()
    logger.info("Firebase initialized successfully")
except Exception as e:
    logger.error(f"Firebase initialization failed: {e}")
    exit(1)

# Configuration with fallbacks
FRAME_SKIP = getattr(config, 'FRAME_SKIP', 2)
FACE_DETECTION_SCALE = getattr(config, 'FACE_DETECTION_SCALE', 0.25)
MIN_FACE_CONFIDENCE = getattr(config, 'MIN_FACE_CONFIDENCE', 0.6)
FACE_DETECTION_MODEL = getattr(config, 'FACE_DETECTION_MODEL', 'cnn')

# Global variables for thread-safe operations
student_info_cache = {}
img_student_cache = {}
firebase_thread = None
last_processed_time = 0

def load_encoding_file():
    """Load the encoded face data with error handling"""
    try:
        logger.info("Loading encoding file...")
        with open('Encoded file.p', 'rb') as file:
            encodeltKnownwithid = pickle.load(file)
        encodeltKnown, studentsid = encodeltKnownwithid
        logger.info(f"Encoding file loaded successfully with {len(studentsid)} students")
        return encodeltKnown, studentsid
    except Exception as e:
        logger.error(f"Failed to load encoding file: {e}")
        return None, None

def load_mode_images():
    """Load mode images with error handling"""
    try:
        ModePath = 'Resources/Modes'
        modePathList = os.listdir(ModePath)
        imgModeList = []
        for path in modePathList:
            img_path = os.path.join(ModePath, path)
            img = cv2.imread(img_path)
            if img is not None:
                imgModeList.append(img)
            else:
                logger.warning(f"Failed to load image: {img_path}")
        logger.info(f"Loaded {len(imgModeList)} mode images")
        return imgModeList
    except Exception as e:
        logger.error(f"Failed to load mode images: {e}")
        return []

def process_firebase_operations(student_id, encodeltKnown, studentsid):
    """Process Firebase operations in a separate thread"""
    global student_info_cache, img_student_cache
    
    try:
        # Get student info from Firebase
        student_info = db.reference(f'Students/{student_id}').get()
        if not student_info:
            logger.warning(f"No data found for student ID: {student_id}")
            return None, None
        
        # Cache the student info
        student_info_cache[student_id] = student_info
        
        # Get student image from storage
        blob = bucket.get_blob(f'images/{student_id}.png')
        if blob:
            array = np.frombuffer(blob.download_as_string(), np.uint8)
            img_student = cv2.imdecode(array, cv2.IMREAD_COLOR)
            img_student_cache[student_id] = img_student
            logger.info(f"Loaded image for student {student_id}")
        else:
            logger.warning(f"No image found for student ID: {student_id}")
            
        # Update attendance if needed
        datetime_object = datetime.strptime(student_info['Last_attendance_time'], "%Y-%m-%d %H:%M:%S")
        seconds_elapsed = (datetime.now() - datetime_object).total_seconds()
        
        if seconds_elapsed > 300:  # 5 minutes cooldown
            ref = db.reference(f'Students/{student_id}')
            student_info['total_attendance'] += 1
            ref.child('total_attendance').set(student_info['total_attendance'])
            ref.child('Last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            logger.info(f"Updated attendance for student {student_id}")
            
        return student_info, img_student
        
    except Exception as e:
        logger.error(f"Firebase operation failed: {e}")
        return None, None

def main():
    global last_processed_time, firebase_thread
    
    # Load resources
    encodeltKnown, studentsid = load_encoding_file()
    if encodeltKnown is None or studentsid is None:
        return
    
    imgModeList = load_mode_images()
    if not imgModeList:
        return
    
    # Load background image
    imgBackground = cv2.imread('Resources/background.png')
    if imgBackground is None:
        logger.error("Failed to load background image")
        return
    
    # Initialize camera
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        logger.error("Failed to open camera")
        return
    
    cap.set(3, 640)
    cap.set(4, 480)
    
    # Main variables
    modeType = 0
    counter = 0
    current_id = -1
    frame_count = 0
    
    logger.info("Starting face recognition system...")
    
    try:
        while True:
            success, img = cap.read()
            if not success:
                logger.warning("Failed to capture frame")
                continue
            
            frame_count += 1
            
            # Skip frames to reduce processing load
            if frame_count % FRAME_SKIP != 0:
                # Still update display but skip face recognition
                imgBackground[162:162+480, 55:55+640] = img
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                cv2.imshow("Face Attendance", imgBackground)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue
            
            # Process frame for face recognition
            imgS = cv2.resize(img, (0, 0), None, FACE_DETECTION_SCALE, FACE_DETECTION_SCALE)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            
            # Detect faces with GPU acceleration if available
            faceCurframe = face_recognition.face_locations(imgS, model=FACE_DETECTION_MODEL)
            encodecurframe = face_recognition.face_encodings(imgS, faceCurframe)
            
            # Update display
            imgBackground[162:162+480, 55:55+640] = img
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
            
            # Process detected faces
            if faceCurframe:
                for encoFace, faceloc in zip(encodecurframe, faceCurframe):
                    matches = face_recognition.compare_faces(encodeltKnown, encoFace)
                    face_distances = face_recognition.face_distance(encodeltKnown, encoFace)
                    
                    if len(face_distances) > 0:
                        match_index = np.argmin(face_distances)
                        
                        if matches[match_index] and face_distances[match_index] < MIN_FACE_CONFIDENCE:
                            # Scale face location back to original size
                            y1, x2, y2, x1 = faceloc
                            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                            
                            detected_id = studentsid[match_index]
                            
                            if current_id != detected_id or counter == 0:
                                current_id = detected_id
                                if counter == 0:
                                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                                    cv2.imshow("Face Attendance", imgBackground)
                                    cv2.waitKey(1)
                                    counter = 1
                                    modeType = 1
                                    
                                    # Start Firebase operations in a separate thread
                                    if firebase_thread is None or not firebase_thread.is_alive():
                                        firebase_thread = threading.Thread(
                                            target=process_firebase_operations,
                                            args=(current_id, encodeltKnown, studentsid)
                                        )
                                        firebase_thread.daemon = True
                                        firebase_thread.start()
                                        logger.info(f"Started Firebase thread for student {current_id}")
            
            # Handle counter and mode transitions
            if counter != 0:
                # Check if we have cached data from Firebase thread
                if current_id in student_info_cache and current_id in img_student_cache:
                    studentInfo = student_info_cache[current_id]
                    imgStudent = img_student_cache[current_id]
                    
                    if 10 < counter < 20:
                        modeType = 2
                    
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                    
                    if counter <= 10:
                        # Display student information
                        cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(current_id), (1006, 493),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['Starting_year']), (1125, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        
                        (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414 - w) // 2
                        cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                        
                        imgStudent_resized = cv2.resize(imgStudent, (216, 216))
                        imgBackground[175:175+216, 909:909+216] = imgStudent_resized
                    
                    counter += 1
                    
                    if counter >= 20:
                        counter = 0
                        modeType = 0
                        current_id = -1
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                else:
                    # Still waiting for Firebase data
                    counter += 1
                    if counter > 30:  # Timeout after 30 frames
                        counter = 0
                        modeType = 0
                        current_id = -1
            else:
                modeType = 0
                counter = 0
            
            # Display frame
            cv2.imshow("Face Attendance", imgBackground)
            
            # Check for quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        logger.info("Application closed")

if __name__ == "__main__":
    main()
