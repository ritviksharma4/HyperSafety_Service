import socketio
from Face_Recognition.Face_Rec_Frames import imgURL_to_img, del_employee_from_encodings

sio = socketio.Client()

def connectNodejs():
    print("Connecting...")
    sio.connect("http://localhost:7091")
    print("Connected to NodeJS")

@sio.on("Employee Added Successfully.")
def employee_added(data):
    print("Employee Added Successfully.")
    empID = data["empID"]
    imageURL = data["imageURL"]
    imgURL_to_img(empID, imageURL)

@sio.on("Employee Successfully Deleted.")
def employee_deleted(data):
    print("Employee Successfully Deleted.")
    empID = data["empID"]
    del_employee_from_encodings(empID)