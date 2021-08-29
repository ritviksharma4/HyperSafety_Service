import cv2
from .Frame_Face_Recognition import detectFace_Mask

def sendFrames(webcam):
    while True:
        ret, frame = webcam.read()
        if (ret == True):
            # data = pickle.dumps(frame)
            # message_size = struct.pack("L", len(data)) 
            # detectFace_Mask(message_size + data)
            mask_detect = detectFace_Mask(frame)
            if (mask_detect == None):
                mask_detect = "No Face Detected"
            print("Mask Detected or Not :", mask_detect)

if __name__ == '__main__':

    webcam = cv2.VideoCapture(0)
    if (webcam.isOpened() == False):
        print("Error Opening Web-Cam.")
    
    sendFrames(webcam)