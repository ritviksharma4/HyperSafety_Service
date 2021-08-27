import cv2
import numpy as np
import socket
import time
import pickle
import struct

""" 
    VideoCapture(0) turns on the webcam.
    VideoCapture("your_video_path") to read a specific video.
"""


# Client communicates with mask detection server.

def comms_server_mask(webcam): 

    print("In Mask Client")
    mask_client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    mask_client_socket.connect(('localhost',7089))

    while True:

        """ 
            ret stores a bool value depending on the status of the webcam.
            Frame stores each frame of the webcam
        """
        ret, frame = webcam.read()
        if (ret == True):
            data = pickle.dumps(frame)
            message_size = struct.pack("L", len(data)) 
            mask_client_socket.sendall(message_size + data)

            mask_server_reply = mask_client_socket.recv(1024)
            mask_server_reply = mask_server_reply.decode()

            if (mask_server_reply == "Still Processing..."):
                pass
            else :
                print("Server Reply :", mask_server_reply)

            if (mask_server_reply == "0"):
                mask_client_socket.close()
                comms_server_face_rec(webcam)
        else :
            print("Web-Cam could not be opened")
        

            
# Client communicates with the face recog server if mask is not detected.

def comms_server_face_rec(webcam):

    print("Client is in face rec")
    face_rec_client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    face_rec_client_socket.connect(('localhost',7090))

    while True:
        ret,frame = webcam.read()
        # start = time.time()
        # while (time.time() - start < 1):
        if (ret == True):
            data = pickle.dumps(frame)
            message_size = struct.pack("L", len(data)) 
            face_rec_client_socket.sendall(message_size + data)

            face_rec_server_reply = face_rec_client_socket.recv(1024)
            face_rec_server_reply = face_rec_server_reply.decode()
            print("Face Rec Server Sent :", face_rec_server_reply)
        
        face_rec_client_socket.close()
    
        comms_server_mask(webcam)

if __name__ == '__main__':

    """ 
        VideoCapture(0) turns on the webcam.
        VideoCapture("your_video_path") to read a specific video.
    """
    
    webcam = cv2.VideoCapture(0)

    comms_server_mask(webcam)