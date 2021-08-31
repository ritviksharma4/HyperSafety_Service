import face_recognition
import cv2
import numpy as np
from collections import Counter
from pathlib import Path
import json

known_face_encodings = []
known_face_names = []
name_face_encoding_dict = {}

"""
    For adding new employee, save the file in Employee_Images in form of
    your_client_name.jpg, e.g. Vivek Nichani.jpg.
"""
def add_employee_to_encodings(employee_name):

    global known_face_encodings, known_face_names, name_face_encoding_dict
    
    employee_image = face_recognition.load_image_file(str(Path.home()) + 
                                                    "/github/Mask_Detection_Face_Recognition_Service/" + 
                                                    "Face_Recognition/Employee_Images/" + 
                                                    employee_name + ".jpg")

    employee_face_encoding = face_recognition.face_encodings(employee_image)[0]

    known_face_encodings.append(employee_face_encoding)
    known_face_names.append(employee_name)

    name_face_encoding_dict[employee_name] = employee_face_encoding.tolist()
    
    # Update the JSON File with the new employee's data.
    name_face_encoding_file = open("Face_Recognition/Name_Face_Encodings/name_face_encoding.txt", "w")
    name_face_encoding_file.write(json.dumps(name_face_encoding_dict))
    name_face_encoding_file.close()

"""
    Upon Server restart, initialise existing employees' data.
    We save all employees' data in JSON format in a .txt file.
    Now, we extract them.
"""
def initialise_database():

    global known_face_encodings, known_face_names

    name_face_encoding_file = open("Face_Recognition/Name_Face_Encodings/name_face_encoding.txt", "r")
    name_face_encoding_json = name_face_encoding_file.read()
    name_face_encoding_dict = json.loads(name_face_encoding_json)

    known_face_encodings = list(name_face_encoding_dict.values())
    known_face_names = list(name_face_encoding_dict.keys())

    # name_list = ["Akul Jain", "Harsh Ambasta", "Ritvik Sharma", "Steve Aby", "Vivek Nichani"]
    # for name in name_list:
    #     add_employee_to_encodings(name)


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
                    name = known_face_names[best_match_index]

                Detected_Faces.append(name)

        # Make process_this_frame False for Alternate Frame
        process_this_frame = not process_this_frame
    
    return most_probable_face_recognition(Detected_Faces)


if __name__ == '__main__':
    pass