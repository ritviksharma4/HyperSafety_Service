""" Detect people wearing masks in videos
"""
from pathlib import Path

import click
import cv2
import torch
from skvideo.io import FFmpegWriter, vreader
from torchvision.transforms import Compose, Resize, ToPILImage, ToTensor

from .common.facedetector import FaceDetector
from .train import MaskDetector

# Models Trained
modelpath_vivek = str(Path.home()) + "/github/Multi_Server_Video_Streaming/covid_mask_detector/tensorboard/mask-detector/version_0/checkpoints/epoch=8-val_loss=0.08-val_acc=98.95.ckpt"
modelpath_old = str(Path.home()) + "/github/Multi_Server_Video_Streaming/covid_mask_detector/tensorboard/mask-detector/version_0/checkpoints/epoch=8-val_loss=0.08-val_acc=99.09.ckpt"
modelpath_new = str(Path.home()) + "/github/Multi_Server_Video_Streaming/covid_mask_detector/tensorboard/mask-detector/version_1/checkpoints/epoch=8-val_loss=0.08-val_acc=98.91.ckpt"

@torch.no_grad()

def detectFace_Mask(frame):

    model = MaskDetector()
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(torch.load(modelpath_new, map_location=device)['state_dict'],
                          strict=False)
    # model.load_state_dict(torch.load(modelpath_old, map_location=device)['state_dict'],
    #                     strict=False)
    model = model.to(device)
    model.eval()
    
    faceDetector = FaceDetector(
        prototype='covid_mask_detector/models/deploy.prototxt.txt',
        model='covid_mask_detector/models/res10_300x300_ssd_iter_140000.caffemodel',
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
        
        # predict mask label on extracted face
        faceImg = frame[yStart:yStart+height, xStart:xStart+width]
        output = model(transformations(faceImg).unsqueeze(0).to(device))
        _, predicted = torch.max(output.data, 1)

        return labels[predicted]

if __name__ == '__main__':
    detectFace_Mask()
