import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://smart-attendance-system-204cd-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    '1': {
        "name": "Steve Jobs",
        "major": "Apple",
        "starting_year": 1999,
        "total_attendance": 7,
        "standing": "A+",
        "year": 5,
        "last_attendance": "2002-12-12 00:12:12"
    },
    '2': {
        "name": "Bill Gates",
        "major": "Microsoft",
        "starting_year": 2001,
        "total_attendance": 5,
        "standing": "AA",
        "year": 7,
        "last_attendance": "2005-10-10 00:03:04"
    },
    '3': {
        "name": "Elon Musk",
        "major": "Tesla",
        "starting_year": 2020,
        "total_attendance": 10,
        "standing": "B+",
        "year": 3,
        "last_attendance": "2020-02-02 00:02:02"
    }
}

for key, value in data.items():
    ref.child(key).set(value)

