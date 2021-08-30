import pickle
import socket
import struct
import threading
from collections import Counter
from Covid_Mask_Detector.Frame_Face_Recognition import detect_face_mask
from Face_Recognition.Face_Rec_Frames import face_recognition_service


"""
    Frame_Mask_Detect_Pair is a List of Tuples. Each Pair is (mask_detect, frame).
    e.g ("Mask", frame).
    We create an Output_List which stores only mask_detect from Frame_Mask_Detect_Pair.
"""
def create_mask_detect_Output_List(Frame_Mask_Detect_Pair):

    Output_List = []
    
    for pair in Frame_Mask_Detect_Pair:
        Output_List.append(pair[0])
    
    return Output_List


# From Output_List, we return the most frequent mask_detect.
def most_probable_mask_detection(Frame_Mask_Detect_Pair):

    Output_List = create_mask_detect_Output_List(Frame_Mask_Detect_Pair)
    data = Counter(Output_List)

    try :
        most_frequent_mask_detect = max(Output_List, key=data.get)
    except :
        return "Encountered an Unexpected Error! Retrying...\n"

    return most_frequent_mask_detect


# Creating a Server Socket.
def create_server_socket():

    HOST = ''
    PORT = 7089
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)

    return server_socket


# Sending required message from Server to Client.
def send_result_to_client(client_socket, msg_to_client):
    
    encoded_msg_to_client = msg_to_client.encode()
    client_socket.send(encoded_msg_to_client)

def create_client_connection(server_socket):
    client_socket, client_address = server_socket.accept()
    thread_unq_client = threading.Thread(target = mask_detect_face_recog_server, 
                                        args = (server_socket, client_socket, client_address))
    thread_unq_client.start()
    create_client_connection(server_socket)


# Server communicates with Client and accepts camera frames.
def mask_detect_face_recog_server(server_socket, client_socket, client_address):

    Frame_Mask_Detect_Pair = []

    # Accepting Frames in batch size of 2^32 ("L").
    data = b''  
    payload_size = struct.calcsize("L")  
    
    print("\nGot Connection from :", client_address)

    while (True):

        while (len(data) < payload_size):
            msg_frm_client = client_socket.recv(4096)

            """
                In Case Client experiences some errors and has to restart or
                Client turns off the system, we disconnect the Client and make the 
                Server Ready for next Connection.
            """
            if (msg_frm_client == b'Closing Client'):
                print("Client Disconnected :", client_address)
                client_socket.close()
                return

            data += msg_frm_client

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0]  
        
        while (len(data) < msg_size):
            data += client_socket.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]
        
        # Now we have the frame and can begin predicting.
        frame = pickle.loads(frame_data)

        # ValueError handling
        error_flag = 0
        try :
            mask_detect = detect_face_mask(frame)
        except ValueError:
            error_flag = 1
            mask_detect = "*** NO FACE DETECTED! ***"

        if (error_flag == 1):
            mask_detect = "No Face Detected"
            error_flag = 0

        # Model Predicts None if no face detected
        if (mask_detect == None):
            mask_detect = "No Face Detected" 
        
        # For every person, we store their mask_detect output and
        # their frame in case we need to use Face Recognition.
        Frame_Mask_Detect_Pair.append((mask_detect, frame))
        
        print("Mask Prediction :", mask_detect, " address :", client_address)

        
        """
            For every 25 predictions for the same person, we pick the most frequent 
            prediction and send the result to the client.
            If the person walks away from the camera before 25 predictions are made, 
            we make a final prediction based on how many predictions were already 
            made for him.
        """
        if (len(Frame_Mask_Detect_Pair) == 25 or (mask_detect == "No Face Detected" 
                                                and len(Frame_Mask_Detect_Pair) > 0)):

            final_mask_detection = most_probable_mask_detection(Frame_Mask_Detect_Pair)
            print("Most Probable Mask Detection :", final_mask_detection, " address :", client_address)

            # If person is found without a mask, then we send the same set of
            # frames for Face Recognition. 
            if (final_mask_detection == "No Mask"):
                face_recog_reply = face_recognition_service(Frame_Mask_Detect_Pair)
                msg_to_client = "Person Found Without Mask : " + face_recog_reply         

            
            elif (final_mask_detection == "Mask"):
                msg_to_client = "Wearing a Mask"

            # This can happen when people walk away from the camera or
            # while waiting for the next person to enter.
            elif (final_mask_detection == "No Face Detected"):
                msg_to_client = "Still Processing..."
            
            Frame_Mask_Detect_Pair = []

        else :
            msg_to_client = "Still Processing..."
            
        # Prediction / Required Message is then sent to the Client.
        send_result_to_client(client_socket, msg_to_client)


if __name__ == '__main__':

    # Launching the Mask Detection - Face Recognition Server.
    try :
        server_socket = create_server_socket()
        print('Mask Detection - Face Recognition Server is Running...\n')
        # mask_detect_face_recog_server(server_socket)
        create_client_connection(server_socket)

    # Shutting the Mask Detection - Face Recognition Server Down.
    except KeyboardInterrupt:
        server_socket.close()
        print("\n\nMask Detection - Face Recognition Server has Shutdown.\n")