import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Try to import config for Firebase settings
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Try to import config for Firebase settings
try:
    import config
    service_account_key = getattr(config, 'SERVICE_ACCOUNT_KEY', 'serviceAccountKey.json')
    firebase_config = getattr(config, 'FIREBASE_CONFIG', {
        'databaseURL': "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    })
except ImportError:
    # Use defaults if config is not available
    service_account_key = 'serviceAccountKey.json'
    firebase_config = {
        'databaseURL': "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    }

cred = credentials.Certificate(service_account_key)
firebase_admin.initialize_app(cred, firebase_config)

ref = db.reference('Students')

data = {
    "11232950": {
        "name": "Sharukh khan",
        "major": "Hero",
        "Starting_year": 2000,
        "total_attendance": 6,
        "standing": "G",
        "year": 4,
        "Last_attendance_time": "2022-08-25 00:54:23"
    },
    "11232955": {
        "name": "Salman khan",
        "major": "single",
        "Starting_year": 2007,
        "total_attendance": 6,
        "standing": "E",
        "year": 4,
        "Last_attendance_time": "2022-08-25 00:54:23"
    },
    "11232957": {
        "name": "Ryan Reynolds",
        "major": "Comedian",
        "Starting_year": 2008,
        "total_attendance": 6,
        "standing": "EX",
        "year": 4,
        "Last_attendance_time": "2022-08-25 00:54:23"
    },
    "11232958": {
        "name": "Tom",
        "major": "Action",
        "Starting_year": 2004,
        "total_attendance": 6,
        "standing": "S",
        "year": 4,
        "Last_attendance_time": "2022-08-25 00:54:23"
    },
    "11232959": {
        "name": "Saif Ansari",
        "major": "AI & ML",
        "Starting_year": 2023,
        "total_attendance": 10,
        "standing": "G",
        "year": 1,
        "Last_attendance_time": "2022-08-25 00:54:23"
    },
}

for key, value in data.items():


    ref = db.reference('Students')

data = {
        "11232950":
        {
                "name":"Sharukh khan",
                "major":"Hero",
                "Starting_year":2000,
                "total_attendance":6,
                "standing":"G",
                "year":4,
                "Last_attendance_time":"2022-08-25 00:54:23"
        },
        "11232955":
        {
                "name":"Salman khan",
                "major":"single",
                "Starting_year":2007,
                "total_attendance":6,
                "standing":"E",
                "year":4,
                "Last_attendance_time":"2022-08-25 00:54:23"
        },
        "11232957":
        {
                "name":"Ryan Reynolds",
                "major":"Comedian",
                "Starting_year":2008,
                "total_attendance":6,
                "standing":"EX",
                "year":4,
                "Last_attendance_time":"2022-08-25 00:54:23"
        },
        "11232958":
        {
                "name":"Tom",
                "major":"Action",
                "Starting_year":2004,
                "total_attendance":6,
                "standing":"S",
                "year":4,
                "Last_attendance_time":"2022-08-25 00:54:23"
        },
        "11232959":
        {
                "name":"Saif Ansari",
                "major":"AI & ML",
                "Starting_year":2023,
                "total_attendance":10,
                "standing":"G",
                "year":1,
                "Last_attendance_time":"2022-08-25 00:54:23"
        },

}
for key,value in data.items():
        ref.child(key).set(value)