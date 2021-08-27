from collections import Counter

Detect_Face_Mask_Output = [1,2,3,4,5,5,5,5,5,6,3,4,4,4,4,4,4,4,4,4,4]

def most_probable_mask_prediction():
    global Detect_Face_Mask_Output
    data = Counter(Detect_Face_Mask_Output)
    return max(Detect_Face_Mask_Output, key=data.get)

print(most_probable_mask_prediction())