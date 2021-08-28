from collections import Counter

Frame_Mask_detect_Pair = [("asdf", 1),("d", 2),("acf", 3),("f", 4),("f", 5),("af", 6),("acf", 7),("acf", 8),("acf", 9)]
Output_List = []

def create_Output_List():

    global Frame_Mask_detect_Pair, Output_List
    for pair in Frame_Mask_detect_Pair:
        Output_List.append(pair[0])

def most_probable_mask_prediction():
    # print("Finding most Probable..")
    create_Output_List()
    global Output_List
    data = Counter(Output_List)
    print("Data :", data)
    return max(Output_List, key=data.get)

if __name__ == '__main__':
    print("Most Probable :", most_probable_mask_prediction())