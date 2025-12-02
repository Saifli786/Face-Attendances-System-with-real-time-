# Face Recognition Real-Time Attendance System

A **real-time automated attendance tracking system** using facial recognition technology, OpenCV, and Firebase Realtime Database. The system automatically identifies students from a webcam feed and records their attendance with timestamps, eliminating manual roll calls.

## 🎯 Project Overview

This project implements an intelligent attendance system that:
- 📸 Captures live video from a webcam
- 🧠 Recognizes student faces in real-time
- 📊 Updates attendance records automatically in Firebase
- 🎨 Displays student information on a GUI overlay
- ⚡ Processes multiple faces simultaneously
- 🔒 Maintains a 5-minute cooldown to prevent duplicate entries

## 🏗️ System Architecture

The system follows a three-stage pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│              Face Recognition Attendance System             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Stage 1: Data Preparation (encoding.py)                   │
│  ├─ Read student images from Images/ folder                │
│  ├─ Generate face encodings using deep learning            │
│  ├─ Upload images to Firebase Storage                       │
│  └─ Save encodings to "Encoded file.p" (binary)            │
│                                                             │
│  Stage 2: Database Setup (AddDatatodata.py)                │
│  ├─ Populate Firebase Realtime Database                    │
│  ├─ Create student records with metadata                   │
│  └─ Initialize attendance counters                         │
│                                                             │
│  Stage 3: Real-Time Recognition (Main.py)                  │
│  ├─ Capture frames from webcam (Camera #1)                 │
│  ├─ Detect and encode faces in each frame                  │
│  ├─ Compare with known encodings                           │
│  ├─ Load student info from Firebase                        │
│  ├─ Update attendance if cooldown passed                   │
│  └─ Display GUI with student information                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

```
FACE RECOGNITION WITH REALTIME DATABASE/
│
├── Main.py                          # ⭐ Main application (run this to start)
├── encoding.py                       # Face encoding generator
├── AddDatatodata.py                  # Firebase database initializer
├── config.py                         # Centralized configuration settings
│
├── Encoded file.p                    # Generated face encodings (binary pickle)
├── serviceAccountKey.json            # Firebase credentials (KEEP SECURE!)
├── face_recognition.log              # Application logs
│
├── Images/                           # Student photos (INPUT)
│   ├── 11232950.png
│   ├── 11232955.png
│   ├── 11232957.png
│   └── ... (student_id.png format)
│
├── Resources/                        # UI assets
│   ├── background.png                # Main GUI template (640x480)
│   └── Modes/                        # State indicators
│       ├── 0.png                     # Ready state
│       ├── 1.png                     # Loading indicator
│       └── 2.png                     # Confirmed state
│
├── .github/
│   └── copilot-instructions.md       # AI agent guidelines
│
└── readme.md                         # This file
```

## 🚀 How to Use

### Prerequisites
```bash
pip install opencv-python face-recognition firebase-admin cvzone numpy
```

### Step 1: Add Student Photos
1. Place student photos in the `Images/` folder
2. Name each photo as `{student_id}.png` (e.g., `11232950.png`)
3. Ensure faces are clearly visible in images
4. Supported formats: PNG, JPG, JPEG

### Step 2: Generate Face Encodings
Run the encoding script to process all images:
```bash
python encoding.py
```

**What it does:**
- Reads all images from `Images/` folder
- Extracts face coordinates and encodings
- Uploads images to Firebase Storage
- Generates `Encoded file.p` with all encodings

**Expected output:**
```
Loading images...
Loaded 5 images
Starting encoding...
Successfully encoded 5 faces
Encoded file.p generated successfully
```

### Step 3: Initialize Firebase Database
Run the database setup script:
```bash
python AddDatatodata.py
```

**What it does:**
- Connects to Firebase
- Creates student records under `Students/` node
- Sets initial attendance to 0
- Records initial timestamp

**Database structure created:**
```
Students/
├── 11232950/
│   ├── name: "Sharukh khan"
│   ├── major: "Hero"
│   ├── Starting_year: 2000
│   ├── total_attendance: 0
│   ├── standing: "G"
│   ├── year: 4
│   └── Last_attendance_time: "YYYY-MM-DD HH:MM:SS"
├── 11232955/
│   └── ...
└── ...
```

### Step 4: Start Real-Time Attendance System
Run the main application:
```bash
python Main.py
```

**What happens:**
1. Webcam window opens showing live feed
2. System displays student info when face detected
3. Attendance automatically updates if 5-minute cooldown passed
4. Press 'q' to exit the application

## ⚙️ Configuration (config.py)

Customize system behavior by editing `config.py`:

```python
# Face Recognition Settings
FACE_DETECTION_SCALE = 0.25          # 0.25x scaling for speed (lower = faster)
MIN_FACE_CONFIDENCE = 0.6             # Confidence threshold (lower = permissive)
FACE_DETECTION_MODEL = 'cnn'          # 'cnn' (accurate) or 'hog' (faster)

# Performance Settings
FRAME_SKIP = 2                        # Process every Nth frame (reduce load)
MAX_FRAME_WIDTH = 640                 # Webcam resolution
MAX_FRAME_HEIGHT = 480

# Attendance Logic
ATTENDANCE_COOLDOWN = 300             # 5 minutes (300 seconds) between records

# Firebase Credentials
SERVICE_ACCOUNT_KEY = "serviceAccountKey.json"
FIREBASE_CONFIG = {
    'databaseURL': "https://...",
    'storageBucket': "..."
}
```

## 📊 Data Flow & Core Concepts

### 1. Face Encoding Process
```
Student Photo (.png)
    ↓
Convert BGR → RGB
    ↓
Detect Face Locations (CNN/HOG model)
    ↓
Extract 128-D Face Encodings
    ↓
Store in "Encoded file.p" as [encodings, ids]
```

**Why encodings?** Instead of storing raw images, face_recognition library extracts a 128-dimensional vector representing facial features. This enables fast comparison.

### 2. Real-Time Recognition Pipeline
```
Webcam Frame (640x480)
    ↓
Scale down to 25% (160x120) for speed
    ↓
Detect face locations using CNN/HOG
    ↓
Extract encoding from detected face
    ↓
Compare with all known encodings using L2 Euclidean distance
    ↓
If distance < MIN_FACE_CONFIDENCE → Match found!
    ↓
Load student info from Firebase
    ↓
Check Last_attendance_time + 5 minute cooldown
    ↓
If cooldown passed → Increment total_attendance
    ↓
Display student info on GUI overlay
```

### 3. Attendance Update Logic
```
Face Detected
    ↓
Student Info Retrieved: Last_attendance_time = "2025-12-02 14:30:00"
    ↓
Current Time: "2025-12-02 14:36:00" (6 minutes later)
    ↓
6 minutes > 5 minute cooldown ✓
    ↓
Update Database:
  - total_attendance += 1
  - Last_attendance_time = "2025-12-02 14:36:00"
```

## 🔍 Key Technical Details

### Face Comparison Algorithm
- **Method**: L2 Euclidean Distance
- **Formula**: `distance = √[(x₁-x₂)² + (y₁-y₂)² + ... + (x₁₂₈-x₂₁₂₈)²]`
- **Threshold**: Faces match if `distance < MIN_FACE_CONFIDENCE` (0.6 default)
- **Lower distance** = More similar faces

### Threading Model
The system uses background threads for Firebase operations:
```
Main Thread:
├─ Capture frames from webcam
├─ Detect faces using face_recognition
├─ Display GUI
└─ Spawn Firebase thread for each new face

Firebase Thread:
├─ Retrieve student info from database
├─ Download student image from storage
├─ Check attendance cooldown
└─ Update attendance if conditions met
```

**Benefit**: Face detection doesn't block on slow Firebase operations.

### Caching System
```
student_info_cache = {
    "11232950": {student_data},
    "11232955": {student_data},
    ...
}

img_student_cache = {
    "11232950": <image_array>,
    "11232955": <image_array>,
    ...
}
```

**Purpose**: Minimize Firebase reads - reuse cached data if same student detected again.

## 🎨 GUI Display System

### Screen Layout
```
┌──────────────────────────────────────────────┐
│                                              │
│  ┌─────────────────────────┐    ┌─────────┐ │
│  │                         │    │ Mode    │ │
│  │    Live Webcam Feed     │    │ Overlay │ │
│  │    (640x480)            │    │         │ │
│  │    Face detection       │    │ State   │ │
│  │    rectangles drawn     │    │ 0/1/2   │ │
│  │                         │    │         │ │
│  └─────────────────────────┘    └─────────┘ │
│                                              │
│  ┌─────────────────────────────────────────┐ │
│  │ Student ID: 11232950                    │ │
│  │ Name: Sharukh Khan                      │ │
│  │ Attendance: 6                           │ │
│  │ Major: Hero                             │ │
│  │ Year: 4 | Standing: G                   │ │
│  └─────────────────────────────────────────┘ │
│                                              │
└──────────────────────────────────────────────┘
```

### Mode States
- **Mode 0**: Ready (No face detected)
- **Mode 1**: Loading (Face detected, fetching Firebase data)
- **Mode 2**: Confirmed (Student info displayed)

## 🐛 Logging & Debugging

All events are logged to `face_recognition.log`:

```
2025-12-02 14:35:10,123 - INFO - Encoding file loaded successfully with 5 students
2025-12-02 14:35:11,456 - INFO - Face detected: student 11232950
2025-12-02 14:35:12,789 - INFO - Updated attendance for student 11232950
2025-12-02 14:35:15,012 - WARNING - No face found in frame
```

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| `Encoded file.p not found` | encoding.py never run | Run `python encoding.py` |
| `Face not detected` | Poor image quality or lighting | Improve lighting, retake photo |
| `Firebase connection error` | Invalid credentials | Verify serviceAccountKey.json |
| `Attendance not updating` | Cooldown period active | Wait 5 minutes before re-detection |
| `Camera not opening` | Wrong camera index | Change `cv2.VideoCapture(1)` to `0` in Main.py |

## 📈 Performance Optimization

### Speed Up Recognition
```python
# In config.py:
FRAME_SKIP = 3                          # Process every 3rd frame (default 2)
FACE_DETECTION_SCALE = 0.15             # Smaller scale = faster (default 0.25)
FACE_DETECTION_MODEL = 'hog'            # HOG faster than CNN (less accurate)
```

### Reduce Firebase Load
- Caching system automatically minimizes database reads
- Student info cached for repeated detections
- Increase `ATTENDANCE_COOLDOWN` to reduce update frequency

### Enable GPU Acceleration
```python
# In config.py:
USE_GPU = True
```

Requires dlib compiled with CUDA/OpenCL support.

## 🔐 Security Considerations

1. **serviceAccountKey.json**: 
   - Contains Firebase credentials
   - Never commit to public repository
   - Keep file secure and restricted

2. **Student Images**:
   - Stored in Firebase Storage
   - Only uploaded by authorized scripts
   - Deletion requires Firebase Console access

3. **Attendance Records**:
   - Stored in Firebase Realtime Database
   - Consider implementing role-based access control in Firebase Rules

## 📋 Firebase Database Schema

### Students Node
```json
{
  "Students": {
    "11232950": {
      "name": "Sharukh khan",
      "major": "Hero",
      "Starting_year": 2000,
      "total_attendance": 6,
      "standing": "G",
      "year": 4,
      "Last_attendance_time": "2025-12-02 14:36:00"
    },
    "11232955": {
      "name": "Salman khan",
      "major": "single",
      "Starting_year": 2007,
      "total_attendance": 10,
      "standing": "E",
      "year": 4,
      "Last_attendance_time": "2025-12-02 14:35:45"
    }
  }
}
```

### Storage Structure
```
images/
├── 11232950.png
├── 11232955.png
├── 11232957.png
└── ...
```

## 🛠️ Troubleshooting Guide

### Encoding Step Issues

**"No face found in image"**
- Reason: Face not clearly visible in photo
- Solution: Retake photo with better lighting, ensure face is centered

**"Error uploading to Firebase Storage"**
- Reason: Invalid Firebase credentials or storage bucket
- Solution: Verify serviceAccountKey.json and FIREBASE_CONFIG

### Main.py Issues

**"Camera not opening"**
- Reason: Webcam not connected or wrong camera index
- Solution: Try changing `cv2.VideoCapture(1)` to `cv2.VideoCapture(0)`

**"Face detection is too slow"**
- Reason: Processing every frame with CNN model
- Solution: Increase FRAME_SKIP or use HOG model (faster, less accurate)

**"Attendance not updating"**
- Reason: 5-minute cooldown still active
- Solution: Wait 5 minutes and try again

### Database Issues

**"Last_attendance_time format error"**
- Format required: "YYYY-MM-DD HH:MM:SS"
- Example: "2025-12-02 14:35:00"

## 📚 Dependencies & Libraries

| Library | Purpose | Version |
|---------|---------|---------|
| `opencv-python` | Image capture and processing | ≥4.5.0 |
| `face-recognition` | Face detection and encoding | ≥1.3.5 |
| `firebase-admin` | Firebase integration | ≥6.0.0 |
| `cvzone` | GUI overlays and text rendering | ≥1.5.0 |
| `numpy` | Array operations | ≥1.21.0 |
| `dlib` | Deep learning models (face_recognition dependency) | ≥19.20.0 |

## 🎓 Educational Purpose

This system demonstrates:
- Deep learning for computer vision (face recognition)
- Real-time image processing with OpenCV
- Thread-safe database operations
- Cloud integration with Firebase
- GUI overlays and display management
- Logging and error handling best practices

## 📝 Sample Workflow

```bash
# 1. Setup
$ pip install opencv-python face-recognition firebase-admin cvzone numpy

# 2. Add student photos
$ cp student_photos/*.png Images/

# 3. Generate encodings
$ python encoding.py
Loading images...
Loaded 5 images
Starting encoding...
Successfully encoded 5 faces
Encoded file.p generated successfully

# 4. Initialize database
$ python AddDatatodata.py
Connecting to Firebase...
Adding 5 student records...
Database initialized successfully

# 5. Start attendance system
$ python Main.py
Starting face recognition system...
Press 'q' to quit
[Webcam window opens, ready for attendance tracking]

# 6. Test
[Show student face to webcam]
→ System detects face
→ Loads student info
→ Displays on GUI
→ Updates attendance in Firebase
→ Press 'q' to close
```

## 🤝 Contributing

To add features or improvements:
1. Test changes with sample data
2. Update configuration in `config.py` if needed
3. Check logs in `face_recognition.log` for errors
4. Document changes in comments

## 📄 License

Educational project for attendance automation.

## 👨‍💻 Author

Created as a semester project for real-time attendance tracking system.

---

## ✅ Quick Checklist

Before running the system:
- [ ] Student photos placed in `Images/` folder
- [ ] Photos named as `{student_id}.png`
- [ ] `serviceAccountKey.json` present and valid
- [ ] `python encoding.py` executed successfully
- [ ] `python AddDatatodata.py` executed successfully
- [ ] `Encoded file.p` generated
- [ ] Webcam connected to computer
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Firebase Realtime Database and Storage created
- [ ] Firebase Rules allow read/write access

## 💬 Questions?

Refer to:
- `.github/copilot-instructions.md` for AI agent guidelines
- `face_recognition.log` for detailed error messages
- Individual `.py` files for code comments and documentation
