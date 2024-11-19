import os
import cv2
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://smart-attendance-system-204cd-default-rtdb.firebaseio.com/",
    'storageBucket': "smart-attendance-system-204cd.appspot.com"
})


# Imports all the Images to the List and Id's List based on Image Name
img_path = 'Images'
img_path_list = os.listdir(img_path)
img_list = []
student_ids = []

for path in img_path_list:
    img_list.append(cv2.imread(os.path.join(img_path, path)))
    student_ids.append(os.path.splitext(path)[0])

    file_name = f'{img_path}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)


# Generating Encodings for Images

def find_encodings(images_list):
    encodings_list = []
    for img in images_list:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodings_list.append(encode)

    return encodings_list


print("Begin the generation of Image Encodings :-) ")
generated_encoding_list = find_encodings(img_list)
encodings_list_with_ids = [generated_encoding_list, student_ids]
print("Image Encoding Generation Completed :-) ")

file = open("Encoding_file.p", 'wb')
pickle.dump(encodings_list_with_ids, file)
file.close()
print("Image Encodings File Save :-) ")
