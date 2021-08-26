import pickle
import socket
import struct
import cv2

def comms_client():

    HOST = ''
    PORT = 8090

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)

    print('Face Recognition Server is Running...\n')

    client_socket, addr = server_socket.accept()

    data = b''  
    payload_size = struct.calcsize("L")  
    
    while True:
        print("Got Connection from :", addr)

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
        
        # Display
        cv2.imshow('Face Recognition', frame)
        cv2.waitKey(1)


if __name__ == '__main__':
    comms_client()