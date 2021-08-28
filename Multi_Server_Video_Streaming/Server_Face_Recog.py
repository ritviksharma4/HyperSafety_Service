import pickle
import socket
import struct
import cv2
from collections import Counter
from Face_Recognition_Project.face_recognition.face_recognition_webcam import face_recognition_service

server_socket = None

Detected_Faces_List = []

def most_probable_mask_prediction():
    print("Finding most Probable..")
    global Detected_Faces_List
    data = Counter(Detected_Faces_List)
    return max(Detected_Faces_List, key=data.get)

def create_server_socket():
    global server_socket
    HOST = ''
    PORT = 7090
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)

def comms_client():

    global server_socket, Detected_Faces_List

    client_socket, addr = server_socket.accept()

    print("Got Connection from :", addr)

    data = b''  
    payload_size = struct.calcsize("L")  
    
    while True:

        while len(data) < payload_size:
            data += client_socket.recv(4096)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0]  

        while len(data) < msg_size:
            data += client_socket.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)

        name_prediction_list = face_recognition_service(frame)
        print("Server_Face_Recog Recieved :", name_prediction_list)
        
        for name in name_prediction_list:
            Detected_Faces_List.append(name)

        if (len(Detected_Faces_List) > 0):

            final_face_recog = most_probable_mask_prediction()
            msg_2_client = final_face_recog

            print("Msg to client :", msg_2_client)

            encoded_msg_2_client = msg_2_client.encode()
            client_socket.send(encoded_msg_2_client)
            Detected_Faces_List = []

            # comms_client()

        # msg_2_client = "Person Found"

        # if (msg_2_client == "Person Found"):
            # encoded_msg_2_client = msg_2_client.encode()
            # client_socket.send(encoded_msg_2_client)
            # comms_client()

        # client_socket.close()
        
        # # Display
        # cv2.imshow('Face Recognition', frame)
        # cv2.waitKey(1)


if __name__ == '__main__':
    create_server_socket()
    print('Face Recognition Server is Running...\n')
    comms_client()