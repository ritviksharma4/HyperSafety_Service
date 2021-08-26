import cv2
import numpy as np
import socket
import time
import pickle
import struct


def comms_server_mask(webcam):

    mask_client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    mask_client_socket.connect(('localhost',8089))

    while True:

        ret, frame = webcam.read()
        if (ret == True):
            data = pickle.dumps(frame)
            message_size = struct.pack("L", len(data)) 
            mask_client_socket.sendall(message_size + data)

            mask_server_reply = mask_client_socket.recv(1024)
            mask_server_reply = mask_server_reply.decode()

            if (mask_server_reply == "0"):
                comms_server_face_rec()

def comms_server_face_rec():

    # start = time.time()
    # while (time.time() - start < 5):
    print("Client is in face rec")
    face_rec_client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    face_rec_client_socket.connect(('localhost',8090))

    while True:
        ret,frame = webcam.read()
        if (ret == True):
            data = pickle.dumps(frame)
            message_size = struct.pack("L", len(data)) 
            face_rec_client_socket.sendall(message_size + data)
    
    # comms_server_mask()

if __name__ == '__main__':

    webcam = cv2.VideoCapture(0)

    if (webcam.isOpened() == False):
        print("Error Opening Web-Cam.")

    comms_server_mask(webcam)