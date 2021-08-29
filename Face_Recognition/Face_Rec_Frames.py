import face_recognition
import cv2
import numpy as np
from collections import Counter
from pathlib import Path

# Loading Employee's Images For Face Recognition Model to Recognize

ritvik_image = face_recognition.load_image_file(str(Path.home()) + "/github/Mask_Detection_Face_Recognition_Service/Face_Recognition/Employee_Images/Ritvik Sharma.jpg")
ritvik_face_encoding = face_recognition.face_encodings(ritvik_image)[0]

akul_image = face_recognition.load_image_file(str(Path.home()) + "/github/Mask_Detection_Face_Recognition_Service/Face_Recognition/Employee_Images/Akul Jain.jpg")
akul_face_encoding = face_recognition.face_encodings(akul_image)[0]

steve_image = face_recognition.load_image_file(str(Path.home()) + "/github/Mask_Detection_Face_Recognition_Service/Face_Recognition/Employee_Images/Steve Aby.jpg")
steve_face_encoding = face_recognition.face_encodings(steve_image)[0]

vivek_image = face_recognition.load_image_file(str(Path.home()) + "/github/Mask_Detection_Face_Recognition_Service/Face_Recognition/Employee_Images/Vivek Nichani.jpg")
vivek_face_encoding = face_recognition.face_encodings(vivek_image)[0]

harsh_image = face_recognition.load_image_file(str(Path.home()) + "/github/Mask_Detection_Face_Recognition_Service/Face_Recognition/Employee_Images/Harsh Ambasta.jpg")
harsh_face_encoding = face_recognition.face_encodings(harsh_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    ritvik_face_encoding,
    akul_face_encoding,
    steve_face_encoding,
    vivek_face_encoding,
    harsh_face_encoding
]

known_face_names = [
    "Ritvik Sharma",
    "Akul Jain",
    "Steve Aby",
    "Vivek Nichani",
    "Harsh Ambasta"
]

# List of Detected Faces
Detected_Faces = []


# From Detected_Faces, we return the most frequent Name.
def most_probable_face_recognition():

    global Detected_Faces

    data = Counter(Detected_Faces)

    try :
        most_frequent_name = max(Detected_Faces, key=data.get)
    except :
        return "Encountered an Unexpected Error! Retrying...\n"

    Detected_Faces = []
    return most_frequent_name


# Face Recognition Service, which accepts Frame_Mask_Detect_Pair.
# Frame_Mask_Detect_Pair = [(mask_detect, frame)]
def face_recognition_service(Frame_Mask_Detect_Pair):

    global Detected_Faces

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
    
    return most_probable_face_recognition()

if __name__ == '__main__':
    pass