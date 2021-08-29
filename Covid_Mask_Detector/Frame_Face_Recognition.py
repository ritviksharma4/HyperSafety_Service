""" Detect people wearing masks in videos
"""
from pathlib import Path
import torch
from skvideo.io import FFmpegWriter, vreader
from torchvision.transforms import Compose, Resize, ToPILImage, ToTensor

from .Common.Face_Detector import FaceDetector
from .Train import MaskDetector

# Various Trained Models
modelpath_vivek = str(Path.home()) + "/github/Mask_Detection_Face_Recognition_Service/Covid_Mask_Detector/Tensorboard/Mask_Detector/version_0/checkpoints/epoch=8-val_loss=0.08-val_acc=98.95.ckpt"
modelpath_old = str(Path.home()) + "/github/Mask_Detection_Face_Recognition_Service/Covid_Mask_Detector/Tensorboard/Mask_Detector/version_0/checkpoints/epoch=8-val_loss=0.08-val_acc=99.09.ckpt"
modelpath_new = str(Path.home()) + "/github/Mask_Detection_Face_Recognition_Service/Covid_Mask_Detector/Tensorboard/Mask_Detector/version_1/checkpoints/epoch=8-val_loss=0.08-val_acc=98.91.ckpt"

@torch.no_grad()

def detect_face_mask(frame):

    model = MaskDetector()

    # Use GPU for processing if Available. Else use CPU.
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(torch.load(modelpath_new, map_location=device)['state_dict'], strict=False)

    model = model.to(device)
    model.eval()
    
    faceDetector = FaceDetector(
        prototype = 'Covid_Mask_Detector/Models/deploy.prototxt.txt',
        model = 'Covid_Mask_Detector/Models/res10_300x300_ssd_iter_140000.caffemodel',
    )
    
    transformations = Compose([
        ToPILImage(),
        Resize((100, 100)),
        ToTensor(),
    ])

    labels = ['No Mask', 'Mask']

    faces = faceDetector.detect(frame)
    for face in faces:
        xStart, yStart, width, height = face
        
        xStart, yStart = max(xStart, 0), max(yStart, 0)
        
        # Predict mask label on extracted face
        faceImg = frame[yStart:yStart+height, xStart:xStart+width]
        output = model(transformations(faceImg).unsqueeze(0).to(device))

        # We only need the Predicted Data. Discard first returned Value.
        _, predicted = torch.max(output.data, 1)

        return labels[predicted]

if __name__ == '__main__':
    detect_face_mask()