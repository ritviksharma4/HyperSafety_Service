import cv2
import socket
import pickle
import struct

mask_client_socket = None

# Creating a Client Socket.
def create_client_socket():

    global mask_client_socket

    mask_client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    mask_client_socket.connect(('localhost',7089))


# Client communicates with Mask-Detection_Face-Recognition server.
def mask_detect_face_recog_client(camera): 

    global mask_client_socket
    
    while (True):

        """ 
            is_webcam_open stores a bool value depending on the status of the webcam.
            frame stores each frame of the webcam.
        """
        is_webcam_open, frame = camera.read()
        if (is_webcam_open):

            # Data is Serialized for ease of re-construction of frames in server side.
            data = pickle.dumps(frame)

            # L denotes larger frames of size 2^32.
            # H denotes smaller frames of size 2^16.
            message_size = struct.pack("L", len(data)) 
            mask_client_socket.sendall(message_size + data)

            mask_server_reply = mask_client_socket.recv(1024)
            mask_server_reply = mask_server_reply.decode()

            # Discarding this message on client side as server is still processing.
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

    # Launching Client with camera switched ON.
    try : 
        
        create_client_socket()
        camera = cv2.VideoCapture(0)
        mask_detect_face_recog_client(camera)

    # Shutting the Client Down.
    except KeyboardInterrupt:

        print("\nClosing Client...\n")
        mask_client_socket.close()