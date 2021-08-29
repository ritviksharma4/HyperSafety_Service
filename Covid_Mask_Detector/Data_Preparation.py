""" Add images into a pandas Dataframe
"""
from pathlib import Path

import pandas as pd
from google_drive_downloader import GoogleDriveDownloader as gdd
from tqdm import tqdm

# download dataset from link provided by
# https://github.com/ThisIsTeddyBear/facedataset.git (TO BE MADE PUBLIC BEFORE USE)

"""
UNCOMMENT THESE IF USING ANOTHER DATASET
datasetPath = Path('Covid_Mask_Detector/Data/mask.zip')
gdd.download_file_from_google_drive(file_id='1UlOk6EtiaXTHylRUx2mySgvJX9ycoeBp',
                                    dest_path=str(datasetPath),
                                    unzip=True)
# delete zip file
datasetPath.unlink()

"""

datasetPath = Path('Covid_Mask_Detector/Data/self-built-masked-face-recognition-dataset')
maskPath = datasetPath/'AFDB_masked_face_dataset'
nonMaskPath = datasetPath/'AFDB_face_dataset'
maskDF = pd.DataFrame()

# Label Mask images with 1 or True.
for subject in tqdm(list(maskPath.iterdir()), desc='mask photos'):
    for imgPath in subject.iterdir():
        maskDF = maskDF.append({
            'image': str(imgPath),
            'mask': 1
        }, ignore_index=True)

# Label No Mask images with 0 or False.
for subject in tqdm(list(nonMaskPath.iterdir()), desc='non mask photos'):
    for imgPath in subject.iterdir():
        maskDF = maskDF.append({
            'image': str(imgPath),
            'mask': 0
        }, ignore_index=True)

dfName = 'Covid_Mask_Detector/Data/mask_df.csv'
print(f'Saving Dataframe to: {dfName}')
maskDF.to_csv(dfName)