import cv2
import numpy as np
import socket
import pickle
import struct

""" 
    VideoCapture(0) turns on the webcam.
    VideoCapture("your_video_path") to read a specific video.
"""

mask_client_socket = None

# Client communicates with mask detection server.

def comms_server_mask(webcam): 

    global mask_client_socket
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

        else :
            print("Web-Cam could not be opened")


if __name__ == '__main__':

    """ 
        VideoCapture(0) turns on the webcam.
        VideoCapture("your_video_path") to read a specific video.
    """
    try : 

        webcam = cv2.VideoCapture(0)
        comms_server_mask(webcam)

    except KeyboardInterrupt:
        print("\nClosing Client...\n")
        mask_client_socket.close()