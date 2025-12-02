import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def findencoding(imagesList):
    """Find face encodings for a list of images with error handling"""
    encodeList = []
    for i, img in enumerate(imagesList):
        try:
            if img is None:
                logger.warning(f"Image at index {i} is None, skipping")
                continue
                
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(img_rgb)
            
            if encodings:
                encodeList.append(encodings[0])
                logger.info(f"Successfully encoded image {i+1}/{len(imagesList)}")
            else:
                logger.warning(f"No face found in image {i+1}/{len(imagesList)}")
                
        except Exception as e:
            logger.error(f"Error encoding image {i+1}: {e}")
    
    return encodeList

def main():
    try:
        # Try to import config for Firebase settings
        try:
            import config
            service_account_key = getattr(config, 'SERVICE_ACCOUNT_KEY', 'serviceAccountKey.json')
            firebase_config = getattr(config, 'FIREBASE_CONFIG', {
                'databaseURL': "https://face-attendance-realtime-6b86f-default-rtdb.asia-southeast1.firebasedatabase.app/",
                'storageBucket': "face-attendance-realtime-6b86f.appspot.com"
            })
        except ImportError:
            # Use defaults if config is not available
            service_account_key = 'serviceAccountKey.json'
            firebase_config = {
                'databaseURL': "https://face-attendance-realtime-6b86f-default-rtdb.asia-southeast1.firebasedatabase.app/",
                'storageBucket': "face-attendance-realtime-6b86f.appspot.com"
            }
        
        # Initialize Firebase
        cred = credentials.Certificate(service_account_key)
        firebase_admin.initialize_app(cred, firebase_config)
        logger.info("Firebase initialized successfully")
    except Exception as e:
        logger.error(f"Firebase initialization failed: {e}")
        return

    # Import student images
    FolderPath = 'Images'  # Changed from 'images' to 'Images' to match actual directory
    try:
        PathList = os.listdir(FolderPath)
        logger.info(f"Found {len(PathList)} images in {FolderPath}")
    except FileNotFoundError:
        logger.error(f"Directory {FolderPath} not found")
        return
    except Exception as e:
        logger.error(f"Error accessing directory {FolderPath}: {e}")
        return

    imgList = []
    studentsid = []
    bucket = storage.bucket()

    for path in PathList:
        try:
            if path.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(FolderPath, path)
                img = cv2.imread(img_path)
                
                if img is not None:
                    imgList.append(img)
                    student_id = os.path.splitext(path)[0]
                    studentsid.append(student_id)
                    logger.info(f"Loaded image: {path} -> ID: {student_id}")
                    
                    # Upload to Firebase storage
                    fileName = f'images/{path}'
                    blob = bucket.blob(fileName)
                    blob.upload_from_filename(img_path)
                    logger.info(f"Uploaded {fileName} to Firebase storage")
                else:
                    logger.warning(f"Failed to load image: {img_path}")
            else:
                logger.info(f"Skipping non-image file: {path}")
                
        except Exception as e:
            logger.error(f"Error processing file {path}: {e}")

    if not imgList:
        logger.error("No valid images found to process")
        return

    logger.info(f"Starting encoding for {len(imgList)} images...")
    encodeltKnown = findencoding(imgList)
    
    if not encodeltKnown:
        logger.error("No faces were successfully encoded")
        return

    encodeltKnownwithid = [encodeltKnown, studentsid]

    logger.info("Encoding complete. Saving to file...")
    try:
        with open("Encoded file.p", 'wb') as file:
            pickle.dump(encodeltKnownwithid, file)
        logger.info(f"File saved successfully with {len(encodeltKnown)} encodings")
    except Exception as e:
        logger.error(f"Failed to save encoding file: {e}")

if __name__ == "__main__":
    main()
