import os
import pickle
from datetime import datetime
import cv2
import cvzone
import face_recognition
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://smart-attendance-system-204cd-default-rtdb.firebaseio.com/",
    'storageBucket': "smart-attendance-system-204cd.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Width Settings
cap.set(4, 480)  # Height Settings

img_background = cv2.imread('Resources/background.png')

# Importing the Modes of Images into the List
mode_path = 'Resources/Modes'
mode_path_list = os.listdir(mode_path)
img_mode_list = []

for path in mode_path_list:
    img_mode_list.append(cv2.imread(os.path.join(mode_path, path)))

# print(len(img_mode_list))

# Load Encoding File
file = open('Encoding_file.p', 'rb')
encoding_list_with_ids = pickle.load(file)
file.close()
encoding_list, student_ids = encoding_list_with_ids
# print(student_ids)
print("Image Encodings File Loaded Successfully :-) ")

mode_type = 0
counter = 0
id = -1
img_student = []

while True:
    success, img = cap.read()

    img_small = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    img_small_RGB = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)

    face_current_frame_locations = face_recognition.face_locations(img_small_RGB)
    encoding_current_frame = face_recognition.face_encodings(img_small_RGB, face_current_frame_locations)

    img_background[162:162 + 480, 55:55 + 640] = img  # Set Height and Width

    img_background[44:44 + 633, 808:808 + 414] = img_mode_list[mode_type]  # Set the Mode Image to the Home System

    if face_current_frame_locations:
        for encode_face, face_loc in zip(encoding_current_frame, face_current_frame_locations):
            matches = face_recognition.compare_faces(encoding_list, encode_face)
            face_distance = face_recognition.face_distance(encoding_list, encode_face)
            # print("Matches :-) ", matches)
            # print('Distance :-) ', face_distance)

            match_index = np.argmin(face_distance)
            # print("Match Index ", match_index)

            if matches[match_index]:
                # print("Face Detected :-)")
                # print(student_ids[match_index])
                y1, x2, y2, x1 = face_loc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                img_background = cvzone.cornerRect(img_background, bbox, rt=0)
                id = student_ids[match_index]
                if counter == 0:
                    cvzone.putTextRect(img_background, "Loading", (275, 400))
                    cv2.imshow("System Home Page :-) ", img_background)
                    cv2.waitKey(1)
                    counter = 1
                    mode_type = 1

        if counter != 0:

            if counter == 1:
                # Get the Data
                student_info = db.reference(f'Students/{id}').get()
                # print(student_info)
                # Get the Images form the storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                img_student = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                # Update Attendance
                date_time_object = datetime.strptime(student_info['last_attendance'],
                                                    "%Y-%m-%d %H:%M:%S")
                time_elapsed = (datetime.now() - date_time_object).total_seconds()
                # Update Data
                if time_elapsed > 20:
                    ref = db.reference(f'Students/{id}')
                    student_info['total_attendance'] += 1
                    ref.child('total_attendance').set(student_info['total_attendance'])
                    ref.child('last_attendance').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    mode_type = 3
                    counter = 0
                    img_background[44:44 + 633, 808:808 + 414] = img_mode_list[mode_type]

            if mode_type != 3:

                if 10 < counter < 20:
                    mode_type = 2

                img_background[44:44 + 633, 808:808 + 414] = img_mode_list[mode_type]

                if counter <= 10:

                    cv2.putText(img_background, str(student_info['total_attendance']), (861, 125), cv2.FONT_HERSHEY_DUPLEX, 1,
                                (255, 255, 255), 1),

                    cv2.putText(img_background, str(student_info['major']), (1006, 550), cv2.FONT_HERSHEY_DUPLEX, 0.6,
                                (255, 255, 255), 1),

                    cv2.putText(img_background, str(id), (1006, 493), cv2.FONT_HERSHEY_DUPLEX, 0.6,
                                (255, 255, 255), 1),

                    cv2.putText(img_background, str(student_info['standing']), (910, 625), cv2.FONT_HERSHEY_DUPLEX, 0.7,
                                (100, 100, 100), 1),

                    cv2.putText(img_background, str(student_info['year']), (1025, 625), cv2.FONT_HERSHEY_DUPLEX, 0.7,
                                (100, 100, 100), 1),

                    cv2.putText(img_background, str(student_info['starting_year']), (1125, 625), cv2.FONT_HERSHEY_DUPLEX, 0.7,
                                (100, 100, 100), 1),

                    (width, height), _ = cv2.getTextSize(student_info['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414-width)//2
                    cv2.putText(img_background, str(student_info['name']), (808 + offset, 445), cv2.FONT_HERSHEY_COMPLEX, 1,
                                (50, 50, 50), 2),

                    img_background[175:175 + 216, 909:909 + 216] = img_student

                counter += 1

                if counter >= 20:
                    counter = 0
                    mode_type = 0
                    student_info = []
                    img_student = []
                    img_background[44:44 + 633, 808:808 + 414] = img_mode_list[mode_type]
    else:
        mode_type = 0
        counter = 0

    # cv2.imshow("Live Web-cam :-) ", img)
    cv2.imshow("System Home Page :-) ", img_background)
    if cv2.waitKey(1) & 0xFF == ord('a'):
        break
