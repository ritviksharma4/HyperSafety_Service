import pickle
import socket
import struct
from collections import Counter
import cv2
from covid_mask_detector.frame_face_rec import detectFace_Mask
from Face_Recognition_Project.face_recognition.face_recognition_webcam_test import face_recognition_service

server_socket = None
Frame_Mask_Detect_Pair = []
Output_List = []

def create_Output_List():

    global Frame_Mask_Detect_Pair, Output_List
    for pair in Frame_Mask_Detect_Pair:
        Output_List.append(pair[0])

def most_probable_mask_detection_face_recognition():
    print("Finding most Probable..")
    create_Output_List()
    global Output_List
    data = Counter(Output_List)
    most_frequent = max(Output_List, key=data.get)
    Output_List = []
    return most_frequent

def create_server_socket():
    global server_socket
    HOST = ''
    PORT = 7089
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)

# Server communicates with client and accepts video frames
def comms_client():

    global Frame_Mask_Detect_Pair, server_socket

    client_socket, addr = server_socket.accept()

    data = b''  
    payload_size = struct.calcsize("L")  
    
    print("Got Connection from :", addr)

    while True:
        # Retrieve message size
        while len(data) < payload_size:
            data += client_socket.recv(4096)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0]  
        
        # Retrieve all data based on message size
        while len(data) < msg_size:
            data += client_socket.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]
        
        # Extract frame
        frame = pickle.loads(frame_data)

        # Pass the frame to the mask detection model to
        # check if the person is wearing a mask or not
        error_flag = 0
        try :
            mask_detect = detectFace_Mask(frame)
        except ValueError:
            error_flag = 1
            mask_detect = "NOOOOOOOOOOOOOOOOOOOOOOOOOOO FACE DETECTEDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD"

        print("Mask_Detect :", mask_detect)
        if (error_flag == 1):
            mask_detect = "No Face Detected"
            error_flag = 0

        if (mask_detect == None):
            mask_detect = "No Face Detected"        
        # elif (mask_detect == "No Mask"):
        #     face_detect = face_recognition_service(frame)
        #     print("Name :", face_detect)
            # Frame_Mask_Detect_Pair = []
        
        Frame_Mask_Detect_Pair.append((mask_detect, frame))
        
        print("Mask Prediction :", mask_detect)
        # print("Output :", Frame_Mask_Detect_Pair)

        print("Output Lists Size:", len(Frame_Mask_Detect_Pair))
        
        """
            For every 25 predictions for the same person, 
            we pick the most frequent prediction and send
            the result to the client.
        """
        if (len(Frame_Mask_Detect_Pair) == 25 or (mask_detect == "No Face Detected" and len(Frame_Mask_Detect_Pair) > 0)):
            final_mask_detection = most_probable_mask_detection_face_recognition()
            print("Found Most Probable :", final_mask_detection)

            if (final_mask_detection == "No Mask"):
                face_recog_reply = face_recognition_service(Frame_Mask_Detect_Pair)
                print("Face Recog Reply : ", face_recog_reply)
                msg_2_client = final_mask_detection + "\nPerson Found : " + face_recog_reply
                encoded_msg_2_client = msg_2_client.encode()
                client_socket.send(encoded_msg_2_client)
                Frame_Mask_Detect_Pair = []
                # comms_client()
                # client_socket.close()
            
            elif (final_mask_detection == "Mask"):
                msg_2_client = "Wearing a Mask"
                encoded_msg_2_client = msg_2_client.encode()
                Frame_Mask_Detect_Pair = []
                client_socket.send(encoded_msg_2_client)

            elif (final_mask_detection == "No Face Detected"):
                msg_2_client = "Still Processing..."
                encoded_msg_2_client = msg_2_client.encode()
                Frame_Mask_Detect_Pair = []
                client_socket.send(encoded_msg_2_client)
            
            
            Frame_Mask_Detect_Pair = []

        else :
            print("here")
            msg_2_client = "Still Processing..."
            encoded_msg_2_client = msg_2_client.encode()
            client_socket.send(encoded_msg_2_client)


if __name__ == '__main__':
    try :
        create_server_socket()
        print('Mask Detection - Face Recognition Server is Running...\n')
        comms_client()
    except KeyboardInterrupt:
        server_socket.close()
        print("\n\nMask Detection - Face Recognition Server has Shutdown.\n")