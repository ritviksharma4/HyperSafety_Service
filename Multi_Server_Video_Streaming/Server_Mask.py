import pickle
import socket
import struct
import cv2

def comms_client():

    HOST = ''
    PORT = 8089

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)

    print('Mask Detection Server is Running...\n')

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

        # frame_data = data[:msg_size]
        # data = data[msg_size:]
        # frame = pickle.loads(frame_data)

        msg_2_client = "0"
        encoded_msg_2_client = msg_2_client.encode()
        print("Sending Encoded msg to client")
        client_socket.send(encoded_msg_2_client)


if __name__ == '__main__':
    comms_client()