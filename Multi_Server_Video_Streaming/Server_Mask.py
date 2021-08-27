import pickle
import socket
import struct
from collections import Counter
import cv2
from covid_mask_detector.frame_face_rec import detectFace_Mask

# Store 50 mask detection results to find the most probable outcome
Detect_Face_Mask_Output = []

server_socket = None

def most_probable_mask_prediction():
    print("Finding most Probable..")
    global Detect_Face_Mask_Output
    data = Counter(Detect_Face_Mask_Output)
    return max(Detect_Face_Mask_Output, key=data.get)

def create_server_socket():
    global server_socket
    HOST = ''
    PORT = 7089
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)

# Server communicates with client and accepts video frames
def comms_client():

    global Detect_Face_Mask_Output, server_socket

    # HOST = ''
    # PORT = 8089

    # server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_socket.bind((HOST, PORT))
    # server_socket.listen(10)

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
        
        mask_detect = detectFace_Mask(frame)
        if (mask_detect == None):
            mask_detect = "No Face Detected"
            # Detect_Face_Mask_Output = []

        Detect_Face_Mask_Output.append(mask_detect)
        
        print("Mask Prediction :", mask_detect)
        # print("Output :", Detect_Face_Mask_Output)

        print("Output Lists Size:", len(Detect_Face_Mask_Output))
        
        """
            For every 51 predictions for the same person, 
            we pick the most frequent prediction and send
            the result to the client.
        """
        if (len(Detect_Face_Mask_Output) == 51 or (mask_detect == "No Face Detected" and len(Detect_Face_Mask_Output) > 0)):
            final_mask_detection = most_probable_mask_prediction()
            print("Found Most Probable :", final_mask_detection)

            if (final_mask_detection == "No Mask"):
                msg_2_client = "0"
                encoded_msg_2_client = msg_2_client.encode()
                client_socket.send(encoded_msg_2_client)
                Detect_Face_Mask_Output = []
                comms_client()
                # client_socket.close()
            
            elif (final_mask_detection == "Mask"):
                msg_2_client = "1"
                encoded_msg_2_client = msg_2_client.encode()
                Detect_Face_Mask_Output = []
                client_socket.send(encoded_msg_2_client)
            
            elif (final_mask_detection == "No Face Detected"):
                msg_2_client = "Still Processing..."
                encoded_msg_2_client = msg_2_client.encode()
                client_socket.send(encoded_msg_2_client)
            
            Detect_Face_Mask_Output = []

        else :
            msg_2_client = "Still Processing..."
            encoded_msg_2_client = msg_2_client.encode()
            client_socket.send(encoded_msg_2_client)


if __name__ == '__main__':
    create_server_socket()
    print('Mask Detection Server is Running...\n')
    comms_client()