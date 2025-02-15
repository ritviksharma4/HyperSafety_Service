import face_recognition
import cv2
import numpy as np
from collections import Counter
import json
import urllib.request
import os

known_face_encodings = []
known_face_ids = []
name_face_encoding_dict = {}
name_face_encodings_path = "Face_Recognition/Name_Face_Encodings/name_face_encoding.txt"

# Temporarily download image for face recognition.
def imgURL_to_img(employee_id, imageURL):
    if (imageURL.endswith(".jpg")):
        file_extension = ".jpg"
    elif (imageURL.endswith(".jpeg")):
        file_extension = ".jpeg"
    elif (imageURL.endswith(".png")):
        file_extension = ".png"
    file_name = employee_id + file_extension
    file_path = "Face_Recognition/Employee_Images/" + file_name
    urllib.request.urlretrieve(imageURL, file_path)
    add_employee_to_encodings(employee_id, file_path)

"""
    For adding new employee, save the file in Employee_Images in form of
    your_client_id.jpg, e.g. RA006.jpg and store the encodings and then 
    delete the file.
"""
def add_employee_to_encodings(employee_id, file_path):

    global known_face_encodings, known_face_ids, name_face_encoding_dict
    
    employee_image = face_recognition.load_image_file(file_path)

    employee_face_encoding = face_recognition.face_encodings(employee_image)[0]

    known_face_encodings.append(employee_face_encoding)
    known_face_ids.append(employee_id)

    name_face_encoding_dict[employee_id] = employee_face_encoding.tolist()

    delete_image(file_path)
    update_name_face_encodings()

"""
    Find the employee from the list and then remove his ID and then
    remove the encodings from the list.
"""

def del_employee_from_encodings(employee_id):

    global known_face_encodings, known_face_ids, name_face_encoding_dict
    employee_index = known_face_ids.index(employee_id)
    known_face_ids.pop(employee_index)
    known_face_encodings.pop(employee_index)
    name_face_encoding_dict.pop(employee_id)
    update_name_face_encodings()

def update_name_face_encodings():

    global known_face_encodings, known_face_ids, name_face_encoding_dict
    # Update the JSON File with the new employee's data.
    name_face_encoding_file = open(name_face_encodings_path, "w")
    name_face_encoding_file.write(json.dumps(name_face_encoding_dict))
    name_face_encoding_file.close()

# Delete image locally once Encodings have been saved.
def delete_image(file_path):

    if os.path.exists(file_path):
        os.remove(file_path)

"""
    Upon Server restart, initialise existing employees' data.
    We save all employees' data in JSON format in a .txt file.
    Now, we extract them.
"""
def update_database():

    global known_face_encodings, known_face_ids, name_face_encoding_dict
    
    name_face_encoding_file = open("Face_Recognition/Name_Face_Encodings/name_face_encoding.txt", "r")
    name_face_encoding_json = name_face_encoding_file.read()
    if (name_face_encoding_json != ""):
        name_face_encoding_dict = json.loads(name_face_encoding_json)
        known_face_encodings = list(name_face_encoding_dict.values())
        known_face_ids = list(name_face_encoding_dict.keys())

# From Detected_Faces, we return the most frequent Name.
def most_probable_face_recognition(Detected_Faces):

    data = Counter(Detected_Faces)
    
    try :
        most_frequent_name = max(Detected_Faces, key=data.get)
    except :
        return "Encountered an Unexpected Error! Retrying...\n"

    return most_frequent_name


# Face Recognition Service, which accepts Frame_Mask_Detect_Pair.
# Frame_Mask_Detect_Pair = [(mask_detect, frame)]
def face_recognition_service(Frame_Mask_Detect_Pair):

    try:
        global known_face_encodings, known_face_ids
        # List of Detected Faces
        Detected_Faces = []
        face_locations = []
        face_encodings = []
        process_this_frame = True

        for pair in Frame_Mask_Detect_Pair:

            # frame is on index 1 of each tuple.
            frame = pair[1]

            # Resize frame of video to 1/4 size for faster face recognition processing.
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses).
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process alternate frame of video to save time.
            if (process_this_frame):

                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                for face_encoding in face_encodings:

                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Not an Employee"

                    # If no match found, use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_ids[best_match_index]

                    Detected_Faces.append(name)

            # Make process_this_frame False for Alternate Frame
            process_this_frame = not process_this_frame
        
        return most_probable_face_recognition(Detected_Faces)

    except :
        return "Employee Database Empty!"


if __name__ == '__main__':
    pass